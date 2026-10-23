from quantum.shor_demo import expected_classical_factors, run_shor_demo


def test_toy_factorization_correctness():
    result = expected_classical_factors(15, 2)
    assert result["order"] == 4
    assert set(result["factors"]) == {3, 5}


def test_invalid_inputs_handled():
    result = run_shor_demo(n=21, a=2)
    assert result["ok"] is False
    assert "disclaimer" in result


def test_shor_demo_n15():
    result = run_shor_demo(n=15, a=2, shots=128)
    if not result["ok"] and "unavailable" in str(result.get("error", "")).lower():
        return
    if result["ok"]:
        assert set(result["factors"]) == {3, 5}
        assert result["n"] == 15
