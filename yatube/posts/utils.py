from django.conf import settings
from django.core.paginator import Paginator


def get_page_obj(posts, request):
    paginator = Paginator(posts, settings.NUMBER_OF_PAGES)
    return paginator.get_page(request.GET.get('page'))
