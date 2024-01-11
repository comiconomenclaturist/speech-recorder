"""speech_recording URL Configuration"""

from django.contrib import admin
from django.urls import path
from rest_framework.routers import SimpleRouter
from recordings.views import CreateBookingView, SpeakersViewSet, ScriptsViewSet

admin.site.site_header = "Speech Recorder admin"
admin.site.site_title = "Speech Recorder admin"
admin.site.index_title = "Welcome to the Speech Recorder admin"


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/bookings/add/", CreateBookingView.as_view()),
]

router = SimpleRouter()
router.register("api/speakers", SpeakersViewSet, basename="speakers")
router.register("api/scripts", ScriptsViewSet, basename="scripts")
urlpatterns += router.urls
