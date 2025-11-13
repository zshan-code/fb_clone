from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import os

@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    """
    Simple healthcheck to verify:
    - Django + DRF are running
    - Environment vars are loaded (we do NOT leak secrets)
    """
    return Response({
        "status": "ok",
        "app": "fbclone",
        "env_debug": os.getenv("DEBUG", "False"),
    })
