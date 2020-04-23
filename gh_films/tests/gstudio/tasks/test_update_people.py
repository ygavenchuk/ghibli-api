from unittest.mock import MagicMock

from django.test import TestCase
from ddt import ddt, data, unpack

from gh_films.pkg.gstudio.models import People
from gh_films.pkg.gstudio.tasks import update_people


__all__ = ["TestUpdatePeople"]


_fx_valid_people = (
    (
        [
            {"id": "78d74675-c365-441e-9fb1-fe1f9188bde4", "name": "foo",
             "gender": "Female", "age": "young", "eye_color": "gray",
             "hair_color": "blue", "films": ["lorem", "ipsum"],
             "dolor": "sit"},
            {"id": "9411138d-306b-48fe-8cc6-54b16d82f6a7", "name": "Ghost",
             "gender": "NA", "age": "999", "eye_color": "",
             "hair_color": "gray", },
            {"id": "43793794-57ff-483b-b3dd-40b9c4828b59", "name": "Some name",
             "gender": "Male", "age": 12, "eye_color": "green",
             "hair_color": "red", },
            {"id": "410927be-21d3-4643-83ca-fe1107c85bff", "gender": "Hidden",
             "age": "33.33", "name": "John Silver", "eye_color": "black",
             "hair_color": "black", },
        ],
        ["78d74675-c365-441e-9fb1-fe1f9188bde4",
         "9411138d-306b-48fe-8cc6-54b16d82f6a7",
         "43793794-57ff-483b-b3dd-40b9c4828b59",
         "410927be-21d3-4643-83ca-fe1107c85bff", ],
    ),
)


_fx_valid_people_for_update = (
    (
        [
            {"id": "78d74675-c365-441e-9fb1-fe1f9188bde4", "name": "foo",
             "gender": "Female", "age": "young", "eye_color": "gray",
             "hair_color": "blue", "films": ["lorem", "ipsum"],
             "dolor": "sit"},
            {"id": "9411138d-306b-48fe-8cc6-54b16d82f6a7", "name": "Ghost",
             "gender": "NA", "age": "999", "eye_color": "",
             "hair_color": "gray", },
            {"id": "43793794-57ff-483b-b3dd-40b9c4828b59", "name": "Some name",
             "gender": "Male", "age": 12, "eye_color": "green",
             "hair_color": "red", },
            {"id": "410927be-21d3-4643-83ca-fe1107c85bff", "gender": "Hidden",
             "age": "33.33", "name": "John Silver", "eye_color": "black",
             "hair_color": "black", },
        ],
        {"id": "9411138d-306b-48fe-8cc6-54b16d82f6a7", "name": "Ghost",
         "gender": "NA", "age": "333", "eye_color": "",
         "hair_color": "gray", },
        ["78d74675-c365-441e-9fb1-fe1f9188bde4",
         "43793794-57ff-483b-b3dd-40b9c4828b59",
         "410927be-21d3-4643-83ca-fe1107c85bff", ],
    ),
)


@ddt
class TestUpdatePeople(TestCase):
    def setUp(self) -> None:
        People.objects.filter().delete()

    def tearDown(self) -> None:
        People.objects.filter().delete()

    @unpack
    @data(*_fx_valid_people)
    def test_valid_items_should_be_saved(self, api_people, expected_ids):
        api = MagicMock(people=api_people)
        update_people(api)

        saved_people_qs = People.objects.filter(pk__in=expected_ids)
        self.assertEqual(len(expected_ids), saved_people_qs.count())

    @unpack
    @data(*_fx_valid_people_for_update)
    def test_saved_items_should_be_unchanged(self, api_dat, stored, expected):
        api = MagicMock(people=api_dat)
        People.objects.create(**stored)
        update_people(api)

        saved_people_qs = People.objects.filter(pk__in=expected)
        self.assertEqual(len(expected), saved_people_qs.count())
        new_person = People.objects.get(pk=stored["id"])
        self.assertEqual(new_person.age, stored["age"])
