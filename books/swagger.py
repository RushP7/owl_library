from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from django.urls import path, re_path, include

schema_view = get_schema_view(
   openapi.Info(
      title="Owl Library API",
      default_version='v1',
      description="API for managing the Owl Library",
   ),
   public=True,
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
