from django import forms
from .models import Stream, StreamSetting

class StreamForm(forms.ModelForm):
    class Meta:
        model = Stream
        fields = ['title', 'event', 'description', 'scheduled_start', 'thumbnail', 'is_public']
        widgets = {
            'scheduled_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class StreamSettingForm(forms.ModelForm):
    class Meta:
        model = StreamSetting
        fields = ['enable_chat', 'enable_qa', 'record_stream', 'resolution', 'bitrate']
