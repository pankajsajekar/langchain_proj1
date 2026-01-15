from django.db import models
from django.contrib.auth.models import User

class AIChats(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
    response = models.TextField(blank=True, null=True)
    tokens_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat {self.id} by {self.user} at {self.created_at}"