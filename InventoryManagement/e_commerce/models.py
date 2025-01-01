from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.apps import apps 
from datetime import date
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.utils.html import escape
from io import BytesIO
from inventory.models import TAX_RATE

class Order(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)    
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    contry= models.CharField(max_length=100)
    address=models.TextField(null=True,blank=True)
    city= models.CharField(max_length=100,null=True,blank=True)
    postcode= models.IntegerField(null=True,blank=True)
    phone=models.IntegerField(null=True,blank=True)
    email= models.CharField(max_length=100,null=True,blank=True)
    additional_info=models.TextField(null=True,blank=True)
    subtotal=models.CharField(max_length=100,null=True,blank=True)
    tax = models.CharField(max_length=100, default=str(TAX_RATE))
    total = models.FloatField(editable=False, null=True, blank=True)
    date= models.DateField(default=date.today,null=True,blank=True)
    payment_id = models.CharField(max_length=300,null=True,blank=True)
    paid = models.BooleanField(default= False ,null= True)
    done = models.BooleanField(default=False)
    seen_by_user = models.BooleanField(default = False)

    def __str__(self):
      return f"{self.user.username} - {self.id}"

    def save(self, *args, **kwargs):
        if self.pk:  # Ensures this only happens when the instance is being updated
            # Sum the total of all related OrderItem objects and update `amount`
            self.subtotal = str(sum(float(item.total) for item in self.orderitem_set.all()))
            if self.subtotal:
                self.total = float((float(self.subtotal) * float(self.tax)) + float(self.subtotal))

        super().save(*args, **kwargs)


    def generate_pdf(self):
        order_items = OrderItem.objects.filter(order=self)
        context = {'order': self, 'order_items': order_items}
        html_string = render_to_string('bills/order_confirmation.html', context)

        try:
            result = BytesIO()
            pdf = pisa.CreatePDF(BytesIO(html_string.encode('utf-8')), dest=result)
            if pdf.err:
                raise Exception("Error generating PDF")
            return result.getvalue()
        except Exception as e:
            # Handle the error appropriately (log it, raise, etc.)
            print(f"Failed to generate PDF: {e}")
            return None
    
class OrderItem(models.Model):    
    order= models.ForeignKey(Order,on_delete=models.CASCADE,null=True) 
    product= models.ForeignKey("inventory.Stock", models.CASCADE, null=True, blank= True)
    quantity= models.CharField(max_length=100)
    price= models.CharField(max_length=100, editable=False)
    total= models.CharField(max_length=1000, editable=False)

    def __str__(self):
        return self.order.user.username
    
    def save(self, *args, **kwargs):
        if self.product:
            self.price = self.product.unit_cost
        self.total = str(float(self.price)*float(self.quantity))
        super().save(*args, **kwargs)
