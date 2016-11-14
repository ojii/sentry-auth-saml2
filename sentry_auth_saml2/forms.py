from django import forms


class ConfigureForm(forms.Form):
    metadata_url = forms.URLField()
    provider = forms.CharField(widget=forms.HiddenInput())
