from django import forms

class UploadFileForm(forms.Form):
    upload_file = forms.FileField()

class ManualFileForm(forms.Form):
    text_content = forms.CharField(max_length=40000)