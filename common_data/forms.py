from django import forms
import models

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
            
period_choices = ['------','Last Month', 'Last Quarter', 'Last 6 Months', 'Last Year']
PERIOD_CHOICES = [(period_choices.index(i), i) for i in period_choices]


class PeriodReportForm(BootstrapMixin, forms.Form):
    default_periods = forms.ChoiceField(choices=PERIOD_CHOICES)
    start_period = forms.DateField(required=False)
    end_period = forms.DateField(required=False)


class OrganizationForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        fields = "__all__"
        model = models.Organization