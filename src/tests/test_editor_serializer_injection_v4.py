# path: src/tests/test_editor_serializer_injection_v4.py
from pytuin_desktop.serializers import SafeYamlSerializer
from pytuin_desktop import DocumentEditor, BlockBuilder
from io import StringIO

class TrackingSerializer(SafeYamlSerializer):
    def __init__(self):
        super().__init__()
        self.dump_calls = 0
        self.loads_calls = 0
    def dump(self, data, stream, **kwargs):
        self.dump_calls += 1
        return super().dump(data, stream, **kwargs)
    def loads(self, text: str):
        self.loads_calls += 1
        return super().loads(text)

def test_editor_uses_injected_serializer(tmp_path):
    tr = TrackingSerializer()
    ed = DocumentEditor.create("T", serializer=tr)
    ed.add_block(BlockBuilder.paragraph("Hi"))
    p = tmp_path / "x.atrb"
    ed.save(p)
    assert tr.dump_calls >= 1
