from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication scheme that doesn't enforce CSRF for API endpoints.
    This is safe when combined with CORS restrictions.
    """
    def enforce_csrf(self, request):
        return  # Skip CSRF check for API requests
