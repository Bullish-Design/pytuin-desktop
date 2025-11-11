"""Block templates for .atrb files."""
from __future__ import annotations

from templateer import TemplateModel
from .content import TextContentTemplate


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


# ---- Step 7 additions -------------------------------------------------------

HEADING_BLOCK_TEMPLATE = """id: "{{ block_id }}"
type: heading
props:
  level: {{ level }}
  isToggleable: {{ is_toggleable|lower }}
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


class HeadingBlockTemplate(TemplateModel):
    """Template for heading blocks."""
    
    __template__ = HEADING_BLOCK_TEMPLATE
    
    block_id: str
    level: int = 1
    is_toggleable: bool = False
    text_color: str = "default"
    background_color: str = "default"
    text_alignment: str = "left"
    content: list[TextContentTemplate] = []


HORIZONTAL_RULE_TEMPLATE = """id: "{{ block_id }}"
type: horizontal_rule
props: {}
children: []"""


class HorizontalRuleTemplate(TemplateModel):
    """Template for horizontal rule divider."""
    
    __template__ = HORIZONTAL_RULE_TEMPLATE
    
    block_id: str


SCRIPT_BLOCK_TEMPLATE = """id: "{{ block_id }}"
type: script
props:
  interpreter: {{ interpreter }}
  outputVariable: {{ output_variable }}
  name: {{ name }}
  code: {{ code|tojson }}
  outputVisible: {{ output_visible|lower }}
  dependency: {{ dependency|tojson }}
children: []"""


class ScriptBlockTemplate(TemplateModel):
    """Template for script execution blocks."""
    
    __template__ = SCRIPT_BLOCK_TEMPLATE
    
    block_id: str
    name: str
    code: str
    interpreter: str = "bash"
    output_variable: str = ""
    output_visible: bool = True
    dependency: str = '{"pip": [], "npm": []}'
