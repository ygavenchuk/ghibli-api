from enum import Enum, unique

from django.db.models import Model, ManyToManyField
from django.db.models.fields import UUIDField, CharField, TextField, \
    PositiveSmallIntegerField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.timezone import now as tz_now


__all__ = ["Films", "People", "Gender", ]


@unique
class Gender(Enum):
    MALE = "Male"
    FEMALE = "Female"
    UNKNOWN = "Unknown"

    def __str__(self):
        return str(self.value)


class People(Model):
    id = UUIDField(primary_key=True)
    name = CharField(max_length=128)
    gender = CharField(max_length=7, choices=[
        (g.name, g.value) for g in Gender])
    age = CharField(max_length=64, blank=True)
    eye_color = CharField(max_length=64)
    hair_color = CharField(max_length=64)


class Films(Model):
    id = UUIDField(primary_key=True)
    title = CharField(max_length=255)
    description = TextField()
    director = CharField(max_length=128)
    producer = CharField(max_length=128)
    release_date = PositiveSmallIntegerField(validators=[
        # The Ghibli studio was founded in 1985, thus it can't release any
        # films before that date
        MinValueValidator(1985),

        # assume that "release date" is about real films and not for plans
        MaxValueValidator(tz_now().year + 1)])
    rt_score = PositiveSmallIntegerField()
    people = ManyToManyField(People, default=None)

    class Meta:
        ordering = ["pk"]
