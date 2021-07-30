from django.forms import ModelForm
from .models import Message

class SignUpForm(ModelForm):
    class Meta:
        model = Message
        fields = ['sender', 'receiver', 'message']