from typing import Union, Dict, Type, List

from django.core.exceptions import ValidationError
from django.db import transaction, Error
from django.db.models.expressions import BaseExpression
from celery import shared_task
from celery.utils.log import get_task_logger

from gh_films.pkg.gstudio.ghibli_api import GhibliApi
from gh_films.pkg.gstudio.models import People, Films


__all__ = ["update_movies", ]


_logger = get_task_logger(__name__)


def _populate_fields(model: Union[Type[Films], Type[People]],
                     api_data: Dict[str, str]) -> Union[Films, People, None]:
    """
    Returns new model's instance which fields are populated by data from api

    :param model:
    :param api_data:

    :return:
    """
    instance_data = {}
    for field in model._meta.get_fields():
        if not field.is_relation:
            instance_data[field.name] = api_data.get(field.name)

    try:
        return model(**instance_data)
    except ValidationError as err:
        _logger.warning(f'Can\'t store {str(model._meta.verbose_name)} '
                        f'#{api_data["id"]} due to error: "{str(err)}')


def update(model: Union[Type[Films], Type[People]],
           api_data: List[Dict[str, str]]) -> None:
    """
    Inserts new records into given model

    :param model: model class to update records
    :param api_data:

    :return:
    """
    model_name = model._meta.verbose_name
    if not api_data:
        _logger.info(f"No {model_name} received.")
        return

    batch = []
    for api_record in api_data:
        db_instance = _populate_fields(model, api_record)
        if db_instance:
            batch.append(db_instance)

    try:
        model.objects.bulk_create(batch, ignore_conflicts=True)
    except (BaseExpression, Error, ) as err:
        _logger.warning(f"Can't update {model_name} records due to "
                        f"\"{str(err)}\"")


def update_relations(api: GhibliApi) -> None:
    """
    Actualize many-to-many relations between films and people

    :param api:
    """
    batch = []

    film_ids = set()

    for person in api.people:
        person_id = person["id"]
        for film_id in person["films"]:
            film_ids.add(film_id)
            batch.append(Films.people.through(films_id=film_id,
                                              people_id=person_id))

    try:
        with transaction.atomic():
            Films.people.through.objects.filter(films_id__in=film_ids).delete()
            Films.people.through.objects.bulk_create(batch,
                                                     ignore_conflicts=True)
    except (BaseExpression, Error, ) as err:
        _logger.warning(f"Can't update films-people relations due to "
                        f"\"{str(err)}\"")


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
    update(People, api.people)
    update(Films, api.films)
    update_relations(api)

    return {"people": len(api.people) if api.people else 0,
            "films": len(api.films) if api.films else 0}
