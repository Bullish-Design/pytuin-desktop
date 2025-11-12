# path: src/tests/test_builders_with_generators_v4.py
from pytuin_desktop import BlockBuilder, DeterministicGenerator, set_default_generator, reset_default_generator, AtrbParser, DocumentEditor

def test_deterministic_ids_stable_across_runs(tmp_path):
    try:
        set_default_generator(DeterministicGenerator(seed=42))
        ed1 = DocumentEditor.create("D1")
        ed1.add_block(BlockBuilder.paragraph("A"))
        p1 = tmp_path / "a.atrb"
        ed1.save(p1)
        id1 = AtrbParser.parse_file(p1).content[0].id

        set_default_generator(DeterministicGenerator(seed=42))
        ed2 = DocumentEditor.create("D2")
        ed2.add_block(BlockBuilder.paragraph("A"))
        p2 = tmp_path / "b.atrb"
        ed2.save(p2)
        id2 = AtrbParser.parse_file(p2).content[0].id

        assert id1 == id2
    finally:
        reset_default_generator()
