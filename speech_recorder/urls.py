from django.urls import path
from .views import SpeakersViewset

app_name = "speakers"
urlpatterns = [path("", SpeakersViewset.as_view({"get": "list"}))]
