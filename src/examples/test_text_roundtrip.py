#!/usr/bin/env -S uv run --script
# tests/test_text_roundtrip.py
#
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pydantic>=2.0.0",
#     "pyyaml>=6.0.0",
# ]
# ///

"""
Text-level roundtrip test for .atrb files.

Parses and writes files, then does line-by-line text comparison using difflib.
Generates HTML diff reports.
"""

from __future__ import annotations

import sys
import difflib
from pathlib import Path
from datetime import datetime


path_dir = str(Path(__file__).parent.parent)

# Add src to path
print(f"Adding directory to path: {path_dir} ")
sys.path.insert(0, path_dir)


from pytuin_desktop.parser import AtrbParser
from pytuin_desktop.writer import AtrbWriter


def generate_html_diff(
    original_lines: list[str], rewritten_lines: list[str], filename: str
) -> str:
    """Generate HTML diff using difflib."""
    differ = difflib.HtmlDiff(wrapcolumn=80)
    html = differ.make_file(
        original_lines,
        rewritten_lines,
        fromdesc=f"Original: {filename}",
        todesc=f"Rewritten: {filename}",
        context=True,
        numlines=3,
    )
    return html


def process_file(
    input_file: Path, output_dir: Path, html_dir: Path
) -> tuple[bool, int]:
    """
    Process single file: parse, write, compare.
    Returns (success, num_differences).
    """
    # Read original
    with open(input_file, "r", encoding="utf-8") as f:
        original_text = f.read()
    original_lines = original_text.splitlines(keepends=True)

    # Parse and write
    doc = AtrbParser.parse_file(input_file)
    output_file = output_dir / input_file.name
    AtrbWriter.write_file(doc, output_file)

    # Read rewritten
    with open(output_file, "r", encoding="utf-8") as f:
        rewritten_text = f.read()
    rewritten_lines = rewritten_text.splitlines(keepends=True)

    # Compare
    diff = list(
        difflib.unified_diff(
            original_lines,
            rewritten_lines,
            fromfile=f"original/{input_file.name}",
            tofile=f"rewritten/{input_file.name}",
            lineterm="",
        )
    )

    # Generate HTML diff
    html_output = html_dir / f"{input_file.stem}_diff.html"
    html_content = generate_html_diff(original_lines, rewritten_lines, input_file.name)
    with open(html_output, "w", encoding="utf-8") as f:
        f.write(html_content)

    success = len(diff) == 0
    return success, len(diff)


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: test_text_roundtrip.py <input_dir> <output_dir>")
        print("\nExample:")
        print("  uv run test_text_roundtrip.py ./tests/fixtures ./output")
        sys.exit(1)

    input_dir = Path(sys.argv[1])
    base_output_dir = Path(sys.argv[2])

    # Create timestamped subdirectory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = base_output_dir / timestamp

    html_dir = output_dir / "diffs"

    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    html_dir.mkdir(parents=True, exist_ok=True)

    print(f"Input:  {input_dir.absolute()}")
    print(f"Output: {output_dir.absolute()}")
    print(f"Diffs:  {html_dir.absolute()}")
    print("=" * 70)
    print()

    atrb_files = list(input_dir.glob("**/*.atrb"))

    if not atrb_files:
        print(f"No .atrb files found in {input_dir}")
        sys.exit(1)

    results = {}

    for atrb_file in atrb_files:
        print(f"Processing: {atrb_file.name}")

        try:
            success, num_diffs = process_file(atrb_file, output_dir, html_dir)
            results[atrb_file.name] = (success, num_diffs)

            if success:
                print(f"  ✓ Identical")
            else:
                print(f"  ✗ {num_diffs} line(s) differ")
                print(f"  → See: {html_dir / f'{atrb_file.stem}_diff.html'}")

        except Exception as e:
            print(f"  ✗ Error: {e}")
            results[atrb_file.name] = (False, -1)

        print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    total = len(results)
    passed = sum(1 for success, _ in results.values() if success)
    failed = total - passed

    print(f"Total: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed > 0:
        print("\nFailed files:")
        for filename, (success, num_diffs) in results.items():
            if not success:
                if num_diffs >= 0:
                    print(f"  - {filename}: {num_diffs} line(s) differ")
                else:
                    print(f"  - {filename}: error")
        print(f"\nHTML diffs: {html_dir}")
        sys.exit(1)
    else:
        print("\n✓ All files identical!")
        sys.exit(0)


if __name__ == "__main__":
    main()
