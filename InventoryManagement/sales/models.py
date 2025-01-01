from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from inventory.models import TAX_RATE

class Sale(models.Model):
    code = models.CharField(max_length=100, null=True)
    user = models.ForeignKey(User, models.CASCADE, null=True, blank=True)
    order = models.ForeignKey('e_commerce.Order', models.CASCADE, null=True, blank=True)
    sub_total = models.FloatField(default=0)#No use
    grand_total = models.FloatField(default=0)#No use
    tax_amount = models.FloatField(default=0)#No use
    tax = models.FloatField(default=0)#No use
    tendered_amount = models.FloatField(default=0, blank=True, null=True)#No use
    amount_change = models.FloatField(default=0, blank=True, null=True)#No use
    date_added = models.DateTimeField(default=timezone.now) 
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.code}'

class SaleItem(models.Model): #saleItem.item.name
    sale = models.ForeignKey(Sale,on_delete=models.CASCADE)
    item = models.ForeignKey('inventory.Stock',on_delete=models.CASCADE)
    price = models.FloatField(default=0)
    qty = models.FloatField(default=0)
    total = models.FloatField(default=0)

class MaterialReport(models.Model):
    inbound = models.ForeignKey('pos.Inbound', models.CASCADE, null=True, blank=True)
    material = models.ForeignKey('inventory.Stock', on_delete=models.CASCADE)
    order = models.ForeignKey('e_commerce.Order', on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    expiration_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.material.name} - {self.quantity}'