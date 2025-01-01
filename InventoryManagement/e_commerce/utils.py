from django.db import transaction
from django.core.exceptions import ValidationError
import random
from inventory.models import InventoryLocation

def assign_random_location_to_inbound_item(inbound_item):

    # Start a transaction block to ensure atomicity
    with transaction.atomic():
        # Retrieve all available locations for this inventory
        available_locations = InventoryLocation.objects.filter(
            reserved=False,  # Only select locations that are not reserved
        )

        # If there are no available locations, raise an exception
        if not available_locations:
            raise ValidationError("No available locations for this inventory.")

        # Randomly select an available location
        selected_location = random.choice(available_locations)

        # Assign the selected location to the inbound item
        inbound_item.location = selected_location
        inbound_item.save()

        # Mark the location as reserved
        selected_location.reserved = True  # Mark as reserved for this item
        selected_location.stock = inbound_item
        selected_location.save()

        return selected_location  # Return the assigned location

from inventory.models import Inventory, InventoryLocation

def generate_locations_for_inventory(inventory):
    # Get the dimensions of the inventory
    rows = inventory.rows_number
    columns = inventory.columns_number
    layers = inventory.layers_number

    # Generate all possible combinations of row, column, and layer
    locations = []
    for row in range(1, rows + 1):
        for column in range(1, columns + 1):
            for layer in range(1, layers + 1):
                # Create and save a location
                location = InventoryLocation.objects.create(
                    inventory=inventory,
                    row=row,
                    column=column,
                    layer=layer,
                    reserved=False,  # Initially, all locations are unreserved
                    stock=None  # No stock assigned initially
                )
                locations.append(location)

    return locations


