{{ fullname }}
{{ underline }}

{% block attributes %}
{% if attributes %}
.. rubric:: Attributes

.. autosummary::
{% for item in attributes %}
  {{ fullname }}.{{ item }}
{%- endfor %}
{% endif %}
{% endblock %}

{% block methods %}
{% if methods %}
.. rubric:: Methods

.. autosummary::
{% for item in methods %}
  {{ fullname }}.{{ item }}
{%- endfor %}
{% endif %}
{% endblock %}

.. autoclass:: {{ fullname }}
    :members:
    :inherited-members:
    :undoc-members:
