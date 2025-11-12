# path: src/tests/test_id_generators_v4.py
from pytuin_desktop import (
    DeterministicGenerator, SequentialGenerator, UUIDv4Generator,
    set_default_generator, reset_default_generator, generate_block_id
)

def test_uuid4_generator_unique():
    gen = UUIDv4Generator()
    ids = [gen.generate() for _ in range(30)]
    assert len(set(ids)) == 30

def test_deterministic_same_seed_sequence():
    g1 = DeterministicGenerator(seed=123)
    g2 = DeterministicGenerator(seed=123)
    a = [g1.generate() for _ in range(5)]
    b = [g2.generate() for _ in range(5)]
    assert a == b

def test_sequential_generator_counts():
    g = SequentialGenerator(start=100)
    ints = [g.generate().int for _ in range(3)]
    assert ints == [101, 102, 103]

def test_builder_uses_default_generator(tmp_path):
    from pytuin_desktop import BlockBuilder, AtrbParser
    try:
        set_default_generator(SequentialGenerator(start=2000))
        from pytuin_desktop import DocumentEditor
        ed = DocumentEditor.create("G")
    finally:
        pass
    ed.add_block(BlockBuilder.paragraph("X"))
    p = tmp_path / "g.atrb"
    ed.save(p)
    doc = AtrbParser.parse_file(p)
    assert doc.content[0].id.int == 2001
    reset_default_generator()
