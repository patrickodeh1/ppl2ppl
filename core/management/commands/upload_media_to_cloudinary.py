from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from core.models import TrainingModule
import os


class Command(BaseCommand):
    help = 'Upload all media files to Cloudinary'

    def handle(self, *args, **options):
        self.stdout.write('Starting to upload media files to Cloudinary...')
        
        # Get all modules with PDF files
        modules_with_pdfs = TrainingModule.objects.filter(pdf_file__isnull=False).exclude(pdf_file='')
        pdf_count = 0
        
        for module in modules_with_pdfs:
            try:
                if module.pdf_file:
                    # The file will be automatically uploaded to Cloudinary 
                    # when we save it using the Cloudinary storage backend
                    file_path = module.pdf_file.name
                    
                    # Read the file from local storage
                    with open(module.pdf_file.path, 'rb') as f:
                        # Save to Cloudinary
                        cloudinary_path = default_storage.save(file_path, f)
                        module.pdf_file.name = cloudinary_path
                        module.save()
                        
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Uploaded: {module.title} - {file_path}')
                    )
                    pdf_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error uploading {module.title}: {str(e)}')
                )
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully uploaded {pdf_count} PDF files to Cloudinary!'))
