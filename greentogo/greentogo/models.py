import uuid

from django.db import models


class Plan(models.Model):
    PLANA = 'A'
    PLANB = 'B'
    PLANC = 'C'
    PLAN_CHOICES = (
        (PLANA, 'Plan A'),
        (PLANB, 'Plan B'),
        (PLANC, 'Plan C'),
    )
    slug = models.CharField(max_length=30)
    name = models.CharField(choices=PLAN_CHOICES, max_length=1)
    amount = models.DecimalField(decimal_places=2, max_digits=10)


class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    stripe_id = models.CharField(max_length=30)


class Subscription(models.Model):
    # TODO - decide whether to cascade delete
    customer = models.ForeignKey(Customer)
    plan = models.ForeignKey(Plan)
    started_on = models.DateField(auto_now_add=True)
    internal_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    stripe_id = models.CharField(max_length=100)


