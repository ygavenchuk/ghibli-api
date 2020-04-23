from unittest.mock import patch

from django.test import TestCase


__all__ = ["TestFilmsView", ]


class TestFilmsView(TestCase):
    def test_films_template_should_be_used(self):
        response = self.client.get("/movies/")
        self.assertTemplateUsed(response, "films.html")

    def test_films_model_should_be_used(self):
        with patch("gh_films.pkg.gstudio.views.Films") as films:
            self.client.get("/movies/")

            films.objects.prefetch_related.assert_called_once()
