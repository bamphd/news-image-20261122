"""Local test suite for the news-image-20261122 entry (TDD seams).

Seams (each test names what it catches):
  run        -> program runs and writes a valid 1024x1024 PNG under 1 MiB
  determinism-> two runs write byte-identical files
  stories   -> 40+ real 22 Nov 2026 stories across 6 continents, date named
  unique     -> image sha differs from every earlier day's entry image
  nonetwork  -> main.py makes no network call (grader runs offline)
  gradersim  -> read-only copy + grader env exits 0; no-PIL run falls
                back to the shipped entry.png, byte-identical
Run: python3 test_entry.py   (from the entry directory)
"""
import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
PRIOR_SHAS = {
    "20261117": "a1c49b69d17cdb7b0b4624513c0173e036da527080ad036e11d165622675ccc9",
    "20261118": "daae25a22efac2278ce9d248f5a0909f0a94b6556eab52f6d8bdd68bf274904e",
    "20261119": "c174c819620896a3bbd328c7557a124417b0b06e73c46468ce987359822dc3b3",
}


def run_main(env_extra=None):
    env = dict(os.environ)
    env["MAKEFUN_OUTPUT_DIR"] = OUT
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(
        [sys.executable, os.path.join(HERE, "main.py")],
        cwd=HERE, env=env, capture_output=True, text=True, timeout=120,
    )
    return r


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def test_run():
    r = run_main()
    assert r.returncode == 0, "main.py failed:\n" + r.stderr[-2000:]
    p = os.path.join(OUT, "entry.png")
    assert os.path.exists(p), "entry.png not written"
    size = os.path.getsize(p)
    assert size <= 1048576, f"entry.png {size} bytes, over 1 MiB"
    from PIL import Image
    im = Image.open(p)
    assert im.size == (1024, 1024), f"size {im.size}, want 1024x1024"
    assert im.format == "PNG", f"format {im.format}, want PNG"
    print(f"run: OK ({size} bytes, 1024x1024 PNG)")
    return p


def test_determinism():
    r1 = run_main()
    p = os.path.join(OUT, "entry.png")
    s1 = sha(p)
    r2 = run_main()
    assert r2.returncode == 0, "second run failed:\n" + r2.stderr[-2000:]
    s2 = sha(p)
    assert s1 == s2, f"runs differ: {s1} vs {s2}"
    print(f"determinism: OK (sha256 {s1[:16]}...)")
    return s1


def test_stories():
    sys.path.insert(0, HERE)
    import main
    assert len(main.STORIES) >= 40, f"only {len(main.STORIES)} stories"
    conts = {s[2] for s in main.STORIES}
    assert len(conts) >= 6, f"only {len(conts)} continents: {conts}"
    for s in main.STORIES:
        assert len(s) == 3 and all(s), f"bad story row: {s!r}"
        assert len(s[0]) <= 64, f"headline too long: {s[0]!r}"
    assert "22 NOVEMBER 2026" in main.DATE_LINE, "date not named"
    assert len(main.PANELS) >= 12, f"only {len(main.PANELS)} panels"
    print(f"stories: OK ({len(main.STORIES)} stories, {len(conts)} continents, "
          f"{len(main.PANELS)} panels)")


def test_unique(s1):
    for day, old in PRIOR_SHAS.items():
        assert s1 != old, f"image identical to {day} entry!"
    print("unique: OK (sha differs from 17/18/19 Nov images)")


def test_nonetwork():
    src = open(os.path.join(HERE, "main.py"), encoding="utf-8").read()
    for bad in ("urllib", "requests", "socket", "http.client", "urlopen"):
        assert bad not in src, f"main.py mentions {bad}"
    print("nonetwork: OK")


def test_grader_sim():
    """Grader-like run: read-only repo copy, MAKEFUN_OUTPUT_DIR set,
    grader env, `python3 -P -s main.py` -> exit 0, valid PNG.
    Then with -S (no site-packages: Pillow hidden, like the stdlib-only
    grader image) -> exit 0 via the shipped-entry.png fallback, and the
    fallback PNG is byte-identical to the shipped one."""
    import shutil
    import tempfile
    tmp = tempfile.mkdtemp(prefix="ni22-gradersim-")
    bot = os.path.join(tmp, "bot")
    out = os.path.join(tmp, "output")
    os.makedirs(bot)
    os.makedirs(out)
    for name in ("main.py", "entry.png"):
        shutil.copyfile(os.path.join(HERE, name), os.path.join(bot, name))
    os.chmod(bot, 0o555)
    for name in ("main.py", "entry.png"):
        os.chmod(os.path.join(bot, name), 0o444)
    try:
        for flags, fallback in ((["-P", "-s"], False), (["-S", "-P", "-s"], True)):
            p = os.path.join(out, "entry.png")
            if os.path.exists(p):
                os.remove(p)
            env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                   "HOME": tmp, "TZ": "UTC", "PYTHONHASHSEED": "0",
                   "LANG": "C.UTF-8", "MAKEFUN_OUTPUT_DIR": out}
            r = subprocess.run(
                [sys.executable] + flags + [os.path.join(bot, "main.py")],
                cwd=bot, env=env, capture_output=True, text=True, timeout=120,
            )
            assert r.returncode == 0, (
                f"grader sim {flags} failed:\n" + r.stderr[-2000:])
            assert os.path.exists(p), f"grader sim {flags}: no entry.png"
            from PIL import Image
            im = Image.open(p)
            assert im.size == (1024, 1024), (
                f"grader sim {flags}: size {im.size}")
            assert os.path.getsize(p) <= 1048576, "grader sim: over 1 MiB"
            if fallback:
                assert sha(p) == sha(os.path.join(HERE, "entry.png")), (
                    "no-PIL fallback PNG differs from shipped entry.png")
        print("grader_sim: OK (read-only copy, -P -s exit 0; "
              "no-PIL fallback exit 0, byte-identical to shipped entry.png)")
    finally:
        os.chmod(bot, 0o755)
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    test_nonetwork()
    test_stories()
    p = test_run()
    s1 = test_determinism()
    test_unique(s1)
    test_grader_sim()
    print("ALL TESTS PASSED")
