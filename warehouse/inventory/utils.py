def prepare_pie_chart_data(stock_levels):
    labels = []
    data = []

    # Assuming you want to create a pie chart based on product names and their quantities
    for stock_level in stock_levels:
        labels.append(stock_level.product.name)
        data.append(stock_level.quantity)

    pie_chart_data = {
        'labels': labels,
        'datasets': [{
            'data': data,
            'backgroundColor': [
                'rgba(255, 99, 132, 0.5)',
                'rgba(54, 162, 235, 0.5)',
                'rgba(255, 206, 86, 0.5)',
                'rgba(75, 192, 192, 0.5)',
                'rgba(153, 102, 255, 0.5)',
                'rgba(255, 159, 64, 0.5)',
                'rgba(255, 99, 132, 0.5)',
                'rgba(54, 162, 235, 0.5)',
                'rgba(255, 206, 86, 0.5)',
                'rgba(75, 192, 192, 0.5)',
                'rgba(153, 102, 255, 0.5)',
                'rgba(255, 159, 64, 0.5)',
                # Add more colors if needed
            ]
        }]
    }

    return pie_chart_data