"""
Management command to migrate PDFs from Cloudinary to Railway S3-compatible storage.
"""
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from core.models import TrainingModule


class Command(BaseCommand):
    help = 'Migrate PDF files from Cloudinary to Railway S3 storage'

    def handle(self, *args, **options):
        modules = TrainingModule.objects.exclude(pdf_file='')
        
        self.stdout.write(f"Found {modules.count()} modules with PDFs to migrate.\n")
        
        success_count = 0
        error_count = 0
        
        for module in modules:
            old_url = module.pdf_file.name
            
            # Skip if not a Cloudinary URL
            if not old_url.startswith('http'):
                self.stdout.write(f"  Skipping {module.title} - not a URL")
                continue
            
            if 'cloudinary' not in old_url:
                self.stdout.write(f"  Skipping {module.title} - not from Cloudinary")
                continue
            
            self.stdout.write(f"Migrating: {module.title}")
            self.stdout.write(f"  From: {old_url}")
            
            try:
                # Download the PDF from Cloudinary
                response = requests.get(old_url, timeout=30)
                response.raise_for_status()
                
                # Extract filename from URL
                filename = old_url.split('/')[-1]
                if not filename.endswith('.pdf'):
                    filename += '.pdf'
                
                # Create a new file and save it (this will upload to Railway S3)
                content = ContentFile(response.content)
                
                # Clear the old value and save the new file
                module.pdf_file.delete(save=False)
                module.pdf_file.save(filename, content, save=True)
                
                self.stdout.write(self.style.SUCCESS(f"  To: {module.pdf_file.name}"))
                success_count += 1
                
            except requests.RequestException as e:
                self.stdout.write(self.style.ERROR(f"  Error downloading: {e}"))
                error_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Error saving: {e}"))
                error_count += 1
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS(f"Successfully migrated: {success_count}"))
        if error_count:
            self.stdout.write(self.style.ERROR(f"Errors: {error_count}"))
