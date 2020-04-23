from typing import Union, Dict

from django.core.exceptions import ValidationError
from django.db.models.expressions import BaseExpression
from celery import shared_task
from celery.utils.log import get_task_logger

from gh_films.pkg.gstudio.ghibli_api import GhibliApi
from gh_films.pkg.gstudio.models import People, Films, Gender


__all__ = ["update_movies", ]


_logger = get_task_logger(__name__)


def update_people(gh_api: GhibliApi) -> Union[None, Dict[str, People]]:
    """
    Stores new information about people into local storage (DB)

    :param gh_api:

    :return: sequence of `People` instances that have been saved into DB
    """
    d_people = {}
    for person in gh_api.people:
        d_people[person["id"]] = person

    if not d_people:
        _logger.info("No people received.")
        return

    people_qs = People.objects.filter(id__in=d_people.keys()).only("id")
    known_people_ids = {str(item.pk) for item in people_qs}

    batch = {}
    for person in d_people.values():
        if person["id"] in known_people_ids:
            continue

        try:
            gender = Gender(person.get("gender"))
        except (TypeError, ValueError):
            gender = Gender.UNKNOWN

        try:
            batch[person["id"]] = People(id=person["id"], name=person["name"],
                                         gender=gender, age=person["age"],
                                         eye_color=person["eye_color"],
                                         hair_color=person["hair_color"])
        except (IndexError, KeyError, ValidationError) as err:
            _logger.warning(f'Can\'t store person #{person["id"]} due to '
                            f'error: "{str(err)}')

    try:
        # the "ignore_conflicts" option doesn't work properly for all engines
        # e.g. OracleDB
        People.objects.bulk_create(batch.values(), ignore_conflicts=True)
    except BaseExpression as err:
        _logger.warning(f"Can't update people records due to \"{str(err)}\"")
        return None

    return batch


def update_films(gh_api: GhibliApi) -> Union[None, Dict[str, Films]]:
    """
    Stores new information about films into local storage (DB)

    :param gh_api:

    :return: sequence of `Films` instances that have been saved into DB
    """
    d_film = {}
    for film in gh_api.films:
        d_film[film["id"]] = film

    film_qs = Films.objects.filter(id__in=d_film.keys()).only("id")
    known_films = {str(film.id) for film in film_qs}

    batch = {}
    for film in d_film.values():
        if film["id"] in known_films:
            continue

        try:
            batch[film["id"]] = Films(id=film["id"], title=film["title"],
                                      description=film["description"],
                                      director=film["director"],
                                      producer=film["producer"],
                                      release_date=int(film["release_date"]),
                                      rt_score=int(film["rt_score"]))
        except (TypeError, IndexError, KeyError, ValidationError) as err:
            _logger.warning(f'Can\'t store film #{film["id"]} because of '
                            f'error: "{str(err)}')

    try:
        # todo: add fallback mode
        # the "ignore_conflicts" option doesn't work properly for all engines
        # e.g. OracleDB
        Films.objects.bulk_create(batch.values(), ignore_conflicts=True)
    except BaseExpression as err:
        _logger.warning(f"Can't update films records due to \"{str(err)}\"")
        return None

    return batch


def update_relations(api: GhibliApi, films: Dict[str, Films],
                     people: Dict[str, People]):
    """
    Actualize many-to-many relations between films and people

    :param api:
    :param films:
    :param people:
    """
    batch = []

    api_film_people_ids = set()
    for person in api.people:
        person_id = person["id"]
        film_ids = person["films"]
        for film_id in film_ids:
            api_film_people_ids.add((film_id, person_id))

    new_film_ids = set(films.keys())
    new_people_ids = set(people.keys())
    for film_id, people_id in api_film_people_ids:
        if film_id in new_film_ids or people_id in new_people_ids:
            batch.append(Films.people.through(films_id=film_id,
                                              people_id=people_id))

    if not batch:
        return

    # fixme
    # there's a special case: the API's data has no new "people" and/or "films"
    # records but relations are changed. This case can be solved in scope of
    # tracking modifications of any data received from API.
    # Note, that properly way to solve this case requires usage temporary
    # tables or "select from values". It means usage of raw sql queries without
    # involving django's ORM

    try:
        Films.people.through.objects.bulk_create(batch, ignore_conflicts=True)
    except BaseExpression as err:
        _logger.warning(f"Can't update films-people relations due to "
                        f"\"{str(err)}\"")
        pass


@shared_task
def update_movies() -> Dict[str, int]:
    """
    Updates local copy list of movies (with people)

    :return: {"people": number_new_people, "films": number_new_films}
    """
    # known issues: current implementation updates (inserts) new entries only.
    # This function can't track changes in already saved records due to
    # limitations of public Ghibli API
    api = GhibliApi(_logger)
    people = update_people(api)
    films = update_films(api)
    update_relations(api, films, people)

    return {"people": len(people), "films": len(films)}
