from wish.models import ActiveWish


def get_active_wish(request):
    user = request.user
    active_wish = ActiveWish.objects.filter(user_to_execute_wish=user.id)
    return {'active_wish': active_wish if user.is_authenticated and active_wish.exists() else []}
