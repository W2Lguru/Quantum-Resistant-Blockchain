import inspect
import traceback

print("=== import oqs ===")
try:
    import oqs
    print("oqs file", getattr(oqs, "__file__", None))
    print("oqs version", getattr(oqs, "__version__", None))
    print("oqs attrs", [x for x in dir(oqs) if not x.startswith("_")])
    if hasattr(oqs, "get_enabled_sig_mechanisms"):
        mechs = list(oqs.get_enabled_sig_mechanisms())
        print("sig mechs", mechs)
        print(
            "ML related",
            [m for m in mechs if any(s in m.upper() for s in ("DSA", "DILITH", "ML-"))],
        )
    if hasattr(oqs, "Signature"):
        print("Signature init", inspect.signature(oqs.Signature.__init__))
        print("Signature methods", [m for m in dir(oqs.Signature) if not m.startswith("_")])
        try:
            sig = oqs.Signature("ML-DSA-44")
            print("created ML-DSA-44", type(sig))
            print("details", getattr(sig, "details", None))
            pk = sig.generate_keypair()
            print("pk type", type(pk), "len", len(pk) if pk is not None else None)
            msg = b"hello-mldsa"
            signature = sig.sign(message=msg) if False else sig.sign(msg)
            print("sig len", len(signature))
            ok = sig.verify(msg, signature, pk)
            print("verify", ok)
            print("sign signature", inspect.signature(sig.sign))
            print("verify signature", inspect.signature(sig.verify))
        except Exception:
            traceback.print_exc()
except Exception:
    traceback.print_exc()

print("\n=== import liboqs / oqs.oqs ===")
try:
    import liboqs
    print("liboqs", liboqs)
except Exception as e:
    print("liboqs import failed", type(e), e)
