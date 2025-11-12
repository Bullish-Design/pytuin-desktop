# path: src/tests/test_serializers_v4.py
from io import StringIO
from pytuin_desktop.serializers import SafeYamlSerializer

def test_safe_yaml_serializer_roundtrip():
    s = SafeYamlSerializer()
    data = {"key": "value", "list": [1,2,3]}
    text = s.dumps(data, sort_keys=False)
    assert "key: value" in text
    fp = StringIO()
    s.dump(data, fp, sort_keys=False)
    fp.seek(0)
    loaded = s.load(fp)
    assert loaded == data
    loaded2 = s.loads(text)
    assert loaded2 == data
