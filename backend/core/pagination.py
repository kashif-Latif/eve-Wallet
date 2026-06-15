from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    """
    Custom pagination class for consistent API responses.
    Returns 20 items per page by default.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'success': True,
            'message': 'Results retrieved successfully',
            'data': {
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'total_pages': self.page.paginator.num_pages,
                'current_page': self.page.number,
                'results': data,
            }
        })

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'success': {'type': 'boolean', 'example': True},
                'message': {'type': 'string', 'example': 'Results retrieved successfully'},
                'data': {
                    'type': 'object',
                    'properties': {
                        'count': {'type': 'integer', 'example': 100},
                        'next': {'type': 'string', 'nullable': True, 'example': 'http://api.example.com/?page=2'},
                        'previous': {'type': 'string', 'nullable': True, 'example': None},
                        'total_pages': {'type': 'integer', 'example': 5},
                        'current_page': {'type': 'integer', 'example': 1},
                        'results': schema,
                    }
                }
            }
        }
