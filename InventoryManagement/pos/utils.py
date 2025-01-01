from .models import Inbound, Outbound, InboundItem, OutboundItem
from sales.models import MaterialReport
from django.contrib import messages  # Use 'django.contrib.messages' instead of 'flash_messages'
from django.shortcuts import get_object_or_404
from inventory.models import Stock
from django.db import IntegrityError, transaction
from datetime import date, datetime
def generate_unique_code(model, prefix):
    """ Generate a unique code for the given model based on a prefix. """
    i = 1
    while True:
        code = '{:0>5}'.format(i)
        check = model.objects.filter(code=f"{prefix}{code}").exists()
        if not check:
            return f"{prefix}{code}"
        i += 1

def process_inbound(user, products, source):
    try:
        # Start a transaction to ensure atomicity
        with transaction.atomic():
            # Create or update the Inbound object
            inbound, created = Inbound.objects.update_or_create(
                responsible_staff=user,
                source=source,
            )

            for id, qty, exp_date in products:
                try:
                    # Ensure quantity is an integer and expiration date is valid
                    qty = int(qty)

                    # Check if the InboundItem already exists for the same inbound and material
                    existing_item = InboundItem.objects.filter(inbound=inbound, material_id=id).first()

                    if existing_item:
                        # If it exists, update the existing item
                        existing_item.quantity += qty  # You can modify this logic based on your needs
                        if exp_date:
                            existing_item.expiration_date = exp_date  # Update expiration date if provided
                        existing_item.save()  # Save the updated item
                    else:
                        # If it doesn't exist, create a new InboundItem

                        InboundItem.objects.create(
                            inbound=inbound,
                            material_id=id,
                            quantity=qty,
                            expiration_date=exp_date,
                        )

                    # Create or update the MaterialReport
                    MaterialReport.objects.update_or_create(
                        material_id=id,
                        quantity=qty,
                        expiration_date=exp_date,
                    )

                    # Ensure the material exists in Stock before saving
                    material = get_object_or_404(Stock, id=id)
                    material.save()

                except IntegrityError as e:
                    # Handle database integrity errors, like foreign key violations or unique constraint errors
                    raise IntegrityError(f"Error processing material {id}: {str(e)}")
                except ValueError as e:
                    # Handle invalid quantity or expiration date formats
                    raise ValueError(f"Invalid data for material {id}: {str(e)}")

            return 'Inbound processed successfully!'

    except IntegrityError as e:
        # Catch errors related to the Inbound object creation/update
        return f"Error processing inbound: {str(e)}"
    
    except Exception as e:
        # Catch all other exceptions and return a message
        return f"An unexpected error occurred: {str(e)}"

def process_outbound(product, quantity):
    stock = get_object_or_404(Stock, id=product.id)

    # Check if product and quantity are valid
    if product is None or quantity is None:
        return 'Null values are passed, track your process!'

    if stock.stocks_availability < quantity:
        message = f"{product.name}'s quantity cannot be processed due to a lack of availability!"
        print(message)
        return message

    inbound_items = InboundItem.objects.filter(material=product).order_by('expiration_date')

    for item in inbound_items:
        if item.quantity <= 0:
            continue  # Skip items with zero quantity

        # Process the outbound quantity
        if quantity > 0:
            if item.quantity >= quantity:
                item.quantity -= quantity
                item.save()
                print(f"Processed {quantity} from {item.material.name}. Remaining quantity: {item.quantity}")
                quantity = 0  # All quantity has been processed
                break
            else:
                quantity -= item.quantity
                print(f"Processed {item.quantity} from {item.material.name}. Remaining quantity to process: {quantity}")
                item.quantity = 0  # All of this item is consumed
                item.save()
        else:
            break  # No quantity left to process

    if quantity > 0:
        message = f"Not all of the requested quantity for {product.name} could be processed."
        print(message)
        stock.save()
        return message
    stock.save()
    return "Outbound processing completed successfully."
