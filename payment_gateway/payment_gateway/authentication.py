from rest_framework.authentication import SessionAuthentication
import logging

logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication scheme that doesn't enforce CSRF for API endpoints.
    This is safe when combined with CORS restrictions.
    """
    def authenticate(self, request):
        logger.info(f"🔐 Auth attempt: {request.method} {request.path}")
        logger.info(f"   Origin: {request.META.get('HTTP_ORIGIN', 'None')}")
        logger.info(f"   Cookies: {list(request.COOKIES.keys())}")
        logger.info(f"   Session Key: {request.session.session_key}")
        
        result = super().authenticate(request)
        
        if result:
            user, auth = result
            logger.info(f"   ✅ Authenticated as: {user.username}")
        else:
            logger.info(f"   ❌ Not authenticated")
        
        return result
    
    def enforce_csrf(self, request):
        logger.info(f"🔓 CSRF check skipped for: {request.path}")
        return  # Skip CSRF check for API requests
