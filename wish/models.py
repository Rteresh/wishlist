from django.db import models
from django.utils.timezone import now

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
    created = models.DateTimeField(auto_now=True)
    expiration = models.DateTimeField()
    is_executed = models.BooleanField(default=False)

    def __str__(self):
        return f':Желание:{self.wish},пользователя:{self.is_executed},' \
               f' которое пользователь:{self.executor} должен выполнить'

    class Meta:
        verbose_name = 'Активные желания'
        verbose_name_plural = 'Активное желание'

    def log_executed_wish_history(self):
        """
        Метод для логирования выполненных желаний пользователя.
        """
        wish_history = {
            'wish': self.wish.__str__(),
            'wish_description': self.wish.description,
            'owner': self.owner.__str__(),
            'created': self.created.strftime("%Y-%m-%d %H:%M:%S"),
            'is_executed': self.is_executed,
            'execution_date': now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.executor.wish_executed.append(wish_history)
        self.executor.save()

    def log_wish_history(self):
        """
            Метод для логирования выполненных желаний пользователя.
        """

        wish_history = {
            'wish': self.wish.__str__(),
            'wish_description': self.wish.description,
            'created': self.created.strftime("%Y-%m-%d %H:%M:%S"),
            'executor': self.executor.__str__(),
            'is_executed': self.is_executed,
            'execution_date': now().strftime("%Y-%m-%d %H:%M:%S")

        }

        self.owner.wish_history.append(wish_history)
        self.owner.save()
