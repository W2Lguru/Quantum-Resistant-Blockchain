"""Educational Qiskit demonstration of Shor's algorithm for N = 15."""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Any

DISCLAIMER = (
    "Educational toy demonstration only. This demonstration does not break "
    "real Bitcoin, ECDSA, or real cryptographic keys. Real-world cryptographic "
    "key sizes require quantum resources far beyond this demonstration."
)


def _c_amod15(a: int, power: int):
    from qiskit import QuantumCircuit

    if a not in {2, 4, 7, 8, 11, 13}:
        raise ValueError("educational circuit supports a in {2, 4, 7, 8, 11, 13}")
    u = QuantumCircuit(4)
    for _ in range(power):
        if a in {2, 13}:
            u.swap(2, 3)
            u.swap(1, 2)
            u.swap(0, 1)
        if a in {7, 8}:
            u.swap(0, 1)
            u.swap(1, 2)
            u.swap(2, 3)
        if a in {4, 11}:
            u.swap(1, 3)
            u.swap(0, 2)
        if a in {7, 11, 13}:
            for q in range(4):
                u.x(q)
    gate = u.to_gate()
    gate.name = f"{a}^{power} mod 15"
    return gate.control()


def _inverse_qft(n: int):
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(n)
    for qubit in range(n // 2):
        qc.swap(qubit, n - qubit - 1)
    for j in range(n):
        for m in range(j):
            qc.cp(-math.pi / float(2 ** (j - m)), m, j)
        qc.h(j)
    qc.name = "IQFT"
    return qc


def build_order_finding_circuit(a: int = 2, counting_qubits: int = 8):
    from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

    n_count = counting_qubits
    counting = QuantumRegister(n_count, "counting")
    work = QuantumRegister(4, "work")
    classic = ClassicalRegister(n_count, "c")
    qc = QuantumCircuit(counting, work, classic)
    qc.h(counting)
    qc.x(work[0])
    for q in range(n_count):
        qc.append(_c_amod15(a, 2**q), [counting[q], *work])
    qc.append(_inverse_qft(n_count), counting)
    qc.measure(counting, classic)
    return qc


def _period_from_phase(phase: float, n: int) -> int:
    if phase == 0:
        return 0
    frac = Fraction(phase).limit_denominator(n)
    return int(frac.denominator)


def _factors_from_order(a: int, n: int, r: int) -> tuple[int, int] | None:
    if r <= 0 or r % 2 != 0:
        return None
    guess1 = math.gcd(pow(a, r // 2, n) - 1, n)
    guess2 = math.gcd(pow(a, r // 2, n) + 1, n)
    if guess1 in (1, n) and guess2 in (1, n):
        return None
    p = guess1 if 1 < guess1 < n else None
    q = guess2 if 1 < guess2 < n else None
    if p and q:
        return int(p), int(q)
    if p:
        return int(p), n // int(p)
    if q:
        return n // int(q), int(q)
    return None


def run_shor_demo(n: int = 15, a: int = 2, shots: int = 256) -> dict[str, Any]:
    """Run a small-scale order-finding circuit, then classical post-processing."""

    if n != 15:
        return {
            "ok": False,
            "error": "this educational circuit is limited to N = 15",
            "disclaimer": DISCLAIMER,
        }
    if math.gcd(a, n) != 1:
        return {
            "ok": False,
            "error": "base a must be coprime to N",
            "disclaimer": DISCLAIMER,
        }

    try:
        from qiskit import transpile
        from qiskit_aer import AerSimulator
    except Exception as exc:
        return {
            "ok": False,
            "error": f"qiskit/qiskit-aer unavailable: {exc}",
            "disclaimer": DISCLAIMER,
        }

    counting_qubits = 8
    circuit = build_order_finding_circuit(a=a, counting_qubits=counting_qubits)
    simulator = AerSimulator()
    compiled = transpile(circuit, simulator)
    result = simulator.run(compiled, shots=shots).result()
    counts = dict(result.get_counts())

    ranked = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    recovered = None
    recovered_order = None
    attempts: list[dict[str, Any]] = []
    for bitstring, count in ranked[:12]:
        decimal = int(bitstring, 2)
        phase = decimal / (2**counting_qubits)
        r = _period_from_phase(phase, n)
        factors = _factors_from_order(a, n, r) if r else None
        attempts.append(
            {
                "bitstring": bitstring,
                "shots": int(count),
                "phase": phase,
                "estimated_order": r,
                "factors": factors,
            }
        )
        if factors and recovered is None:
            recovered = factors
            recovered_order = r
            break

    return {
        "ok": recovered is not None,
        "n": n,
        "base": a,
        "shots": shots,
        "counting_qubits": counting_qubits,
        "circuit_depth": int(compiled.depth()),
        "top_counts": ranked[:8],
        "attempts": attempts,
        "order": recovered_order,
        "factors": recovered,
        "quantum_stage": "phase estimation / order finding on AerSimulator",
        "classical_stage": "continued fractions plus gcd post-processing",
        "disclaimer": DISCLAIMER,
        "note": (
            "The quantum circuit estimates a phase related to the order of a "
            "modulo N. Factors are recovered classically from that order."
        ),
    }


def expected_classical_factors(n: int = 15, a: int = 2) -> dict[str, Any]:
    """Deterministic classical check used by tests when the simulator is unavailable."""

    r = 1
    value = a % n
    while value != 1:
        value = (value * a) % n
        r += 1
        if r > n * n:
            break
    factors = _factors_from_order(a, n, r)
    return {"n": n, "base": a, "order": r, "factors": factors}
