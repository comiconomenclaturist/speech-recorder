"""speech_recording URL Configuration"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import HttpResponseRedirect, resolve_url
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.views.generic.base import RedirectView
from django.urls.base import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from rest_framework.routers import SimpleRouter
from recordings.views import *
from two_factor.urls import urlpatterns as tf_urls
from two_factor.admin import AdminSiteOTPRequiredMixin, AdminSiteOTPRequired

admin.site.site_header = "Speech Recorder admin"
admin.site.site_title = "Speech Recorder admin"
admin.site.index_title = "Welcome to the Speech Recorder admin"


class AdminSiteOTPRequiredMixinRedirSetup(AdminSiteOTPRequired):
    """
    https://github.com/jazzband/django-two-factor-auth/issues/219#issuecomment-494382380
    """

    def login(self, request, extra_context=None):
        redirect_to = request.POST.get(
            REDIRECT_FIELD_NAME, request.GET.get(REDIRECT_FIELD_NAME)
        )
        # For users not yet verified the AdminSiteOTPRequired.has_permission
        # will fail. So use the standard admin has_permission check:
        # (is_active and is_staff) and then check for verification.
        # Go to index if they pass, otherwise make them setup OTP device.
        if request.method == "GET" and super(
            AdminSiteOTPRequiredMixin, self
        ).has_permission(request):
            # Already logged-in and verified by OTP
            if request.user.is_verified():
                # User has permission
                index_path = reverse("admin:index", current_app=self.name)
            else:
                # User has permission but no OTP set:
                index_path = reverse("two_factor:setup", current_app=self.name)
            return HttpResponseRedirect(index_path)

        if not redirect_to or not url_has_allowed_host_and_scheme(
            url=redirect_to, allowed_hosts=[request.get_host()]
        ):
            redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

        return redirect_to_login(redirect_to)


admin.site.__class__ = AdminSiteOTPRequiredMixinRedirSetup

urlpatterns = [
    path("", RedirectView.as_view(url="/admin/", permanent=True)),
    path("admin/", admin.site.urls),
    path("api/bookings/add/", CreateProjectView.as_view()),
    path("api/calendly/", CalendlyWebhookView.as_view()),
    path("", include(tf_urls)),
]

router = SimpleRouter()
router.register("api/projects", ProjectsViewSet, basename="projects")
router.register("api/speakers", SpeakersViewSet, basename="speakers")
router.register("api/scripts", ScriptsViewSet, basename="scripts")
router.register("api/recordings", RecPromptView, basename="recordings")

urlpatterns += router.urls

if settings.DEBUG:
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
