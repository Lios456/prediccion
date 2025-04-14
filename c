{% extends "base.html" %}

{% block content %}
<h2>Predicción de Humedad</h2>
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Predecir</button>
</form>

{% if prediccion %}
    <div class="resultado">
        <h3>Resultado: {{ prediccion|floatformat:1 }}% de humedad</h3>
        <p>Modelo utilizado: {{ form.cleaned_data.modelo }}</p>
        {% if grafico %}
            <img src="data:image/png;base64,{{ grafico }}" alt="Gráfico de predicción">
        {% endif %}
    </div>
{% endif %}
{% endblock %}