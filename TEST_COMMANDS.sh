#!/usr/bin/env bash
# Test Commands for Training Module
# Run these in: python manage.py shell

# ============================================================================
# TEST 1: Verify All Models Are Created
# ============================================================================

# Count objects in database
from core.models import *
print(f"Training Courses: {TrainingCourse.objects.count()}")
print(f"Training Modules: {TrainingModule.objects.count()}")
print(f"Assessments: {Assessment.objects.count()}")
print(f"Assessment Questions: {AssessmentQuestion.objects.count()}")
print(f"Offices: {Office.objects.count()}")

# ============================================================================
# TEST 2: Get Sample Course Details
# ============================================================================

course = TrainingCourse.objects.first()
print(f"Course: {course.title}")
print(f"Modules: {course.modules.count()}")
for module in course.modules.all():
    print(f"  - {module.title} ({module.content_type})")

# ============================================================================
# TEST 3: Get Sample Assessment Details
# ============================================================================

assessment = Assessment.objects.first()
print(f"Assessment: {assessment.title}")
print(f"Questions: {assessment.questions.count()}")
print(f"Passing Score: {assessment.passing_score}%")
print(f"Randomize: {assessment.randomize_questions}")

for question in assessment.questions.all():
    print(f"Q: {question.question_text}")
    for option in question.options.all():
        correct = "✓" if option.is_correct else " "
        print(f"  [{correct}] {option.option_text}")

# ============================================================================
# TEST 4: Create Test User Progress
# ============================================================================

from authentication.models import CustomUser
from django.utils import timezone

# Get a user (or create test user)
user = CustomUser.objects.first()

# Create training progress
progress, created = UserTrainingProgress.objects.get_or_create(
    user=user,
    course=course
)
print(f"Progress created: {created}")
print(f"Status: {progress.status}")

# Start the course
progress.mark_started()
print(f"Status after mark_started: {progress.status}")
print(f"Started at: {progress.started_at}")

# ============================================================================
# TEST 5: Simulate Completing Modules
# ============================================================================

modules = course.modules.all()
for module in modules[:2]:  # Complete first 2 modules
    completion, created = ModuleCompletion.objects.get_or_create(
        user=user,
        module=module
    )
    completion.mark_completed(time_spent=10)
    print(f"Completed: {module.title}")

# Check progress percentage
completed = ModuleCompletion.objects.filter(
    user=user,
    module__course=course,
    is_completed=True
).count()
total = course.modules.filter(is_required=True).count()
percentage = (completed / total * 100) if total > 0 else 0
print(f"Progress: {completed}/{total} ({percentage:.0f}%)")

# ============================================================================
# TEST 6: Create Assessment Attempt
# ============================================================================

from random import choice

attempt = AssessmentAttempt.objects.create(
    user=user,
    assessment=assessment,
    total_questions=assessment.total_questions
)
print(f"Assessment attempt created: {attempt.id}")
print(f"Status: {attempt.status}")

# Simulate answering questions
for question in assessment.questions.all()[:5]:  # Answer first 5 questions
    # Randomly pick an option
    options = list(question.options.all())
    selected = choice(options)
    
    response, created = UserResponse.objects.get_or_create(
        attempt=attempt,
        question=question
    )
    response.selected_option = selected
    response.is_correct = selected.is_correct
    response.save()
    
    if response.is_correct:
        attempt.correct_answers += 1

attempt.save()
print(f"Answered 5 questions, {attempt.correct_answers} correct")

# ============================================================================
# TEST 7: Calculate and Submit Assessment
# ============================================================================

attempt.calculate_score()
print(f"Score: {attempt.score_percentage}%")
print(f"Passed: {attempt.passed}")

if attempt.passed:
    print("✓ User would be certified!")
else:
    print("✗ User needs to improve score")

# ============================================================================
# TEST 8: Check Certification Status
# ============================================================================

cert, created = UserCertification.objects.get_or_create(user=user)
print(f"Certified: {cert.is_certified}")

if attempt.passed:
    cert.certify(attempt)
    print(f"Updated - Certified: {cert.is_certified}")
    print(f"Certification date: {cert.certification_date}")

# ============================================================================
# TEST 9: Query Examples
# ============================================================================

# Get all users who completed training
completed_users = UserTrainingProgress.objects.filter(
    status='completed'
).values_list('user__email', flat=True)
print(f"Completed training: {list(completed_users)}")

# Get certified users
certified = UserCertification.objects.filter(is_certified=True).count()
print(f"Certified users: {certified}")

# Get assessment attempts with score >= 85%
passed_attempts = AssessmentAttempt.objects.filter(
    score_percentage__gte=85
).count()
print(f"Passed assessments: {passed_attempts}")

# Get office hours for a specific day
from core.models import OfficeHours
monday_hours = OfficeHours.objects.filter(day_of_week=0)
for hours in monday_hours:
    if hours.is_open:
        print(f"{hours.office.name}: {hours.opening_time} - {hours.closing_time}")

# ============================================================================
# TEST 10: Admin Access
# ============================================================================

print("\n✓ All tests completed!")
print("\nNext steps:")
print("1. Go to: http://localhost:8000/admin/")
print("2. Login with superuser credentials")
print("3. Create some courses and assessments")
print("4. Track user progress")
print("\nTemplate development next:")
print("- Create /templates/core/training_dashboard.html")
print("- Create /templates/core/assessment_list.html")
print("- etc...")

# Exit shell
exit()
