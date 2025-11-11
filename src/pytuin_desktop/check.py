# src/pytuin_desktop/check.py
import sys, importlib, importlib.metadata as md, pprint
print(sys.executable)
pprint.pp(sys.path)

try:
    import templateer
    print("templateer imported:", templateer.__file__)
    try:
        print("templateer version:", md.version("templateer"))
    except md.PackageNotFoundError:
        print("templateer is importable but not registered in metadata")
    from templateer import discover_templates
    print("discover_templates ok:", discover_templates)
except Exception as e:
    print("IMPORT FAILED:", repr(e))
    raise

