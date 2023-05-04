from wish.models import ActiveWish


def get_active_wish(request):
    """Этот код содержит контекст-процессор, который предоставляет данные о текущем активном желании пользователя. """
    user = request.user
    active_wish = ActiveWish.objects.filter(executor=user.id)
    return {'active_wish': active_wish if user.is_authenticated and active_wish.exists() else []}
