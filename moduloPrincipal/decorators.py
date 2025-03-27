from django.shortcuts import redirect
from functools import wraps

def guest_or_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        

        if request.user.is_authenticated or request.session.get('guest'):
            return view_func(request, *args, **kwargs)
        return redirect('login')
    return _wrapped_view