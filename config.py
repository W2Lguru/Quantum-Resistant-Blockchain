"""Project configuration for the educational quantum-resistant blockchain."""

from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
REPORTS_DIR = ROOT_DIR / "reports"
PLOTS_DIR = REPORTS_DIR / "plots"
WALLET_DIR = ROOT_DIR / "wallets"

BLOCKCHAIN_PATH = DATA_DIR / "blockchain.json"
BENCHMARK_CSV = REPORTS_DIR / "benchmark_results.csv"
BENCHMARK_METADATA = REPORTS_DIR / "benchmark_metadata.json"
BENCHMARK_SUMMARY = REPORTS_DIR / "benchmark_summary.txt"

VALIDATORS = ("Validator1", "Validator2", "Validator3")
DEFAULT_VALIDATOR = VALIDATORS[0]

GENESIS_INDEX = 0
GENESIS_PREVIOUS_HASH = "0"
GENESIS_VALIDATOR = "GENESIS"

ALGORITHM_ECDSA = "ECDSA"
ALGORITHM_MLDSA = "ML-DSA"
MLDSA_VARIANT = "ML-DSA-44"

SUPPORTED_ALGORITHMS = (ALGORITHM_ECDSA, ALGORITHM_MLDSA)

# Educational ledger starting balances (simulation only, not a cryptocurrency).
INITIAL_BALANCES = {
    "Alice": 1000.0,
    "Bob": 500.0,
    "Charlie": 250.0,
}

CRYPTO_BENCHMARK_ITERATIONS = 100
CRYPTO_WARMUP_ITERATIONS = 5
STORAGE_TX_COUNTS = (10, 50, 100, 500)

PASSWORD_SCRYPT_N = 2**14
PASSWORD_SCRYPT_R = 8
PASSWORD_SCRYPT_P = 1
PASSWORD_SALT_BYTES = 16
PASSWORD_DKLEN = 32

MIN_AMOUNT = 0.00000001
