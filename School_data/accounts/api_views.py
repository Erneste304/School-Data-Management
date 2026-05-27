import json
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import UserSerializer, UserCreateSerializer
from .models import CustomUser


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


class RegisterView(generics.CreateAPIView):
    """Public registration endpoint for new users."""
    queryset = CustomUser.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'detail': 'Account created successfully.',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'name': user.get_full_name(),
            }
        }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user(request):
    """Return the currently authenticated user's info."""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_list(request):
    """Return all users (admin only)."""
    if request.user.role not in ('admin', 'head_teacher'):
        return Response({'detail': 'Not authorized.'}, status=403)
    users = CustomUser.objects.all().order_by('last_name', 'first_name')
    role = request.query_params.get('role')
    if role:
        users = users.filter(role=role)
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)
