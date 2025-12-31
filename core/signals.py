"""
Django signals for email notifications and other async tasks
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from .models import (
    UserTrainingProgress, AssessmentAttempt, UserCertification, ModuleCompletion
)


@receiver(post_save, sender=UserTrainingProgress)
def send_course_completion_email(sender, instance, created, **kwargs):
    """Send email when user completes a course"""
    if instance.status == 'completed' and instance.completed_at:
        try:
            user = instance.user
            course = instance.course
            
            subject = f'Course Completed: {course.title}'
            
            context = {
                'user_name': user.first_name or user.email,
                'course_title': course.title,
                'completion_date': instance.completed_at.strftime('%B %d, %Y'),
            }
            
            html_message = render_to_string('emails/course_completed.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=True,
            )
        except Exception as e:
            print(f'Error sending course completion email: {e}')


@receiver(post_save, sender=AssessmentAttempt)
def send_assessment_email(sender, instance, created, **kwargs):
    """Send email based on assessment attempt results"""
    if instance.status == 'graded':
        try:
            user = instance.user
            assessment = instance.assessment
            
            if instance.passed:
                subject = f'Assessment Passed: {assessment.title}'
                template = 'emails/assessment_passed.html'
                message_type = 'passed'
            else:
                subject = f'Assessment Failed: {assessment.title}'
                template = 'emails/assessment_failed.html'
                message_type = 'failed'
            
            context = {
                'user_name': user.first_name or user.email,
                'assessment_title': assessment.title,
                'score': instance.score_percentage,
                'passing_score': assessment.passing_score,
                'message_type': message_type,
            }
            
            html_message = render_to_string(template, context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=True,
            )
        except Exception as e:
            print(f'Error sending assessment email: {e}')


@receiver(post_save, sender=UserCertification)
def send_certification_email(sender, instance, created, **kwargs):
    """Send email when user becomes certified"""
    if instance.is_certified and instance.certification_date:
        try:
            user = instance.user
            
            subject = 'Certification Achieved - P2P Solutions'
            
            context = {
                'user_name': user.first_name or user.email,
                'certification_date': instance.certification_date.strftime('%B %d, %Y'),
                'expiration_date': instance.expires_at.strftime('%B %d, %Y') if instance.expires_at else None,
            }
            
            html_message = render_to_string('emails/certification_earned.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=True,
            )
        except Exception as e:
            print(f'Error sending certification email: {e}')


@receiver(post_save, sender=ModuleCompletion)
def send_module_completion_notification(sender, instance, created, **kwargs):
    """Send notification when user completes a module"""
    if instance.is_completed and instance.completed_at:
        try:
            user = instance.user
            module = instance.module
            course = module.course
            
            # Check if this is the last module in the course
            course_modules = course.modules.filter(is_required=True)
            completed_modules = ModuleCompletion.objects.filter(
                user=user,
                module__course=course,
                is_completed=True
            ).count()
            
            # Only send notification for significant milestones
            if completed_modules % 5 == 0 or completed_modules == course_modules.count():
                subject = f'Progress Update: {course.title}'
                
                if completed_modules == course_modules.count():
                    template = 'emails/course_progress_milestone.html'
                    milestone = 'COMPLETE'
                else:
                    template = 'emails/course_progress_milestone.html'
                    milestone = f'{completed_modules}/{course_modules.count()} modules'
                
                context = {
                    'user_name': user.first_name or user.email,
                    'course_title': course.title,
                    'modules_completed': completed_modules,
                    'total_modules': course_modules.count(),
                    'progress_percentage': int((completed_modules / course_modules.count() * 100)),
                    'milestone': milestone,
                }
                
                html_message = render_to_string(template, context)
                plain_message = strip_tags(html_message)
                
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=html_message,
                    fail_silently=True,
                )
        except Exception as e:
            print(f'Error sending module completion notification: {e}')
