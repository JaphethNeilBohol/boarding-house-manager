from django.db import models

# Create your models here.
class Boarder(models.Model):
    name = models.CharField(max_length=100)
    room_number = models.CharField(max_length=10)
    contact = models.CharField(max_length=20, blank=True)
    move_in_date = models.DateField()

    def __str__(self):
        return f"{self.name} - Room {self.room_number}"