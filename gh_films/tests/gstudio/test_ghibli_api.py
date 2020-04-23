from typing import Callable, Dict
from unittest import TestCase
from unittest.mock import MagicMock, patch
from urllib.parse import urlparse

from ddt import ddt, data, unpack

from gh_films.pkg.gstudio.ghibli_api import GhibliApi


__all__ = ["TestGhibliApi", ]


_fx_endpoints = ("films", "people", )


_fx_valid_people = (
    [
        {"id": 123, "films": [], "lorem": "ipsum", "dolor": "sit",
         "amet": "est"}
    ],
    [
        {"id": 123, "lorem": "ipsum", "dolor": "sit",
         "amet": "est"}
    ],
)


_fx_valid_films = (
    [
        {"id": 123, "people": [], "lorem": "ipsum", "dolor": "sit",
         "amet": "est"}
    ],
    [
        {"id": 123, "lorem": "ipsum", "dolor": "sit",
         "amet": "est"}
    ],
)


_fx_valid_films_full = (
    (
        # emulated response that depends on APIs endpoint
        {
            "people":
                [
                    {"id": 123, "films": ["foo/bar/baz/film-uuid-no-1"],
                     "lorem": "ipsum", "dolor": "sit", "amet": "est"},
                    {"id": "people-uuid-no-2",  "films": [], "lorem": "ipsum3",
                     "dolor": "sit1", "amet": "est2"},
                    {"id": "123-456", "films": ["foo/bar/baz/film-uuid-no-2"],
                     "lorem": "ipsum5", "dolor": "sit5", "amet": "est-"},
                    {"id": "xxx-zzz", "films": ["foo/bar/baz/film-uuid-no-2"],
                     "lorem": "ipsum5", "dolor": "sit5", "amet": "est-"},
                ],
            "films":
                [
                    {"id": 123, "people": [], "lorem": "ipsum", "dolor": "sit",
                     "amet": "est"},
                    {"id": "film-uuid-no-1", "people": ["aaa", "bbb", "ccc"],
                     "lorem": "ipsum", "dolor": "sit", "amet": "est"},
                    {"id": "film-uuid-no-2", "people": ["ttt"],
                     "lorem": "ipsum", "dolor": "sit", "amet": "est"},
                ],
        },

        # expected result of merging people inside "films"
        [
            {"id": 123, "people": [], "lorem": "ipsum", "dolor": "sit",
             "amet": "est"},
            {"id": "film-uuid-no-1", "people": [
                {"id": 123, "films": ["film-uuid-no-1"],
                 "lorem": "ipsum", "dolor": "sit", "amet": "est"},
            ],
             "lorem": "ipsum", "dolor": "sit", "amet": "est"},
            {"id": "film-uuid-no-2", "people": [
                {"id": "123-456", "films": ["film-uuid-no-2"],
                 "lorem": "ipsum5", "dolor": "sit5", "amet": "est-"},
                {"id": "xxx-zzz", "films": ["film-uuid-no-2"],
                 "lorem": "ipsum5", "dolor": "sit5", "amet": "est-"},
            ],
             "lorem": "ipsum", "dolor": "sit", "amet": "est"},

        ],
    ),
)


def _get_endpoint(url: str) -> str:
    """
    Extracts API endpoint from url

    :param url:

    :return:
    """
    return urlparse(url).path.rsplit("/", 1)[-1]


def _rq_fake_json_response(return_values: Dict[str, list]) -> Callable:
    """
    Emulates API's responses that depends on endpoint

    :param return_values: {"endpoint": emulated_result, ...}

    :return:
    """
    def _fake_get(url: str) -> MagicMock:
        """

        :param url: ignored

        :return: MagicMoc instance which json method return
                 required/expected data that depends on given URL
        """
        return MagicMock(json=lambda: return_values.get(_get_endpoint(url)))

    return _fake_get


@ddt
class TestGhibliApi(TestCase):
    def setUp(self) -> None:
        self._rq = MagicMock()

        path = "gh_films.pkg.gstudio.ghibli_api"
        self._patchers = [
            patch(path + ".Session", MagicMock(return_value=self._rq)),
        ]

        for item in self._patchers:
            item.start()

    def tearDown(self) -> None:
        for item in self._patchers:
            item.stop()

    def test_json_header_should_be_added_to_all_requests(self):
        api = GhibliApi()
        self.assertTrue(api._session.headers['Content-Type'].endswith("json"))

    def test_base_url_should_be_used(self):
        api = GhibliApi()
        get_url = api._session.get.call_args[0][0]
        self.assertTrue(get_url.startswith(api.BASE_URL))

    @data(*_fx_endpoints)
    def test_endpoint_should_be_requested(self, endpoint):
        args_list = GhibliApi()._session.get.call_args_list
        rq_endpoints_set = {_get_endpoint(x[0][0]) for x in args_list}

        self.assertIn(endpoint, rq_endpoints_set)

    @data(*_fx_valid_people)
    def test_people_prop_should_return_people_received_from_api(self, resp):
        self._rq.get.return_value = MagicMock(**{"json.return_value": resp})
        self.assertSequenceEqual(resp, GhibliApi().people)

    @data(*_fx_valid_films)
    def test_films_prop_should_return_films_received_from_api(self, resp):
        self._rq.get.return_value = MagicMock(**{"json.return_value": resp})
        self.assertSequenceEqual(resp, GhibliApi().films)

    @unpack
    @data(*_fx_valid_films_full)
    def test_people_field_in_films_list_should_be_updated(self, response, exp):
        self._rq.get.side_effect = _rq_fake_json_response(response)
        self.assertSequenceEqual(GhibliApi().films, exp)
