from django import forms


from django import forms


class CVUploadForm(forms.Form):

    file = forms.FileField(required=False)

    text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "placeholder": "Paste CV text here..."
        })
    )

    job_description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "placeholder": "Paste job description here..."
        })
    )