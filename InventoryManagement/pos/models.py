from django.db import models
from django.contrib.auth.models import User
from inventory.models import Stock
from datetime import date
from django.utils import timezone
from django.core.exceptions import ValidationError

class Inbound(models.Model):
    code = models.CharField(max_length=255, null=True, blank=True)
    responsible_staff = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date_added = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True)
    source = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f'{self.responsible_staff} - {self.source}'

class Outbound(models.Model):
    code = models.CharField(max_length=255, null=True, blank=True)
    responsible_staff = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    sale = models.ForeignKey('sales.Sale', on_delete=models.CASCADE, null=True, blank=True)

from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from e_commerce.utils import assign_random_location_to_inbound_item

class InboundItem(models.Model):
    material = models.ForeignKey('inventory.Stock', on_delete=models.CASCADE, null=True, blank=True)
    inbound = models.ForeignKey(Inbound , on_delete=models.CASCADE, related_name='inbound_items', null=True, blank=True)
    quantity = models.PositiveIntegerField()
    expiration_date = models.DateField(null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError('Quantity must be greater than zero.')
        if self.expiration_date and self.expiration_date < timezone.now().date():
            raise ValidationError('Expiration date cannot be in the past.')

    def __str__(self):
        return f'{self.material} - {self.quantity}' if self.material else 'Unnamed Material'
    
    def is_expiring_soon(self, days_threshold=30):
        return self.expiration_date and (self.expiration_date - date.today()).days <= days_threshold

# Ignored for now
class OutboundItem(models.Model):
    inventory = models.ForeignKey('inventory.Inventory', models.CASCADE, null=True, blank=True)
    material = models.ForeignKey(Stock, on_delete=models.CASCADE, null=True, blank=True)
    outbound = models.ForeignKey(Outbound, on_delete=models.CASCADE, related_name='outbounds_items', null=True, blank=True)
    quantity = models.PositiveIntegerField()
    total_price = models.FloatField()
    sold_date = models.DateField(null=True)

    def __str__(self):
        return f'{self.material} - {self.quantity}'

