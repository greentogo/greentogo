import uuid

from django.db import models


class Plan(models.Model):
    slug = models.CharField(max_length=30)
    name = models.CharField(max_length=30)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    display_price = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    stripe_id = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    # TODO - decide whether to cascade delete
    customer = models.ForeignKey(Customer)
    plan = models.ForeignKey(Plan)
    started_on = models.DateField(auto_now_add=True)
    internal_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True)
    stripe_id = models.CharField(max_length=100)
