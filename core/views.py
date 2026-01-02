from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q, F, Count, Avg, Case, When, IntegerField
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
    courses_list = list(courses)
    
    for idx, course in enumerate(courses_list):
        course_modules = course.modules.all()
        user_course_progress = progress_dict.get(course.id)
        
        # Determine course status - first course is unlocked, others require previous course completion
        if not course_modules.first():
            status = 'Locked'
        else:
            # First course is always unlocked for all users
            if idx == 0:
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
                    status = 'Not Started'  # First course is unlocked
            else:
                # Subsequent courses require completion of previous course
                previous_course = courses_list[idx - 1]
                previous_modules = previous_course.modules.all()
                previous_all_completed = all(
                    ModuleCompletion.objects.filter(user=request.user, module=m, is_completed=True).exists()
                    for m in previous_modules
                ) if previous_modules.exists() else False
                
                if not previous_all_completed:
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
                        status = 'Not Started'
        
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
    first_incomplete_module = None
    
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
        
        # Track first incomplete module for smart navigation
        if not is_completed and first_incomplete_module is None and not is_locked:
            first_incomplete_module = module
        
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
        'first_incomplete_module': first_incomplete_module,
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
    
    # Determine content URL based on content type
    if module.content_type == 'pdf' and module.pdf_file:
        # Get the file URL - works for both Cloudinary and local storage
        pdf_name = module.pdf_file.name
        if pdf_name.startswith('http'):
            # Already a full Cloudinary URL
            content_url = pdf_name
        else:
            # Use .url to get proper path (will be Cloudinary URL if using MediaCloudinaryStorage)
            content_url = module.pdf_file.url
    else:
        content_url = module.video_url
    
    context = {
        'course': module.course,
        'module': module,
        'id': module.id,
        'title': module.title,
        'description': module.description,
        'content_type': module.content_type,
        'content_url': content_url,
        'content_text': module.text_content,
        'duration_minutes': module.duration_minutes,
        'progress': 100 if completion.is_completed else 0,
        'is_completed': completion.is_completed,
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
    
    # For mixed content, require all thresholds to be met
    if module.content_type == 'mixed':
        # This is a placeholder - actual implementation would track each content piece
        # For now, we allow marking complete manually if user has viewed the page
        pass
    
    # Get or create completion
    completion, _ = ModuleCompletion.objects.get_or_create(
        user=request.user,
        module=module
    )
    
    # Mark as completed
    completion.is_completed = True
    completion.completed_at = timezone.now()
    completion.save()
    
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
    progress.progress_percentage = int(progress_percentage)
    
    if progress_percentage >= 100:
        progress.status = 'completed'
        progress.completed_at = timezone.now()
    elif progress_percentage > 0:
        progress.status = 'in_progress'
    
    progress.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Module marked as complete'})
    
    # Redirect to next module if it exists
    next_module = course.modules.filter(order__gt=module.order).order_by('order').first()
    if next_module:
        return redirect('core:module-view', module_id=next_module.id)
    
    # If no next module, go back to training dashboard
    return redirect('core:training-dashboard')


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
    # Allow admins to access without certification
    if not request.user.is_staff:
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
                'open_time': hours.opening_time if hours else None,
                'close_time': hours.closing_time if hours else None,
            })
        
        office_data.append({
            'id': office.id,
            'name': office.name,
            'address': office.address,
            'city': office.city,
            'state': office.state,
            'postal_code': office.postal_code,
            'timezone': office.timezone,
            'phone': office.phone,
            'email': office.email,
            'is_active': office.is_active,
            'is_open': any(s['is_open'] for s in week_schedule),
            'weekly_schedule': week_schedule,
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
    employees = CustomUser.objects.filter(is_active=True).exclude(is_staff=True).order_by('-created_at')
    
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


@login_required
def analytics_dashboard(request):
    """Admin analytics dashboard showing training metrics and engagement"""
    
    from authentication.models import CustomUser
    
    # Total users and stats
    total_users = CustomUser.objects.count()
    total_courses = TrainingCourse.objects.count()
    total_modules = TrainingModule.objects.count()
    
    # Course completion stats
    course_completions = UserTrainingProgress.objects.filter(
        status='completed'
    ).values('course__title').annotate(
        completed_count=Count('id')
    ).order_by('-completed_count')
    
    # Assessment pass rates
    assessment_attempts = AssessmentAttempt.objects.all()
    total_attempts = assessment_attempts.count()
    passed_attempts = assessment_attempts.filter(passed=True).count()
    pass_rate = (passed_attempts / total_attempts * 100) if total_attempts > 0 else 0
    
    # User progress distribution
    progress_distribution = UserTrainingProgress.objects.values('status').annotate(
        count=Count('id')
    )
    
    # Certified users
    certified_users = UserCertification.objects.filter(is_certified=True).count()
    
    # Recent activity
    recent_completions = ModuleCompletion.objects.filter(
        is_completed=True
    ).select_related('user', 'module').order_by('-completed_at')[:10]
    
    # Assessment performance by difficulty
    assessment_stats = AssessmentQuestion.objects.values('difficulty').annotate(
        avg_correct=Avg(
            Case(
                When(options__userresponse__is_correct=True, then=1),
                default=0,
                output_field=IntegerField()
            )
        )
    )
    
    context = {
        'total_users': total_users,
        'total_courses': total_courses,
        'total_modules': total_modules,
        'certified_users': certified_users,
        'pass_rate': round(pass_rate, 1),
        'total_attempts': total_attempts,
        'course_completions': list(course_completions),
        'progress_distribution': list(progress_distribution),
        'recent_completions': recent_completions,
        'assessment_stats': list(assessment_stats),
    }
    
    return render(request, 'core/analytics_dashboard.html', context)


@login_required
def module_progress_api(request):
    """API endpoint to track module progress (video watch %, PDF scroll, text scroll)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        module_id = data.get('module_id')
        progress_percentage = data.get('progress_percentage', 0)
        content_type = data.get('content_type', '')
        
        # Get or create module completion record
        module = get_object_or_404(TrainingModule, id=module_id)
        completion, created = ModuleCompletion.objects.get_or_create(
            user=request.user,
            module=module
        )
        
        # Update progress based on content type
        if content_type == 'video' and progress_percentage >= 90:
            completion.is_completed = True
            completion.completed_at = timezone.now()
        elif content_type in ['pdf', 'text'] and progress_percentage >= 95:
            completion.is_completed = True
            completion.completed_at = timezone.now()
        
        completion.save()
        
        # Update course progress
        course = module.course
        course_modules = course.modules.all()
        completed_count = ModuleCompletion.objects.filter(
            user=request.user,
            module__course=course,
            is_completed=True
        ).count()
        
        progress_percentage_course = int((completed_count / course_modules.count() * 100)) if course_modules.count() > 0 else 0
        
        # Update or create user training progress
        user_progress, _ = UserTrainingProgress.objects.get_or_create(
            user=request.user,
            course=course
        )
        user_progress.progress_percentage = progress_percentage_course
        
        if completed_count == course_modules.count():
            user_progress.status = 'completed'
            user_progress.completed_at = timezone.now()
        elif completed_count > 0:
            user_progress.status = 'in_progress'
        
        user_progress.save()
        
        return JsonResponse({
            'success': True,
            'module_completed': completion.is_completed,
            'course_progress': progress_percentage_course
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ============================================================================
# CSV IMPORT/EXPORT VIEWS
# ============================================================================

@login_required
def import_courses(request):
    """Import courses from CSV file"""
    
    from .forms import CourseImportForm
    
    if request.method == 'POST':
        form = CourseImportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                imported = 0
                errors = []
                
                for row in form.rows:
                    try:
                        # Parse difficulty
                        difficulty = row.get('Difficulty', 'beginner').lower()
                        if difficulty not in ['beginner', 'intermediate', 'advanced']:
                            difficulty = 'beginner'
                        
                        # Parse boolean fields
                        is_mandatory = row.get('Mandatory', 'No').lower() in ['yes', 'true', '1']
                        is_active = row.get('Active', 'Yes').lower() in ['yes', 'true', '1']
                        
                        # Parse order
                        try:
                            order = int(row.get('Order', imported + 1))
                        except (ValueError, TypeError):
                            order = imported + 1
                        
                        # Parse duration
                        try:
                            duration = int(row.get('Duration (minutes)', 60))
                        except (ValueError, TypeError):
                            duration = 60
                        
                        # Create or update course
                        course, created = TrainingCourse.objects.update_or_create(
                            title=row.get('Title', '').strip(),
                            defaults={
                                'description': row.get('Description', ''),
                                'difficulty': difficulty,
                                'is_mandatory': is_mandatory,
                                'is_active': is_active,
                                'order': order,
                                'estimated_duration_minutes': duration,
                            }
                        )
                        imported += 1
                    
                    except Exception as e:
                        errors.append(f"Row error: {str(e)}")
                
                message = f'✓ Successfully imported {imported} course(s)'
                if errors:
                    message += f'\n⚠ {len(errors)} error(s) occurred'
                
                return render(request, 'core/import_courses.html', {
                    'form': form,
                    'message': message,
                    'imported': imported,
                    'errors': errors[:5],  # Show first 5 errors
                })
            
            except Exception as e:
                form.add_error('csv_file', f'Import failed: {str(e)}')
    else:
        form = CourseImportForm()
    
    return render(request, 'core/import_courses.html', {'form': form})


@login_required
def import_modules(request):
    """Import modules from CSV file"""
    
    from .forms import ModuleImportForm
    
    if request.method == 'POST':
        form = ModuleImportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                imported = 0
                errors = []
                
                for row in form.rows:
                    try:
                        # Get course
                        course_name = row.get('Course', '').strip()
                        try:
                            course = TrainingCourse.objects.get(title=course_name)
                        except TrainingCourse.DoesNotExist:
                            errors.append(f"Course not found: {course_name}")
                            continue
                        
                        # Parse content type
                        content_type = row.get('Content Type', 'text').lower()
                        if content_type not in ['video', 'pdf', 'text', 'mixed']:
                            content_type = 'text'
                        
                        # Parse booleans
                        is_required = row.get('Required', 'No').lower() in ['yes', 'true', '1']
                        
                        # Parse order
                        try:
                            order = int(row.get('Order', imported + 1))
                        except (ValueError, TypeError):
                            order = imported + 1
                        
                        # Parse duration
                        try:
                            duration = int(row.get('Duration (minutes)', 30))
                        except (ValueError, TypeError):
                            duration = 30
                        
                        # Create or update module
                        module, created = TrainingModule.objects.update_or_create(
                            course=course,
                            title=row.get('Title', '').strip(),
                            defaults={
                                'description': row.get('Description', ''),
                                'content_type': content_type,
                                'order': order,
                                'duration_minutes': duration,
                                'is_required': is_required,
                            }
                        )
                        imported += 1
                    
                    except Exception as e:
                        errors.append(f"Row error: {str(e)}")
                
                message = f'✓ Successfully imported {imported} module(s)'
                if errors:
                    message += f'\n⚠ {len(errors)} error(s) occurred'
                
                return render(request, 'core/import_modules.html', {
                    'form': form,
                    'message': message,
                    'imported': imported,
                    'errors': errors[:5],
                })
            
            except Exception as e:
                form.add_error('csv_file', f'Import failed: {str(e)}')
    else:
        form = ModuleImportForm()
    
    return render(request, 'core/import_modules.html', {'form': form})
