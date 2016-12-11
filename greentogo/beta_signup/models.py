import uuid

from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    stripe_id = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    stripe_id = models.CharField(max_length=100, unique=True)
    internal_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True)
    customer = models.ForeignKey(Customer)
    plan = models.CharField(max_length=255)
    started_on = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
