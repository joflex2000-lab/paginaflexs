"""
Django management command to import products from an Excel/CSV file.
Usage: python manage.py import_productos <file_path>
"""
import os
from django.core.management.base import BaseCommand, CommandError
from apps.imports.services.products import ProductImporter
from apps.imports.models import ImportLog


class Command(BaseCommand):
    help = 'Import products from an Excel or CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Path to the Excel or CSV file with product data'
        )
        parser.add_argument(
            '--skip-if-exists',
            action='store_true',
            help='Skip import if products already exist in database'
        )

    def handle(self, *args, **options):
        from apps.catalog.models import Producto
        
        file_path = options['file_path']
        skip_if_exists = options['skip_if_exists']

        # Check if we should skip
        if skip_if_exists:
            existing_count = Producto.objects.count()
            if existing_count > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'Skipping import - {existing_count} products already exist in database'
                    )
                )
                return

        # Verify file exists
        if not os.path.exists(file_path):
            raise CommandError(f'File does not exist: {file_path}')

        self.stdout.write(f'Starting product import from: {file_path}')

        try:
            # Open file
            with open(file_path, 'rb') as f:
                # Create importer
                importer = ProductImporter(f)

                # Create import log
                log = ImportLog.objects.create(
                    tipo='productos',
                    archivo=os.path.basename(file_path),
                    estado='procesando',
                    total_filas=0
                )
                importer.log = log

                # Preview (analyze)
                self.stdout.write('Analyzing file...')
                preview_result = importer.preview()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Analysis complete: {preview_result["total_filas"]} rows found'
                    )
                )
                self.stdout.write(f'  - To create: {preview_result["resumen"]["crear"]}')
                self.stdout.write(f'  - To update: {preview_result["resumen"]["actualizar"]}')
                
                if preview_result['errores']:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  - Errors: {len(preview_result["errores"])}'
                        )
                    )
                    for error in preview_result['errores'][:5]:  # Show first 5 errors
                        self.stdout.write(f'    Row {error["fila"]}: {error["error"]}')

                # Execute import
                self.stdout.write('Importing products...')
                result = importer.ejecutar()

                # Show results
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\nImport completed successfully!'
                    )
                )
                self.stdout.write(f'  - Processed: {result["procesados"]}')
                self.stdout.write(f'  - Created: {result["resumen"]["crear"]}')
                self.stdout.write(f'  - Updated: {result["resumen"]["actualizar"]}')
                
                if result['errores']:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  - Errors: {len(result["errores"])}'
                        )
                    )

        except Exception as e:
            raise CommandError(f'Import failed: {str(e)}')
