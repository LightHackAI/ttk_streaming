from django import forms
from .models import MediaFile, Playlist, PlaylistItem, AudioRecording


class MediaFileForm(forms.ModelForm):
    class Meta:
        model = MediaFile
        fields = ['title', 'file', 'media_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].widget.attrs.update({'accept': 'audio/*,video/*'})


class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['name']


class PlaylistItemForm(forms.ModelForm):
    class Meta:
        model = PlaylistItem
        fields = ['media_file', 'order']


class AudioRecordingForm(forms.ModelForm):
    class Meta:
        model = AudioRecording
        fields = ['title', 'audio_file']