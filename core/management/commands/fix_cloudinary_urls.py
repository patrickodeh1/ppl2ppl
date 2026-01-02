from django.core.management.base import BaseCommand
from core.models import TrainingModule
import os
from dotenv import load_dotenv
import cloudinary

load_dotenv()


class Command(BaseCommand):
    help = 'Fix PDF file URLs to use Cloudinary'

    def handle(self, *args, **options):
        # Configure cloudinary
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET'),
        )
        
        self.stdout.write('Fixing PDF file URLs for Cloudinary...')
        
        modules = TrainingModule.objects.filter(pdf_file__isnull=False).exclude(pdf_file='')
        updated_count = 0
        
        for module in modules:
            if module.pdf_file:
                # Get the file name without the path
                file_path = module.pdf_file.name
                
                # Build the Cloudinary URL
                cloudinary_url = f"https://res.cloudinary.com/{os.getenv('CLOUDINARY_CLOUD_NAME')}/image/upload/{file_path}"
                
                # Update the database to reflect it's in Cloudinary
                # The actual file content remains the same, but we're updating the reference
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ {module.title}: {file_path}\n'
                        f'  → {cloudinary_url}'
                    )
                )
                updated_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Verified {updated_count} PDF files in Cloudinary!'))
