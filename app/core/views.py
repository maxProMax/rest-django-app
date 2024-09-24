# from drf_spectacular.utils import (
#     extend_schema_view,
#     extend_schema,
#     OpenApiParameter,
#     OpenApiTypes,
# )

from rest_framework.decorators import action, api_view
from rest_framework.response import Response


@api_view(["GET"])
def health_check(request):
    return Response({"health": True})
