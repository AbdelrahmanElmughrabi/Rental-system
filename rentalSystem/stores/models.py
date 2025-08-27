from django.db import models

# Create your models here.


class Store(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=64, unique=True)
    currency = models.CharField(max_length=8, default='USD')
    timezone = models.CharField(max_length=64, default='UTC')
    settings = models.JSONField(default=dict, blank=True)
    contact = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name
