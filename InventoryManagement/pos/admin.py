from django.contrib import admin
from .models import Inbound, Outbound, InboundItem, OutboundItem

admin.site.register(Inbound)
admin.site.register(Outbound)
admin.site.register(InboundItem)
admin.site.register(OutboundItem)

# Register your models here.
