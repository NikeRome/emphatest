"""Импорт модели"""
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    """Класс представляет пользователя."""
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )

    def __str__(self):
        return str(self.username)

class Room(models.Model):
    """Класс представляет комнату."""
    number = models.IntegerField(primary_key=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField()

    def __str__(self):
        return str(self.number)

class Reservation(models.Model):
    """Класс представляет бронирование"""
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def is_room_available(self, check_in, check_out):
        """Проверка на доступность в указанные даты"""
        return not Reservation.objects.filter(
            room=self.room,
            check_in_date__lt=check_out,
            check_out_date__gt=check_in
        ).exists()
