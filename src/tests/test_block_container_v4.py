# path: src/tests/test_block_container_v4.py
from uuid import uuid4
from pytuin_desktop.block_container import BlockContainer
from pytuin_desktop.models import BaseBlock
from pytuin_desktop.builders import BlockBuilder

def test_block_container_add_existing_and_new():
    c = BlockContainer()
    c.add_existing(BaseBlock(id=uuid4(), type="paragraph", props={}))
    c.add_new(BlockBuilder.paragraph("Hello"))
    assert len(c) == 2
    seq = list(c)
    assert isinstance(seq[0], BaseBlock)

def test_block_container_get_and_remove():
    c = BlockContainer()
    b1 = BaseBlock(id=uuid4(), type="paragraph", props={})
    c.add_existing(b1)
    c.add_new(BlockBuilder.paragraph("X"))
    assert c.get_at(0) == b1
    c.remove_at(0)
    assert len(c) == 1

def test_block_container_move_within_regions():
    c = BlockContainer()
    # existing region
    e1 = BaseBlock(id=uuid4(), type="heading", props={})
    e2 = BaseBlock(id=uuid4(), type="heading", props={})
    c.add_existing(e1); c.add_existing(e2)
    c.move(0,1)
    assert list(c)[0] == e2
    # new region
    n1 = BlockBuilder.paragraph("A")
    n2 = BlockBuilder.paragraph("B")
    c.add_new(n1); c.add_new(n2)
    c.move(2,3)  # move first new after second new
    assert list(c)[2] == n2
    # crossing should fail
    try:
        c.move(0,3)
        assert False, "should raise"
    except ValueError:
        pass

def test_block_container_replace():
    c = BlockContainer()
    e = BaseBlock(id=uuid4(), type="paragraph", props={})
    c.add_existing(e)
    c.replace_at(0, BlockBuilder.paragraph("New"))
    assert len(c.get_existing_blocks()) == 0
    assert len(c.get_new_templates()) == 1

def test_block_container_find():
    c = BlockContainer()
    target = BaseBlock(id=uuid4(), type="heading", props={})
    c.add_existing(BaseBlock(id=uuid4(), type="paragraph", props={}))
    c.add_existing(target)
    pos = c.find_by_id(target.id)
    assert pos and pos[0] == 1
    heads = c.find_blocks_by_type("heading")
    assert len(heads) == 1 and heads[0][0] == 1
