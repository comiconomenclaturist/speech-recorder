from django.urls import path
from .views import CreateBookingView, SpeakersViewset

app_name = "speakers"
urlpatterns = [
    # path("", SpeakersViewset.as_view({"get": "list"})),
    path("add/", CreateBookingView.as_view()),
]
