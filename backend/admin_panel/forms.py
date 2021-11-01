from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field
from django import forms

from bookings.models import Transaction
from vehicles.models import VehicleCategory


class VehicleCategoryModelForm(forms.ModelForm):
    helper = FormHelper()
    helper.layout = Layout(
        "title",
        "commission",
        FormActions(
            Submit('save', 'Save'),
        )
    )

    class Meta:
        model = VehicleCategory
        fields = "__all__"


class TransactionModelForm(forms.ModelForm):
    helper = FormHelper()
    helper.layout = Layout(
        Field('driver', template="select_datalist.html"),
        "driver",
        "amount",
        FormActions(
            Submit('save', 'Save'),
        )
    )

    class Meta:
        model = Transaction
        fields = "__all__"

