from unittest.mock import MagicMock

from django.test import TestCase
from ddt import ddt, data, unpack

from gh_films.pkg.gstudio.models import Films
from gh_films.pkg.gstudio.tasks import update_films


__all__ = ["TestUpdateFilms"]


_fx_valid_films = (
    (
        [
            {"id": "78d74675-c365-441e-9fb1-fe2f9188bde4", "title": "foo",
             "description": "some long text here", "director": "first last",
             "producer": "some name here", "release_date": "1999",
             "rt_score": 33, "people": ["lorem", "ipsum"],  "dolor": "sit"},
            {"id": "9411138d-306b-48fe-8cc6-54316d82f6a7", "title": "bar",
             "description": "another long text here", "director": "first1 lt3",
             "producer": "another name here", "release_date": "1989",
             "rt_score": "25", "people": []},
            {"id": "43793794-57ff-483b-b3dd-4049c4828b59", "title": "baz",
             "description": "a short txt", "director": "who are you",
             "producer": "a famous person", "release_date": "2000",
             "rt_score": 33, "people": ["1234", "fff-ipsum"]},
            {"id": "410927be-21d3-4643-83ca-fe5107c85bff", "title": "tttt",
             "description": "a long long time ago in the galaxy...",
             "director": "cool", "producer": "Richy Rich",
             "release_date": "1999", "rt_score": 22},
        ],
        ["78d74675-c365-441e-9fb1-fe2f9188bde4",
         "9411138d-306b-48fe-8cc6-54316d82f6a7",
         "43793794-57ff-483b-b3dd-4049c4828b59",
         "410927be-21d3-4643-83ca-fe5107c85bff", ],
    ),

    # invalid records should be skipped
    (
        [
            {"id": "78d74675-c365-441e-9fb1-fe1f9188bde0", "title": "foo",
             "description": "some long text here", "director": "first last",
             "producer": "some name here", "release_date": "1999",
             "rt_score": 33, "people": ["lorem", "ipsum"], "dolor": "sit"},

            # the `release_date` is missed
            {"id": "9411138d-306b-48fe-8cc6-04b16d82f6a7", "title": "bar",
             "description": "another long text here", "director": "first1 lt3",
             "producer": "another name here",  "rt_score": "25", "people": []},
        ],
        ["78d74675-c365-441e-9fb1-fe1f9188bde0", ],
    ),

)


_fx_valid_films_for_update = (
    (
        [
            {"id": "78d74675-c365-441e-9fb1-fe1f9188bde4", "title": "foo",
             "description": "some long text here", "director": "first last",
             "producer": "some name here", "release_date": "1999",
             "rt_score": 33, "people": ["lorem", "ipsum"],  "dolor": "sit"},
            {"id": "9411138d-306b-48fe-8cc6-54b16d82f6a7", "title": "bar",
             "description": "another long text here", "director": "first1 lt3",
             "producer": "another name here", "release_date": "1989",
             "rt_score": "25", "people": []},
            {"id": "43793794-57ff-483b-b3dd-40b9c4828b59", "title": "baz",
             "description": "a short txt", "director": "who are you",
             "producer": "a famous person", "release_date": "2000",
             "rt_score": 33, "people": ["1234", "fff-ipsum"]},
            {"id": "410927be-21d3-4643-83ca-fe1107c85bff", "title": "tttt",
             "description": "a long long time ago in the galaxy...",
             "director": "cool", "producer": "Richy Rich",
             "release_date": "1999", "rt_score": 22,
             "people": ["lo-aa-bbrem", "ip-cc-dd-sum"]},
        ],
        {"id": "9411138d-306b-48fe-8cc6-54b16d82f6a7", "title": "bbbbb",
         "description": "another long text here", "director": "first1 lt3",
         "producer": "another name here", "release_date": "1989",
         "rt_score": "25"},
        ["78d74675-c365-441e-9fb1-fe1f9188bde4",
         "43793794-57ff-483b-b3dd-40b9c4828b59",
         "410927be-21d3-4643-83ca-fe1107c85bff", ],
    ),
)


@ddt
class TestUpdateFilms(TestCase):
    def setUp(self) -> None:
        Films.objects.filter().delete()

    def tearDown(self) -> None:
        Films.objects.filter().delete()

    @unpack
    @data(*_fx_valid_films)
    def test_valid_items_should_be_saved(self, api_data, expected_ids):
        api = MagicMock(films=api_data)
        update_films(api)

        saved_films_qs = Films.objects.filter(pk__in=expected_ids)
        self.assertEqual(len(expected_ids), saved_films_qs.count())
        self.assertEqual(len(expected_ids), Films.objects.count())

    @unpack
    @data(*_fx_valid_films_for_update)
    def test_saved_items_should_be_unchanged(self, api_data, stored, expected):
        api = MagicMock(films=api_data)
        Films.objects.create(**stored)
        update_films(api)

        saved_films_qs = Films.objects.filter(pk__in=expected)
        self.assertEqual(len(expected), saved_films_qs.count())
        new_film = Films.objects.get(pk=stored["id"])
        self.assertEqual(new_film.title, stored["title"])
