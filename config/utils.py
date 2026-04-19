from datetime import datetime
from django.utils import timezone
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage

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


def paginate_and_get_page(queryset, page, instances_per_page=20):
    paginator = Paginator(queryset, instances_per_page)
    try:
        return paginator.page(page)
    except EmptyPage:
        return queryset  # empty queryset


def get_snapshot(GET_request):
    snapshot = GET_request.get("snapshot", timezone.now())
    try:
        snapshot = timezone.make_aware(
            datetime.strptime(snapshot.replace(".", ""), "%B %d, %Y, %I:%M %p")
        )
    except ValueError:
        snapshot = timezone.make_aware(
            datetime.strptime(snapshot.replace(".", ""), "%B %d, %Y, %I %p")
        )
    except TypeError:
        pass
    return snapshot
