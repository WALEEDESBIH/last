from django.db import models
from django.utils import timezone
import re
from django.core.exceptions import ValidationError

TAX_RATE = 0.03
SHIPPING_FEES = 7

class Inventory(models.Model):
    name = models.CharField(max_length=255)
    rows_number = models.IntegerField()
    columns_number = models.IntegerField()
    layers_number = models.IntegerField()

    class Meta:
        verbose_name_plural = "Inventories"

    def __str__(self):
        return f'{self.name} - {self.id}'

class InventoryLocation(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, null=True)
    row = models.IntegerField(null=True)
    column = models.IntegerField(null=True)
    layer = models.IntegerField(null=True)
    reserved = models.BooleanField( null=True)

        
    class Meta:
        unique_together = ('inventory', 'row', 'column', 'layer')

    def __str__(self):
        if self.inventory:
            return f"Row {self.row}, Column {self.column}, Layer {self.layer} - {self.inventory.name}"
        else:
            return "Empty"

class Category(models.Model):
    name = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True) 
    date_added = models.DateTimeField(default=timezone.now, null=True, blank=True) 
    date_updated = models.DateTimeField(auto_now=True, null=True, blank=True) 

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Stock(models.Model):
    UNIT_TYPES = [
        ('kg', 'Kilogram'),
        ('l', 'Liter'),
        ('m', 'Meter'),
        ('each', 'Each'),
    ]

    vocab_no = models.CharField(max_length=50, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255, null=True)
    description1 = models.TextField(null=True)
    description2 = models.TextField(null=True)
    image = models.ImageField(default='avatar.jpg', upload_to='stock_images/', null=True, blank=True)
    unit = models.CharField(max_length=255, choices=UNIT_TYPES, null=True)
    unit_cost = models.FloatField(null=True, blank=True)
    stocks_on_hand = models.IntegerField(default=0)
    stocks_committed = models.IntegerField(default=0)
    stocks_availability = models.IntegerField(editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    stored_stocks = models.IntegerField(default=0)
    exp_date = models.DateField(null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    sold_number = models.IntegerField(default=0)
    threshold = models.FloatField(default=0)
    active = models.BooleanField(default=True)
    inventory = models.ForeignKey(Inventory, models.CASCADE, null=True, blank=True)
    location = models.ForeignKey(InventoryLocation, models.CASCADE, null=True, blank=True)

    def is_low_stock(self):
        return self.stocks_availability < self.threshold

    def save(self, *args, **kwargs):
        if self.pk:
            from pos.models import InboundItem  # Avoid circular import
            material_inbounds = InboundItem.objects.filter(material=self)
            self.stocks_on_hand = sum(material.quantity for material in material_inbounds)
            from e_commerce.models import OrderItem  # Avoid circular import
            stock_committed = OrderItem.objects.filter(
                product=self,
                order__done=False
            )
            self.stocks_committed = sum(int(stock.quantity) for stock in stock_committed)
            from pos.models import OutboundItem
            material_sold_number = OutboundItem.objects.filter(
                material=self,
            )
            self.sold_number = sum(material.quantity for material in material_sold_number)

        self.stocks_availability = self.stocks_on_hand - self.stocks_committed
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Color(models.Model):
    product = models.ForeignKey(Stock, models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    rgb = models.CharField(max_length=7)

    class Meta:
        verbose_name = 'Product Color'
        verbose_name_plural = 'Product Colors'


    def clean(self):
        super().clean()
        if not re.match(r'^#[0-9A-Fa-f]{6}$', self.rgb):
            raise ValidationError('RGB must be in the format #RRGGBB.')

    def __str__(self):
        return f"{self.name} - {self.rgb}"

class Contact_us(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField(max_length=100)
    subject=models.CharField(max_length=100)
    message=models.TextField()
    date = models.DateTimeField(auto_now_add=True)    

    def __str__(self):
         return self.email