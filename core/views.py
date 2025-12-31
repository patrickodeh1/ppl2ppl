from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q, F
from django.utils import timezone
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from decimal import Decimal
import random

from .models import (
    TrainingCourse, TrainingModule, UserTrainingProgress, ModuleCompletion,
    Assessment, AssessmentQuestion, AssessmentOption, AssessmentAttempt, UserResponse,
    UserCertification, Office, OfficeHours, EmployeeDirectory
)
from .forms import (
    TrainingCourseForm, TrainingModuleForm, AssessmentForm, AssessmentQuestionForm,
    AssessmentOptionForm, QuizForm, OfficeForm, OfficeHoursForm, EmployeeDirectoryForm
)
from authentication.models import CustomUser


# ============================================================================
# TRAINING MODULE VIEWS
# ============================================================================

@login_required
def training_dashboard(request):
    """Dashboard showing all available training courses and user progress"""
    courses = TrainingCourse.objects.filter(is_active=True).prefetch_related('modules')
    
    # Get user's progress for each course
    user_progress = UserTrainingProgress.objects.filter(user=request.user)
    progress_dict = {p.course_id: p for p in user_progress}
    
    # Check if user is certified
    try:
        certification = request.user.certification
        is_certified = certification.is_certified
    except UserCertification.DoesNotExist:
        is_certified = False
    
    # Count total and completed modules
    total_modules = TrainingModule.objects.count()
    completed_modules = ModuleCompletion.objects.filter(user=request.user, is_completed=True).count()
    overall_progress = int((completed_modules / total_modules * 100)) if total_modules > 0 else 0
    
    # Prepare course data with status
    course_data = []
    for course in courses:
        course_modules = course.modules.all()
        user_course_progress = progress_dict.get(course.id)
        
        # Determine course status
        if not course_modules.first():
            status = 'Locked'
        else:
            first_module = course_modules.first()
            has_started = ModuleCompletion.objects.filter(user=request.user, module=first_module).exists()
            all_completed = all(
                ModuleCompletion.objects.filter(user=request.user, module=m, is_completed=True).exists()
                for m in course_modules
            )
            
            if all_completed:
                status = 'Completed'
            elif has_started:
                status = 'In Progress'
            else:
                status = 'Locked'
        
        course_data.append({
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'estimated_time': course.estimated_duration_minutes,
            'status': status,
            'progress': user_course_progress.progress_percentage if user_course_progress else 0,
        })
    
    context = {
        'courses': course_data,
        'total_modules': total_modules,
        'completed_modules': completed_modules,
        'overall_progress': overall_progress,
        'all_modules_completed': completed_modules == total_modules and total_modules > 0,
    }
    return render(request, 'core/training_dashboard.html', context)


@login_required
def course_detail(request, course_id):
    """Detailed view of a single course with all modules"""
    course = get_object_or_404(TrainingCourse, id=course_id, is_active=True)
    modules = course.modules.all().order_by('order')
    
    # Get module completions for this user
    completed_module_ids = set(ModuleCompletion.objects.filter(
        user=request.user,
        module__course=course,
        is_completed=True
    ).values_list('module_id', flat=True))
    
    # Add status and lock info to modules
    module_list = []
    previous_completed = True
    
    for module in modules:
        is_completed = module.id in completed_module_ids
        is_locked = not previous_completed and not is_completed
        
        module_list.append({
            'id': module.id,
            'title': module.title,
            'description': module.description,
            'content_type': module.content_type,
            'duration_minutes': module.duration_minutes,
            'is_completed': is_completed,
            'is_locked': is_locked,
        })
        
        # Only first module or after completed modules are unlocked
        if not is_completed:
            previous_completed = False
    
    completed_modules = len(completed_module_ids)
    total_modules = modules.count()
    
    context = {
        'course': course,
        'modules': module_list,
        'completed_modules': completed_modules,
        'total_modules': total_modules,
        'total_duration': sum(m.duration_minutes or 0 for m in modules),
    }
    return render(request, 'core/course_detail.html', context)


@login_required
def module_view(request, module_id):
    """View a specific training module"""
    module = get_object_or_404(TrainingModule, id=module_id)
    
    # Get or create progress tracking
    progress, _ = UserTrainingProgress.objects.get_or_create(
        user=request.user,
        course=module.course
    )
    
    # Mark as started if not already
    progress.mark_started()
    
    # Get or create module completion
    completion, created = ModuleCompletion.objects.get_or_create(
        user=request.user,
        module=module
    )
    
    # Get all modules in course for navigation
    course_modules = module.course.modules.all().order_by('order')
    module_list = list(course_modules)
    current_index = module_list.index(module)
    
    next_module = module_list[current_index + 1] if current_index < len(module_list) - 1 else None
    prev_module = module_list[current_index - 1] if current_index > 0 else None
    
    context = {
        'course': module.course,
        'id': module.id,
        'title': module.title,
        'description': module.description,
        'content_type': module.content_type,
        'content_url': module.video_url,
        'content_text': module.text_content,
        'duration_minutes': module.duration_minutes,
        'progress': completion.progress_percentage if completion else 0,
        'can_mark_complete': True,
        'next_module': next_module,
        'prev_module': prev_module,
        'current_index': current_index + 1,
        'total_modules': len(module_list),
    }
    return render(request, 'core/module_view.html', context)


@login_required
def mark_module_complete(request, module_id):
    """Mark a module as complete"""
    if request.method != 'POST':
        return HttpResponseForbidden()
    
    module = get_object_or_404(TrainingModule, id=module_id)
    
    # Get or create completion
    completion, _ = ModuleCompletion.objects.get_or_create(
        user=request.user,
        module=module
    )
    
    completion.mark_completed()
    
    # Update course progress
    course = module.course
    all_modules = course.modules.filter(is_required=True)
    completed_count = ModuleCompletion.objects.filter(
        user=request.user,
        module__course=course,
        is_completed=True
    ).count()
    
    progress_percentage = (completed_count / all_modules.count() * 100) if all_modules.count() > 0 else 0
    
    progress, _ = UserTrainingProgress.objects.get_or_create(user=request.user, course=course)
    progress.update_progress(progress_percentage)
    
    if progress_percentage >= 100:
        progress.mark_completed()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Module marked as complete'})
    
    return redirect('core:module-view', module_id=module_id)


# ============================================================================
# ASSESSMENT VIEWS
# ============================================================================

@login_required
def assessment_list(request):
    """List all available assessments"""
    assessments = Assessment.objects.filter(is_active=True)
    
    # Check if all modules are completed
    total_modules = TrainingModule.objects.count()
    completed_modules = ModuleCompletion.objects.filter(user=request.user, is_completed=True).count()
    all_modules_completed = completed_modules == total_modules and total_modules > 0
    
    # Get user's last attempt for each assessment
    assessment_data = []
    for assessment in assessments:
        last_attempt = AssessmentAttempt.objects.filter(
            user=request.user,
            assessment=assessment
        ).order_by('-created_at').first()
        
        assessment_data.append({
            'id': assessment.id,
            'title': assessment.title,
            'description': assessment.description,
            'questions_count': assessment.total_questions,
            'last_attempt': last_attempt,
        })
    
    context = {
        'assessments': assessment_data,
        'all_modules_completed': all_modules_completed,
    }
    return render(request, 'core/assessment_list.html', context)


@login_required
def start_assessment(request, assessment_id):
    """Start taking an assessment"""
    assessment = get_object_or_404(Assessment, id=assessment_id, is_active=True)
    
    # Create a new attempt
    attempt = AssessmentAttempt.objects.create(
        user=request.user,
        assessment=assessment,
        total_questions=assessment.total_questions
    )
    
    # Get questions for this assessment
    questions = assessment.questions.all()
    
    if assessment.randomize_questions:
        questions = list(questions)
        random.shuffle(questions)
    else:
        questions = list(questions.order_by('order'))
    
    # Create user response records for each question
    for question in questions:
        UserResponse.objects.create(
            attempt=attempt,
            question=question
        )
    
    return redirect('core:take-assessment', attempt_id=attempt.id)


@login_required
def take_assessment(request, attempt_id):
    """Take/view an assessment"""
    attempt = get_object_or_404(AssessmentAttempt, id=attempt_id, user=request.user)
    
    if request.method == 'POST':
        # Process responses
        for response in attempt.responses.all():
            option_id = request.POST.get(f'question_{response.question.id}')
            
            if option_id:
                option = get_object_or_404(AssessmentOption, id=option_id)
                response.selected_option = option
                response.is_correct = option.is_correct
                response.save()
                
                if option.is_correct:
                    attempt.correct_answers += 1
        
        # Calculate score
        attempt.calculate_score()
        attempt.submit()
        
        # If passed, update certification
        if attempt.passed:
            try:
                cert = request.user.certification
            except UserCertification.DoesNotExist:
                cert = UserCertification.objects.create(user=request.user)
            
            if not cert.is_certified:
                cert.certify(attempt)
        
        return redirect('core:assessment-result', attempt_id=attempt.id)
    
    # GET request - display form
    form = QuizForm(attempt.assessment)
    
    # Pre-fill with existing responses
    for response in attempt.responses.all():
        if response.selected_option:
            form[f'question_{response.question.id}'].initial = response.selected_option.id
    
    context = {
        'attempt': attempt,
        'assessment': attempt.assessment,
        'form': form,
    }
    return render(request, 'core/take_assessment.html', context)


@login_required
def assessment_result(request, attempt_id):
    """View assessment results"""
    attempt = get_object_or_404(AssessmentAttempt, id=attempt_id, user=request.user)
    
    # Get detailed response information
    responses = attempt.responses.all().select_related('question', 'selected_option')
    
    context = {
        'attempt': attempt,
        'responses': responses,
        'passed': attempt.passed,
    }
    return render(request, 'core/assessment_result.html', context)


# ============================================================================
# OFFICE SCHEDULE VIEWS
# ============================================================================

@login_required
def office_schedule(request):
    """View office locations and hours (certified users only)"""
    # Check if user is certified
    try:
        certification = request.user.certification
        if not certification.is_certified:
            return redirect('core:assessment-list')
    except UserCertification.DoesNotExist:
        return redirect('core:assessment-list')
    
    offices = Office.objects.filter(is_active=True).prefetch_related('hours')
    
    # Add weekly schedule data to each office
    office_data = []
    for office in offices:
        week_schedule = []
        for day in range(7):  # 0 = Monday, 6 = Sunday
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            hours = office.hours.filter(day_of_week=day).first()
            
            week_schedule.append({
                'day': day_names[day],
                'is_open': hours.is_open if hours else False,
                'open_time': hours.open_time if hours else None,
                'close_time': hours.close_time if hours else None,
                'break_start': hours.break_start if hours else None,
                'break_end': hours.break_end if hours else None,
            })
        
        office_data.append({
            'id': office.id,
            'name': office.name,
            'code': office.code,
            'address_line_1': office.address_line_1,
            'address_line_2': office.address_line_2,
            'city': office.city,
            'state': office.state,
            'zip_code': office.zip_code,
            'timezone': office.timezone,
            'phone_number': office.phone_number,
            'email': office.email,
            'notes': office.notes,
            'is_open': any(s['is_open'] for s in week_schedule),
            'get_weekly_schedule': week_schedule,
        })
    
    context = {
        'offices': office_data,
    }
    return render(request, 'core/office_schedule.html', context)


@login_required
def office_detail(request, office_id):
    """View details of a specific office"""
    # Check certification
    try:
        certification = request.user.certification
        if not certification.is_certified:
            return redirect('core:assessment-list')
    except UserCertification.DoesNotExist:
        return redirect('core:assessment-list')
    
    office = get_object_or_404(Office, id=office_id, is_active=True)
    
    # Build weekly schedule
    week_schedule = []
    for day in range(7):  # 0 = Monday, 6 = Sunday
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        hours = office.hours.filter(day_of_week=day).first()
        
        week_schedule.append({
            'day': day_names[day],
            'is_open': hours.is_open if hours else False,
            'open_time': hours.open_time if hours else None,
            'close_time': hours.close_time if hours else None,
            'break_start': hours.break_start if hours else None,
            'break_end': hours.break_end if hours else None,
        })
    
    context = {
        'office': {
            'id': office.id,
            'name': office.name,
            'code': office.code,
            'address_line_1': office.address_line_1,
            'address_line_2': office.address_line_2,
            'city': office.city,
            'state': office.state,
            'zip_code': office.zip_code,
            'timezone': office.timezone,
            'phone_number': office.phone_number,
            'email': office.email,
            'notes': office.notes,
            'get_weekly_schedule': week_schedule,
        }
    }
    return render(request, 'core/office_detail.html', context)


# ============================================================================
# EMPLOYEE DIRECTORY (ADMIN ONLY)
# ============================================================================

@login_required
def employee_directory(request):
    """Employee directory view (admin only)"""
    if not request.user.is_staff:
        return HttpResponseForbidden()
    
    # Get all employees (CustomUser)
    employees = CustomUser.objects.filter(is_active=True).exclude(is_staff=True).order_by('date_joined').reverse()
    
    # Pagination
    paginator = Paginator(employees, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'employees': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    }
    return render(request, 'core/employee_directory.html', context)


@login_required
def user_profile_view(request, user_id=None):
    """View a user's profile (employees/admins)"""
    if user_id is None:
        user = request.user
    else:
        user = get_object_or_404(CustomUser, id=user_id)
    
    # Check permissions
    if not (request.user.is_staff or request.user == user):
        return HttpResponseForbidden()
    
    # Get user's training progress
    training_progress = UserTrainingProgress.objects.filter(user=user)
    
    # Get user's assessment attempts
    assessment_attempts = AssessmentAttempt.objects.filter(user=user).order_by('-created_at')
    
    # Get certification status
    try:
        certification = user.certification
    except UserCertification.DoesNotExist:
        certification = None
    
    context = {
        'profile_user': user,
        'training_progress': training_progress,
        'assessment_attempts': assessment_attempts,
        'certification': certification,
    }
    return render(request, 'core/user_profile.html', context)
