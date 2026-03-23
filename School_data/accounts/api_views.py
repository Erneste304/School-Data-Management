import json
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View

@method_decorator(csrf_exempt, name='dispatch')
class APILoginView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
        except json.JSONDecodeError:
            return JsonResponse({'detail': 'Invalid JSON format.'}, status=400)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return JsonResponse({
                    'detail': 'Successfully logged in.',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'role': user.role,
                        'name': user.get_full_name()
                    }
                })
            else:
                return JsonResponse({'detail': 'Account inactive.'}, status=403)
        else:
            return JsonResponse({'detail': 'Invalid credentials. Please try again.'}, status=401)


@method_decorator(csrf_exempt, name='dispatch')
class APILogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        return JsonResponse({'detail': 'Successfully logged out.'})

    def get(self, request, *args, **kwargs):
        logout(request)
        return JsonResponse({'detail': 'Successfully logged out.'})
