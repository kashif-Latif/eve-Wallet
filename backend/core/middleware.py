import json
import logging

from django.utils import timezone

logger = logging.getLogger(__name__)


class AuditLogMiddleware:
    """
    Middleware that logs all API requests for audit purposes.
    Records user, action, IP address, and request details.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.request = request
        response = self.get_response(request)
        self._log_request(request, response)
        return response

    def _log_request(self, request, response):
        """
        Log the request details to the AuditLog model.
        """
        try:
            from apps.accounts.models import AuditLog

            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None

            # Skip logging for static files and admin media
            path = request.path
            if path.startswith('/static/') or path.startswith('/admin/') or path.startswith('/media/'):
                return

            # Determine the action based on HTTP method
            method_map = {
                'GET': 'READ',
                'POST': 'CREATE',
                'PUT': 'UPDATE',
                'PATCH': 'UPDATE',
                'DELETE': 'DELETE',
            }
            action = method_map.get(request.method, 'UNKNOWN')

            # Get IP address
            ip_address = self._get_client_ip(request)

            # Build changes dict
            changes = {}
            if request.method in ('POST', 'PUT', 'PATCH'):
                try:
                    if hasattr(request, 'data') and isinstance(request.data, dict):
                        changes = {
                            'request_body': {
                                k: v for k, v in request.data.items()
                                if k not in ('password', 'confirm_password', 'token', 'refresh')
                            }
                        }
                    elif request.body:
                        body = json.loads(request.body)
                        if isinstance(body, dict):
                            changes = {
                                'request_body': {
                                    k: v for k, v in body.items()
                                    if k not in ('password', 'confirm_password', 'token', 'refresh')
                                }
                            }
                except (json.JSONDecodeError, AttributeError):
                    changes = {}

            # Extract model name from URL path
            path_parts = path.strip('/').split('/')
            model_name = ''
            for part in path_parts:
                if part not in ('api', 'v1', 'auth', 'admin', '') and not part.isdigit():
                    model_name = part
                    break

            # Determine object_id from URL
            object_id = None
            for part in reversed(path_parts):
                if part.isdigit():
                    object_id = part
                    break

            # Only log API requests
            if path.startswith('/api/'):
                AuditLog.objects.create(
                    user=user,
                    action=action,
                    model_name=model_name,
                    object_id=object_id or '',
                    changes=changes,
                    ip_address=ip_address,
                )
        except Exception as e:
            logger.error(f"AuditLog middleware error: {str(e)}")

    @staticmethod
    def _get_client_ip(request):
        """
        Get the client's IP address from the request.
        Checks X-Forwarded-For header first (for reverse proxy setups).
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip


class ResponseFormattingMiddleware:
    """
    Middleware that ensures all API responses follow a consistent format:
    {success: bool, message: str, data: any}
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only format API responses
        if request.path.startswith('/api/') and response.status_code < 500:
            try:
                if hasattr(response, 'data'):
                    data = response.data
                    # Skip if already formatted
                    if isinstance(data, dict) and 'success' in data:
                        return response

                    if response.status_code >= 400:
                        # Error response
                        if isinstance(data, dict):
                            message = data.pop('detail', data.pop('message', 'An error occurred'))
                            # Handle DRF validation errors
                            if 'detail' not in data and any(k for k in data.keys() if k not in ('success', 'message', 'data')):
                                errors = {k: v for k, v in data.items() if k not in ('success', 'message', 'data')}
                                response.data = {
                                    'success': False,
                                    'message': message if isinstance(message, str) else 'Validation error',
                                    'data': {'errors': errors} if errors else None,
                                }
                            else:
                                response.data = {
                                    'success': False,
                                    'message': str(message),
                                    'data': None,
                                }
                        else:
                            response.data = {
                                'success': False,
                                'message': 'An error occurred',
                                'data': None,
                            }
                    else:
                        # Success response
                        if isinstance(data, dict) and 'success' not in data:
                            response.data = {
                                'success': True,
                                'message': 'Operation successful',
                                'data': data,
                            }
            except Exception:
                pass

        return response
