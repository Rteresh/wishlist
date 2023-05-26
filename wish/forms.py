from django import forms

from wish.models import Wish
from users.models import User


class WishForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={
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
            'title',
            'description',
        )

    def message_and_record(self, user):
        """Вывод сообщения и сохранения в базе данных"""

        if user.count_wish <= 0:
            message = 'Вы больше не можете добавлять желания'
            return False, message

        message = 'Желание успешно добавлено в список '
        Wish.objects.create(
            title=self.cleaned_data['title'],
            description=self.cleaned_data['description'],
            user=user,
        )
        user.decrease_wish_quantity()
        return True, message
