from pathlib import Path


def test_release_docs_exist() -> None:
    assert Path("docs/FIRST_RUN.md").exists()
    assert Path("docs/RELEASE_CHECKLIST.md").exists()
    assert Path("KNOWN_LIMITATIONS.md").exists()

