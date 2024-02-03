"""speech_recording URL Configuration"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from recordings.views import *

admin.site.site_header = "Speech Recorder admin"
admin.site.site_title = "Speech Recorder admin"
admin.site.index_title = "Welcome to the Speech Recorder admin"


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/bookings/add/", CreateProjectView.as_view()),
    path("api/calendly/", CalendlyWebhookView.as_view()),
]

router = SimpleRouter()
router.register("api/projects", ProjectsViewSet, basename="projects")
router.register("api/speakers", SpeakersViewSet, basename="speakers")
router.register("api/scripts", ScriptsViewSet, basename="scripts")
router.register("api/recordings", RecPromptView, basename="recordings")

urlpatterns += router.urls

if settings.DEBUG:
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
