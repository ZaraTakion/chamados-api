from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenBlacklistView, TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from accounts.views import RegisterView, me
from tickets.views import TicketAuditHistoryView, TicketViewSet, TicketCommentListCreateView
from chamados_api.health import health, liveness, readiness

router = DefaultRouter()
router.register("tickets", TicketViewSet, basename="ticket")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health, name="health"),
    path("api/health/live/", liveness, name="health-live"),
    path("api/health/ready/", readiness, name="health-ready"),
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
    path("api/auth/me/", me, name="me"),
    path("api/tickets/<int:ticket_pk>/comments/", TicketCommentListCreateView.as_view(), name="ticket-comments"),
    path("api/tickets/<int:ticket_pk>/history/", TicketAuditHistoryView.as_view(), name="ticket-history"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/", include(router.urls)),
]
