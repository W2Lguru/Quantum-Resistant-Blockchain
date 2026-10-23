# Design and Performance Evaluation of a Quantum-Resistant Blockchain using ML-DSA

**Short Title:** Quantum-Resistant Blockchain  
**Academic Prototype:** 2nd-Year Computer Science and Engineering Research Project

---

## Abstract

Modern blockchain networks rely primarily on classical public-key cryptography—predominantly the Elliptic Curve Digital Signature Algorithm (ECDSA) over curves such as `secp256k1`—to authenticate transactions and guarantee non-repudiation. However, a sufficiently powerful fault-tolerant quantum computer executing Shor's algorithm could solve the elliptic-curve discrete logarithm problem in polynomial time $\mathcal{O}(n^3)$, breaking transaction authentication.

This project designs, implements, and evaluates an educational blockchain architecture integrating **ML-DSA-44** (Module-Lattice Digital Signature Algorithm, standardized under NIST FIPS 204 / CRYSTALS-Dilithium) alongside conventional **ECDSA**. Using a common wallet abstraction, the system measures empirical performance and storage trade-offs across key generation, signing latency, verification latency, key/signature sizes, and blockchain ledger expansion on the same hardware. Additionally, the system provides ten interactive security attack demonstrations, scrypt-based password-protected wallet storage, and an educational Qiskit quantum circuit demonstrating Shor's order-finding mechanism for $N=15$.

---

## Problem Statement

Current blockchain systems commonly use classical public-key cryptography such as ECDSA for transaction authentication. A sufficiently capable fault-tolerant quantum computer running Shor's algorithm threatens cryptographic schemes based on discrete logarithms.

This project investigates:
> *"How can post-quantum digital signatures be integrated into a blockchain, and what performance and storage trade-offs result when compared with conventional ECDSA signatures?"*

---

## High-Level Research Story

```
TODAY:
ECDSA (secp256k1) ──▶ Transaction Signing ──▶ Blockchain Authentication
       │
       ▼
QUANTUM FUTURE:
Fault-Tolerant Quantum Computer ──▶ Shor's Algorithm ──▶ Discrete Logarithms Solved in BQP
       │
       ▼
OUR APPROACH:
ML-DSA-44 (NIST FIPS 204) ──▶ Module-Lattice Signatures ──▶ Quantum-Resistant Blockchain Prototype
       │
       ▼
EVALUATION:
Security Verification  +  Cryptographic Latency  +  Ledger Storage Overhead
```

---

## Objectives

1. **Custom Educational Blockchain Core:** Develop a Proof-of-Authority (PoA) blockchain with authorized validators (`Validator1`, `Validator2`, `Validator3`), deterministic SHA-256 block hashing (excluding the hash field), and strict hash-linked immutability.
2. **Cryptographic Signatures Behind Common Interface:** Implement both classical ECDSA (`secp256k1`) and genuine post-quantum ML-DSA-44 (`liboqs`) conforming to the `BaseWallet` interface.
3. **Decoupled Architecture:** Ensure the blockchain engine is decoupled from cryptographic primitives using the `CryptoFactory` design pattern.
4. **Comprehensive Security Center:** Build automated detection and rejection for 10 attack vectors (tampering, forgery, replay, double spending, unauthorized validators, invalid blocks, algorithm mismatch, malformed inputs).
5. **Application-Layer Password Protection:** Implement scrypt password hashing and Fernet encryption for wallet access, ensuring private keys are never exposed in plaintext, logs, blocks, or the UI.
6. **Empirical Benchmarking Suite:** Benchmark key generation, signing, verification, and ledger storage at 10, 50, 100, and 500 transactions using `time.perf_counter()` over 100 iterations.
7. **Matplotlib Visualizations:** Generate high-resolution (300 DPI) comparative plots directly from measured CSV data.
8. **Quantum Shor Circuit Demonstration:** Construct an educational Qiskit Aer quantum circuit simulating modular order finding for $N=15$.
9. **Interactive Streamlit Research UI:** Provide an 8-page cyber-laboratory dashboard for interactive experimentation and demonstration.

---

## Architecture

The project maintains a strict separation between the frontend UI, runtime helpers, and core backend logic:

```
quantum-resistant-blockchain/
│
├── Streamlit Frontend (ui/app.py)
│   ├── Command Center
│   ├── Transaction / Crypto Lab
│   ├── Blockchain Explorer
│   ├── Security Center
│   ├── Performance & Storage Laboratory
│   ├── Quantum Threat Lab
│   ├── Wallet / Authentication
│   └── About, Methodology & Frequently Asked Questions (FAQ)
│
├── Runtime Helper (runtime.py)
│
├── Core Python Backend
│   ├── blockchain/
│   │   ├── block.py           (SHA-256 hashed blocks, deterministic payload)
│   │   ├── blockchain.py      (Ledger state, PoA validation, JSON persistence)
│   │   ├── transaction.py     (Canonical message, ID computation, verify)
│   │   ├── validator.py       (Proof-of-Authority validator engine)
│   │   └── serialization.py   (Canonical JSON & millisecond timestamps)
│   │
│   ├── crypto/
│   │   ├── base_wallet.py     (Abstract base wallet interface)
│   │   ├── ecdsa_wallet.py    (secp256k1 via cryptography package)
│   │   ├── mldsa_wallet.py    (ML-DSA-44 via Open Quantum Safe liboqs)
│   │   ├── crypto_factory.py  (CryptoFactory abstraction layer)
│   │   └── crypto_utils.py    (Hex encoding helpers)
│   │
│   ├── security/
│   │   ├── transaction_tampering.py
│   │   ├── block_tampering.py
│   │   ├── signature_forgery.py
│   │   ├── replay_attack.py
│   │   ├── double_spending.py
│   │   ├── validator_attack.py
│   │   ├── malformed_input.py
│   │   ├── password_auth.py   (scrypt KDF)
│   │   └── wallet_store.py    (Fernet-encrypted keystore)
│   │
│   ├── quantum/
│   │   ├── shor_demo.py       (Qiskit order finding on AerSimulator)
│   │   └── quantum_attack_explanation.py
│   │
│   ├── benchmarks/
│   │   ├── benchmark_crypto.py
│   │   ├── benchmark_blockchain.py
│   │   └── plot_results.py    (Matplotlib 300 DPI generator)
│   │
│   └── tests/                 (Automated pytest suite: 48 test cases)
```

---

## Technology Stack

- **Python 3.11+ / 3.13+**
- **Streamlit:** Interactive web interface
- **cryptography:** Conventional ECDSA over secp256k1, Fernet authenticated encryption
- **Open Quantum Safe (`liboqs` / `liboqs-python`):** Native C library implementation of ML-DSA-44 (NIST FIPS 204)
- **Qiskit & Qiskit Aer:** Quantum circuit synthesis and local simulator for order-finding
- **Matplotlib & Pandas:** Data processing and 300 DPI publication-quality plotting
- **pytest:** Automated test harness
- **Standard Library:** `hashlib` (SHA-256, scrypt), `time.perf_counter()`, `statistics`

---

## Blockchain Design

- **Block Structure:** `index`, `timestamp` (integer milliseconds), `transactions` (list), `previous_hash` (hex string), `validator` (authorized name), and `hash` (computed SHA-256 hex digest).
- **Hashing Rule:** The block hash is calculated over the canonical JSON of `{index, timestamp, transactions, previous_hash, validator}`. The `hash` field itself is strictly excluded during calculation.
- **Genesis Block:** `index = 0`, `previous_hash = "0"`, `transactions = []`, `validator = "GENESIS"`.
- **Proof-of-Authority Consensus:** Blocks must be signed/mined by an authorized validator (`Validator1`, `Validator2`, `Validator3`). Blocks from unauthorized identities are rejected.
- **Persistence:** Ledger state is stored in `data/blockchain.json`. On startup, valid chains are restored; corrupted or tampered chains are rejected safely.

---

## Cryptographic Implementation

### 1. Conventional: ECDSA (secp256k1)
- Elliptic curve digital signature algorithm over the Koblitz curve `secp256k1`.
- Standard SHA-256 message hashing.
- Public key size: **88 bytes** (DER SubjectPublicKeyInfo format).
- Signature size: **~70–72 bytes** (DER ASN.1 format).

### 2. Post-Quantum: ML-DSA-44 (FIPS 204)
- Standardized by NIST in August 2024 as the Module-Lattice Digital Signature Standard (based on CRYSTALS-Dilithium).
- Security relies on the hardness of the Module Learning With Errors (M-LWE) and Module Short Integer Solution (M-SIS) problems in polynomial rings.
- Implemented using the genuine native Open Quantum Safe C-library (`liboqs 0.16.0`).
- Public key size: **1,312 bytes** (~15× larger than ECDSA).
- Signature size: **2,420 bytes** (~34× larger than ECDSA).

### 3. Canonical Message Format
The signed payload is deterministically serialized with sorted keys and no extraneous whitespace:
```json
{"amount": 10.0, "receiver": "Bob", "sender": "Alice", "timestamp": 1726050000000, "transaction_id": "sha256_hash"}
```
The signature is never included in the message it signs.

---

## Security Model & Attack Demonstrations

The system evaluates security across three clearly separated layers:

| Layer | Responsibility | Defense Mechanisms |
|---|---|---|
| **Blockchain Layer** | History immutability, consensus integrity | SHA-256 hash linking, authorized validator whitelist, nonce tracking, balance reservation |
| **Cryptographic Layer** | Identity authentication, transaction integrity | Digital signature verification (ECDSA / ML-DSA-44), canonical message hashing |
| **Application Layer** | Access control, key secrecy | scrypt password KDF ($N=16384, r=8, p=1$), Fernet keystore encryption, input sanitization |

### Demonstrated Attack Scenarios

1. **Transaction Tampering:** Mutating amount (Alice → Bob ₹100 changed to ₹1000) invalidates signature verification.
2. **Block Tampering:** Modifying a historical block invalidates its hash and breaks the hash chain for all subsequent blocks.
3. **Previous-Hash Manipulation:** Changing `previous_hash` breaks validator chain continuity.
4. **Signature Forgery:** An attacker signing with their own key pretending to be Alice fails verification against Alice's public key.
5. **Replay Attack:** Resubmitting an identical signed transaction is rejected because the transaction ID and `(sender, nonce)` pair are already marked spent.
6. **Double Spending:** Submitting conflicting transactions exceeding available balance rejects the second spend.
7. **Unauthorized Validator:** Block creation by `AttackerValidator` is rejected by the PoA engine.
8. **Invalid Block Injection:** Blocks with skip indices or invalid parents are rejected.
9. **Algorithm Mismatch:** Claiming `ML-DSA` in metadata while attaching an ECDSA key/signature is detected and rejected.
10. **Malformed Transaction:** Negative amounts, empty sender/receiver, invalid timestamps, or non-hex signatures are rejected safely without crashing.

---

## Password & Wallet Keystore Security

- **scrypt Key Derivation:** Master passwords are processed using `hashlib.scrypt` with a cryptographically secure 16-byte random salt. Plaintext passwords are never stored or printed.
- **Encrypted Keystore:** Wallets are saved to `wallets/<name>.wallet.json` (protected in `.gitignore`). Secret keys are encrypted with Fernet symmetric encryption derived via HKDF-SHA256 from the master password.
- **Zero Key Leakage:** Private keys exist in ephemeral memory only during unlocked session operations and are never included in blocks or transaction JSON.

---

## Experimental Benchmarks & Results

Empirical results measured on a development workstation running **Windows 11 AMD64, Python 3.13.5, cryptography 50.0.1, liboqs-python 0.16.0** over 100 iterations with 5 warmup iterations:

### 1. Cryptographic Operation Latency & Artifact Sizes

| Metric | ECDSA (secp256k1) | ML-DSA-44 (FIPS 204) | Trade-off Ratio |
|---|---:|---:|---:|
| **Key Generation (avg)** | 0.2692 ms | 0.0930 ms | ML-DSA is **2.9× faster** |
| **Signing Latency (avg)** | 0.2521 ms | 0.1827 ms | ML-DSA is **1.4× faster** |
| **Verification Latency (avg)** | 0.2570 ms | 0.0399 ms | ML-DSA is **6.4× faster** |
| **Public Key Size** | 88 Bytes | 1,312 Bytes | ML-DSA is **14.9× larger** |
| **Signature Size** | 72 Bytes | 2,420 Bytes | ML-DSA is **33.6× larger** |

### 2. Serialized Blockchain Storage Expansion

| Transaction Count | ECDSA Ledger Size | ML-DSA-44 Ledger Size | Storage Overhead Factor |
|---:|---:|---:|---:|
| **10 Transactions** | 7,727 Bytes | 79,202 Bytes | 10.2× |
| **50 Transactions** | 36,347 Bytes | 393,683 Bytes | 10.8× |
| **100 Transactions** | 72,256 Bytes | 786,980 Bytes | 10.9× |
| **500 Transactions** | 359,797 Bytes | 3,933,330 Bytes | **10.9×** |

> **Key Research Finding:** On the tested hardware, ML-DSA-44 exhibits faster signing and verification operations than ECDSA, but imposes an approximately **11× storage multiplier** on serialized blockchain blocks and network transaction propagation due to larger lattice vectors.

---

## Quantum Shor Demonstration (Qiskit)

The project includes an educational quantum simulation module using Qiskit Aer to demonstrate modular order finding—the core quantum subroutine of Shor's algorithm:

1. **Problem Definition:** Given $N = 15$ and coprime base $a \in \{2, 4, 7, 8, 11, 13\}$, find smallest $r > 0$ such that $a^r \equiv 1 \pmod{15}$.
2. **Quantum Register:** 8 counting qubits in superposition perform Quantum Phase Estimation (QPE) over controlled modular multiplier unitary gates.
3. **Inverse QFT:** The Inverse Quantum Fourier Transform maps phase eigenvalues onto computational basis states.
4. **Classical Post-Processing:** Measurement yields bitstrings representing phase $\phi = s/r$. Classical continued fraction expansion recovers candidate period $r = 4$.
5. **Factor Recovery:** $\gcd(a^{r/2} \pm 1, N) = \gcd(2^2 \pm 1, 15)$ yields non-trivial prime factors $\{3, 5\}$.

> **Academic Disclaimer:** This is an educational toy demonstration on $N=15$. It does not break real Bitcoin, ECDSA keys, or real-world cryptography. Factoring real 2048-bit RSA or breaking 256-bit elliptic curves requires millions of physical fault-tolerant qubits far beyond today's quantum hardware.

---

## Frequently Asked Questions (Technical & Cryptographic FAQ)

### Key Technical Inquiries & Answers

**1. Why does Shor's algorithm threaten ECDSA but not SHA-256?**
> Shor's algorithm solves problems with periodic hidden subgroups (discrete logarithms and factoring) in polynomial time $\mathcal{O}(n^3)$. ECDSA relies directly on the discrete logarithm problem over an elliptic curve group. SHA-256 is an iterated cryptographic hash function with no periodic group structure; quantum computers can only attack it using Grover's search algorithm, which provides a quadratic speedup (reducing effective security from 256 bits to 128 bits, which remains secure).

**2. What mathematical foundation makes ML-DSA quantum-resistant?**
> ML-DSA (CRYSTALS-Dilithium / FIPS 204) is based on lattice cryptography—specifically the Module Learning With Errors (M-LWE) and Module Short Integer Solution (M-SIS) problems in polynomial rings $\mathbb{Z}_q[X]/(X^{256} + 1)$. There are no known polynomial-time quantum algorithms capable of solving high-dimensional lattice shortest vector problems.

**3. If ML-DSA is faster in signing, why has the industry not switched immediately?**
> The dominant barrier is **storage and bandwidth overhead**. While signing is computationally efficient, each ML-DSA-44 signature is 2,420 bytes compared to 71 bytes for ECDSA (a 34× increase). In decentralized blockchain networks, where every node must store and relay every transaction, this represents severe ledger bloat and bandwidth saturation.

**4. How does the system handle replay attacks?**
> Each transaction contains a cryptographic nonce and a deterministic transaction ID computed as $\text{SHA-256}(\text{sender} \parallel \text{receiver} \parallel \text{amount} \parallel \text{timestamp} \parallel \text{nonce})$. The blockchain tracks all processed transaction IDs and `(sender, nonce)` pairs, immediately rejecting duplicates.

**5. Is this a toy or a real implementation of ML-DSA?**
> The ML-DSA implementation uses the genuine, native Open Quantum Safe (`liboqs`) C-library through `liboqs-python` using standard ML-DSA-44 (NIST Security Category 2). The measurements and signatures are real cryptographic outputs, not simulations or mocks.

**6. What is the purpose of the Qiskit Shor demo?**
> It provides an educational visualization of how quantum phase estimation finds the order $r$ of $a \pmod N$ on a small scale ($N=15$). It illustrates the fundamental quantum mechanism that threatens classical cryptography, while explicitly clarifying that real cryptographic key sizes (e.g. 256-bit ECDSA) require millions of physical qubits far beyond today's quantum simulators.

---

## Installation & Setup

### 1. Environment Setup

```powershell
# Clone the repository
git clone <repo-url>
cd "Quantum Resist. BlkChain"

# Create and activate virtual environment
py -3.13 -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Native liboqs Library Requirement
ML-DSA-44 requires the native C library of Open Quantum Safe (`oqs.dll` on Windows). Ensure `third_party/liboqs/bin/oqs.dll` is present or set `OQS_INSTALL_PATH`.

---

## Running the Application

### Launch Streamlit Dashboard:
```powershell
.\.venv\Scripts\python.exe -m streamlit run ui/app.py
```
Or launch via the entrypoint script:
```powershell
.\.venv\Scripts\python.exe main.py
```

### Run Automated Tests (48 Test Cases):
```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

### Run Benchmarks & Regenerate Plots:
```powershell
.\.venv\Scripts\python.exe -m benchmarks.run_all
```

---

## Limitations

- **Single-Node Prototype:** Proof-of-Authority validation runs in a single process rather than an asynchronous peer-to-peer network.
- **Simplified Ledger Accounting:** Balances are simulated rather than using a full UTXO or state-trie model.
- **Quantum Simulator Scale:** Qiskit order finding is demonstrated for $N=15$ due to exponential classical simulation overhead of quantum circuits.

---

## License & Attribution

Developed for academic research and educational demonstration in Quantum Cryptography and Blockchain Engineering.
Complies with NIST FIPS 204 and Open Quantum Safe standards.
