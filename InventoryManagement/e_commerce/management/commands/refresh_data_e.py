# your_app/management/commands/refresh_data.py

from django.core.management.base import BaseCommand
from e_commerce.models import Order, OrderItem
from inventory.models import Stock

class Command(BaseCommand):
    help = 'Refresh data in the database'

    def handle(self, *args, **kwargs):
        # Example: refresh stock availability
        stocks = Order.objects.all()
        for stock in stocks:
            stock.save()  # or update specific fields as necessary
        self.stdout.write(self.style.SUCCESS('Successfully refreshed data'))
        
        orderitems = OrderItem.objects.all()
        for stock in orderitems:
            stock.save()  # or update specific fields as necessary
        self.stdout.write(self.style.SUCCESS('Successfully refreshed data'))

        stocks = Stock.objects.all()
        for stock in stocks:
            stock.save()
        self.stdout.write(self.style.SUCCESS('Successfully refreshed data'))