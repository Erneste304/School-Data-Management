from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Stream, StreamArchive, ViewerStat
from accounts.views import role_required
from .forms import StreamForm

@login_required
def stream_list_view(request):
    live_streams = Stream.objects.filter(status='live', is_public=True)
    upcoming_streams = Stream.objects.filter(status='scheduled', is_public=True).order_by('scheduled_start')
    past_streams = StreamArchive.objects.all().order_by('-created_at')[:12]
    
    context = {
        'live_streams': live_streams,
        'upcoming_streams': upcoming_streams,
        'past_streams': past_streams,
    }
    return render(request, 'livestream/list.html', context)

@login_required
def live_stream_view(request, pk):
    stream = get_object_or_404(Stream, pk=pk)
    if stream.status == 'live':
        ViewerStat.objects.create(
            stream=stream,
            user=request.user,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        stream.view_count += 1
        stream.save()
    
    return render(request, 'livestream/watch.html', {'stream': stream})

@login_required
@role_required(['head_teacher', 'animateur', 'admin'])
def manage_streams_view(request):
    streams = Stream.objects.all()
    return render(request, 'livestream/manage.html', {'streams': streams})

@login_required
@role_required(['head_teacher', 'animateur', 'admin'])
def create_stream_view(request):
    if request.method == 'POST':
        form = StreamForm(request.POST, request.FILES)
        if form.is_valid():
            stream = form.save(commit=False)
            stream.created_by = request.user
            stream.save()
            messages.success(request, f'Stream "{stream.title}" scheduled successfully!')
            return redirect('livestream:manage')
    else:
        form = StreamForm()
    return render(request, 'livestream/form.html', {'form': form})


from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

class StreamSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Stream
        fields = ['id', 'title', 'description', 'status', 'status_display', 'stream_url', 'hls_url', 
                  'scheduled_start', 'created_by_name', 'view_count', 'is_public']

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def streams_list_api(request):
    if request.method == 'GET':
        streams = Stream.objects.filter(is_public=True)
        serializer = StreamSerializer(streams, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        if request.user.role not in ('admin', 'head_teacher', 'teacher'):
            return Response({'detail': 'Not authorized.'}, status=403)
        serializer = StreamSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

