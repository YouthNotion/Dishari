from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView

from . import content


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            service_areas=content.SERVICE_AREAS,
            projects=content.PROJECTS,
            trainings=content.TRAININGS,
            years_active=timezone.localdate().year - content.ORGANISATION.established_year,
        )
        return context


@require_GET
@never_cache
def healthz(request: HttpRequest) -> HttpResponse:
    """Liveness probe for load balancers / uptime monitors."""
    return HttpResponse("ok", content_type="text/plain")
