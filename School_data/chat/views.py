from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ChatRoom, Message, ParticipantStatus
from .serializers import MessageSerializer

@login_required
def room_list_view(request):
    rooms = ChatRoom.objects.filter(is_active=True)
    if not request.user.is_staff:
        rooms = rooms.filter(Q(room_type='public') | Q(members=request.user))
    
    return render(request, 'chat/room_list.html', {'rooms': rooms})

@login_required
def chat_room_view(request, slug):
    room = get_object_or_404(ChatRoom, slug=slug, is_active=True)
    messages = room.messages.all().order_by('timestamp')[:50]
    participants = ParticipantStatus.objects.filter(room=room).select_related('user')
    
    context = {
        'room': room,
        'messages': messages,
        'participants': participants,
    }
    return render(request, 'chat/room_detail.html', context)

@login_required
def get_messages_api(request, slug):
    room = get_object_or_404(ChatRoom, slug=slug)
    messages = room.messages.all().order_by('timestamp')[:50]
    serializer = MessageSerializer(messages, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unread_counts(request):
    """Get unread message counts for all rooms"""
    rooms = request.user.chat_rooms.filter(is_active=True)
    
    unread_counts = {}
    for room in rooms:
        last_read = ParticipantStatus.objects.filter(
            user=request.user,
            room=room
        ).values_list('last_read', flat=True).first()
        
        if last_read:
            unread = Message.objects.filter(
                room=room,
                timestamp__gt=last_read
            ).exclude(sender=request.user).count()
        else:
            unread = Message.objects.filter(
                room=room
            ).exclude(sender=request.user).count()
        
        unread_counts[room.id] = unread
    
    return Response(unread_counts)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_room_read(request, room_id):
    """Mark all messages in room as read"""
    room = get_object_or_404(ChatRoom, id=room_id)
    
    # Update last read timestamp
    status, created = ParticipantStatus.objects.get_or_create(
        user=request.user,
        room=room
    )
    status.last_read = timezone.now()
    status.save()
    
    # Mark individual messages as read
    Message.objects.filter(
        room=room
    ).exclude(
        sender=request.user
    ).update(is_read=True)
    
    return Response({'success': True})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_messages(request):
    """Search through message history"""
    query = request.GET.get('q', '')
    room_id = request.GET.get('room')
    
    messages = Message.objects.filter(
        Q(content__icontains=query) |
        Q(sender__first_name__icontains=query) |
        Q(sender__last_name__icontains=query)
    )
    
    if room_id:
        messages = messages.filter(room_id=room_id)
    
    if request.user.role != 'admin':
        messages = messages.filter(room__members=request.user)
    
    messages = messages.order_by('-timestamp')[:100]
    serializer = MessageSerializer(messages, many=True)
    
    return Response(serializer.data)
