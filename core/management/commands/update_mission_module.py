from django.core.management.base import BaseCommand
from core.models import TrainingCourse, TrainingModule


class Command(BaseCommand):
    help = 'Update the first module with mission content'

    def handle(self, *args, **options):
        # Get the first course
        course = TrainingCourse.objects.filter(order=1).first()
        if not course:
            self.stdout.write(self.style.ERROR('No course with order 1 found'))
            return
        
        # Get the first module
        module = course.modules.filter(order=1).first()
        if not module:
            self.stdout.write(self.style.ERROR('No module with order 1 found in course'))
            return
        
        # Update module with mission content
        mission_content = """
<h2>Understanding the Core Mission and Your Role</h2>

<p>The core mission of professional signature gathering is to <strong>empower the people through Direct Democracy</strong>. Our work secures verifiable signatures to place initiatives and referenda onto the public ballot.</p>

<h3>Mission Outcomes:</h3>
<ul>
    <li><strong>To Make a Law (Initiatives)</strong></li>
    <li><strong>To Amend a Law (Constitutional Amendments)</strong></li>
    <li><strong>To Repeal a Law (Referenda)</strong></li>
</ul>

<p>Your role as a Circulator is critical: you are responsible for securing <strong>Verifiable Signatures</strong> that enable citizens to vote on these important measures. The Petition Document itself is a <strong>legal instrument</strong> that must be treated with the utmost care and respect for its integrity.</p>

<h3>Key Responsibilities:</h3>
<ul>
    <li>Gather authentic, verifiable signatures from eligible voters</li>
    <li>Maintain the integrity of petition documents at all times</li>
    <li>Follow all compliance and legal requirements</li>
    <li>Represent the mission with professionalism and dedication</li>
    <li>Ensure all information collected is accurate and verifiable</li>
</ul>

<p>As a member of our team, you are the face of direct democracy. Every interaction represents our commitment to this important mission. Your work directly impacts citizens' ability to participate in the democratic process.</p>
"""
        
        module.title = 'Understanding the Core Mission and Your Role'
        module.description = 'Learn the core purpose of signature gathering and understand your critical role as a circulator in enabling direct democracy.'
        module.content_type = 'text'
        module.text_content = mission_content
        module.duration_minutes = 10
        module.save()
        
        self.stdout.write(self.style.SUCCESS(f'✓ Updated module: {module.title}'))
