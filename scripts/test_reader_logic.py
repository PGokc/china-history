"""Compile and exercise the app's actual chronology and reading-position logic."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix="shiji-reader-tests-") as temporary:
    directory = Path(temporary)
    binary = directory / "reader-tests"
    # FileProvider can change timestamps during compilation. Compile a byte
    # snapshot of the actual sources in the temporary directory instead.
    inputs = []
    for relative in ["App/EventChronology.swift", "App/ReadingProgress.swift", "scripts/tests/ReaderLogicTests.swift"]:
        source = root / relative
        snapshot = directory / source.name
        snapshot.write_bytes(source.read_bytes())
        inputs.append(str(snapshot))
    subprocess.run([
        "xcrun", "swiftc", "-module-cache-path", str(directory / "modules"),
        *inputs, "-o", str(binary),
    ], check=True)
    subprocess.run([str(binary)], check=True)
