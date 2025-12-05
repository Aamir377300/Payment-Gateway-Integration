import logging

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """
    Middleware to log all incoming requests with detailed information
    about headers, cookies, and session data.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log request details
        logger.info(f"🌐 Incoming Request: {request.method} {request.path}")
        logger.info(f"   Origin: {request.META.get('HTTP_ORIGIN', 'None')}")
        logger.info(f"   Referer: {request.META.get('HTTP_REFERER', 'None')}")
        logger.info(f"   Host: {request.META.get('HTTP_HOST', 'None')}")
        logger.info(f"   User-Agent: {request.META.get('HTTP_USER_AGENT', 'None')[:80]}")
        logger.info(f"   Content-Type: {request.META.get('CONTENT_TYPE', 'None')}")
        
        # Log cookies
        if request.COOKIES:
            cookie_names = list(request.COOKIES.keys())
            logger.info(f"   Cookies: {cookie_names}")
            if 'sessionid' in request.COOKIES:
                logger.info(f"   Session ID: {request.COOKIES['sessionid'][:20]}...")
            if 'csrftoken' in request.COOKIES:
                logger.info(f"   CSRF Token: {request.COOKIES['csrftoken'][:20]}...")
        else:
            logger.warning(f"   ⚠️  No cookies received!")
        
        # Log session info
        if hasattr(request, 'session'):
            logger.info(f"   Session Key: {request.session.session_key}")
            logger.info(f"   Session Empty: {request.session.is_empty()}")
        
        # Log authentication
        if hasattr(request, 'user'):
            if request.user.is_authenticated:
                logger.info(f"   User: {request.user.username} (authenticated)")
            else:
                logger.info(f"   User: Anonymous")
        
        # Process request
        response = self.get_response(request)
        
        # Log response
        logger.info(f"📤 Response: {request.method} {request.path} -> {response.status_code}")
        
        # Log response cookies being set
        if hasattr(response, 'cookies') and response.cookies:
            cookie_names = list(response.cookies.keys())
            logger.info(f"   Setting Cookies: {cookie_names}")
        
        return response


class CORSDebugMiddleware:
    """
    Middleware to debug CORS issues
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origin = request.META.get('HTTP_ORIGIN')
        
        if origin:
            logger.info(f"🔗 CORS Check for origin: {origin}")
            
            # Check if origin is in allowed origins
            from django.conf import settings
            if hasattr(settings, 'CORS_ALLOWED_ORIGINS'):
                if origin in settings.CORS_ALLOWED_ORIGINS:
                    logger.info(f"   ✅ Origin is in CORS_ALLOWED_ORIGINS")
                else:
                    logger.warning(f"   ⚠️  Origin NOT in CORS_ALLOWED_ORIGINS!")
                    logger.warning(f"   Allowed origins: {settings.CORS_ALLOWED_ORIGINS}")
        
        response = self.get_response(request)
        
        # Log CORS headers in response
        if 'Access-Control-Allow-Origin' in response:
            logger.info(f"   CORS Header Set: {response['Access-Control-Allow-Origin']}")
        else:
            if origin:
                logger.warning(f"   ⚠️  No CORS header in response!")
        
        return response
