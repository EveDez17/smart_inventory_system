from django.core.management.base import BaseCommand
from warehouse.inbound.models import FLTTask
from warehouse.inventory.models import Report, StockLevel, Supplier
from warehouse.outbound.models import Customer, Order, VNATask
from django.utils import timezone

class Command(BaseCommand):
    help = 'Populate reports for stock levels, tasks, orders, suppliers, and customers'

    def handle(self, *args, **options):
        # Populate stock levels report
        stock_levels_report = Report.objects.create(name='Stock Levels Report', report_type='stock_levels')
        stock_levels_data = StockLevel.objects.values('product__name', 'quantity')
        stock_levels_report.report_data = stock_levels_data
        stock_levels_report.save()
        self.stdout.write(self.style.SUCCESS('Stock Levels Report populated successfully.'))

        # Populate tasks report
        tasks_report = Report.objects.create(name='Tasks Report', report_type='tasks')
        tasks_data = VNATask.objects.values('name', 'status')
        tasks_report.report_data = tasks_data
        tasks_report.save()
        self.stdout.write(self.style.SUCCESS('Tasks Report populated successfully.'))

        # Populate orders report
        orders_report = Report.objects.create(name='Orders Report', report_type='orders')
        orders_data = Order.objects.values('order_number', 'status', 'total_amount')
        orders_report.report_data = orders_data
        orders_report.save()
        self.stdout.write(self.style.SUCCESS('Orders Report populated successfully.'))

        # Populate suppliers report
        suppliers_report = Report.objects.create(name='Suppliers Report', report_type='suppliers')
        suppliers_data = Supplier.objects.values('name', 'contact_person', 'email')
        suppliers_report.report_data = suppliers_data
        suppliers_report.save()
        self.stdout.write(self.style.SUCCESS('Suppliers Report populated successfully.'))

        # Populate customers report
        customers_report = Report.objects.create(name='Customers Report', report_type='customers')
        customers_data = Customer.objects.values('name', 'contact_person', 'email')
        customers_report.report_data = customers_data
        customers_report.save()
        self.stdout.write(self.style.SUCCESS('Customers Report populated successfully.'))
        


class Command(BaseCommand):
    help = 'Populate reports'

    def handle(self, *args, **options):
        # Populate reports for VNATasks
        vna_tasks_data = VNATask.objects.values('status')

        # Populate reports for FLTTasks
        flt_tasks_data = FLTTask.objects.values('status')

        # Populate reports for Orders
        orders_data = Order.objects.filter(order_date__gte=timezone.now() - timezone.timedelta(days=30)) \
            .values('status', 'total_amount')

        # Populate reports for Stock Levels
        stock_levels_data = StockLevel.objects.values('product__name', 'quantity')

        # Print or process the data as needed
        print("VNA Tasks Data:", vna_tasks_data)
        print("FLT Tasks Data:", flt_tasks_data)
        print("Orders Data:", orders_data)
        print("Stock Levels Data:", stock_levels_data)

