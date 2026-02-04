"""
Django management command to clear all clients and products from the database.
Usage: python manage.py clear_data
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import Cliente
from apps.catalog.models import Producto


class Command(BaseCommand):
    help = 'Clear all clients and products from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion without prompting'
        )

    def handle(self, *args, **options):
        from apps.orders.models import Pedido
        
        confirm = options['confirm']

        # Count items
        client_count = Cliente.objects.count()
        product_count = Producto.objects.count()
        order_count = Pedido.objects.count()

        if client_count == 0 and product_count == 0 and order_count == 0:
            self.stdout.write(
                self.style.SUCCESS('Database is already empty - nothing to clear')
            )
            return

        self.stdout.write(
            f'Found {order_count} orders, {client_count} clients and {product_count} products'
        )

        # Delete all
        if confirm or (client_count + product_count + order_count) < 100:  # Auto-confirm if few items
            self.stdout.write('Clearing database...')
            
            # Delete orders first (they reference clients)
            if order_count > 0:
                deleted_orders = Pedido.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS(f'Deleted {deleted_orders[0]} orders')
                )
            
            # Delete clients (this also deletes associated users)
            if client_count > 0:
                deleted_clients = Cliente.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS(f'Deleted {deleted_clients[0]} clients')
                )
            
            # Delete products
            if product_count > 0:
                deleted_products = Producto.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS(f'Deleted {deleted_products[0]} products')
                )
            
            self.stdout.write(
                self.style.SUCCESS('Database cleared successfully!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Use --confirm flag to delete data')
            )
