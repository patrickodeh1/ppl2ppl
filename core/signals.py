"""
Django signals for async tasks
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging
from .models import (
    UserTrainingProgress, AssessmentAttempt, UserCertification, ModuleCompletion
)

logger = logging.getLogger(__name__)



@receiver(post_save, sender=UserTrainingProgress)
def log_course_completion(sender, instance, created, **kwargs):
    """Log when user completes a course"""
    if instance.status == 'completed' and instance.completed_at:
        try:
            user = instance.user
            course = instance.course
            logger.info(f"[COURSE_COMPLETED] User {user.email} - Course: {course.title}")
        except Exception as e:
            logger.error(f'[COURSE_COMPLETION] Error: {type(e).__name__}')


@receiver(post_save, sender=AssessmentAttempt)
def log_assessment_result(sender, instance, created, **kwargs):
    """Log assessment attempt results"""
    if instance.status == 'graded':
        try:
            user = instance.user
            assessment = instance.assessment
            
            if instance.passed:
                logger.info(f"[ASSESSMENT_PASSED] User {user.email} - Assessment: {assessment.title} - Score: {instance.score_percentage}%")
            else:
                logger.info(f"[ASSESSMENT_FAILED] User {user.email} - Assessment: {assessment.title} - Score: {instance.score_percentage}%")
        except Exception as e:
            logger.error(f'[ASSESSMENT] Error: {type(e).__name__}')


@receiver(post_save, sender=UserCertification)
def log_certification_earned(sender, instance, created, **kwargs):
    """Log when user becomes certified"""
    if instance.is_certified and instance.certification_date:
        try:
            user = instance.user
            logger.info(f"[CERTIFICATION_EARNED] User {user.email} - Certification Date: {instance.certification_date}")
        except Exception as e:
            logger.error(f'[CERTIFICATION] Error: {type(e).__name__}')


@receiver(post_save, sender=ModuleCompletion)
def log_module_completion(sender, instance, created, **kwargs):
    """Log when user completes a module"""
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
            
            logger.info(f"[MODULE_COMPLETED] User {user.email} - Module: {module.title} - Course: {course.title} - Progress: {completed_modules}/{course_modules.count()}")
        except Exception as e:
            logger.error(f'[MODULE_COMPLETION] Error: {type(e).__name__}')
