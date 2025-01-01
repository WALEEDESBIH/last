import random
from .models import Inventory, Stock, InventoryLocation
from django.db import connection
import pandas as pd
import plotly.express as px
import plotly.io as pio
from django.shortcuts import get_object_or_404
def generate_rgba_colors(n):
    colors = []
    #random.seed(seed)  # Set the seed for reproducibility
    for _ in range(n):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        a = 1  # Fixed alpha value
        color = f'rgba({r}, {g}, {b}, {a})'
        colors.append(color)
    return colors

def prepare_inventory_data():
    inventories = Inventory.objects.all()
    stocks = Stock.objects.all()
    inventory_data = []
    for inventory in inventories:
        rows = []
        for row_num in range(1, inventory.rows_number + 1):
            total_spaces = inventory.columns_number * inventory.layers_number
            reserved_spaces = InventoryLocation.objects.filter(
                inventory=inventory, row=row_num, reserved=True
            ).count()
            
            available_spaces = total_spaces - reserved_spaces
            rows.append({
                'row': row_num,
                'empty_spaces': available_spaces
            })

        inventory_data.append({
            'inventory': inventory,
            'rows': rows,
        })

    return {
        'inventory_data': inventory_data,
        'stocks': stocks,
    }

def fetch_top_stocks():
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM inventory_stock ORDER BY sold_number DESC LIMIT 10;')
        rows = cursor.fetchall()
        # Assuming the columns are known and in the correct order
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
    return df

def top_10_stocks_chart():
    stocks = Stock.objects.raw('SELECT * FROM inventory_stock;')  # Fetch all stock items
    data = fetch_top_stocks()  # Fetch the top 10 selling items data
    chart_type = 'bar'

    try:
        # Check if data is not empty and has the necessary columns
        if not data.empty and 'name' in data.columns and 'sold_number' in data.columns:
            if chart_type == 'bar':
                fig = px.bar(
                    data,
                    x='name',  # Column name for the x-axis (item names)
                    y='sold_number',  # Column name for the y-axis (selling numbers)
                    title='Top 10 Selling Items',
                    color='name'  # Optional: Color bars by item names
                )
                
                fig.update_layout(
                    xaxis_title='Item Name',
                    yaxis_title='Selling Number'
                )
                
            # Convert Plotly figure to HTML
            plot_html = pio.to_html(fig, full_html=False)
        else:
            plot_html = None
            context ={
                'error': 'Data is empty or missing necessary columns.',
                'chart_type': chart_type,
                'stocks':stocks,
            }
            return context

    except Exception as e:
        plot_html = None
        context =  {
            'error': f'Error generating plot: {e}',
            'chart_type': chart_type,
            'stocks':stocks,
        }
        return context

    context = {
        'plot_html': plot_html,
        'chart_type': chart_type,
        'stocks':stocks,
    }
    return context

def generate_charts(order_labels, order_data, products):
    # Validate input data
    if len(order_labels) != len(order_data):
        raise ValueError("The length of order_labels must match the length of order_data.")
    
    if not products:
        raise ValueError("The products list cannot be empty.")
    
    # Pie Chart using Plotly Express
    pie_chart = px.pie(
        names=order_labels,
        values=order_data,
        title='E-Commerce Orders Analysis',
        hover_data={'values': order_data},  # Improved hover data for clarity
    )
    pie_chart.update_traces(textinfo='percent+label')
    pie_chart.update_layout(title_x=0.5)

    pie_chart_html = pio.to_html(pie_chart, full_html=False)

    # Bar Chart using Plotly Express
    product_names = [product.name for product in products]
    stocks_availability = [product.stocks_availability for product in products]

    bar_chart = px.bar(
        x=product_names,
        y=stocks_availability,
        title='Product Availability',
        color=stocks_availability,  # Use actual stock values for coloring
        color_continuous_scale='Viridis',
        text=stocks_availability
    )

    bar_chart.update_traces(texttemplate='%{text}', textposition='outside')
    bar_chart.update_layout(
        xaxis_title='Products',  # Improved axis title
        yaxis_title='Stocks Availability',
        plot_bgcolor='rgba(0,0,0,0)',
        title_x=0.5,
        showlegend=False
    )
    
    bar_chart_html = pio.to_html(bar_chart, full_html=False)

    return pie_chart_html, bar_chart_html

from django.core.exceptions import ValidationError
from .models import InventoryLocation


def create_location_until_available(pk):
    # Set minimum values for row, column, and layer to 1
    r_min, cl_min, layer_min = 1, 1, 1
    inventory = get_object_or_404(Inventory, id=pk)

    # Calculate the maximum possible locations in the inventory
    max_locations = inventory.rows_number * inventory.columns_number * inventory.layers_number

    # Check if there is enough space for new locations
    existing_objects_count = InventoryLocation.objects.count()
    if existing_objects_count >= max_locations:
        raise ValueError("No more space left to create any location.")  # Raise an error if no space is available

    # Loop to generate locations until an available one is found or all options are exhausted
    for r in range(r_min, inventory.rows_number + 1):
        for cl in range(cl_min, inventory.columns_number + 1):
            for layer in range(layer_min, inventory.layers_number + 1):
                try:
                    # Check if the location already exists
                    location = InventoryLocation.objects.filter(row=r, column=cl, layer=layer, inventory=inventory).first()

                    if location is None:
                        # If the location doesn't exist, create it with reserved=True
                        new_location = InventoryLocation(row=r, column=cl, layer=layer, reserved=True, inventory=inventory)
                        new_location.save()
                        # Return the new location object as it is available
                        return new_location
                    elif location.reserved is False:
                        # If the location exists and is not reserved, return it as it can be assigned
                        return location
                    else:
                        # If the location is reserved, continue to try other locations
                        continue

                except Exception as e:
                    # Handle any exceptions (e.g., database issues)
                    raise ValueError(f"Error creating location ({r}, {cl}, {layer}): {str(e)}")

    # If no available location is found, raise an error
    raise ValueError("No available location found.")
 