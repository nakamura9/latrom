from django import forms

class BootstrapMixin(forms.Form):
    """This class intergrates bootstrap into select form fields
    
    The class is a mixin that adds the 'form-control class' to each field in the form as well as making each text input have a placeholder instead of a label. It can be used as a common point for inserting other standard behaviour in the future."""

    def __init__(self, *args, **kwargs):
        super(BootstrapMixin, self).__init__(*args, **kwargs)
        for field in self.fields:
            field = self.fields.get(field)
            field.widget.attrs['class'] ="form-control"

            if isinstance(field.widget, forms.widgets.DateInput):
                field.widget.attrs['class'] += " ui-date-picker"
            

