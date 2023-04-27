from django import forms

from wish.models import Wish


class WishForm(forms.ModelForm):
    tittle = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control py-4',
        'placeholder': 'Название желания'
    }))

    description = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control py-4',
        'placeholder': 'Описание желания'
    }))

    class Meta:
        model = Wish
        fields = (
            'tittle',
            'description',
        )
