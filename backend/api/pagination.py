from rest_framework.pagination import PageNumberPagination


class PageLimitPagination(PageNumberPagination):
    """Пагинация требуемого количества страниц в зависимости от запроса."""
    page_size_query_param = 'limit'
