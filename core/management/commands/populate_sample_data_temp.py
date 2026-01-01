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

        # ========== CREATE SAMPLE TRAINING MODULES ==========
        self.stdout.write('Creating training modules...')
        
        # Course 1 modules - Foundations (Text/PDF)
        TrainingModule.objects.create(
            course=course1,
            title='The Mission and Impact',
            description='Understand the core purpose of professional signature gathering and how it empowers direct democracy.',
            content_type='text',
            order=1,
            text_content='''Professional signature gathering is a cornerstone of direct democracy. By collecting valid signatures, you help bring important issues to the ballot, giving citizens a direct voice in their government. Your work ensures that the democratic process remains accessible and responsive to the will of the people.

Key Points:
- Signature gathering empowers communities.
- It is a legal and ethical responsibility.
- Your professionalism directly impacts the success of the initiative.''',
            duration_minutes=8,
            is_required=True,
        )
        
        TrainingModule.objects.create(
            course=course1,
            title='Understanding the Petition Document',
            description='Learn about the legal importance of the petition document and its critical components.',
            content_type='pdf',
            order=2,
            pdf_url='/static/sample_pdfs/petition_document_overview.pdf',
            duration_minutes=10,
            is_required=True,
        )
        
        TrainingModule.objects.create(
            course=course1,
            title='Who Can Sign?',
            description='Master voter eligibility rules and required information collection.',
            content_type='text',
            order=3,
            text_content='''Eligibility Rules:
- Only registered voters in the relevant jurisdiction may sign.
- All required fields must be completed legibly.
- Each signature must be witnessed by the circulator.

Required Information:
- Printed name
- Signature
- Address (must match voter registration)
- County (if required)
- Date''',
            duration_minutes=12,
            is_required=True,
        )

        TrainingModule.objects.create(
            course=course1,
            title='Voter Validation Thresholds',
            description='Critical information about validation rates and payment structure.',
            content_type='text',
            order=4,
            text_content='''
CRITICAL THRESHOLD: VALIDATION AND PAY

We pay for Valid Signatures. We understand errors happen. Your baseline pay rate assumes a minimum validation rate:

• If your submitted sheets validate at 75% or higher, you receive 100% of the agreed rate for all submitted signatures.
• If your sheets validate below 75%, you will only be paid for the signatures that are verified as valid.
• Your focus must be on achieving 90% validity or higher to ensure maximum efficiency and income.

VALIDATION REQUIREMENTS:
• Must be registered voters in the state where the petition is circulating
• Signatures must be legible
• All required information must be complete
• County rules must be followed (all signatures on one sheet from same county)
• Address must match voter registration
            ''',
            duration_minutes=8,
            is_required=True,
