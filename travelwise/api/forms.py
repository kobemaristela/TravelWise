from django import forms

class CreatePlanForm(forms.Form):
    name = forms.CharField(label="Name", max_length=100)
    note = forms.CharField(label="Note", max_length=256)