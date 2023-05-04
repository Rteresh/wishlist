from django.db import models

from users.models import User


# Create your models here.
class Wish(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishes')

    class Meta:
        verbose_name = 'Желания'
        verbose_name_plural = 'Желания'

    def __str__(self):
        return f'{self.title}'


class ActiveWish(models.Model):
    wish = models.ForeignKey(to=Wish, on_delete=models.CASCADE, related_name='active_wishes')
    executor = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='assigned_wishes')
    owner = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name='created_wishes')
    created_at = models.DateTimeField(auto_now=True)
    expiration = models.DateTimeField()
    is_executed = models.BooleanField(default=False)

    def __str__(self):
        return f':Желание:{self.wish},пользователя:{self.is_executed},' \
               f' которое пользователь:{self.executor} должен выполнить'

    class Meta:
        verbose_name = 'Активные желания'
        verbose_name_plural = 'Активное желание'


class HistoryExecutionWishes(models.Model):
    user_to_execute_wish = models.ForeignKey(to=User, on_delete=models.CASCADE)
    wish = models.ForeignKey(to=Wish, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.wish.title}'

    class Meta:
        verbose_name = 'Выполненные желания'
        verbose_name_plural = 'Выполненное желание'
