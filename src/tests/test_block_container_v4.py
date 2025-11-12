# path: src/tests/test_block_container_v4.py
import pytest
from uuid import uuid4
from pytuin_desktop import BaseBlock
from pytuin_desktop import BlockBuilder
from pytuin_desktop.block_container import BlockContainer

def test_block_container_add_existing_and_new():
    c = BlockContainer()
    existing = BaseBlock(id=uuid4(), type="paragraph", props={}, content=[], children=[])
    c.add_existing(existing)
    new_t = BlockBuilder.paragraph("hello")
    c.add_new(new_t)
    assert len(c) == 2
    assert c.get_at(0) == existing
    assert c.get_at(1) == new_t

def test_block_container_get_and_remove():
    c = BlockContainer()
    a = BaseBlock(id=uuid4(), type="paragraph", props={}, content=[], children=[])
    b = BaseBlock(id=uuid4(), type="heading", props={}, content=[], children=[])
    c.add_existing(a); c.add_existing(b)
    assert c.get_at(1) == b
    c.remove_at(0)
    assert len(c) == 1
    assert c.get_at(0) == b

def test_block_container_move_within_regions():
    c = BlockContainer()
    a = BaseBlock(id=uuid4(), type="paragraph", props={}, content=[], children=[])
    b = BaseBlock(id=uuid4(), type="heading", props={}, content=[], children=[])
    c.add_existing(a); c.add_existing(b)
    # move within existing
    c.move(0, 1)
    assert c.get_at(0) == b and c.get_at(1) == a

    # new region
    n1 = BlockBuilder.paragraph("one")
    n2 = BlockBuilder.paragraph("two")
    c.add_new(n1); c.add_new(n2)
    c.move(3, 2)  # swap n1/n2
    assert c.get_at(2) == n2 and c.get_at(3) == n1

    # cannot cross boundary
    with pytest.raises(ValueError):
        c.move(0, 3)

def test_block_container_replace():
    c = BlockContainer()
    a = BaseBlock(id=uuid4(), type="paragraph", props={}, content=[], children=[])
    c.add_existing(a)
    n = BlockBuilder.heading("Replaced")
    # replacing index 0 should put a new template at start of new-section
    c.replace_at(0, n)
    assert len(c) == 1
    assert c.get_at(0) == n

def test_block_container_find():
    c = BlockContainer()
    target_id = uuid4()
    c.add_existing(BaseBlock(id=uuid4(), type="paragraph", props={}, content=[], children=[]))
    tgt = BaseBlock(id=target_id, type="heading", props={}, content=[], children=[])
    c.add_existing(tgt)
    idx, blk = c.find_by_id(target_id)
    assert blk.id == target_id and idx == 1
    heads = c.find_blocks_by_type("heading")
    assert len(heads) == 1 and heads[0][1].type == "heading"
