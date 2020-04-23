from django.views.generic.base import TemplateView

from gh_films.pkg.gstudio.models import Films


__all__ = ["FilmsView", ]


class FilmsView(TemplateView):
    template_name = "films.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["films"] = Films.objects.prefetch_related().all()
        return context
