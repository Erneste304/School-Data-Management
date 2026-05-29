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
        
        # Auto-create Student record for student role
        if user.role == 'student':
            from academics.models import Student
            import random
            student_id = f"STU{random.randint(10000, 99999)}"
            Student.objects.create(
                user=user,
                student_id=student_id,
                enrollment_date=timezone.now().date()
            )
        
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


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def parent_children(request):
    """Return all students linked to the current parent user."""
    if request.user.role != 'parent':
        return Response({'detail': 'Only parents can access this endpoint.'}, status=403)
    
    from accounts.models import ParentStudentRelationship
    from academics.serializers import StudentSerializer
    
    relationships = ParentStudentRelationship.objects.filter(parent__user=request.user)
    students = [rel.student for rel in relationships]
    serializer = StudentSerializer(students, many=True)
    return Response(serializer.data)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def user_detail(request, user_id):
    """Retrieve, update, partial update or delete a specific user (admin/head_teacher only)."""
    if request.user.role not in ('admin', 'head_teacher'):
        return Response({'detail': 'Not authorized.'}, status=403)
    
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({'detail': 'User not found.'}, status=404)
    
    # Prevent admin from deleting themselves or being deactivated by others
    if request.method == 'DELETE' and user.id == request.user.id:
        return Response({'detail': 'Cannot delete your own account.'}, status=400)
    
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    elif request.method in ('PUT', 'PATCH'):
        # Prevent deactivating admin users (only admin can deactivate themselves)
        if 'is_active' in request.data and not request.data['is_active']:
            if user.role == 'admin' and user.id != request.user.id:
                return Response({'detail': 'Cannot deactivate another admin user.'}, status=400)
        
        serializer = UserSerializer(user, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    elif request.method == 'DELETE':
        user.delete()
        return Response({'detail': 'User deleted successfully.'}, status=204)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_user_active(request, user_id):
    """Activate or deactivate a user (admin/head_teacher only)."""
    if request.user.role not in ('admin', 'head_teacher'):
        return Response({'detail': 'Not authorized.'}, status=403)
    
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({'detail': 'User not found.'}, status=404)
    
    # Prevent deactivating admin users (only admin can deactivate themselves)
    if user.role == 'admin' and user.id != request.user.id:
        return Response({'detail': 'Cannot deactivate another admin user.'}, status=400)
    
    # Prevent deactivating yourself
    if user.id == request.user.id:
        return Response({'detail': 'Cannot deactivate your own account.'}, status=400)
    
    user.is_active = not user.is_active
    user.save()
    
    return Response({
        'detail': f'User {"activated" if user.is_active else "deactivated"} successfully.',
        'is_active': user.is_active
    })
