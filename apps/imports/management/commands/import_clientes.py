"""
Django management command to import clients from an Excel/CSV file.
Usage: python manage.py import_clientes <file_path>
"""
import os
from django.core.management.base import BaseCommand, CommandError
from apps.imports.services.clients import ClientImporter
from apps.imports.models import ImportLog


class Command(BaseCommand):
    help = 'Import clients from an Excel or CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Path to the Excel or CSV file with client data'
        )
        parser.add_argument(
            '--update-passwords',
            action='store_true',
            help='Update passwords for existing clients'
        )
        parser.add_argument(
            '--skip-if-exists',
            action='store_true',
            help='Skip import if clients already exist in database'
        )

    def handle(self, *args, **options):
        from apps.accounts.models import Cliente
        
        file_path = options['file_path']
        update_passwords = options['update_passwords']
        skip_if_exists = options['skip_if_exists']

        # Check if we should skip
        if skip_if_exists:
            existing_count = Cliente.objects.count()
            if existing_count > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'Skipping import - {existing_count} clients already exist in database'
                    )
                )
                return

        # Verify file exists
        if not os.path.exists(file_path):
            raise CommandError(f'File does not exist: {file_path}')

        self.stdout.write(f'Starting client import from: {file_path}')

        try:
            # Open file
            with open(file_path, 'rb') as f:
                # Create importer
                opciones = {'actualizar_passwords': update_passwords}
                importer = ClientImporter(f, opciones=opciones)

                # Create import log
                log = ImportLog.objects.create(
                    tipo='clientes',
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
                self.stdout.write('Importing clients...')
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
