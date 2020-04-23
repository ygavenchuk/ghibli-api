import logging
from typing import List, Dict, Union
from urllib.parse import urljoin, urlparse

from requests import Session, RequestException


__all__ = ["GhibliApi"]


# Detail documentation of the API is here: http://ghibliapi.herokuapp.com

# todo: add a checksum for each entry as a way to detect updated records
# note: checksum should include variable number of properties (some subset of
#       properties)
class GhibliApi(object):
    """
    A simple implementation of GhibliAPI with a couple required methods
    """
    BASE_URL = "https://ghibliapi.herokuapp.com"

    def __init__(self, logger=None):
        """

        :param logger: a logger instance or None to use default python's logger
        """
        self._logger = logger or logging.getLogger("gstudio.fetch.GhibliApi")
        self._session = Session()
        self._session.headers.update({"Content-Type": "application/json"})
        self._films = None
        self._people = None
        self.refresh()

    def __del__(self):
        self._session.close()

    def refresh(self) -> None:
        """
        Updates cached properties by new data via API
        """
        self._films = None
        self._people = None

        self._get_people()
        self._get_films()

    @staticmethod
    def _merge(films: List[Dict], people: List[Dict]) -> None:
        """
        Merges "people" into correspond films "in-place"

        :param films: sequence of films
        :param people: sequence of people
        """
        d_films = {}
        for film in films:
            d_films[film["id"]] = film
            film["people"] = []

        for person in people:
            p_films = person.get("films")
            if not p_films:
                continue

            film_ids = []

            for f_url in p_films:
                film_id = urlparse(f_url).path.rsplit("/", 1)[-1]
                film_ids.append(film_id)
                if film_id in d_films:
                    d_films[film_id]["people"].append(person)

            person["films"] = film_ids

    def _get_people(self) -> Union[List[Dict], None]:
        """
        Retrieves sequence of people

        :return: sequence of people or None in case of any error
        """
        if self._people is not None:
            return self._people

        try:
            resp = self._session.get(urljoin(self.BASE_URL, "people"))

        except RequestException as err:
            self._logger.error(err)
            return None

        try:
            self._people = resp.json()
        except ValueError as err:
            self._logger.error(str(err))
            return None

        return self._people

    def _get_films(self) -> Union[List[Dict], None]:
        """
        Retrieves sequence of films

        :return: sequence of films or None in case of any error
        """
        if self._films is not None:
            return self._films

        try:
            resp = self._session.get(urljoin(self.BASE_URL, "films"))
        except RequestException as err:
            self._logger.error(str(err))
            return None

        try:
            result = resp.json()
        except ValueError as err:
            self._logger.error(str(err))
            return None

        # because the "people" field in films endpoint seems to be broken
        # we have to fix it manually
        people = self.people
        if people:
            self._merge(result, self.people)
        else:
            self._logger.warning("Can't merge people into films")

        self._films = result

        return self._films

    @property
    def films(self) -> Union[List[Dict], None]:
        """
        Retrieves sequence of films

        :return: sequence of films or None in case of any error
        """
        return self._films

    @property
    def people(self) -> Union[List[Dict], None]:
        """
        Retrieves sequence of people

        :return: sequence of people or None in case of any error
        """
        return self._people
