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
        
        # Course 1 modules - Foundations
        TrainingModule.objects.create(
            course=course1,
            title='Video 1.1: The Mission and Impact',
            description='Understand the core purpose of professional signature gathering and how it empowers direct democracy.',
            content_type='video',
            order=1,
            video_url='https://www.youtube.com/embed/dQw4w9WgXcQ',
            duration_minutes=8,
            is_required=True,
        )
        
        TrainingModule.objects.create(
            course=course1,
            title='Video 1.2: Understanding the Petition Document',
            description='Learn about the legal importance of the petition document and its critical components.',
            content_type='video',
            order=2,
            video_url='https://www.youtube.com/embed/9bZkp7q19f0',
            duration_minutes=10,
            is_required=True,
        )
        
        TrainingModule.objects.create(
            course=course1,
            title='Video 1.3: Who Can Sign?',
            description='Master voter eligibility rules and required information collection.',
            content_type='video',
            order=3,
            video_url='https://www.youtube.com/embed/5XeFesPBDbE',
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
        )
        
        # Course 2 modules - Compliance
        TrainingModule.objects.create(
            course=course2,
            title='Video 2.1: The Golden Rules of Compliance',
            description='Learn the non-negotiable rules that must be followed to maintain compliance.',
            content_type='video',
            order=1,
            video_url='https://www.youtube.com/embed/dQw4w9WgXcQ',
            duration_minutes=12,
            is_required=True,
        )
        
        TrainingModule.objects.create(
            course=course2,
            title='Golden Rules Summary',
            description='Critical compliance rules and their consequences.',
            content_type='text',
            order=2,
            text_content='''
THE GOLDEN RULES OF COMPLIANCE

You are an independent contractor, NOT an employee.

RULE 1: No Payment/Gifts
- NEVER pay, give cash, or offer anything of value in exchange for a signature
- Consequence: Immediate termination and potential criminal prosecution

RULE 2: No Falsification
- You must personally witness every signature
- You cannot sign for someone else
- You cannot complete missing information for others
- You cannot have a non-Circulator collect signatures on your behalf
- Consequence: Zero-Tolerance Policy - this is voter fraud, punishable by law

RULE 3: Accuracy of Declaration
- Start date must be the date of the FIRST signature
- End date must be the date you COMPLETE and sign the form
- Consequence: Invalidates the entire sheet and may lead to prosecution
            ''',
            duration_minutes=10,
            is_required=True,
        )
        
        TrainingModule.objects.create(
            course=course2,
            title='Video 2.2: Ethical Engagement',
            description='Master ethical engagement and de-escalation techniques.',
            content_type='video',
            order=3,
            video_url='https://www.youtube.com/embed/9bZkp7q19f0',
            duration_minutes=10,
            is_required=True,
        )
        
        TrainingModule.objects.create(
            course=course2,
            title='Video 2.3: Avoiding Invalid Signatures',
            description='Learn how to catch and prevent the most common invalidation issues.',
            content_type='video',
            order=4,
            video_url='https://www.youtube.com/embed/5XeFesPBDbE',
            duration_minutes=12,
            is_required=True,
        )

        TrainingModule.objects.create(
            course=course2,
            title='Signature Validation Checklist',
            description='Step-by-step guide to checking signatures for validity.',
            content_type='text',
            order=5,
            text_content='''
AVOIDING INVALID SIGNATURES

The highest rate of invalidation comes from legibility and completeness.

IMMEDIATE REVIEW PROCESS:
• Check every signature IMMEDIATELY after it's completed
• Guide the voter through the process
• Watch them sign and check the fields BEFORE they leave

THE ADDRESS MATCH (Critical):
• The address they write MUST exactly match the address where they are registered to vote
• If it doesn't match: INVALID SIGNATURE
• If handwriting is illegible ("The Fatal Flaw"): INVALID SIGNATURE

CORRECTION PROCESS:
• You can ONLY ask the voter to correct errors WHILE they are in your presence
• You CANNOT make any correction yourself
• Only the signer can correct their own error

REQUIRED FIELDS TO CHECK:
✓ Printed Name (First and Last) - Must be legible
✓ Signature - Must be legible and match registration
✓ Address - Must exactly match voter registration address
✓ Zip Code - Must be complete and correct
            ''',
            duration_minutes=9,
            is_required=True,
        )
        
        # Course 3 modules - Field Operations
        TrainingModule.objects.create(
            course=course3,
            title='Video 3.1: Preparation - Gear and Paperwork',
            description='Learn what to bring and how to organize your circulator kit.',
            content_type='video',
            order=1,
            video_url='https://www.youtube.com/embed/dQw4w9WgXcQ',
            duration_minutes=10,
            is_required=True,
        )

        TrainingModule.objects.create(
            course=course3,
            title='Circulator Kit Checklist',
            description='Complete list of essential items for fieldwork.',
            content_type='text',
            order=2,
            text_content='''
YOUR CIRCULATOR KIT (Mobile Office)

Essential Items:
✓ Sturdy Board (Clipboard or foam board) - for writing support
✓ Black Ink Pens - Black ink ONLY is acceptable on official documents
✓ Official Petition Documents - All sheets clearly marked for the correct county
✓ Donor Page - Available if requested by voters
✓ Voter Registration Cards - If you plan to register new voters
✓ Daily Tracking Log - Digital or paper to log your progress

ORGANIZATION TIPS:
• Keep your area clean and organized
• Keep drinks and non-essential items AWAY from the signing table
• Have petitions secured and ready
• The easiest way to get a signature is to physically hand the petition and pen to the person
• Do NOT make them walk to a table to find materials
            ''',
            duration_minutes=8,
            is_required=True,
        )

        TrainingModule.objects.create(
            course=course3,
            title='Video 3.2: Safety and Professionalism',
            description='Master public interaction, authority engagement, and professional behavior.',
            content_type='video',
            order=3,
            video_url='https://www.youtube.com/embed/9bZkp7q19f0',
            duration_minutes=10,
            is_required=True,
        )

        TrainingModule.objects.create(
            course=course3,
            title='Video 3.3: Setting Up Your Station',
            description='Learn optimal presentation and station setup for maximum conversions.',
            content_type='video',
            order=4,
            video_url='https://www.youtube.com/embed/5XeFesPBDbE',
            duration_minutes=8,
            is_required=True,
        )
        
        # Course 4 modules - Pitch & Persuasion
        TrainingModule.objects.create(
            course=course4,
            title='Video 4.1: The 15-Second Hook',
            description='Master the initial contact and transition to the ask.',
            content_type='video',
            order=1,
            video_url='https://www.youtube.com/embed/dQw4w9WgXcQ',
            duration_minutes=12,
            is_required=True,
        )

        TrainingModule.objects.create(
            course=course4,
            title='The Perfect Pitch',
            description='The exact words and techniques to use when approaching voters.',
            content_type='text',
            order=2,
            text_content='''
THE 15-SECOND HOOK (Initial Contact)

Your goal: Transition immediately from greeting to the ask.

KEY PRINCIPLE: The number one reason people sign is because YOU ASK THEM TO.

THE PERFECT ASK:
"Hi there! Are you a registered voter in [County Name]? Great, we're trying to get a few different measures onto the ballot for November so Californians can have their say. Mind signing for us? It only takes a minute."

KEY ELEMENTS:
✓ Start with a qualification question (registered voter + location)
✓ Explain the process in simple terms
✓ Focus on the democratic process, not the issue
✓ Emphasize it only takes a minute
✓ Make the ask confidently and directly

CRITICAL REMINDER:
Emphasize that they are NOT voting today, just ensuring the measures are put before the people.
            ''',
            duration_minutes=8,
            is_required=True,
        )

        TrainingModule.objects.create(
            course=course4,
            title='Video 4.2: Handling Objections',
            description='Learn proven responses to common objections.',
            content_type='video',
            order=3,
            video_url='https://www.youtube.com/embed/9bZkp7q19f0',
            duration_minutes=12,
            is_required=True,
        )

        TrainingModule.objects.create(
            course=course4,
            title='Objection Handling Guide',
            description='Detailed responses to overcome common objections.',
            content_type='text',
            order=4,
            text_content='''
HANDLING OBJECTIONS

Objection 1: "I don't have time."
Response: "I totally understand. It only takes about 3 minutes for all of these. We only do this once every couple of years—can you spare the minute?"
Technique: Dispute the time - challenge the excuse with a specific, small ask

Objection 2: "I already signed it."
Response: "No problem! Which one did you sign? Was it the [Color] one or the [Topic] one? We have a couple—if you can just confirm which ones you didn't sign, I'd really appreciate the help."
Technique: Verification - don't let them off the hook immediately; they usually don't know what they signed

Objection 3: "I don't know enough about it."
Response: "That's why we're just getting it on the ballot! You don't have to know anything right now, just sign to give yourself the right to research it later and vote. You can do the research once you get your voter packet."
Technique: Remove the barrier - separate the act of signing from the responsibility of voting

Objection 4: "I'm not interested."
Response: "I hear you, and no problem. Have a great day!"
Technique: Polite Exit - don't waste valuable time and energy on a hard no
            ''',
            duration_minutes=9,
            is_required=True,
        )

        TrainingModule.objects.create(
            course=course4,
            title='Video 4.3: Maximizing Conversion',
            description='Learn signature psychology and crowd-building techniques.',
            content_type='video',
            order=5,
            video_url='https://www.youtube.com/embed/5XeFesPBDbE',
            duration_minutes=10,
            is_required=True,
        )

        TrainingModule.objects.create(
            course=course4,
            title='Signature Psychology',
            description='Advanced techniques to maximize conversion rates.',
            content_type='text',
            order=6,
            text_content='''
MAXIMIZING CONVERSION (Signature Psychology)

BUILD THE CROWD:
The best time to get signatures is when OTHER PEOPLE are signing.
• When you have one person signing, IMMEDIATELY engage the next person
• Create a small audience or "micro-crowd"
• People are MORE LIKELY to participate if they see others doing it

THE COMMITMENT TECHNIQUE:
Get small "yeses" first before the big ask:
1. "It's a beautiful day, isn't it?" (Yes)
2. "You believe in the right to vote, right?" (Yes)
3. Now: "Can you just help me with these signatures?" (Much higher conversion!)

PSYCHOLOGICAL PRINCIPLES:
• Social Proof: People follow what others are doing
• Consistency: Once they commit to small things, they're more likely to commit to bigger asks
• Reciprocity: When you help them (nice weather comment), they feel obligated to help you
            ''',
            duration_minutes=8,
            is_required=True,
        )
        
        # Course 5 modules - Quality Control
        TrainingModule.objects.create(
            course=course5,
            title='Video 5.1: The Quality Check Process',
            description='Master the immediate review and correction process.',
            content_type='video',
            order=1,
            video_url='https://www.youtube.com/embed/dQw4w9WgXcQ',
            duration_minutes=10,
            is_required=True,
        )

        TrainingModule.objects.create(
            course=course5,
            title='Quality Control Procedures',
            description='Step-by-step quality check and submission procedures.',
            content_type='text',
            order=2,
            text_content='''
QUALITY CONTROL & SUBMISSION

IMMEDIATE REVIEW PROCESS:
✓ Check every signature AFTER it's completed
✓ Review for legibility and completeness of ALL required fields
✓ Only the signer can correct their own error
✓ Politely ask them to re-write any unclear numbers or letters
✓ Complete your tracking log accurately

END-OF-DAY WRAP-UP CHECKLIST:
□ Security: Safeguard all completed petitions (legal documents with private voter information)
□ Circulator Declaration: Fill out accurately on EVERY sheet
□ Start Date: The date of the FIRST signature on that sheet
□ End Date: The date you COMPLETE and sign the form
□ Verification: Double-check county rules compliance
□ Submission: Follow official hand-off or drop-off procedure immediately

CRITICAL REMINDERS:
• These are LEGAL DOCUMENTS containing private voter information
• Never leave petitions unattended
• Follow exact submission procedures for your supervisor
• Ensure voter registrations are processed quickly
• Maintain chain of custody for all documents
            ''',
            duration_minutes=9,
            is_required=True,
        )

        TrainingModule.objects.create(
            course=course5,
            title='Video 5.2: End-of-Day Wrap-Up',
            description='Complete guide to securing and submitting your work.',
            content_type='video',
            order=3,
            video_url='https://www.youtube.com/embed/9bZkp7q19f0',
            duration_minutes=10,
            is_required=True,
        )
        
        # Course 6 modules - Team Management & Tech
        TrainingModule.objects.create(
            course=course6,
            title='Video 6.1: Using Data and Mapping Technology',
            description='Learn how to use tools to optimize your routes and performance.',
            content_type='video',
            order=1,
            video_url='https://www.youtube.com/embed/dQw4w9WgXcQ',
            duration_minutes=12,
            is_required=True,
        )

        TrainingModule.objects.create(
            course=course6,
            title='Video 6.2: Troubleshooting Common Scenarios',
            description='How to handle lost documents, difficult situations, and emergency procedures.',
            content_type='video',
            order=2,
            video_url='https://www.youtube.com/embed/9bZkp7q19f0',
            duration_minutes=12,
            is_required=True,
        )

        self.stdout.write(self.style.SUCCESS(f'✓ Created 28 training modules across 6 courses'))

        # ========== CREATE COMPREHENSIVE ASSESSMENT ==========
        self.stdout.write('Creating assessment...')
        
        assessment = Assessment.objects.create(
            title='Professional Signature Gathering Certification Assessment',
            description='Comprehensive assessment covering all modules of the Professional Signature Gathering Training Manual. You must score 85% or higher to become certified.',
            total_questions=20,
            passing_score=85,
            randomize_questions=True,
            randomize_options=True,
            time_limit_minutes=30,
            is_mandatory=True,
        )

        self.stdout.write(self.style.SUCCESS(f'✓ Created assessment'))

        # ========== CREATE ASSESSMENT QUESTIONS & OPTIONS ==========
        self.stdout.write('Creating assessment questions...')
        
        questions_data = [
            {
                'question': 'What is the core purpose of professional signature gathering?',
                'difficulty': 'easy',
                'explanation': 'Professional signature gathering empowers people through Direct Democracy by securing verifiable signatures.',
                'options': [
                    ('To register voters for a political party', False),
                    ('To empower people through Direct Democracy', True),
                    ('To sell products to voters', False),
                    ('To collect personal information', False),
                ]
            },
            {
                'question': 'You are an independent contractor. What does this mean legally?',
                'difficulty': 'medium',
                'explanation': 'As an independent contractor, you are NOT an employee and operate independently.',
                'options': [
                    ('You work full-time for P2P Solutions', False),
                    ('You are NOT an employee and operate independently', True),
                    ('You receive employee benefits', False),
                    ('You must work set hours', False),
                ]
            },
            {
                'question': 'What is the minimum validation rate to receive 100% of your agreed pay rate?',
                'difficulty': 'medium',
                'explanation': 'You must achieve 75% or higher validation to receive 100% of the agreed rate for all submitted signatures.',
                'options': [
                    ('50%', False),
                    ('65%', False),
                    ('75%', True),
                    ('85%', False),
                ]
            },
            {
                'question': 'What is the CRITICAL FATAL FLAW that invalidates a signature?',
                'difficulty': 'hard',
                'explanation': 'Illegible handwriting (not matching registration) is the fatal flaw that invalidates signatures.',
                'options': [
                    ('Incorrect zip code', False),
                    ('Illegible handwriting or address not matching registration', True),
                    ('Signed in blue ink', False),
                    ('Signed on the wrong line', False),
                ]
            },
            {
                'question': 'Can you pay a voter for their signature or offer them a gift?',
                'difficulty': 'easy',
                'explanation': 'NEVER pay, give cash, or offer anything of value in exchange for a signature. This is an immediate termination offense.',
                'options': [
                    ('Yes, if it\'s under $5', False),
                    ('Yes, a small gift is acceptable', False),
                    ('No, absolutely never', True),
                    ('Only if they ask first', False),
                ]
            },
            {
                'question': 'Can you sign for a voter or complete missing information on their behalf?',
                'difficulty': 'easy',
                'explanation': 'No. You must personally witness every signature. Falsification is voter fraud and a zero-tolerance offense.',
                'options': [
                    ('Yes, as long as you do it neatly', False),
                    ('Yes, if they ask you to help', False),
                    ('No, absolutely never - this is voter fraud', True),
                    ('Only for elderly voters', False),
                ]
            },
            {
                'question': 'What date should the START DATE on your Circulator Declaration be?',
                'difficulty': 'hard',
                'explanation': 'The start date must be the date of the FIRST signature on that sheet.',
                'options': [
                    ('The date you started circulating ever', False),
                    ('The date of the first signature on THAT SHEET', True),
                    ('The first day of the month', False),
                    ('The date you submitted the petition', False),
                ]
            },
            {
                'question': 'All signatures on a single petition sheet must be from which group?',
                'difficulty': 'medium',
                'explanation': 'All signatures on one petition sheet MUST be from voters registered in the same county.',
                'options': [
                    ('The same city', False),
                    ('The same zip code', False),
                    ('The same county', True),
                    ('The same state', False),
                ]
            },
            {
                'question': 'When can you correct a voter\'s error on their signature sheet?',
                'difficulty': 'hard',
                'explanation': 'You can ONLY ask the voter to correct errors WHILE they are in your presence. You cannot make corrections yourself.',
                'options': [
                    ('After they leave', False),
                    ('While they are in your presence - they must correct it', True),
                    ('You can correct it yourself if needed', False),
                    ('Never - just submit it as is', False),
                ]
            },
            {
                'question': 'What is the primary reason people sign a petition?',
                'difficulty': 'easy',
                'explanation': 'The number one reason people sign is simply because you ASK them to.',
                'options': [
                    ('They fully understand the issue', False),
                    ('Because you ask them to', True),
                    ('Because they see your sign', False),
                    ('Because a crowd is gathering', False),
                ]
            },
            {
                'question': 'What should you emphasize when asking for a signature?',
                'difficulty': 'medium',
                'explanation': 'Emphasize that voters are NOT voting today, just ensuring measures are put before the people.',
                'options': [
                    ('Your political opinion on the issue', False),
                    ('That they must vote yes on the measure', False),
                    ('That they are giving the right to research and vote later', True),
                    ('That the issue is very urgent', False),
                ]
            },
            {
                'question': 'How should you respond to "I don\'t have time"?',
                'difficulty': 'medium',
                'explanation': 'Challenge the time excuse with a specific, small ask: "It only takes about 3 minutes."',
                'options': [
                    ('Agree and move to the next person', False),
                    ('Dispute the time - "It only takes about 3 minutes. We only do this once every couple of years."', True),
                    ('Leave and come back later', False),
                    ('Argue that they do have time', False),
                ]
            },
            {
                'question': 'When is the BEST time to get signatures?',
                'difficulty': 'medium',
                'explanation': 'The best time is when other people are signing - build the crowd (micro-crowd effect).',
                'options': [
                    ('Early morning', False),
                    ('Late afternoon', False),
                    ('When other people are already signing', True),
                    ('During lunch rush', False),
                ]
            },
            {
                'question': 'What is the Commitment Technique?',
                'difficulty': 'hard',
                'explanation': 'Get small "yeses" first ("Is it a beautiful day?") before making the big ask for signatures.',
                'options': [
                    ('Ask them to sign immediately', False),
                    ('Get small "yeses" first before the big ask', True),
                    ('Promise them something valuable', False),
                    ('Build a crowd before asking', False),
                ]
            },
            {
                'question': 'What is the correct composition of your Circulator Kit?',
                'difficulty': 'medium',
                'explanation': 'You must have: sturdy board, BLACK ink pens only, official petition documents, donor page, and tracking log.',
                'options': [
                    ('Clipboard, any color ink pens, petitions, tablet', False),
                    ('Board, black ink pens, petitions, donor page, tracking log', True),
                    ('Just the petitions and a pen', False),
                    ('Clipboard and any supplies you have', False),
                ]
            },
            {
                'question': 'What color ink is acceptable on official petition documents?',
                'difficulty': 'easy',
                'explanation': 'Black ink ONLY is acceptable on official documents.',
                'options': [
                    ('Any color', False),
                    ('Blue or black', False),
                    ('Black ink only', True),
                    ('Blue ink only', False),
                ]
            },
            {
                'question': 'If a store manager tells you to leave, what should you do?',
                'difficulty': 'medium',
                'explanation': 'You must respectfully leave immediately and call your supervisor. Do not engage in a rights conflict.',
                'options': [
                    ('Argue your right to be there', False),
                    ('Respectfully leave and call your supervisor', True),
                    ('Continue your work in the parking lot', False),
                    ('Ask for the manager\'s manager', False),
                ]
            },
            {
                'question': 'What must you do before a voter leaves after signing?',
                'difficulty': 'hard',
                'explanation': 'You must CHECK every signature immediately for legibility and completeness of all required fields.',
                'options': [
                    ('Thank them and let them go', False),
                    ('Check the signature for legibility and complete fields BEFORE they leave', True),
                    ('Check it later when you\'re back at the office', False),
                    ('Trust that they filled it out correctly', False),
                ]
            },
            {
                'question': 'What information must each voter provide to have a VALID signature?',
                'difficulty': 'hard',
                'explanation': 'Printed name, signature, address where registered to vote (exact match), and zip code.',
                'options': [
                    ('Name and signature only', False),
                    ('Name, signature, phone number, and address', False),
                    ('Printed name, signature, registered address (exact match), zip code', True),
                    ('Just a signature is enough', False),
                ]
            },
            {
                'question': 'How should you handle a voter who says "I\'m not interested"?',
                'difficulty': 'easy',
                'explanation': 'Politely exit: "I hear you, and no problem. Have a great day!" Don\'t waste time on hard nos.',
                'options': [
                    ('Keep pushing them', False),
                    ('Argue why they should sign', False),
                    ('Politely say "Have a great day!" and move on', True),
                    ('Give them your number to call later', False),
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

        self.stdout.write(self.style.SUCCESS(f'✓ Created 20 assessment questions with options'))

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
