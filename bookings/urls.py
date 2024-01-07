from django.urls import path
from .views import CreateBookingView


urlpatterns = [path("add/", CreateBookingView.as_view())]
