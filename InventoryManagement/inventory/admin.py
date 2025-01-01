from django.contrib import admin
from .models import Stock, Inventory, InventoryLocation, Category, Color

class ProductColorsAdmin(admin.ModelAdmin):
    list_display = ['rgb']
    search_fields = ('name', 'rgb')
admin.site.register(Color, ProductColorsAdmin)
admin.site.register(Inventory)
admin.site.register(Category)
admin.site.register(Stock)


from django.db.models import Q

class ReservedFilter(admin.SimpleListFilter):
    title = 'Reserved Status'  # The label for the filter
    parameter_name = 'reserved'  # The query parameter in the URL

    def lookups(self, request, model_admin):
        # Display filter options
        return (
            (None, 'All'),  # Option to show all (default)
            (True, 'Reserved'),
            (False, 'Not Reserved'),
        )

    def queryset(self, request, queryset):
        # Apply the filter based on the selected option
        if self.value() is not None:
            return queryset.filter(reserved=self.value())
        return queryset

class InventoryLocationAdmin(admin.ModelAdmin):
    # Adding the filters to the list_filter attribute
    list_filter = ('inventory', 'row', 'column', 'layer', ReservedFilter)

    # You can also add fields to search for in the search bar (optional)
    search_fields = ('inventory__name', 'row', 'column', 'layer')

    # Optionally, specify the fields to display in the list view
    list_display = ('inventory', 'row', 'column', 'layer', 'reserved')

    # You could also use `list_editable` to allow in-line editing in the list view
    list_editable = ('reserved',)

# Register the admin class with the model
admin.site.register(InventoryLocation, InventoryLocationAdmin)

# Register your models here.
