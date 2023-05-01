from django.db import models

from users.models import User


# Create your models here.
class Wish(models.Model):
    tittle = models.CharField(max_length=256)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Желания'
        verbose_name_plural = 'Желания'

    def __str__(self):
        return f'{self.tittle}'


class ActiveWish(models.Model):
    name_wish = models.ForeignKey(to=Wish, on_delete=models.CASCADE, related_name='name_wish')
    user_to_execute_wish = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='user_to_execute_wish')
    user_whose_wish_to_execute = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name='user_whose_wish_to_execute')
    created_at = models.DateTimeField(auto_now=True)
    expiration = models.DateTimeField()
    wish_execution_state = models.BooleanField(default=False)

    def __str__(self):
        return f':Желание:{self.name_wish},пользователя:{self.wish_execution_state},' \
               f' которое пользователь:{self.user_to_execute_wish} должен выполнить'

    class Meta:
        verbose_name = 'Активные желания'
        verbose_name_plural = 'Активное желание'


class HistoryExecutionWishes(models.Model):
    user_to_execute_wish = models.ForeignKey(to=User, on_delete=models.CASCADE)
    wish = models.ForeignKey(to=ActiveWish, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.wish.name_wish.tittle}'

    class Meta:
        verbose_name = 'Выполненные желания'
        verbose_name_plural = 'Выполненное желание'
