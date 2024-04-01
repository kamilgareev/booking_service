from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


class Room(models.Model):
    number = models.CharField(max_length=20, unique=True)
    cost_per_day = models.DecimalField(max_digits=7,
                                       decimal_places=2, validators=[MinValueValidator(Decimal(0))])
    beds = models.PositiveIntegerField()

    def __str__(self):
        return f'Room number {self.number}'


class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f'Booking of room {self.room} by {self.client}'

