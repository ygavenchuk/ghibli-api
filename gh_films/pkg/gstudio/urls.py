from django.urls import path
from .views import FilmsView


urlpatterns = [
    path("", FilmsView.as_view(), name="films"),
]
