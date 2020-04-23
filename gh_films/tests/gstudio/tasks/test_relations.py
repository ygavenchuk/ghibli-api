from unittest.mock import MagicMock

from django.test import TestCase
from ddt import ddt, data, unpack

from gh_films.pkg.gstudio.models import Films, People, Gender
from gh_films.pkg.gstudio.tasks import update_relations


__all__ = ["TestRelations"]


_fx_films = (
    {
        "id": "78d74675-c365-441e-9fb1-fe2f9188bde4", "title": "foo",
        "description": "some long text here", "director": "first last",
        "producer": "some name here", "release_date": "1999", "rt_score": 33,
    },
    {
        "id": "9411138d-306b-48fe-8cc6-54316d82f6a7", "title": "bar",
        "description": "another long text here", "director": "first1 lt3",
        "producer": "another name here", "release_date": "1989",
        "rt_score": "25",
    },
)

_fx_people = (
    {"id": "78d74675-c365-441e-9fb1-fe1f9188bde4", "name": "foo",
     "gender": Gender.FEMALE, "age": "young", "eye_color": "gray",
     "hair_color": "blue", },
    {"id": "9411138d-306b-48fe-8cc6-54b16d82f6a7", "name": "Ghost",
     "gender": Gender.UNKNOWN, "age": "999", "eye_color": "",
     "hair_color": "gray", },
    {"id": "43793794-57ff-483b-b3dd-40b9c4828b59", "name": "Some name",
     "gender": Gender.MALE, "age": 12, "eye_color": "green",
     "hair_color": "red", }
)

_fx_relations = (
    (
        # minimal required people data from api
        [
            {"id": "78d74675-c365-441e-9fb1-fe1f9188bde4", "films": [
                "78d74675-c365-441e-9fb1-fe2f9188bde4",
                "9411138d-306b-48fe-8cc6-54316d82f6a7",
            ]},
            {"id": "9411138d-306b-48fe-8cc6-54b16d82f6a7", "films": []},
            {"id": "43793794-57ff-483b-b3dd-40b9c4828b59", "films": [
                "9411138d-306b-48fe-8cc6-54316d82f6a7",
            ]},
        ],

        # minimal required films data (record's ids) from DB
        {"78d74675-c365-441e-9fb1-fe2f9188bde4": [],
         "9411138d-306b-48fe-8cc6-54316d82f6a7": []},

        # minimal required poeple data (record's ids) from DB
        {"78d74675-c365-441e-9fb1-fe1f9188bde4": None, },

        # expected film_id:people_id pairs
        {
            ("78d74675-c365-441e-9fb1-fe2f9188bde4",
             "78d74675-c365-441e-9fb1-fe1f9188bde4"),
            ("9411138d-306b-48fe-8cc6-54316d82f6a7",
             "78d74675-c365-441e-9fb1-fe1f9188bde4"),
            ("9411138d-306b-48fe-8cc6-54316d82f6a7",
             "43793794-57ff-483b-b3dd-40b9c4828b59", )
        },
    ),
)


@ddt
class TestRelations(TestCase):
    def setUp(self) -> None:
        Films.objects.bulk_create([Films(**f) for f in _fx_films])
        People.objects.bulk_create([People(**p) for p in _fx_people])

    def tearDown(self) -> None:
        Films.objects.filter().delete()
        People.objects.filter().delete()
        Films.people.through.objects.filter().delete()

    @unpack
    @data(*_fx_relations)
    def test_new_relations_should_be_saved(self, d_api, films, peoples, exp):
        api = MagicMock(people=d_api)
        update_relations(api, films, peoples)

        relations_qs = Films.people.through.objects.all()
        result = {(str(r.films_id), str(r.people_id)) for r in relations_qs}
        self.assertSequenceEqual(exp, result)
