from django.http import JsonResponse
from .models import APIKey

class APIKeyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip key validation for certain paths (e.g., admin section)
        if request.path.startswith('/admin/'):
            return self.get_response(request)
        if request.path.startswith('/portfolio/'):
            return self.get_response(request)
        if request.path.startswith('/'):
            return self.get_response(request)
        # Check for API key in the request headers
        api_key = request.headers.get('X-API-KEY')

        # If the API key is missing or invalid, return a 403 Forbidden response
        if not api_key or not APIKey.objects.filter(key=api_key, is_active=True).exists():
            return JsonResponse({'status': 'error', 'message': 'Invalid or missing API key'}, status=403)

        # Proceed with the request if the API key is valid
        return self.get_response(request)
