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
