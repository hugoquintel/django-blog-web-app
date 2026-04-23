from django.db.models import Q, Count


def GET_params_str(request):
    params = request.GET.copy()
    params.pop("page", None)
    params.pop("snapshot", None)
    result = params.urlencode()
    return {"GET_params_str": result}


def top_users(request):
    user = request.user
    context = {}
    if user.is_authenticated:
        context["top_followings"] = user.followings.with_is_followed(
            user=request.user
        ).order_by("-follower_count", "-id")[:5]
        context["top_followers"] = user.followers.with_is_followed(
            user=request.user
        ).order_by("-follower_count", "-id")[:5]
    return context


def notifications(request):
    context = {}
    if request.user.is_authenticated:
        curr_user_notifications = request.user.received_notifications.select_related(
            "sender", "blog", "comment"
        )
        context["notifications"] = curr_user_notifications.order_by(
            "-created_at", "-id"
        )
        context["unseen_notis_num"] = curr_user_notifications.aggregate(
            result=Count("id", filter=Q(is_seen=False))
        )["result"]
    return context
