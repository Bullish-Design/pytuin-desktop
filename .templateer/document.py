# .templateer/document.py
"""Document templates for .atrb files."""
from __future__ import annotations

from templateer import TemplateModel


EMPTY_DOCUMENT_TEMPLATE = """id: "{{ document_id }}"
name: "{{ name }}"
version: {{ version }}
content: []
"""


class EmptyDocumentTemplate(TemplateModel):
    """Template for an empty .atrb document."""
    
    __template__ = EMPTY_DOCUMENT_TEMPLATE
    
    document_id: str
    name: str
    version: int = 1
    
    
# DOCUMENT_TEMPLATE = """id: "{{ document_id }}"
# name: "{{ name }}"
# version: {{ version }}
# content:
# {% for block in blocks %}
#   - {{ block|indent(4, true) }}
# {% endfor %}
# """

# DOCUMENT_TEMPLATE = """id: "{{ document_id }}"
# name: "{{ name }}"
# version: {{ version }}
# content:
# {% if blocks|length == 0 %}
#   []
# {% else %}
# {% for block in blocks %}
#   -
# {{ block|indent(4, true) }}
# {% endfor %}
# {% endif %}
# """

# DOCUMENT_TEMPLATE = """id: "{{ document_id }}"
# name: "{{ name }}"
# version: {{ version }}
# content:
# {% if blocks|length == 0 %}
#   []
# {% else %}
# {% for block in blocks %}
# {%- set lines = block.split('\\n') -%}
#   - {{ lines[0] }}
# {{ (lines[1:] | join('\\n')) | indent(4, true) }}
# {% endfor %}
# {% endif %}
# """

# DOCUMENT_TEMPLATE = """id: "{{ document_id }}"
# name: "{{ name }}"
# version: {{ version }}
# content:
# {% if blocks|length == 0 %}
#   []
# {% else %}
# {# Indent the entire list item (dash + mapping) by 2 spaces #}
# {% for block in blocks -%}
# {{ ("- " ~ (block | replace('\\n', '\\n  '))) | indent(2, True) }}
# {% endfor %}
# {% endif %}
# """

DOCUMENT_TEMPLATE = """id: "{{ document_id }}"
name: "{{ name }}"
version: {{ version }}
content:
{% if blocks|length == 0 %}
  []
{% else %}
{% for block in blocks %}
{%- set head, tail = (block.split('\\n', 1) + [''])[:2] -%}
  - {{ head }}
{{ tail | indent(2, true) }}
{% endfor %}
{% endif %}
"""

class DocumentTemplate(TemplateModel):
    """Template for a complete .atrb document with blocks."""
    
    __template__ = DOCUMENT_TEMPLATE
    
    document_id: str
    name: str
    version: int = 1
    blocks: list[TemplateModel] = []