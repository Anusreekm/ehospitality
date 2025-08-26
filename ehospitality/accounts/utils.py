from .models import User

def get_session_user(request):

    uid = request.session.get('user_id')
    if not uid:
        return None
    try:
        return User.objects.get(pk=uid)
    except User.DoesNotExist:
        return None

def require_role(request, allowed_roles):

    user = get_session_user(request)
    if not user:
        return None
    if user.role not in allowed_roles:
        return None
    return user
