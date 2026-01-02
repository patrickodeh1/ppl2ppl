from django.core.management.base import BaseCommand
from core.models import TrainingModule
import os
from dotenv import load_dotenv
import cloudinary
from cloudinary import uploader
import glob

load_dotenv()


class Command(BaseCommand):
    help = 'Upload all PDF files to Cloudinary'

    def handle(self, *args, **options):
        # Configure cloudinary
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET'),
        )
        
        self.stdout.write('Uploading all PDFs to Cloudinary...')
        
        # Get all modules with PDF files
        modules = TrainingModule.objects.filter(pdf_file__isnull=False).exclude(pdf_file='')
        upload_count = 0
        
        for module in modules:
            if module.pdf_file:
                file_path = module.pdf_file.name
                local_file = os.path.join('/home/soarer/freelance/ppl/ppl2ppl/media', file_path)
                
                if os.path.exists(local_file):
                    try:
                        # Upload to Cloudinary
                        result = uploader.upload(
                            local_file,
                            public_id=f"training/pdfs/modules/{module.id}/{module.slug}",
                            resource_type='raw',
                            overwrite=True
                        )
                        
                        # Update module with Cloudinary URL
                        module.pdf_file.name = f"cloudinary/{module.id}/{module.slug}.pdf"
                        module.save()
                        
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ {module.title}')
                        )
                        upload_count += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'✗ {module.title}: {str(e)}')
                        )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠ File not found: {file_path}')
                    )
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully uploaded {upload_count} PDFs to Cloudinary!'))
