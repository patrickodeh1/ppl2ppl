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
            title='Onboarding Fundamentals',
            description='Essential information for new employees including company policies, procedures, and culture.',
            difficulty='beginner',
            is_mandatory=True,
            order=1,
            estimated_duration_minutes=45,
        )
        
        course2 = TrainingCourse.objects.create(
            title='Product Knowledge',
            description='Deep dive into our products, features, and competitive advantages.',
            difficulty='intermediate',
            is_mandatory=True,
            order=2,
            estimated_duration_minutes=60,
        )
        
        course3 = TrainingCourse.objects.create(
            title='Customer Service Excellence',
            description='Best practices for delivering exceptional customer service.',
            difficulty='intermediate',
            is_mandatory=False,
            order=3,
            estimated_duration_minutes=30,
        )

        self.stdout.write(self.style.SUCCESS(f'✓ Created 3 training courses'))

        # ========== CREATE SAMPLE TRAINING MODULES ==========
        self.stdout.write('Creating training modules...')
        
        # Course 1 modules
        TrainingModule.objects.create(
            course=course1,
            title='Welcome to P2P Solutions',
            description='Introduction video and welcome message',
            content_type='video',
            order=1,
            video_url='https://www.youtube.com/embed/dQw4w9WgXcQ',
            duration_minutes=5,
            is_required=True,
        )
        
        TrainingModule.objects.create(
            course=course1,
            title='Company Policies & Procedures',
            description='Complete guide to company policies',
            content_type='pdf',
            order=2,
            pdf_file=None,  # Would be uploaded via admin
            duration_minutes=15,
            is_required=True,
        )
        
        TrainingModule.objects.create(
            course=course1,
            title='Code of Conduct',
            description='Our commitment to ethical business practices',
            content_type='text',
            order=3,
            text_content='''
            Our Code of Conduct outlines the values and principles that guide our business.
            
            Core Principles:
            1. Integrity - We conduct business honestly and ethically
            2. Respect - We respect all individuals and their differences
            3. Excellence - We strive for quality in everything we do
            4. Accountability - We take responsibility for our actions
            
            All employees are expected to uphold these principles.
            ''',
            duration_minutes=10,
            is_required=True,
        )
        
        # Course 2 modules
        TrainingModule.objects.create(
            course=course2,
            title='Product Overview',
            description='High-level overview of all product offerings',
            content_type='video',
            order=1,
            video_url='https://www.youtube.com/embed/9bZkp7q19f0',
            duration_minutes=10,
            is_required=True,
        )
        
        TrainingModule.objects.create(
            course=course2,
            title='Feature Deep Dive',
            description='Detailed walkthrough of key features',
            content_type='text',
            order=2,
            text_content='''
            Our products include:
            
            Platform Features:
            - Real-time analytics dashboard
            - Multi-user collaboration tools
            - Advanced reporting capabilities
            - API integration support
            
            Security Features:
            - End-to-end encryption
            - Role-based access control
            - Audit logging
            - Compliance certifications
            ''',
            duration_minutes=15,
            is_required=True,
        )
        
        TrainingModule.objects.create(
            course=course2,
            title='Competitive Advantages',
            description='Why our products stand out',
            content_type='mixed',
            order=3,
            video_url='https://www.youtube.com/embed/5XeFesPBDbE',
            text_content='Our unique value propositions set us apart from competitors.',
            duration_minutes=20,
            is_required=True,
        )

        self.stdout.write(self.style.SUCCESS(f'✓ Created 6 training modules'))

        # ========== CREATE SAMPLE ASSESSMENT ==========
        self.stdout.write('Creating assessment...')
        
        assessment = Assessment.objects.create(
            title='Onboarding Certification Assessment',
            description='Comprehensive assessment to verify understanding of onboarding material.',
            total_questions=10,
            passing_score=85,
            randomize_questions=True,
            randomize_options=True,
            time_limit_minutes=15,
            is_mandatory=True,
        )

        self.stdout.write(self.style.SUCCESS(f'✓ Created assessment'))

        # ========== CREATE ASSESSMENT QUESTIONS & OPTIONS ==========
        self.stdout.write('Creating assessment questions...')
        
        questions_data = [
            {
                'question': 'What is our primary commitment to customers?',
                'difficulty': 'easy',
                'explanation': 'Excellence and integrity are our core values that drive customer satisfaction.',
                'options': [
                    ('Providing the lowest prices', False),
                    ('Delivering excellence with integrity', True),
                    ('Having the most employees', False),
                    ('Operating in the most locations', False),
                ]
            },
            {
                'question': 'Which of the following is NOT mentioned in our Code of Conduct?',
                'difficulty': 'medium',
                'explanation': 'The Code of Conduct emphasizes: Integrity, Respect, Excellence, and Accountability.',
                'options': [
                    ('Integrity', False),
                    ('Respect', False),
                    ('Accountability', False),
                    ('Maximizing profit at any cost', True),
                ]
            },
            {
                'question': 'What is a key security feature of our platform?',
                'difficulty': 'easy',
                'explanation': 'End-to-end encryption is a fundamental security feature.',
                'options': [
                    ('End-to-end encryption', True),
                    ('No user authentication', False),
                    ('Cloud storage only', False),
                    ('Manual backups', False),
                ]
            },
            {
                'question': 'How many core principles are in our Code of Conduct?',
                'difficulty': 'medium',
                'explanation': 'The four core principles are: Integrity, Respect, Excellence, and Accountability.',
                'options': [
                    ('2', False),
                    ('3', False),
                    ('4', True),
                    ('5', False),
                ]
            },
            {
                'question': 'What does RBAC stand for?',
                'difficulty': 'hard',
                'explanation': 'RBAC stands for Role-Based Access Control, a security feature of our platform.',
                'options': [
                    ('Random Backup Access Control', False),
                    ('Role-Based Access Control', True),
                    ('Rapid Batch Analysis Code', False),
                    ('Real-time Business Analytics Core', False),
                ]
            },
            {
                'question': 'Which team should you contact for product questions?',
                'difficulty': 'easy',
                'explanation': 'During onboarding, familiarize yourself with department contacts.',
                'options': [
                    ('Marketing only', False),
                    ('Engineering only', False),
                    ('Your direct manager or product team', True),
                    ('CEO directly', False),
                ]
            },
            {
                'question': 'What is the recommended frequency for security compliance reviews?',
                'difficulty': 'hard',
                'explanation': 'Regular compliance reviews ensure adherence to security standards.',
                'options': [
                    ('Never needed', False),
                    ('Only when required by law', False),
                    ('Quarterly at minimum', True),
                    ('Once every 5 years', False),
                ]
            },
            {
                'question': 'Which feature enables real-time collaboration?',
                'difficulty': 'medium',
                'explanation': 'Multi-user collaboration tools allow teams to work together in real-time.',
                'options': [
                    ('Email only', False),
                    ('Multi-user collaboration tools', True),
                    ('Scheduled meetings', False),
                    ('Document sharing twice daily', False),
                ]
            },
            {
                'question': 'What is the foundation of ethical business practice?',
                'difficulty': 'easy',
                'explanation': 'Integrity is the foundation of all ethical business practices.',
                'options': [
                    ('Profit maximization', False),
                    ('Speed of execution', False),
                    ('Integrity', True),
                    ('Market dominance', False),
                ]
            },
            {
                'question': 'Which of the following is a compliance certification we maintain?',
                'difficulty': 'hard',
                'explanation': 'We maintain multiple compliance certifications as listed on our security page.',
                'options': [
                    ('ISO 27001', True),
                    ('None required', False),
                    ('Internal only', False),
                    ('Voluntary only', False),
                ]
            },
        ]

        for i, q_data in enumerate(questions_data, 1):
            question = AssessmentQuestion.objects.create(
                assessment=assessment,
                question_text=q_data['question'],
                difficulty=q_data['difficulty'],
                explanation=q_data['explanation'],
                order=i,
            )
            
            for j, (option_text, is_correct) in enumerate(q_data['options'], 1):
                AssessmentOption.objects.create(
                    question=question,
                    option_text=option_text,
                    is_correct=is_correct,
                    order=j,
                )

        self.stdout.write(self.style.SUCCESS(f'✓ Created 10 assessment questions with options'))

        # ========== CREATE SAMPLE OFFICES ==========
        self.stdout.write('Creating office locations...')
        
        office1 = Office.objects.create(
            name='New York Headquarters',
            address='123 Broadway',
            city='New York',
            state='NY',
            postal_code='10001',
            country='USA',
            timezone='America/New_York',
            phone='+1-212-555-0001',
            email='newyork@p2p.com',
            order=1,
        )
        
        office2 = Office.objects.create(
            name='San Francisco Office',
            address='456 Market Street',
            city='San Francisco',
            state='CA',
            postal_code='94102',
            country='USA',
            timezone='America/Los_Angeles',
            phone='+1-415-555-0002',
            email='sanfrancisco@p2p.com',
            order=2,
        )
        
        office3 = Office.objects.create(
            name='Chicago Regional Office',
            address='789 Michigan Avenue',
            city='Chicago',
            state='IL',
            postal_code='60611',
            country='USA',
            timezone='America/Chicago',
            phone='+1-312-555-0003',
            email='chicago@p2p.com',
            order=3,
        )

        self.stdout.write(self.style.SUCCESS(f'✓ Created 3 office locations'))

        # ========== CREATE OFFICE HOURS ==========
        self.stdout.write('Creating office hours...')
        
        # NYC Hours: Mon-Fri 9AM-6PM, Sat 10AM-3PM, Sun Closed
        for office in [office1, office2, office3]:
            for day in range(5):  # Mon-Fri
                OfficeHours.objects.create(
                    office=office,
                    day_of_week=day,
                    is_open=True,
                    opening_time='09:00',
                    closing_time='18:00',
                )
            # Saturday
            OfficeHours.objects.create(
                office=office,
                day_of_week=5,
                is_open=True,
                opening_time='10:00',
                closing_time='15:00',
            )
            # Sunday
            OfficeHours.objects.create(
                office=office,
                day_of_week=6,
                is_open=False,
            )

        self.stdout.write(self.style.SUCCESS(f'✓ Created office hours for all locations'))

        self.stdout.write(self.style.SUCCESS(
            '\n✅ Sample data populated successfully!\n'
            'You can now:\n'
            '1. Login and access the training module\n'
            '2. Complete training courses\n'
            '3. Take the assessment (aim for 85%+ to pass)\n'
            '4. View office locations and hours\n'
        ))
