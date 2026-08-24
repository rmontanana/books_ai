import json
from pathlib import Path

from books_ai.pipeline.fingerprint import Fingerprints


def test_missing_path_has_no_digest(tmp_path: Path) -> None:
    fp = Fingerprints()
    assert fp.of(tmp_path / "no-existe.txt") is None


def test_same_content_same_digest(tmp_path: Path) -> None:
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("hola")
    b.write_text("hola")
    fp = Fingerprints()
    assert fp.of(a) == fp.of(b)


def test_changed_content_changes_digest(tmp_path: Path) -> None:
    f = tmp_path / "a.txt"
    f.write_text("hola")
    fp = Fingerprints()
    before = fp.of(f)
    f.write_text("adios")
    assert fp.of(f) != before


def test_directory_digest_covers_contents(tmp_path: Path) -> None:
    d = tmp_path / "libros"
    (d / "sub").mkdir(parents=True)
    (d / "sub" / "uno.txt").write_text("uno")
    fp = Fingerprints()
    before = fp.of(d)
    (d / "sub" / "dos.txt").write_text("dos")
    assert fp.of(d) != before


def test_directory_digest_ignores_file_order(tmp_path: Path) -> None:
    left = tmp_path / "left"
    right = tmp_path / "right"
    left.mkdir()
    right.mkdir()
    for name in ("b.txt", "a.txt"):
        (left / name).write_text(name)
    for name in ("a.txt", "b.txt"):
        (right / name).write_text(name)
    fp = Fingerprints()
    assert fp.of(left) == fp.of(right)


def test_cache_survives_a_reload(tmp_path: Path) -> None:
    f = tmp_path / "a.txt"
    f.write_text("hola")
    cache = tmp_path / "fingerprints.json"
    first = Fingerprints(cache_path=cache)
    digest = first.of(f)
    first.save()
    assert cache.exists()
    assert Fingerprints(cache_path=cache).of(f) == digest


def test_una_cache_corrupta_no_tumba_el_arranque(tmp_path: Path) -> None:
    """La cache es una optimizacion: si esta mal, se recalcula y ya."""
    f = tmp_path / "a.txt"
    f.write_text("hola")
    cache = tmp_path / "fingerprints.json"
    stat = f.stat()
    cache.write_text(
        json.dumps(
            {
                str(f.resolve()): [stat.st_size, stat.st_mtime_ns],  # sin la huella
                "/otro": "ni siquiera una lista",
            }
        )
    )
    assert Fingerprints(cache_path=cache).of(f) == Fingerprints().of(f)
