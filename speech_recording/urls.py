"""speech_recording URL Configuration"""

from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
from recordings.views import CreateBookingView, SpeakersViewSet, ScriptsViewSet

admin.site.site_header = "Speech Recorder admin"
admin.site.site_title = "Speech Recorder admin"
admin.site.index_title = "Welcome to the Speech Recorder admin"


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/bookings/add/", CreateBookingView.as_view()),
]

router = DefaultRouter()
router.register(r"api/speakers", SpeakersViewSet, basename="speakers")
router.register(r"api/scripts", ScriptsViewSet, basename="scripts")
urlpatterns += router.urls
