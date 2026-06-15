from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class AnonBurstRateThrottle(AnonRateThrottle):
    """
    Throttle class for anonymous users.
    Limits anonymous requests to 100 per hour.
    """
    rate = '100/hour'


class UserBurstRateThrottle(UserRateThrottle):
    """
    Throttle class for authenticated users.
    Limits authenticated requests to 1000 per hour.
    """
    rate = '1000/hour'


class AdminRateThrottle(UserRateThrottle):
    """
    Throttle class for admin users.
    Limits admin requests to 2000 per hour.
    """
    rate = '2000/hour'

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated and request.user.role == 'admin':
            return self.cache_format % {
                'scope': self.scope,
                'ident': request.user.pk
            }
        return None
