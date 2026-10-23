"""Quantum-Resistant Blockchain Research Laboratory (Streamlit Frontend).

A polished, educational, interactive research dashboard demonstrating:
1. Proof-of-Authority blockchain with SHA-256 hash linking
2. ECDSA (secp256k1) vs Post-Quantum ML-DSA-44 (FIPS 204) transaction authentication
3. Blockchain and cryptographic attack detection
4. Real-world performance and storage benchmarking
5. Educational Qiskit Shor algorithm order-finding demonstration
6. Password-authenticated encrypted wallet storage
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from blockchain.smart_contract import create_hash_lock, execute_hash_lock
from config import (
    ALGORITHM_ECDSA,
    ALGORITHM_MLDSA,
    BENCHMARK_CSV,
    BENCHMARK_SUMMARY,
    DEFAULT_VALIDATOR,
    MLDSA_VARIANT,
    PLOTS_DIR,
    VALIDATORS,
)
from quantum.quantum_attack_explanation import narrative
from quantum.shor_demo import DISCLAIMER, run_shor_demo
from runtime import (
    commit_pending_block,
    create_and_commit_transaction,
    load_or_create_chain,
    wallet_store,
)
from security.block_tampering import (
    demonstrate_block_tampering,
    demonstrate_previous_hash_manipulation,
)
from security.demonstrations import run_all_demonstrations
from security.double_spending import demonstrate_double_spending
from security.malformed_input import (
    demonstrate_algorithm_mismatch,
    demonstrate_malformed_transactions,
)
from security.replay_attack import demonstrate_replay_attack
from security.signature_forgery import demonstrate_signature_forgery
from security.transaction_tampering import demonstrate_transaction_tampering
from security.validator_attack import (
    demonstrate_invalid_block_injection,
    demonstrate_unauthorized_validator,
)

st.set_page_config(
    page_title="Quantum-Resistant Blockchain Lab",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

THEME = """
<style>
.stApp { background: #080d1a; color: #d7e2f2; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
[data-testid="stSidebar"] { background: #0c1424; border-right: 1px solid #1a2942; }

.main-header {
    background: linear-gradient(135deg, #0e1a30 0%, #080e1c 100%);
    border: 1px solid #1e355b;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 20px;
}
.main-title {
    color: #4da6ff;
    font-size: 1.8rem;
    font-weight: 800;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}
.main-sub {
    color: #8da2c0;
    font-size: 0.95rem;
    font-weight: 500;
}

.metric-card {
    background: #0f1c33;
    border: 1px solid #1f3b64;
    border-radius: 10px;
    padding: 14px 16px;
    text-align: center;
}
.metric-num {
    font-size: 1.5rem;
    font-weight: 700;
    color: #3ee0a4;
}
.metric-label {
    font-size: 0.8rem;
    color: #8da2c0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.block-card {
    border: 1px solid #1f3b64;
    border-radius: 10px;
    padding: 12px;
    background: linear-gradient(180deg, #101c33, #0b1426);
    margin-bottom: 8px;
    font-size: 0.85rem;
}
.block-card-header {
    font-weight: 700;
    color: #4da6ff;
    margin-bottom: 6px;
}
.chain-arrow {
    font-size: 1.4rem;
    color: #4da6ff;
    text-align: center;
    line-height: 120px;
}

.ok { color: #3ee0a4; font-weight: 700; }
.bad { color: #ff6b7a; font-weight: 700; }
.mono { font-family: ui-monospace, Consolas, monospace; font-size: 0.78rem; word-break: break-all; }

.status-badge-ok {
    background: rgba(62, 224, 164, 0.15);
    border: 1px solid #3ee0a4;
    color: #3ee0a4;
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: 700;
    display: inline-block;
}
.status-badge-bad {
    background: rgba(255, 107, 122, 0.15);
    border: 1px solid #ff6b7a;
    color: #ff6b7a;
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: 700;
    display: inline-block;
}

.comparison-box {
    background: #0d172a;
    border: 1px solid #1d3356;
    border-radius: 10px;
    padding: 16px;
}
</style>
"""
st.markdown(THEME, unsafe_allow_html=True)


def _chain():
    if "chain" not in st.session_state:
        st.session_state.chain = load_or_create_chain()
    return st.session_state.chain


def _status_chip(ok: bool, good: str, bad: str) -> str:
    if ok:
        return f'<span class="status-badge-ok">✓ {good}</span>'
    return f'<span class="status-badge-bad">✗ {bad}</span>'


def _load_benchmark_data() -> pd.DataFrame | None:
    if BENCHMARK_CSV.exists():
        try:
            return pd.read_csv(BENCHMARK_CSV)
        except Exception:
            return None
    return None


# ==============================================================================
# PAGE 1: COMMAND CENTER
# ==============================================================================
def page_command_center():
    st.markdown(
        """
        <div class="main-header">
            <div class="main-title">🛡️ QUANTUM-RESISTANT BLOCKCHAIN</div>
            <div class="main-sub">ECDSA → ML-DSA-44 | Security Verification | Real Benchmarking | Shor's Threat Model</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    chain = _chain()
    ok, reason = chain.is_chain_valid()
    latest = chain.get_latest_block()
    history = chain.get_transaction_history()
    last_tx = history[-1] if history else None

    bench = _load_benchmark_data()
    from benchmarks.plot_results import lookup_metric_ms

    algo_name = last_tx["algorithm"] if last_tx else "ECDSA"
    sign_ms = lookup_metric_ms(bench, algo_name, "sign") if bench is not None else "—"
    verify_ms = lookup_metric_ms(bench, algo_name, "verify") if bench is not None else "—"

    # Row 1: Live Cards
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Blockchain Height", f"Block #{latest.index}")
    c2.metric("Pending Transactions", len(chain.pending_transactions))
    c3.metric("Active Validator", DEFAULT_VALIDATOR)
    c4.metric("Accounts Tracked", len(chain.balances))

    # Row 2: Security & Crypto Cards
    d1, d2, d3, d4 = st.columns(4)
    with d1:
        st.markdown("**Chain Integrity Status**")
        st.markdown(_status_chip(ok, "SECURE", reason), unsafe_allow_html=True)
    d2.metric("Last Algorithm", algo_name)
    d3.metric("Measured Signing Time", sign_ms)
    d4.metric("Measured Verify Time", verify_ms)

    st.divider()

    # Block commitment control
    st.subheader("⚡ Validator Consensus & Block Mining")
    b_col1, b_col2 = st.columns([3, 1])
    validator = b_col2.selectbox("Authorizing Validator", list(VALIDATORS), key="cmd_validator")
    if b_col1.button("COMMIT PENDING TRANSACTIONS AS NEW BLOCK", type="primary", use_container_width=True):
        res = commit_pending_block(chain, validator)
        if res["added"]:
            st.success(f"✓ Block #{res['block_index']} successfully authorized by {validator} and committed to ledger.")
        else:
            st.warning(f"Commitment notice: {res['reason']}")

    st.divider()

    # Visual Connected Chain
    st.subheader("🔗 Connected Blockchain Visualization")
    st.caption("Each block is linked by SHA-256 hash to its parent. Hover or expand below to inspect payload.")

    recent_blocks = chain.chain[-6:]
    cols = st.columns(len(recent_blocks))
    for i, b in enumerate(recent_blocks):
        with cols[i]:
            prev_b = chain.chain[b.index - 1] if b.index > 0 else None
            is_valid_block = chain.validator_engine.validate_block(b, prev_b)[0]
            st.markdown(
                f"""
                <div class="block-card">
                    <div class="block-card-header">BLOCK #{b.index}</div>
                    <div><b>Validator:</b> {b.validator}</div>
                    <div><b>Transactions:</b> {len(b.transactions)}</div>
                    <div><b>Hash:</b> <span class="mono">{b.hash[:12]}…</span></div>
                    <div style="margin-top:6px;">{_status_chip(is_valid_block, 'VALID', 'INVALID')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    selected_idx = st.selectbox(
        "🔍 Inspect Block Details",
        [b.index for b in reversed(chain.chain)],
        format_func=lambda idx: f"Block #{idx} ({'Genesis' if idx == 0 else f'{len(chain.chain[idx].transactions)} txs'})",
        key="inspect_block_select",
    )
    b_obj = chain.chain[selected_idx]
    with st.expander(f"Detailed Payload: Block #{b_obj.index}", expanded=True):
        m1, m2, m3 = st.columns(3)
        m1.markdown(f"**Index:** {b_obj.index}")
        m2.markdown(f"**Timestamp (ms):** `{b_obj.timestamp}`")
        m3.markdown(f"**Validator:** `{b_obj.validator}`")
        st.markdown(f"**Previous Hash:** `{b_obj.previous_hash}`")
        st.markdown(f"**Current Hash:** `{b_obj.hash}`")
        st.markdown("**Transactions in Block:**")
        if b_obj.transactions:
            st.dataframe(pd.DataFrame([tx.to_dict() for tx in b_obj.transactions]), use_container_width=True)
        else:
            st.info("No transactions in this block (Genesis block).")


# ==============================================================================
# PAGE 2: TRANSACTION / CRYPTOGRAPHY LAB
# ==============================================================================
def page_crypto_lab():
    st.header("🧪 Transaction / Cryptography Lab")
    st.caption(
        "Create, sign, and verify transactions using either classical ECDSA (secp256k1) or post-quantum ML-DSA-44."
    )

    chain = _chain()

    # Flow banner
    st.info(
        "**Transaction Lifecycle:** "
        "User Input ──▶ Canonical Message ──▶ Cryptographic Signing ──▶ Signature Verification ──▶ PoA Block Insertion"
    )

    c1, c2 = st.columns([1, 1])

    with c1:
        st.subheader("1. Configure Transaction")
        algorithm = st.radio(
            "Digital Signature Scheme",
            [ALGORITHM_ECDSA, ALGORITHM_MLDSA],
            horizontal=True,
            help="Choose between conventional ECDSA (secp256k1) and NIST Post-Quantum standard ML-DSA-44.",
            key="tx_lab_alg",
        )
        col_s, col_r = st.columns(2)
        sender = col_s.text_input("Sender Account", "Alice", key="lab_sender")
        receiver = col_r.text_input("Receiver Account", "Bob", key="lab_receiver")
        amount = st.number_input("Amount (Educational Ledger Units)", min_value=0.01, value=25.0, step=1.0)
        auto_mine = st.checkbox("Automatically commit block after signing", value=True)

        if st.button("CREATE & SIGN TRANSACTION", type="primary", use_container_width=True):
            with st.spinner("Generating keys, signing canonical message, and verifying..."):
                res = create_and_commit_transaction(
                    chain, sender, receiver, amount, algorithm, auto_mine=auto_mine
                )
                st.session_state.last_tx_result = res

    with c2:
        st.subheader("2. Cryptographic Scheme Comparison")
        st.markdown(
            """
            <div class="comparison-box">
                <table style="width:100%; border-collapse: collapse; font-size: 0.9rem;">
                    <tr style="border-bottom: 1px solid #1f3b64;">
                        <th style="text-align:left; padding:6px;">Property</th>
                        <th style="text-align:left; padding:6px; color:#4C9BE8;">ECDSA (secp256k1)</th>
                        <th style="text-align:left; padding:6px; color:#3EE0A4;">ML-DSA-44 (FIPS 204)</th>
                    </tr>
                    <tr>
                        <td style="padding:6px;"><b>Security Basis</b></td>
                        <td style="padding:6px;">Elliptic Curve Discrete Log</td>
                        <td style="padding:6px;">Module Learning With Errors (Lattice)</td>
                    </tr>
                    <tr>
                        <td style="padding:6px;"><b>Quantum Resistance</b></td>
                        <td style="padding:6px; color:#ff6b7a;">Vulnerable (Shor's)</td>
                        <td style="padding:6px; color:#3ee0a4;">Resistant to Known Attacks</td>
                    </tr>
                    <tr>
                        <td style="padding:6px;"><b>Public Key Size</b></td>
                        <td style="padding:6px;">88 Bytes</td>
                        <td style="padding:6px;">1,312 Bytes (~15× larger)</td>
                    </tr>
                    <tr>
                        <td style="padding:6px;"><b>Signature Size</b></td>
                        <td style="padding:6px;">~70–72 Bytes</td>
                        <td style="padding:6px;">2,420 Bytes (~34× larger)</td>
                    </tr>
                    <tr>
                        <td style="padding:6px;"><b>NIST Security Level</b></td>
                        <td style="padding:6px;">Classical 128-bit</td>
                        <td style="padding:6px;">Category 2 (SHA-256 equivalent)</td>
                    </tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Result Section
    tx_res = st.session_state.get("last_tx_result")
    if tx_res:
        st.divider()
        st.subheader("3. Transaction Execution Result")
        tx = tx_res["transaction"]

        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Transaction ID", tx["transaction_id"][:12] + "…")
        r2.metric("Algorithm Applied", tx_res["algorithm_display"])
        r3.metric("Signature Size", f"{tx_res['signature_size']} Bytes")
        r4.metric("Public Key Size", f"{tx_res['public_key_size']} Bytes")

        if tx_res["accepted"] and tx_res.get("block_added"):
            st.success(
                f"✓ Signature Verified! Transaction committed to Block #{tx_res['block_index']}. "
                f"Ledger balance updated."
            )
        elif tx_res["accepted"]:
            st.info("✓ Signature Verified! Transaction is queued in pending transactions.")
        else:
            st.error(f"✗ Transaction Rejected: {tx_res['reason']}")

        with st.expander("Inspect Full Signed Canonical Transaction JSON"):
            st.json(tx)


# ==============================================================================
# PAGE 3: BLOCKCHAIN EXPLORER
# ==============================================================================
def page_explorer():
    st.header("🔎 Blockchain Explorer")
    st.caption("Search, inspect, and verify blocks, hash linking, and individual transaction signatures.")

    chain = _chain()
    ok, reason = chain.is_chain_valid()
    st.markdown(
        f"**Chain Status:** {_status_chip(ok, f'ALL BLOCKS VALID ({reason})', f'CHAIN CORRUPTED: {reason}')}",
        unsafe_allow_html=True,
    )

    tab_txs, tab_blocks, tab_balances = st.tabs(["Transaction Ledger", "Block Inspector", "Account Balances"])

    with tab_txs:
        search_query = st.text_input("🔍 Search by Sender, Receiver, or Transaction ID", key="explorer_search")
        history = chain.get_transaction_history()
        if search_query:
            q = search_query.lower()
            history = [
                tx
                for tx in history
                if q in tx["sender"].lower() or q in tx["receiver"].lower() or q in tx["transaction_id"].lower()
            ]

        if history:
            df_history = pd.DataFrame(history)
            st.dataframe(df_history, use_container_width=True)

            # Detailed individual transaction inspector
            tx_ids = [tx["transaction_id"] for tx in history]
            selected_tx_id = st.selectbox("Inspect Full Transaction Artifact", tx_ids)
            selected_tx = next(tx for tx in history if tx["transaction_id"] == selected_tx_id)
            with st.expander(f"Transaction: {selected_tx_id}", expanded=True):
                k1, k2, k3 = st.columns(3)
                k1.write(f"**Sender:** {selected_tx['sender']}")
                k2.write(f"**Receiver:** {selected_tx['receiver']}")
                k3.write(f"**Amount:** {selected_tx['amount']}")
                k4, k5, k6 = st.columns(3)
                k4.write(f"**Algorithm:** {selected_tx['algorithm']}")
                k5.write(f"**Timestamp:** {selected_tx['timestamp']}")
                k6.write(f"**Block Index:** #{selected_tx.get('block_index', 'Pending')}")
                st.text_area("Public Key (Hex)", selected_tx["public_key"], height=70)
                st.text_area("Cryptographic Signature (Hex)", selected_tx["signature"], height=90)
        else:
            st.info("No committed transactions found matching the query.")

    with tab_blocks:
        b_idx = st.selectbox("Select Block Number", [b.index for b in reversed(chain.chain)])
        b = chain.chain[b_idx]
        st.write(
            {
                "index": b.index,
                "timestamp": b.timestamp,
                "validator": b.validator,
                "transaction_count": len(b.transactions),
                "previous_hash": b.previous_hash,
                "hash": b.hash,
            }
        )
        st.dataframe(pd.DataFrame([t.to_dict() for t in b.transactions]) if b.transactions else pd.DataFrame())

    with tab_balances:
        st.subheader("Simulated Account Balances")
        st.table(pd.DataFrame(list(chain.balances.items()), columns=["Account", "Available Balance"]))


# ==============================================================================
# PAGE 4: SECURITY CENTER
# ==============================================================================
def page_security():
    st.header("🚨 Security Center")
    st.caption(
        "Interactive attack simulations verifying that blockchain integrity, digital signatures, and "
        "consensus rules reliably reject invalid or malicious actions."
    )

    attack_types = [
        "1. Transaction Tampering (Payload Mutation)",
        "2. Block Tampering (Historical Modification)",
        "3. Previous-Hash Manipulation",
        "4. Signature Forgery Attempt",
        "5. Replay Attack (Duplicate Submission)",
        "6. Double Spending Simulation",
        "7. Unauthorized Validator Attack",
        "8. Invalid Block Injection",
        "9. Algorithm Mismatch Attack",
        "10. Malformed Transaction Inputs",
    ]

    col_sel, col_alg = st.columns([2, 1])
    attack_choice = col_sel.selectbox("Select Attack Scenario", attack_types)
    attack_alg = col_alg.selectbox(
        "Cryptographic Scheme",
        ["ECDSA", "ML-DSA"],
        help="Select which digital signature scheme to evaluate in this attack.",
    )

    if st.button("EXECUTE ATTACK DEMONSTRATION", type="primary", use_container_width=True):
        if "1. Transaction Tampering" in attack_choice:
            st.session_state.attack_res = demonstrate_transaction_tampering(attack_alg)
        elif "2. Block Tampering" in attack_choice:
            st.session_state.attack_res = demonstrate_block_tampering()
        elif "3. Previous-Hash" in attack_choice:
            st.session_state.attack_res = demonstrate_previous_hash_manipulation()
        elif "4. Signature Forgery" in attack_choice:
            st.session_state.attack_res = demonstrate_signature_forgery(attack_alg)
        elif "5. Replay Attack" in attack_choice:
            st.session_state.attack_res = demonstrate_replay_attack(attack_alg)
        elif "6. Double Spending" in attack_choice:
            st.session_state.attack_res = demonstrate_double_spending(attack_alg)
        elif "7. Unauthorized Validator" in attack_choice:
            st.session_state.attack_res = demonstrate_unauthorized_validator()
        elif "8. Invalid Block Injection" in attack_choice:
            st.session_state.attack_res = demonstrate_invalid_block_injection()
        elif "9. Algorithm Mismatch" in attack_choice:
            st.session_state.attack_res = demonstrate_algorithm_mismatch()
        elif "10. Malformed" in attack_choice:
            st.session_state.attack_res = demonstrate_malformed_transactions()

    res = st.session_state.get("attack_res")
    if res:
        st.divider()
        st.markdown(
            "### Attack Analysis: `NORMAL STATE` ──▶ `ATTACK INJECTION` ──▶ `SYSTEM DEFENSE RESPONSE`"
        )

        detected = res.get("detected", False)
        headline = res.get("headline", "ATTACK RESULT")
        explanation = res.get("explanation", "")

        if detected:
            st.markdown(
                f"""
                <div style="background: rgba(255, 107, 122, 0.15); border: 2px solid #ff6b7a; border-radius: 10px; padding: 16px; margin: 12px 0;">
                    <div style="font-size: 1.25rem; font-weight: 800; color: #ff6b7a;">🛡️ SECURITY SYSTEM: {headline}</div>
                    <div style="color: #e0e8f5; margin-top: 6px;"><b>Defense Outcome:</b> Attack was identified and rejected before ledger corruption could occur.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.warning(headline)

        st.info(f"**Technical Explanation:** {explanation}")

        # Visual Comparison Card for Tampering / Forgery
        if "original" in res and "tampered" in res:
            o_col, t_col = st.columns(2)
            with o_col:
                st.markdown("**✓ Legitimate Signed Transaction (Normal)**")
                st.markdown(
                    f"""
                    <div class="comparison-box" style="border-left: 4px solid #3ee0a4;">
                        <b>Sender:</b> {res['original']['sender']}<br>
                        <b>Receiver:</b> {res['original']['receiver']}<br>
                        <b>Amount:</b> ₹{res['original']['amount']}<br>
                        <b>Algorithm:</b> {res['original']['algorithm']}<br>
                        <b>Status:</b> <span class="ok">✓ Signature Valid</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with t_col:
                st.markdown("**✗ Tampered Transaction (Attacker Modification)**")
                st.markdown(
                    f"""
                    <div class="comparison-box" style="border-left: 4px solid #ff6b7a;">
                        <b>Sender:</b> {res['tampered']['sender']}<br>
                        <b>Receiver:</b> {res['tampered']['receiver']}<br>
                        <b>Amount:</b> ₹{res['tampered']['amount']} (MUTATED!)<br>
                        <b>Algorithm:</b> {res['tampered']['algorithm']}<br>
                        <b>Status:</b> <span class="bad">✗ Signature Invalid ({res.get('reason_after')})</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        if "cases" in res:
            st.markdown("**Evaluated Malformed Cases:**")
            st.dataframe(pd.DataFrame(res["cases"]), use_container_width=True)

        with st.expander("Raw Attack Diagnostic Data"):
            st.json({k: v for k, v in res.items() if k not in {"original", "tampered", "cases"}})

    st.divider()
    with st.expander("⚡ Run Comprehensive Security Test Battery"):
        st.write("Executes all 10 attack vectors sequentially across ECDSA and ML-DSA schemes.")
        if st.button("Run Full Security Suite"):
            all_attacks = run_all_demonstrations(attack_alg)
            summary_data = [
                {
                    "Attack Scenario": a["name"].title(),
                    "Detected / Rejected": "✓ PASS" if a["detected"] else "✗ FAIL",
                    "System Response": a.get("headline", ""),
                }
                for a in all_attacks
            ]
            st.table(pd.DataFrame(summary_data))


# ==============================================================================
# PAGE 5: PERFORMANCE LAB
# ==============================================================================
def page_performance():
    st.header("📊 Performance & Storage Laboratory")
    st.caption(
        "Empirical benchmarks measured on this machine using `time.perf_counter()`. "
        "Compares cryptographic latency, key sizes, signature sizes, and serialized blockchain expansion."
    )

    bench = _load_benchmark_data()
    if bench is None:
        st.warning("No benchmark results found. Click below to execute the benchmark suite.")
        if st.button("Run Benchmarks Now (100 Iterations)", type="primary"):
            from benchmarks.run_all import run_all_benchmarks

            with st.spinner("Executing cryptographic timing and storage measurements..."):
                run_all_benchmarks()
            st.rerun()
        return

    from benchmarks.plot_results import (
        generate_all_plots,
        size_chart_frame,
        storage_chart_frame,
        throughput_chart_frame,
        timing_chart_frame,
        transaction_size_chart_frame,
    )

    # Comparison Table
    st.subheader("1. Measured Cryptographic Metrics")
    ops = ["key_generation", "sign", "verify", "public_key_size", "signature_size"]
    labels = {
        "key_generation": "Key Generation Time (ms)",
        "sign": "Signing Time (ms)",
        "verify": "Verification Time (ms)",
        "public_key_size": "Public Key Size (Bytes)",
        "signature_size": "Signature Size (Bytes)",
    }
    table = {}
    for op in ops:
        subset = bench[bench["operation"] == op]
        row = {}
        for _, item in subset.iterrows():
            if op.endswith("size"):
                row[item["algorithm"]] = f"{int(item['data_size_bytes']):,} B"
            else:
                row[item["algorithm"]] = f"{item['average_time_ms']:.4f} ms (±{item['std_dev_ms']:.4f})"
        table[labels[op]] = row
    st.table(pd.DataFrame(table).T)

    st.subheader("2. Interactive Benchmark Visualizations")
    graph_tab = st.selectbox(
        "Select Graph View",
        [
            "Cryptographic Operation Latency (ms)",
            "Public Key & Signature Storage Size (Bytes)",
            "Signing Throughput (Signatures/sec)",
            "Blockchain Storage Expansion vs Transaction Count",
            "Average Serialized Transaction Size (Bytes)",
            "High-Resolution Matplotlib Plot Export",
        ],
    )

    if graph_tab == "Cryptographic Operation Latency (ms)":
        timing_df = timing_chart_frame(bench)
        if not timing_df.empty:
            st.bar_chart(timing_df, color=["#4C9BE8", "#3EE0A4"][: len(timing_df.columns)])
            st.caption("Lower is faster. Measurements averaged over 100 iterations with 5 warmup rounds.")

    elif graph_tab == "Public Key & Signature Storage Size (Bytes)":
        size_df = size_chart_frame(bench)
        if not size_df.empty:
            st.bar_chart(size_df, color=["#4C9BE8", "#3EE0A4"][: len(size_df.columns)])
            st.caption("ML-DSA-44 public keys are 1,312 B (~15× ECDSA); signatures are 2,420 B (~34× ECDSA).")

    elif graph_tab == "Signing Throughput (Signatures/sec)":
        tp_df = throughput_chart_frame(bench)
        if not tp_df.empty:
            st.bar_chart(tp_df, color=["#4C9BE8"])
            st.caption("Derived directly from measured average signing latency: (1000 / avg_ms).")

    elif graph_tab == "Blockchain Storage Expansion vs Transaction Count":
        stg_df = storage_chart_frame(bench)
        if not stg_df.empty:
            st.line_chart(stg_df, color=["#4C9BE8", "#3EE0A4"][: len(stg_df.columns)])
            st.caption("Total serialized JSON blockchain size across 10, 50, 100, and 500 committed transactions.")

    elif graph_tab == "Average Serialized Transaction Size (Bytes)":
        tx_size_df = transaction_size_chart_frame(bench)
        if not tx_size_df.empty:
            st.bar_chart(tx_size_df, color=["#3EE0A4"])
            st.caption("Average byte length of canonical transaction JSON including hex-encoded keys and signatures.")

    elif graph_tab == "High-Resolution Matplotlib Plot Export":
        plot_files = sorted(list(PLOTS_DIR.glob("*.png")))
        if plot_files:
            chosen_plot = st.selectbox("Select Generated Matplotlib Plot (300 DPI)", [p.name for p in plot_files])
            st.image(str(PLOTS_DIR / chosen_plot), use_container_width=True)
            if st.button("Regenerate All Matplotlib Plots"):
                generate_all_plots(BENCHMARK_CSV)
                st.success("Plots refreshed.")

    st.subheader("3. Benchmark Empirical Summary")
    if BENCHMARK_SUMMARY.exists():
        st.markdown(
            f"""
            <div class="comparison-box" style="border-left: 4px solid #4da6ff;">
                <pre style="color: #d7e2f2; font-size: 0.9rem; margin:0;">{BENCHMARK_SUMMARY.read_text(encoding='utf-8')}</pre>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==============================================================================
# PAGE 6: QUANTUM THREAT LAB
# ==============================================================================
def page_quantum():
    st.header("⚛️ Quantum Threat Lab")
    st.caption("Educational Qiskit quantum circuit demonstrating Shor's order-finding concept for period recovery.")

    story = narrative()
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            """
            <div class="comparison-box" style="border-top: 3px solid #ff6b7a;">
                <div style="font-size:1.1rem; font-weight:700; color:#ff6b7a;">CLASSICAL CRYPTOGRAPHY</div>
                <div style="margin: 8px 0; font-weight:600; color:#4C9BE8;">ECDSA (secp256k1) ──▶ Discrete Log Problem ──▶ Shor's Algorithm Threat</div>
                <p style="font-size:0.85rem; color:#8da2c0;">Current blockchains rely on ECDSA whose security rests on the hardness of computing discrete logarithms on elliptic curves. A fault-tolerant quantum computer running Shor's algorithm solves discrete logarithms in polynomial time BQP.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            <div class="comparison-box" style="border-top: 3px solid #3ee0a4;">
                <div style="font-size:1.1rem; font-weight:700; color:#3ee0a4;">POST-QUANTUM APPROACH</div>
                <div style="margin: 8px 0; font-weight:600; color:#3EE0A4;">ML-DSA-44 ──▶ Module Learning With Errors ──▶ Quantum-Resistant Lattice</div>
                <p style="font-size:0.85rem; color:#8da2c0;">ML-DSA (FIPS 204) is based on hard lattice problems over module polynomial rings. No known polynomial-time quantum algorithm solves high-dimensional Shortest Vector Problems (SVP), offering resistance to Shor's algorithm.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div style="background: rgba(255, 180, 50, 0.1); border: 1px solid #e6a700; border-radius: 8px; padding: 12px; margin: 16px 0;">
            <b style="color:#e6a700;">⚠️ Academic Disclaimer:</b> {DISCLAIMER}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Interactive Quantum Circuit: Order Finding for N = 15")
    st.write(
        "Shor's algorithm reduces the problem of integer factorization to **quantum order finding**: "
        "finding the period $r$ such that $a^r \\equiv 1 \\pmod N$. Once period $r$ is determined by the quantum "
        "phase estimation register, the classical processor computes non-trivial factors via $\\gcd(a^{r/2} \\pm 1, N)$."
    )

    q1, q2 = st.columns([1, 1])
    base_a = q1.selectbox("Coprime Base $a$ for $N=15$", [2, 4, 7, 8, 11, 13], index=0)
    shots = q2.slider("Simulation Measurement Shots", min_value=64, max_value=512, value=256, step=64)

    if st.button("RUN QUANTUM SHOR SIMULATION (AerSimulator)", type="primary", use_container_width=True):
        with st.spinner("Compiling Qiskit quantum circuit and executing on AerSimulator..."):
            shor_res = run_shor_demo(n=15, a=int(base_a), shots=shots)
            st.session_state.shor_res = shor_res

    res = st.session_state.get("shor_res")
    if res:
        st.divider()
        st.subheader("Quantum Order-Finding & Factorization Result")

        if res.get("ok"):
            p, q = res["factors"]
            st.success(
                f"✓ Quantum period found: r = {res.get('order')} | "
                f"Factors successfully recovered: {p} × {q} = {res.get('n')}"
            )
        else:
            st.error(f"Factor recovery failed: {res.get('error', 'Period was odd or yielded trivial factors.')}")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Modulus N", res.get("n"))
        m2.metric("Base a", res.get("base"))
        m3.metric("Quantum Period (r)", res.get("order", "—"))
        m4.metric("Circuit Depth", res.get("circuit_depth", "—"))

        st.markdown("**Top Measurement Outcomes from Quantum Phase Register:**")
        top_counts = res.get("top_counts", [])
        if top_counts:
            df_counts = pd.DataFrame(top_counts, columns=["Register State (Bitstring)", "Measurement Count"])
            st.dataframe(df_counts, use_container_width=True)


# ==============================================================================
# PAGE 7: WALLET / AUTHENTICATION
# ==============================================================================
def page_wallet():
    st.header("🔑 Password-Protected Wallet Access")
    st.caption(
        "Application security layer protecting wallet operations with scrypt password hashing and Fernet encryption. "
        "Private keys are never printed, never logged, and never stored in the blockchain."
    )

    store = wallet_store()
    tab_create, tab_unlock = st.tabs(["Create New Protected Wallet", "Unlock & Sign Transactions"])

    with tab_create:
        c1, c2 = st.columns(2)
        w_name = c1.text_input("Wallet Identifier", "alice-vault")
        w_algo = c2.selectbox("Signature Algorithm", ["ECDSA", "ML-DSA"], key="w_algo_select")
        w_pass = st.text_input("Master Password", type="password", key="create_w_pass")

        if st.button("CREATE ENCRYPTED WALLET", type="primary"):
            if not w_name or not w_pass:
                st.error("Wallet name and master password are required.")
            else:
                try:
                    meta = store.create(w_name, w_pass, w_algo)
                    st.success(f"✓ Wallet '{meta['name']}' created and encrypted using scrypt KDF.")
                    st.json(meta)
                except Exception as exc:
                    st.error(f"Error creating wallet: {exc}")

    with tab_unlock:
        available = store.list_wallets()
        if not available:
            st.info("No wallets found. Create one using the tab above.")
            return

        u_col1, u_col2 = st.columns(2)
        selected_wallet = u_col1.selectbox("Select Wallet to Unlock", available)
        unlock_password = u_col2.text_input("Enter Password", type="password", key="unlock_w_pass")

        if st.button("AUTHENTICATE & UNLOCK"):
            ok, reason, wallet = store.authenticate(selected_wallet, unlock_password)
            if ok:
                st.session_state.unlocked_wallet = wallet
                st.session_state.unlocked_name = selected_wallet
                st.success(f"✓ Authenticated. Wallet '{selected_wallet}' unlocked in memory. Private key remains protected.")
            else:
                st.error(f"Authentication failed: {reason}")

        if st.session_state.get("unlocked_wallet"):
            w = st.session_state.unlocked_wallet
            w_label = st.session_state.unlocked_name
            st.markdown(
                f"""
                <div class="comparison-box" style="border-left: 4px solid #3ee0a4; margin: 14px 0;">
                    <b>Active Wallet:</b> {w_label}<br>
                    <b>Algorithm:</b> {w.get_algorithm_name()}<br>
                    <b>Public Key Size:</b> {w.get_public_key_size()} Bytes<br>
                    <b>Private Key Status:</b> <span class="ok">Encrypted / Never Exposed</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.subheader("Sign Transaction with Unlocked Wallet")
            t_col1, t_col2 = st.columns(2)
            recv_target = t_col1.text_input("Recipient Account", "Bob", key="auth_recv")
            send_amt = t_col2.number_input("Amount", min_value=0.1, value=15.0, step=1.0, key="auth_amt")

            if st.button("SIGN & DISPATCH TRANSACTION", type="primary"):
                chain = _chain()
                res = create_and_commit_transaction(
                    chain,
                    w_label,
                    recv_target,
                    send_amt,
                    w.get_algorithm_name(),
                    wallet=w,
                )
                if res["accepted"]:
                    st.success("✓ Transaction signed with unlocked wallet and committed to blockchain.")
                else:
                    st.error(f"Transaction rejected: {res['reason']}")


# ==============================================================================
# PAGE 8: ABOUT, METHODOLOGY & FREQUENTLY ASKED QUESTIONS (FAQ)
# ==============================================================================
def page_about():
    st.header("📚 About, Methodology & Frequently Asked Questions")
    st.caption("Research context, mathematical background, and frequently asked technical questions.")

    tab_overview, tab_faq = st.tabs(["Research Architecture & Methodology", "Frequently Asked Questions (FAQ)"])

    with tab_overview:
        st.markdown(
            """
### 1. Research Problem & Motivation
- **Classical Vulnerability:** Mainstream blockchains (Bitcoin, Ethereum) use ECDSA (secp256k1) for digital signatures. Shor's quantum algorithm can solve the elliptic-curve discrete logarithm problem in polynomial time $\\mathcal{O}(n^3)$, threatening transaction authentication once cryptographically relevant quantum computers exist.
- **Post-Quantum Solution:** ML-DSA (Module Lattice Digital Signature Algorithm, FIPS 204), standardized by NIST in 2024, is based on the hardness of Module Learning With Errors (M-LWE). It is designed to resist quantum cryptanalysis.
- **Core Research Question:** *How can post-quantum digital signatures be integrated into an educational blockchain, and what performance and storage trade-offs result when compared with conventional ECDSA signatures?*

### 2. Architectural Layers
1. **Blockchain Core:** Proof-of-Authority consensus with authorized validators (`Validator1`, `Validator2`, `Validator3`), deterministic SHA-256 block hashing excluding the hash field, and strict hash linking.
2. **Cryptographic Layer:** `CryptoFactory` pattern abstracting `ECDSAWallet` and `MLDSAWallet` (via native `liboqs` ML-DSA-44), ensuring zero blockchain coupling to algorithm specifics.
3. **Application Security Layer:** Scrypt password hashing with PBKDF2/Fernet encryption ensuring zero plaintext private-key exposure.
4. **Quantum Demonstration:** 8-qubit Qiskit Aer simulation demonstrating quantum period finding for $N=15$, followed by classical continued fraction extraction.
            """
        )

    with tab_faq:
        st.markdown(
            """
### 💡 Frequently Asked Questions (Technical & Cryptographic FAQ)

**Q1: Why does Shor's algorithm threaten ECDSA but not SHA-256?**
> **Answer:** Shor's algorithm solves problems with periodic algebraic structure—specifically period-finding, integer factorization, and discrete logarithms (including elliptic curves). SHA-256 is a cryptographic hash function with no periodic algebraic group structure; it is only susceptible to Grover's quantum search algorithm, which provides a quadratic speedup (reducing SHA-256 to 128 bits of security, still well within safe margins).

**Q2: What is ML-DSA and what mathematical problem is it based on?**
> **Answer:** ML-DSA (formerly CRYSTALS-Dilithium) is a post-quantum signature scheme standardized in NIST FIPS 204. It is based on the hardness of finding short vectors in high-dimensional module lattices—specifically the Module Learning With Errors (M-LWE) and Module Short Integer Solution (M-SIS) problems, for which no polynomial-time quantum algorithm is known.

**Q3: What are the primary trade-offs of using ML-DSA-44 over ECDSA?**
> **Answer:** While ML-DSA-44 offers quantum resistance and fast signing/verification, its primary trade-off is **storage overhead**:
> - An ECDSA signature is ~70–72 bytes; an ML-DSA-44 signature is 2,420 bytes (~34× larger).
> - An ECDSA public key is 88 bytes; an ML-DSA-44 public key is 1,312 bytes (~15× larger).
> - This expands blockchain block size and network transmission bandwidth by approximately 10× to 34× per transaction.

**Q4: How does the blockchain prevent replay attacks?**
> **Answer:** Every transaction includes a unique nonce and a deterministic transaction ID computed as $\\text{SHA-256}(\\text{sender} \\parallel \\text{receiver} \\parallel \\text{amount} \\parallel \\text{timestamp} \\parallel \\text{nonce})$. The blockchain tracks all processed transaction IDs and `(sender, nonce)` pairs, immediately rejecting duplicates.

**Q5: Is this a toy or a real implementation of ML-DSA?**
> **Answer:** The ML-DSA implementation uses the genuine, native Open Quantum Safe (`liboqs`) C-library through `liboqs-python` using standard ML-DSA-44 (NIST Security Category 2). The measurements and signatures are real cryptographic outputs, not simulations or mocks.

**Q6: What is the purpose of the Qiskit Shor demo?**
> **Answer:** It provides an educational visualization of how quantum phase estimation finds the order $r$ of $a \\pmod N$ on a small scale ($N=15$). It illustrates the fundamental quantum mechanism that threatens classical cryptography, while explicitly clarifying that real cryptographic key sizes (e.g. 256-bit ECDSA) require millions of physical qubits far beyond today's quantum simulators.
            """
        )


PAGES = {
    "Command Center": page_command_center,
    "Transaction / Crypto Lab": page_crypto_lab,
    "Blockchain Explorer": page_explorer,
    "Security Center": page_security,
    "Performance Lab": page_performance,
    "Quantum Threat Lab": page_quantum,
    "Wallet / Authentication": page_wallet,
    "About & FAQ": page_about,
}

with st.sidebar:
    st.markdown("### 🛡️ Research Laboratory")
    page_sel = st.radio("Navigation", list(PAGES.keys()))
    st.divider()
    st.caption("Custom PoA Chain · SHA-256 · secp256k1 · ML-DSA-44 (FIPS 204)")
    st.caption("Academic Research Prototype")

PAGES[page_sel]()
