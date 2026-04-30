import time
from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect

class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            now = time.time()

            # Timeout de 30 minutes (1800 secondes) par défaut
            timeout = getattr(settings, 'AUTO_LOGOUT_DELAY', 1800)

            if last_activity and (now - last_activity) > timeout:
                logout(request)
                return redirect('login')

            request.session['last_activity'] = now

        response = self.get_response(request)
        return response
