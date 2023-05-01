from users.models import User


def active_complete_wish(request):
    wish = User.objects.get(id=request.user.id). \
        matched_user.active_wishes().first()
    return {"wish": wish}
