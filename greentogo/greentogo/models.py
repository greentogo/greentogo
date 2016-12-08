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
    slug = models.CharField()
    name = models.CharField(choices=PLAN_CHOICES)
    amount = models.DecimalField(decimal_places=2)


class Customer(models.Model):
    name = models.CharField()
    email = models.EmailField()
    stripe_id = models.CharField()


class Subscription(models.Model):
    # TODO - decide whether to cascade delete
    customer = models.ForeignKey(Customer)
    plan = models.ForeignKey(Plan)
    started_on = models.DateField.auto_now_add()
    internal_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    stripe_id = models.CharField()


