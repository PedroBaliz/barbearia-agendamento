from django import forms, template

register = template.Library()


@register.filter
def bootstrap(campo):
    """Desenha o widget do campo com as classes do Bootstrap e o vínculo com a mensagem de erro."""
    widget = campo.field.widget
    if isinstance(widget, forms.CheckboxInput):
        classe = "form-check-input"
    elif isinstance(widget, forms.Select):
        classe = "form-select"
    else:
        classe = "form-control"
    attrs = {"class": f"{classe} is-invalid" if campo.errors else classe}
    if campo.errors:
        attrs["aria-describedby"] = f"{campo.id_for_label}-erro"
    return campo.as_widget(attrs=attrs)
