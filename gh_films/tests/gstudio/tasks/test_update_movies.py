from unittest.mock import MagicMock, patch, ANY

from django.test import TestCase

from gh_films.pkg.gstudio.tasks import update_movies


__all__ = ["TestUpdateMovies", ]


class TestUpdateMovies(TestCase):
    def setUp(self) -> None:
        path = "gh_films.pkg.gstudio.tasks"

        self._api = MagicMock()
        self._api_cls = MagicMock(return_value=self._api)
        self._mk_update_people = MagicMock()
        self._mk_update_films = MagicMock()
        self._mk_update_relations = MagicMock()
        self._logger = MagicMock()

        self._patchers = [
            patch(path + ".GhibliApi", self._api_cls),
            patch(path + ".update_people", self._mk_update_people),
            patch(path + ".update_films", self._mk_update_films),
            patch(path + ".update_relations", self._mk_update_relations),
            patch(path + "._logger", self._logger),
        ]

        for item in self._patchers:
            item.start()
        update_movies()

    def tearDown(self) -> None:
        for item in self._patchers:
            item.stop()

    def test_ghibli_api_instance_should_be_created(self):
        self._api_cls.assert_called_once()

    def test_custom_logger_should_be_passed_into_api_instance(self):
        self._api_cls.assert_called_once_with(self._logger)

    def test_update_people_should_be_invoked(self):
        self._mk_update_people.assert_called_once_with(self._api)

    def test_update_films_should_be_invoked(self):
        self._mk_update_films.assert_called_once_with(self._api)

    def test_update_relations_should_be_invoked(self):
        self._mk_update_relations.assert_called_once_with(self._api, ANY, ANY)
