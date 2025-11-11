# .templateer/blocks.py
"""Block templates for .atrb files."""
from __future__ import annotations

from templateer import TemplateModel
from .content import TextContentTemplate


# PARAGRAPH_BLOCK_TEMPLATE = """id: "{{ block_id }}"
# type: paragraph
# props:
#   textColor: {{ text_color }}
#   backgroundColor: {{ background_color }}
#   textAlignment: {{ text_alignment }}
# content:
# {% if content|length == 0 %}
#   []
# {% else %}
# {% for item in content %}
#   -
# {{ item|indent(4, true) }}
# {% endfor %}
# {% endif %}
# children: []"""

# PARAGRAPH_BLOCK_TEMPLATE = """id: "{{ block_id }}"
# type: paragraph
# props:
#   textColor: {{ text_color }}
#   backgroundColor: {{ background_color }}
#   textAlignment: {{ text_alignment }}
# content:
# {% if content|length == 0 %}
#   []
# {% else %}
# {%- for item in content -%}
# {{ ("- " ~ (item | replace('\\n', '\\n  '))) | indent(2, true) }}
# {%- endfor %}
# {% endif %}
# children: []"""

# PARAGRAPH_BLOCK_TEMPLATE = """id: "{{ block_id }}"
# type: paragraph
# props:
#   textColor: {{ text_color }}
#   backgroundColor: {{ background_color }}
#   textAlignment: {{ text_alignment }}
# content:
# {% if content|length == 0 %}
#   []
# {% else %}
# {% for item in content %}
# {{ ("- " ~ (item | replace('\\n', '\\n  '))) | indent(2, true) }}
# {% endfor %}
# {% endif %}
# children: []"""

PARAGRAPH_BLOCK_TEMPLATE = """id: "{{ block_id }}"
type: paragraph
props:
  textColor: {{ text_color }}
  backgroundColor: {{ background_color }}
  textAlignment: {{ text_alignment }}
content:
{% if content|length == 0 %}
  []
{% else %}
{% for item in content -%}
{{ "- " ~ (item | replace('\\n', '\\n  ')) }}
{% endfor %}
{% endif %}
children: []"""


class ParagraphBlockTemplate(TemplateModel):
    """Template for paragraph blocks."""
    
    __template__ = PARAGRAPH_BLOCK_TEMPLATE
    
    block_id: str
    text_color: str = "default"
    background_color: str = "default"
    text_alignment: str = "left"
    content: list[TextContentTemplate] = []