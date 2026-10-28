from django import template
from django.utils.safestring import mark_safe

from services.chat_contrato import desde_estructura, render_html as render_contrato, validar
from services.chat_presentacion import render_html as render_legacy

register = template.Library()


@register.filter(name="asistente_html")
def asistente_html(estructura):
    """Renderiza el contrato o la estructura legacy. HTML ya escapado."""
    if not isinstance(estructura, dict) or not estructura:
        return ""
    if estructura.get("schema_version") == "1.0":
        ok, _ = validar(estructura)
        if ok:
            return mark_safe(render_contrato(estructura))
        return mark_safe(render_contrato(estructura))  # render_contrato muestra aviso si falla
    # Compatibilidad con respuestas antiguas del historial de sesión
    return mark_safe(render_legacy(estructura))
