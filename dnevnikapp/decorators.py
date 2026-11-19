import functools
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
def roles_required(*roles):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role not in roles:
                raise PermissionDenied
            return func(request, *args, **kwargs)
        return wrapper
    return decorator
