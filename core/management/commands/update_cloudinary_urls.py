from django.core.management.base import BaseCommand
from core.models import TrainingModule
import os
from dotenv import load_dotenv

load_dotenv()


class Command(BaseCommand):
    help = 'Update PDF file references to Cloudinary URLs'

    def handle(self, *args, **options):
        self.stdout.write('Updating PDF file references to Cloudinary...')
        
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        cloudinary_base = f'https://res.cloudinary.com/{cloud_name}/raw/upload/'
        
        modules = TrainingModule.objects.filter(pdf_file__isnull=False).exclude(pdf_file='')
        updated_count = 0
        
        for module in modules:
            if module.pdf_file and module.pdf_file.name:
                old_path = module.pdf_file.name
                
                # Update to Cloudinary URL
                module.pdf_file.name = f"{cloudinary_base}{old_path}.pdf"
                module.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {module.title}')
                )
                updated_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Updated {updated_count} PDF file references to Cloudinary!'))
