"""Download a Windows liboqs 0.16 shared library if ML-DSA cannot load."""

from __future__ import annotations

import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "third_party" / "liboqs" / "bin"
URL = "https://mirror.msys2.org/mingw/ucrt64/mingw-w64-ucrt-x86_64-liboqs-0.16.0-1-any.pkg.tar.zst"


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    if (DEST / "oqs.dll").exists() or (DEST / "liboqs.dll").exists():
        print("liboqs DLL already present")
        return
    archive = ROOT / "third_party" / "liboqs.pkg.tar.zst"
    print("Downloading", URL)
    urllib.request.urlretrieve(URL, archive)
    tar_path = ROOT / "third_party" / "liboqs.pkg.tar"
    try:
        import zstandard as zstd
    except ImportError:
        raise SystemExit("Decompress with zstd.exe then copy ucrt64/bin/liboqs-9.dll to third_party/liboqs/bin/oqs.dll")
    with archive.open("rb") as src, tar_path.open("wb") as out:
        zstd.ZstdDecompressor().copy_stream(src, out)
    with tarfile.open(tar_path) as tar:
        for member in tar.getmembers():
            if member.name.endswith("liboqs-9.dll"):
                extracted = tar.extractfile(member)
                if extracted is None:
                    continue
                data = extracted.read()
                (DEST / "liboqs-9.dll").write_bytes(data)
                (DEST / "liboqs.dll").write_bytes(data)
                (DEST / "oqs.dll").write_bytes(data)
                print("Installed", DEST / "oqs.dll")
                return
    raise SystemExit("DLL not found in archive")


if __name__ == "__main__":
    main()
