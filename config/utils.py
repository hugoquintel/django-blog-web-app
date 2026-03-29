from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model

User = get_user_model()

sign_in_url = reverse_lazy("user:sign-in", kwargs={"partial": None})

tailwind_comment_spaces = {
    "padding_left": {0: "", 1: "pl-6", 2: "pl-15", 3: "pl-24"},
    "position_left": {0: "", 1: "left-0", 2: "left-8", 3: "left-17"},
    "before_position_left": {
        0: "",
        1: "before:left-0",
        2: "before:left-8",
        3: "before:left-17",
    },
}


def paginate_and_get_page(queryset, page, instances_per_page=10):
    paginator = Paginator(queryset, instances_per_page)
    return paginator.get_page(page)
