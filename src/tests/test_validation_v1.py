"""Step 8: Validate all generated .atrb files using AtrbParser."""
from __future__ import annotations

from pathlib import Path
import pytest

from pytuin_desktop import AtrbParser


TEST_OUTPUT_DIR = Path(__file__).parent / "v1"


def _all_v1_files() -> list[Path]:
    if not TEST_OUTPUT_DIR.exists():
        return []
    return sorted(TEST_OUTPUT_DIR.glob("*.atrb"))


@pytest.mark.parametrize("atrb_file", _all_v1_files())
def test_validate_every_generated_file(atrb_file: Path):
    """Every .atrb generated in previous steps should parse cleanly."""
    doc = AtrbParser.parse_file(atrb_file)
    assert doc.id is not None
    assert doc.name
    assert isinstance(doc.version, int)
    assert isinstance(doc.content, list)


def test_validate_specific_known_files():
    """Spot-check a few expected files with expected block counts if present."""
    cases = [
        ("00_empty.atrb", 0),
        ("01_single_paragraph.atrb", 1),
        ("03_heading.atrb", 1),
        ("04_horizontal_rule.atrb", 1),
        ("05_script.atrb", 1),
    ]
    for fname, count in cases:
        p = TEST_OUTPUT_DIR / fname
        if not p.exists():
            pytest.skip(f"{fname} not generated yet")
        doc = AtrbParser.parse_file(p)
        assert len(doc.content) == count


def test_parse_rejects_incomplete_document():
    """Missing required top-level keys should raise an error."""
    invalid = "id: '1234'\nname: 'Missing version'\n"
    with pytest.raises(Exception):
        AtrbParser.parse_string(invalid)
