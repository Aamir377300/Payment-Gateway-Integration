from rest_framework.authentication import SessionAuthentication

# It Skip CSRF check for API requests
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  