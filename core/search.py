from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import TrainingCourse, TrainingModule


@login_required
def search_courses(request):
    """Search and filter courses with advanced options"""
    
    query = request.GET.get('q', '').strip()
    difficulty = request.GET.get('difficulty', '')
    content_type = request.GET.get('content_type', '')
    status = request.GET.get('status', '')
    
    # Start with active courses
    courses = TrainingCourse.objects.filter(is_active=True).prefetch_related('modules')
    
    # Full-text search across title and description
    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )
    
    # Filter by difficulty
    if difficulty:
        courses = courses.filter(difficulty=difficulty)
    
    # Filter by status (if user is not staff, only show non-locked courses)
    if status:
        from .models import UserTrainingProgress
        if status == 'completed':
            completed_courses = UserTrainingProgress.objects.filter(
                user=request.user,
                status='completed'
            ).values_list('course_id', flat=True)
            courses = courses.filter(id__in=completed_courses)
        elif status == 'in-progress':
            in_progress_courses = UserTrainingProgress.objects.filter(
                user=request.user,
                status='in_progress'
            ).values_list('course_id', flat=True)
            courses = courses.filter(id__in=in_progress_courses)
        elif status == 'not-started':
            started_courses = UserTrainingProgress.objects.filter(
                user=request.user
            ).values_list('course_id', flat=True)
            courses = courses.exclude(id__in=started_courses)
    
    # Filter by module content type
    if content_type:
        courses = courses.filter(modules__content_type=content_type).distinct()
    
    # Order by difficulty then title
    courses = courses.order_by('difficulty', 'title')
    
    context = {
        'courses': courses,
        'query': query,
        'difficulty': difficulty,
        'content_type': content_type,
        'status': status,
        'difficulty_choices': [
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        'content_type_choices': [
            ('video', 'Video'),
            ('pdf', 'PDF'),
            ('text', 'Text'),
            ('mixed', 'Mixed Content'),
        ],
        'status_choices': [
            ('not-started', 'Not Started'),
            ('in-progress', 'In Progress'),
            ('completed', 'Completed'),
        ],
    }
    
    return render(request, 'core/search_courses.html', context)
