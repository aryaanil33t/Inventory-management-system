from django.shortcuts import redirect


def user_role_permission(roles,redirect_url):

    def decorator(fn):

        def wrapper(request,*args,**kwargs):

            if request.user.is_authenticated and request.user.role in roles:

                return fn(request,*args,**kwargs)
            
            return redirect(redirect_url)

        return wrapper
    
    return decorator