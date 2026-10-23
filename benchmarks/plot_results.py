"""Generate matplotlib plots from measured CSV data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from matplotlib import pyplot as plt

from config import BENCHMARK_CSV, PLOTS_DIR

ECDSA_COLOR = "#4C9BE8"
MLDSA_COLOR = "#3EE0A4"
COLORS = {"ECDSA": ECDSA_COLOR, "ML-DSA": MLDSA_COLOR, "ML-DSA-44": MLDSA_COLOR}


def _style(ax, title: str, ylabel: str) -> None:
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.set_axisbelow(True)


def _bar_colors(algorithms) -> list[str]:
    return [COLORS.get(str(name), "#888888") for name in algorithms]


def _load(path: Path | None = None) -> pd.DataFrame | None:
    target = Path(path or BENCHMARK_CSV)
    if not target.exists():
        print(f"skipping plots: missing {target}")
        return None
    frame = pd.read_csv(target)
    if frame.empty:
        print("skipping plots: empty CSV")
        return None
    return frame


def _save(fig, name: str) -> Path:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    out = PLOTS_DIR / name
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_signing_time(df: pd.DataFrame) -> Path | None:
    data = df[df["operation"] == "sign"]
    if data.empty:
        print("skipping plot_signing_time: no sign rows")
        return None
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(data["algorithm"], data["average_time_ms"], color=_bar_colors(data["algorithm"]))
    if "std_dev_ms" in data.columns:
        ax.errorbar(
            data["algorithm"],
            data["average_time_ms"],
            yerr=data["std_dev_ms"],
            fmt="none",
            ecolor="#cccccc",
            capsize=4,
        )
    _style(ax, "Signing time (this machine)", "Average signing time (ms)")
    fig.tight_layout()
    return _save(fig, "signing_time.png")


def plot_verification_time(df: pd.DataFrame) -> Path | None:
    data = df[df["operation"] == "verify"]
    if data.empty:
        print("skipping plot_verification_time: no verify rows")
        return None
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(data["algorithm"], data["average_time_ms"], color=_bar_colors(data["algorithm"]))
    _style(ax, "Verification time (this machine)", "Average verification time (ms)")
    fig.tight_layout()
    return _save(fig, "verification_time.png")


def plot_key_generation_time(df: pd.DataFrame) -> Path | None:
    data = df[df["operation"] == "key_generation"]
    if data.empty:
        print("skipping plot_key_generation_time: no key_generation rows")
        return None
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(data["algorithm"], data["average_time_ms"], color=_bar_colors(data["algorithm"]))
    _style(ax, "Key generation time (this machine)", "Average key-generation time (ms)")
    fig.tight_layout()
    return _save(fig, "key_generation_time.png")


def plot_signature_size(df: pd.DataFrame) -> Path | None:
    data = df[df["operation"] == "signature_size"]
    if data.empty:
        print("skipping plot_signature_size: no signature_size rows")
        return None
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(data["algorithm"], data["data_size_bytes"], color=_bar_colors(data["algorithm"]))
    _style(ax, "Signature size", "Signature size (bytes)")
    fig.tight_layout()
    return _save(fig, "signature_size.png")


def plot_public_key_size(df: pd.DataFrame) -> Path | None:
    data = df[df["operation"] == "public_key_size"]
    if data.empty:
        print("skipping plot_public_key_size: no public_key_size rows")
        return None
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(data["algorithm"], data["data_size_bytes"], color=_bar_colors(data["algorithm"]))
    _style(ax, "Public-key size", "Public-key size (bytes)")
    fig.tight_layout()
    return _save(fig, "public_key_size.png")


def plot_blockchain_storage(df: pd.DataFrame) -> Path | None:
    data = df[df["operation"].astype(str).str.startswith("storage_")]
    if data.empty:
        print("skipping plot_blockchain_storage: no storage rows")
        return None
    fig, ax = plt.subplots(figsize=(8, 4.8))
    for algorithm, group in data.groupby("algorithm"):
        ax.plot(
            group["transaction_count"],
            group["total_blockchain_size"],
            marker="o",
            color=COLORS.get(str(algorithm), None),
            label=algorithm,
        )
    ax.set_xlabel("Transaction count")
    ax.set_ylabel("Serialized blockchain size (bytes)")
    ax.set_title("Blockchain storage (this experiment)")
    ax.legend()
    fig.tight_layout()
    return _save(fig, "blockchain_storage.png")


def plot_throughput(df: pd.DataFrame) -> Path | None:
    data = df[df["operation"] == "sign"]
    if data.empty:
        print("skipping plot_throughput: no sign rows")
        return None
    fig, ax = plt.subplots(figsize=(7, 4.5))
    throughput = 1000.0 / data["average_time_ms"]
    ax.bar(data["algorithm"], throughput, color=_bar_colors(data["algorithm"]))
    _style(ax, "Signing throughput from measured signing times", "Signatures per second")
    fig.tight_layout()
    return _save(fig, "throughput.png")


def plot_timing_comparison(df: pd.DataFrame) -> Path | None:
    data = df[df["operation"].isin(["key_generation", "sign", "verify"])]
    if data.empty:
        print("skipping plot_timing_comparison: no timing rows")
        return None
    pivot = data.pivot_table(index="operation", columns="algorithm", values="average_time_ms")
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    pivot.plot(kind="bar", ax=ax, color=[COLORS.get(c, "#888") for c in pivot.columns])
    _style(ax, "ECDSA vs ML-DSA-44 operation time", "Average time (ms)")
    ax.set_xlabel("Operation")
    ax.tick_params(axis="x", rotation=0)
    ax.legend(title="Algorithm")
    fig.tight_layout()
    return _save(fig, "timing_comparison.png")


def plot_size_comparison(df: pd.DataFrame) -> Path | None:
    data = df[df["operation"].isin(["public_key_size", "signature_size"])]
    if data.empty:
        print("skipping plot_size_comparison: no size rows")
        return None
    pivot = data.pivot_table(index="operation", columns="algorithm", values="data_size_bytes")
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    pivot.plot(kind="bar", ax=ax, color=[COLORS.get(c, "#888") for c in pivot.columns])
    _style(ax, "ECDSA vs ML-DSA-44 key and signature size", "Size (bytes)")
    ax.set_xlabel("Artifact")
    ax.tick_params(axis="x", rotation=0)
    ax.legend(title="Algorithm")
    fig.tight_layout()
    return _save(fig, "size_comparison.png")


def plot_transaction_size(df: pd.DataFrame) -> Path | None:
    data = df[df["operation"].astype(str).str.startswith("storage_")]
    if data.empty or "serialized_transaction_size_avg" not in data.columns:
        print("skipping plot_transaction_size: no storage rows")
        return None
    summary = (
        data.groupby("algorithm")["serialized_transaction_size_avg"].mean().reset_index()
    )
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(summary["algorithm"], summary["serialized_transaction_size_avg"], color=_bar_colors(summary["algorithm"]))
    _style(ax, "Serialized transaction size (this experiment)", "Average transaction size (bytes)")
    fig.tight_layout()
    return _save(fig, "transaction_size.png")


def generate_all_plots(csv_path: Path | None = None) -> list[Path]:
    df = _load(csv_path)
    if df is None:
        return []
    created = []
    for fn in (
        plot_signing_time,
        plot_verification_time,
        plot_key_generation_time,
        plot_signature_size,
        plot_public_key_size,
        plot_blockchain_storage,
        plot_throughput,
        plot_timing_comparison,
        plot_size_comparison,
        plot_transaction_size,
    ):
        path = fn(df)
        if path is not None:
            created.append(path)
    return created


def _float_frame(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.apply(pd.to_numeric, errors="coerce").astype(float)


def timing_chart_frame(df: pd.DataFrame) -> pd.DataFrame:
    data = df[df["operation"].isin(["key_generation", "sign", "verify"])].copy()
    labels = {
        "key_generation": "Key generation",
        "sign": "Signing",
        "verify": "Verification",
    }
    data["Metric"] = data["operation"].map(labels)
    return _float_frame(data.pivot_table(index="Metric", columns="algorithm", values="average_time_ms"))


def size_chart_frame(df: pd.DataFrame) -> pd.DataFrame:
    data = df[df["operation"].isin(["public_key_size", "signature_size"])].copy()
    labels = {"public_key_size": "Public key", "signature_size": "Signature"}
    data["Metric"] = data["operation"].map(labels)
    return _float_frame(data.pivot_table(index="Metric", columns="algorithm", values="data_size_bytes"))


def storage_chart_frame(df: pd.DataFrame) -> pd.DataFrame:
    data = df[df["operation"].astype(str).str.startswith("storage_")].copy()
    return _float_frame(
        data.pivot_table(
            index="transaction_count",
            columns="algorithm",
            values="total_blockchain_size",
        )
    )


def throughput_chart_frame(df: pd.DataFrame) -> pd.DataFrame:
    data = df[df["operation"] == "sign"].copy()
    data["signatures_per_second"] = 1000.0 / data["average_time_ms"]
    return _float_frame(data.set_index("algorithm")[["signatures_per_second"]])


def transaction_size_chart_frame(df: pd.DataFrame) -> pd.DataFrame:
    data = df[df["operation"].astype(str).str.startswith("storage_")].copy()
    summary = data.groupby("algorithm")["serialized_transaction_size_avg"].mean()
    return _float_frame(summary.to_frame("avg_transaction_bytes"))


def lookup_metric_ms(df: pd.DataFrame, algorithm: str, operation: str) -> str:
    subset = df[(df["algorithm"] == algorithm) & (df["operation"] == operation)]
    if subset.empty:
        return "—"
    return f"{float(subset.iloc[0]['average_time_ms']):.3f} ms"
