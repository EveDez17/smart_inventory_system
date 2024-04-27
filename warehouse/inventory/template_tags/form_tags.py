from django import template
register = template.Library()

@register.filter(name='add_class')
def add_class(value, arg):
    attrs = value.field.widget.attrs
    css_classes = attrs.get('class', '')
    if css_classes:
        css_classes = f"{css_classes} {arg}"
    else:
        css_classes = arg
    attrs['class'] = css_classes
    rendered_field = str(value)
    return rendered_field