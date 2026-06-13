def user_role(request):
    if request.user.is_authenticated:
        is_analyst = request.user.groups.filter(name='analyst').exists() or request.user.is_superuser
        return {'is_analyst': is_analyst}
    return {'is_analyst': False}