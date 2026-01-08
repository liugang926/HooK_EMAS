"""
自定义分页器 - 精臣云资产管理系统
"""
from rest_framework.pagination import PageNumberPagination


class FlexiblePageNumberPagination(PageNumberPagination):
    """
    灵活的分页器，支持自定义 page_size
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 10000
