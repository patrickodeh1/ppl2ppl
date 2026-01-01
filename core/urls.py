from django.urls import path
from . import views


app_name = 'core'

urlpatterns = [
    # Training Module
    path('training/', views.training_dashboard, name='training-dashboard'),
    path('training/course/<int:course_id>/', views.course_detail, name='course-detail'),
    path('training/module/<int:module_id>/', views.module_view, name='module-view'),
    path('training/module/<int:module_id>/complete/', views.mark_module_complete, name='mark-module-complete'),
    
    # Assessment Module
    path('assessment/', views.assessment_list, name='assessment-list'),
    path('assessment/<int:assessment_id>/start/', views.start_assessment, name='start-assessment'),
    path('assessment/take/<int:attempt_id>/', views.take_assessment, name='take-assessment'),
    path('assessment/result/<int:attempt_id>/', views.assessment_result, name='assessment-result'),
    
    # Office Schedule
    path('schedule/', views.office_schedule, name='office-schedule'),
    path('schedule/office/<int:office_id>/', views.office_detail, name='office-detail'),
    
    # Employee Directory
    path('directory/', views.employee_directory, name='employee-directory'),
    path('profile/', views.user_profile_view, name='user-profile'),
    path('profile/<int:user_id>/', views.user_profile_view, name='user-profile-detail'),
    
    # API endpoints
    path('api/module-progress/', views.module_progress_api, name='module-progress-api'),
    path('analytics/', views.analytics_dashboard, name='analytics-dashboard'),
    
    # CSV Import/Export
    path('import/courses/', views.import_courses, name='import-courses'),
    path('import/modules/', views.import_modules, name='import-modules'),
    
    # Search (removed)
]
