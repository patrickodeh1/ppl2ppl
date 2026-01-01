from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import (
    TrainingCourse, TrainingModule, Assessment, AssessmentQuestion, AssessmentOption,
    Office, OfficeHours
)


class Command(BaseCommand):
    help = 'Populate sample data for testing the training module'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate sample data...'))

        # ========== CREATE SAMPLE TRAINING COURSES ==========
        self.stdout.write('Creating training courses...')
        
        course1 = TrainingCourse.objects.create(
            title='Module 1: Foundations & The Legal Landscape',
            description='Master the core purpose of signature gathering, understand the petition document, and learn voter eligibility rules.',
            difficulty='beginner',
            is_mandatory=True,
            order=1,
            estimated_duration_minutes=45,
        )
        
        course2 = TrainingCourse.objects.create(
            title='Module 2: Compliance, Ethics, & Rules',
            description='Learn the golden rules of compliance, ethical engagement practices, and how to avoid invalid signatures.',
            difficulty='intermediate',
            is_mandatory=True,
            order=2,
            estimated_duration_minutes=50,
        )
        
        course3 = TrainingCourse.objects.create(
            title='Module 3: Field Operations & Logistics',
            description='Prepare your circulator kit, understand safety protocols, and master station setup and presentation.',
            difficulty='beginner',
            is_mandatory=True,
            order=3,
            estimated_duration_minutes=40,
        )

        course4 = TrainingCourse.objects.create(
            title='Module 4: The Art of the Pitch & Persuasion',
            description='Master the 15-second hook, learn objection handling, and maximize conversion through signature psychology.',
            difficulty='intermediate',
            is_mandatory=True,
            order=4,
            estimated_duration_minutes=45,
        )

        course5 = TrainingCourse.objects.create(
            title='Module 5: Quality Control & Submission',
            description='Perform quality checks, complete circulator declarations accurately, and follow submission procedures.',
            difficulty='beginner',
            is_mandatory=True,
            order=5,
            estimated_duration_minutes=35,
        )

        course6 = TrainingCourse.objects.create(
            title='Module 6: Team Management & Tech',
            description='Use data and mapping technology, log performance metrics, and troubleshoot common field scenarios.',
            difficulty='intermediate',
            is_mandatory=False,
            order=6,
            estimated_duration_minutes=30,
        )

        self.stdout.write(self.style.SUCCESS(f'✓ Created 6 training courses'))
