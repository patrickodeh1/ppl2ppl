from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.http import JsonResponse, HttpResponse
from .models import (
    # Training
    TrainingCourse, TrainingModule, UserTrainingProgress, ModuleCompletion,
    # Assessment
    Assessment, AssessmentQuestion, AssessmentOption, AssessmentAttempt, UserResponse,
    # Certification
    UserCertification,
    # Office Schedule
    Office, OfficeHours, EmployeeDirectory
)


# ============================================================================
# CSV EXPORT FUNCTIONS
# ============================================================================

def export_as_csv(description):
    """Factory function to create CSV export actions"""
    def export_csv(modeladmin, request, queryset):
        """Export queryset as CSV file"""
        model = queryset.model
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{model._meta.verbose_name_plural}.csv"'
        
        writer = csv.writer(response)
        
        # Get all fields except ManyToMany
        fields = [f for f in model._meta.get_fields() 
                  if not f.many_to_one and not f.one_to_many and not f.many_to_many]
        
        # Write header
        writer.writerow([f.name for f in fields])
        
        # Write data
        for obj in queryset:
            row = []
            for field in fields:
                value = getattr(obj, field.name)
                # Handle ForeignKey display
                if hasattr(value, '__str__'):
                    value = str(value)
                row.append(value or '')
            writer.writerow(row)
        
        return response
    
    export_csv.short_description = description
    return export_csv


# ============================================================================
# CUSTOM ADMIN SITE
# ============================================================================

class P2PAdminSite(admin.AdminSite):
    """Custom admin site with P2P Solutions branding"""
    site_header = "P2P Solutions Admin"
    site_title = "P2P Admin"
    index_title = "Dashboard"
    
    def get_urls(self):
        """Add custom admin endpoints"""
        urls = super().get_urls()
        custom_urls = [
            path('stats/', self.admin_view(self.stats_view), name='admin-stats'),
        ]
        return custom_urls + urls
    
    def stats_view(self, request):
        """Return admin dashboard statistics as JSON"""
        from authentication.models import CustomUser
        
        stats = {
            'courses': TrainingCourse.objects.count(),
            'modules': TrainingModule.objects.count(),
            'users': CustomUser.objects.count(),
            'assessments': Assessment.objects.count(),
        }
        return JsonResponse(stats)
    
    def index(self, request, extra_context=None):
        """Override index to add custom context"""
        extra_context = extra_context or {}
        extra_context['site_url'] = '/training/'  # Redirect "View Site" to training
        return super().index(request, extra_context)


# Create custom admin site instance
admin_site = P2PAdminSite(name='p2p_admin')


# ============================================================================
# TRAINING ADMIN
# ============================================================================

class TrainingModuleInline(admin.TabularInline):
    """Inline editing for training modules"""
    model = TrainingModule
    extra = 1
    fields = ('order', 'title', 'content_type', 'duration_minutes', 'is_required', 'video_preview')
    readonly_fields = ('video_preview',)
    ordering = ['order']
    
    def video_preview(self, obj):
        """Display YouTube video preview link"""
        if obj.video_url:
            return format_html(
                '<a href="{}" target="_blank" style="color: #C41E3A; text-decoration: none;">🎬 Preview</a>',
                obj.video_url
            )
        return '—'
    video_preview.short_description = 'Preview'


class TrainingCourseAdminClass(admin.ModelAdmin):
    """Admin for training courses"""
    list_display = ('title', 'difficulty_badge', 'is_mandatory_badge', 'module_count', 'duration_display', 'order', 'is_active_badge')
    list_filter = ('difficulty', 'is_mandatory', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    ordering = ['order']
    inlines = [TrainingModuleInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'difficulty', 'is_mandatory')
        }),
        ('Content Management', {
            'fields': ('estimated_duration_minutes', 'order')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    actions = ['export_to_csv']
    
    def export_to_csv(self, request, queryset):
        """Export courses to CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="courses.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Title', 'Description', 'Difficulty', 'Mandatory', 'Duration (minutes)', 'Order', 'Active'])
        
        for course in queryset:
            writer.writerow([
                course.title,
                course.description,
                course.get_difficulty_display(),
                'Yes' if course.is_mandatory else 'No',
                course.estimated_duration_minutes,
                course.order,
                'Yes' if course.is_active else 'No',
            ])
        
        return response
    
    export_to_csv.short_description = '📥 Export selected courses to CSV'
    
    def difficulty_badge(self, obj):
        """Display difficulty as colored badge"""
        colors = {
            'beginner': '#22c55e',
            'intermediate': '#f59e0b',
            'advanced': '#ef4444',
        }
        color = colors.get(obj.difficulty, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">{}</span>',
            color,
            obj.get_difficulty_display()
        )
    difficulty_badge.short_description = 'Difficulty'
    
    def is_mandatory_badge(self, obj):
        """Display mandatory status"""
        icon = '✓' if obj.is_mandatory else '○'
        color = '#22c55e' if obj.is_mandatory else '#9ca3af'
        return format_html(
            '<span style="color: {}; font-weight: 600; font-size: 16px;">{}</span>',
            color,
            icon
        )
    is_mandatory_badge.short_description = 'Mandatory'
    
    def module_count(self, obj):
        """Display number of modules"""
        count = obj.modules.count()
        return format_html(
            '<span style="background-color: #dbeafe; color: #0c4a6e; padding: 2px 8px; border-radius: 12px; font-weight: 600;">{}</span>',
            count
        )
    module_count.short_description = 'Modules'
    
    def duration_display(self, obj):
        """Display estimated duration"""
        return f'{obj.estimated_duration_minutes} min'
    duration_display.short_description = 'Est. Time'
    
    def is_active_badge(self, obj):
        """Display active status"""
        color = '#22c55e' if obj.is_active else '#ef4444'
        status = 'Active' if obj.is_active else 'Inactive'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">{}</span>',
            color,
            status
        )
    is_active_badge.short_description = 'Status'


class TrainingModuleAdminClass(admin.ModelAdmin):
    """Admin for training modules"""
    list_display = ('title', 'course', 'content_type_badge', 'order', 'duration_display', 'video_link', 'is_required_badge')
    list_filter = ('course', 'content_type', 'is_required', 'created_at')
    search_fields = ('title', 'course__title')
    ordering = ['course', 'order']
    actions = ['export_to_csv']
    readonly_fields = ('video_help',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('course', 'title', 'description', 'content_type', 'order')
        }),
        ('Video Content', {
            'fields': ('video_url',),
            'classes': ('collapse',),
            'description': 'For video content, paste YouTube URL (e.g., https://www.youtube.com/embed/dQw4w9WgXcQ)'
        }),
        ('PDF Content', {
            'fields': ('pdf_file',),
            'classes': ('collapse',)
        }),
        ('Text Content', {
            'fields': ('text_content',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('duration_minutes', 'is_required')
        }),
    )
    
    def get_fieldsets(self, request, obj=None):
        """Dynamically show relevant content fields"""
        fieldsets = super().get_fieldsets(request, obj)
        return fieldsets
    
    def video_help(self, obj):
        """Helper text for video URL"""
        return format_html(
            '<div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 10px; border-radius: 4px; margin-top: 10px;">'
            '<strong>📺 How to add YouTube videos:</strong><br>'
            '1. Go to YouTube and find the video<br>'
            '2. Click "Share" → "Embed"<br>'
            '3. Copy the src URL from the embed code (e.g., https://www.youtube.com/embed/VIDEO_ID)<br>'
            '4. Paste it above'
            '</div>'
        )
    video_help.short_description = ''
    
    def content_type_badge(self, obj):
        """Display content type as badge"""
        colors = {
            'video': '#3b82f6',
            'pdf': '#ef4444',
            'text': '#8b5cf6',
            'mixed': '#f59e0b',
        }
        color = colors.get(obj.content_type, '#6b7280')
        icons = {
            'video': '🎬',
            'pdf': '📄',
            'text': '📝',
            'mixed': '📦',
        }
        icon = icons.get(obj.content_type, '📌')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">{} {}</span>',
            color,
            icon,
            obj.get_content_type_display()
        )
    content_type_badge.short_description = 'Type'
    
    def duration_display(self, obj):
        """Display duration"""
        return f'{obj.duration_minutes} min' if obj.duration_minutes else '—'
    duration_display.short_description = 'Duration'
    
    def video_link(self, obj):
        """Display clickable link to video"""
        if obj.video_url:
            return format_html(
                '<a href="{}" target="_blank" style="color: #C41E3A; text-decoration: none; font-weight: 600;">🎬 Watch</a>',
                obj.video_url
            )
        return '—'
    video_link.short_description = 'Video'
    
    def is_required_badge(self, obj):
        """Display required status"""
        icon = '✓' if obj.is_required else '○'
        color = '#22c55e' if obj.is_required else '#9ca3af'
        return format_html(
            '<span style="color: {}; font-weight: 600; font-size: 16px;">{}</span>',
            color,
            icon
        )
    is_required_badge.short_description = 'Required'
    
    def export_to_csv(self, request, queryset):
        """Export modules to CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="modules.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Course', 'Title', 'Content Type', 'Order', 'Duration (minutes)', 'Required'])
        
        for module in queryset:
            writer.writerow([
                module.course.title,
                module.title,
                module.get_content_type_display(),
                module.order,
                module.duration_minutes or 0,
                'Yes' if module.is_required else 'No',
            ])
        
        return response
    
    export_to_csv.short_description = '📥 Export selected modules to CSV'


# Register with custom admin site
admin_site.register(TrainingCourse, TrainingCourseAdminClass)
admin_site.register(TrainingModule, TrainingModuleAdminClass)


@admin.register(UserTrainingProgress)
class UserTrainingProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'status', 'progress_percentage', 'started_at', 'completed_at')
    list_filter = ('status', 'course', 'created_at')
    search_fields = ('user__email', 'course__title')
    readonly_fields = ('user', 'course', 'created_at', 'updated_at')
    fieldsets = (
        ('User & Course', {
            'fields': ('user', 'course')
        }),
        ('Progress', {
            'fields': ('status', 'progress_percentage', 'started_at', 'completed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


admin_site.register(UserTrainingProgress, UserTrainingProgressAdmin)


@admin.register(ModuleCompletion)
class ModuleCompletionAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'is_completed', 'time_spent_minutes', 'started_at')
    list_filter = ('is_completed', 'module__course', 'started_at')
    search_fields = ('user__email', 'module__title')
    readonly_fields = ('started_at',)


admin_site.register(ModuleCompletion, ModuleCompletionAdmin)


# ============================================================================
# ASSESSMENT ADMIN
# ============================================================================

class AssessmentOptionInline(admin.TabularInline):
    model = AssessmentOption
    extra = 1
    fields = ('order', 'option_text', 'is_correct')
    ordering = ['order']


class AssessmentQuestionInline(admin.TabularInline):
    model = AssessmentQuestion
    extra = 1
    fields = ('order', 'question_text', 'difficulty')
    ordering = ['order']


class AssessmentAdminClass(admin.ModelAdmin):
    list_display = ('title', 'question_count', 'passing_score_display', 'time_limit_display', 'status_badge', 'created_at')
    list_filter = ('is_mandatory', 'is_active', 'randomize_questions', 'created_at')
    search_fields = ('title', 'description')
    inlines = [AssessmentQuestionInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description')
        }),
        ('Scoring', {
            'fields': ('total_questions', 'passing_score')
        }),
        ('Question Settings', {
            'fields': ('randomize_questions', 'randomize_options')
        }),
        ('Time Limit', {
            'fields': ('time_limit_minutes',)
        }),
        ('Status', {
            'fields': ('is_mandatory', 'is_active')
        }),
    )
    
    def question_count(self, obj):
        """Display number of questions"""
        count = obj.questions.count()
        return format_html(
            '<span style="background-color: #dbeafe; color: #0c4a6e; padding: 2px 8px; border-radius: 12px; font-weight: 600;">{}</span>',
            count
        )
    question_count.short_description = 'Questions'
    
    def passing_score_display(self, obj):
        """Display passing score"""
        return f'{obj.passing_score}%'
    passing_score_display.short_description = 'Pass Score'
    
    def time_limit_display(self, obj):
        """Display time limit"""
        return f'{obj.time_limit_minutes} min' if obj.time_limit_minutes else '—'
    time_limit_display.short_description = 'Time Limit'
    
    def status_badge(self, obj):
        """Display status badge"""
        color = '#22c55e' if obj.is_active else '#ef4444'
        status = 'Active' if obj.is_active else 'Inactive'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">{}</span>',
            color,
            status
        )
    status_badge.short_description = 'Status'


admin_site.register(Assessment, AssessmentAdminClass)


class AssessmentQuestionAdminClass(admin.ModelAdmin):
    list_display = ('assessment', 'order', 'question_text_short', 'difficulty_badge', 'option_count')
    list_filter = ('assessment', 'difficulty')
    search_fields = ('question_text', 'assessment__title')
    ordering = ['assessment', 'order']
    inlines = [AssessmentOptionInline]
    fieldsets = (
        ('Question', {
            'fields': ('assessment', 'order', 'question_text', 'difficulty')
        }),
        ('Feedback', {
            'fields': ('explanation',)
        }),
    )
    
    def question_text_short(self, obj):
        """Display shortened question text"""
        return obj.question_text[:60] + '...' if len(obj.question_text) > 60 else obj.question_text
    question_text_short.short_description = 'Question'
    
    def difficulty_badge(self, obj):
        """Display difficulty badge"""
        colors = {
            'easy': '#22c55e',
            'medium': '#f59e0b',
            'hard': '#ef4444',
        }
        color = colors.get(obj.difficulty, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_difficulty_display()
        )
    difficulty_badge.short_description = 'Difficulty'
    
    def option_count(self, obj):
        """Display number of options"""
        count = obj.options.count()
        return format_html(
            '<span style="color: #666;">{} options</span>',
            count
        )
    option_count.short_description = 'Options'


admin_site.register(AssessmentQuestion, AssessmentQuestionAdminClass)


class AssessmentOptionAdminClass(admin.ModelAdmin):
    list_display = ('question', 'order', 'option_text_short', 'correct_badge')
    list_filter = ('question__assessment', 'is_correct')
    search_fields = ('option_text', 'question__question_text')
    ordering = ['question', 'order']
    
    def option_text_short(self, obj):
        """Display shortened option text"""
        return obj.option_text[:50] + '...' if len(obj.option_text) > 50 else obj.option_text
    option_text_short.short_description = 'Option'
    
    def correct_badge(self, obj):
        """Display if option is correct"""
        icon = '✓' if obj.is_correct else '✗'
        color = '#22c55e' if obj.is_correct else '#ef4444'
        return format_html(
            '<span style="color: {}; font-weight: 600; font-size: 16px;">{}</span>',
            color,
            icon
        )
    correct_badge.short_description = 'Correct'


admin_site.register(AssessmentOption, AssessmentOptionAdminClass)


class UserResponseInline(admin.TabularInline):
    model = UserResponse
    extra = 0
    fields = ('question', 'selected_option', 'is_correct')
    readonly_fields = ('question', 'selected_option', 'is_correct')
    can_delete = False


class AssessmentAttemptAdminClass(admin.ModelAdmin):
    list_display = ('user', 'assessment', 'score_display', 'passed_badge', 'status_badge', 'started_at')
    list_filter = ('assessment', 'passed', 'status', 'started_at')
    search_fields = ('user__email', 'assessment__title')
    readonly_fields = ('user', 'assessment', 'started_at', 'submitted_at', 'created_at', 'updated_at')
    inlines = [UserResponseInline]
    fieldsets = (
        ('Attempt Information', {
            'fields': ('user', 'assessment', 'status')
        }),
        ('Scoring', {
            'fields': ('total_questions', 'correct_answers', 'score_percentage', 'passed')
        }),
        ('Timing', {
            'fields': ('started_at', 'submitted_at', 'time_taken_minutes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def score_display(self, obj):
        """Display score as percentage"""
        return f'{obj.score_percentage}%'
    score_display.short_description = 'Score'
    
    def passed_badge(self, obj):
        """Display pass/fail badge"""
        color = '#22c55e' if obj.passed else '#ef4444'
        status = 'Passed' if obj.passed else 'Failed'
        icon = '✓' if obj.passed else '✗'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">{} {}</span>',
            color,
            icon,
            status
        )
    passed_badge.short_description = 'Result'
    
    def status_badge(self, obj):
        """Display status badge"""
        colors = {
            'in_progress': '#f59e0b',
            'submitted': '#3b82f6',
            'graded': '#22c55e',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


admin_site.register(AssessmentAttempt, AssessmentAttemptAdminClass)


class UserResponseAdminClass(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_option', 'correct_badge')
    list_filter = ('is_correct', 'attempt__assessment')
    search_fields = ('attempt__user__email', 'question__question_text')
    readonly_fields = ('attempt', 'question', 'answered_at')
    
    def correct_badge(self, obj):
        """Display if answer is correct"""
        icon = '✓' if obj.is_correct else '✗'
        color = '#22c55e' if obj.is_correct else '#ef4444'
        return format_html(
            '<span style="color: {}; font-weight: 600; font-size: 16px;">{}</span>',
            color,
            icon
        )
    correct_badge.short_description = 'Correct'


admin_site.register(UserResponse, UserResponseAdminClass)


# ============================================================================
# CERTIFICATION ADMIN
# ============================================================================

class UserCertificationAdminClass(admin.ModelAdmin):
    list_display = ('user', 'certified_badge', 'certification_date', 'expires_at')
    list_filter = ('is_certified', 'certification_date')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('certification_date', 'created_at', 'updated_at')
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Certification', {
            'fields': ('is_certified', 'certification_date', 'passing_attempt')
        }),
        ('Expiration', {
            'fields': ('expires_at',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def certified_badge(self, obj):
        """Display certification status"""
        color = '#22c55e' if obj.is_certified else '#ef4444'
        status = 'Certified' if obj.is_certified else 'Not Certified'
        icon = '✓' if obj.is_certified else '✗'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">{} {}</span>',
            color,
            icon,
            status
        )
    certified_badge.short_description = 'Status'


admin_site.register(UserCertification, UserCertificationAdminClass)


# ============================================================================
# OFFICE SCHEDULE ADMIN
# ============================================================================

class OfficeHoursInline(admin.TabularInline):
    model = OfficeHours
    extra = 0
    fields = ('day_of_week', 'is_open', 'opening_time', 'closing_time')
    ordering = ['day_of_week']


class OfficeAdminClass(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'timezone', 'status_badge', 'order')
    list_filter = ('is_active', 'timezone', 'country')
    search_fields = ('name', 'city', 'address')
    ordering = ['order']
    inlines = [OfficeHoursInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'address', 'city', 'state', 'postal_code', 'country')
        }),
        ('Location Settings', {
            'fields': ('timezone', 'order')
        }),
        ('Contact', {
            'fields': ('phone', 'email')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def status_badge(self, obj):
        """Display active status"""
        color = '#22c55e' if obj.is_active else '#ef4444'
        status = 'Active' if obj.is_active else 'Inactive'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">{}</span>',
            color,
            status
        )
    status_badge.short_description = 'Status'


admin_site.register(Office, OfficeAdminClass)


class OfficeHoursAdminClass(admin.ModelAdmin):
    list_display = ('office', 'day_of_week', 'open_badge', 'hours_display')
    list_filter = ('office', 'day_of_week', 'is_open')
    ordering = ['office', 'day_of_week']
    fieldsets = (
        ('Office & Day', {
            'fields': ('office', 'day_of_week')
        }),
        ('Hours', {
            'fields': ('is_open', 'opening_time', 'closing_time')
        }),
    )
    
    def open_badge(self, obj):
        """Display if office is open"""
        color = '#22c55e' if obj.is_open else '#ef4444'
        status = 'Open' if obj.is_open else 'Closed'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">{}</span>',
            color,
            status
        )
    open_badge.short_description = 'Status'
    
    def hours_display(self, obj):
        """Display office hours"""
        if not obj.is_open:
            return 'Closed'
        return f'{obj.opening_time} - {obj.closing_time}'
    hours_display.short_description = 'Hours'


admin_site.register(OfficeHours, OfficeHoursAdminClass)


class EmployeeDirectoryAdminClass(admin.ModelAdmin):
    list_display = ('full_name', 'title', 'department', 'office', 'phone', 'status_badge')
    list_filter = ('office', 'department', 'is_active')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'title', 'department')
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Professional Information', {
            'fields': ('title', 'department', 'office')
        }),
        ('Communication', {
            'fields': ('phone', 'extension')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def full_name(self, obj):
        """Display full name"""
        return f'{obj.user.first_name} {obj.user.last_name}'
    full_name.short_description = 'Name'
    
    def status_badge(self, obj):
        """Display active status"""
        color = '#22c55e' if obj.is_active else '#ef4444'
        status = 'Active' if obj.is_active else 'Inactive'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">{}</span>',
            color,
            status
        )
    status_badge.short_description = 'Status'


admin_site.register(EmployeeDirectory, EmployeeDirectoryAdminClass)

# Register authentication app
from authentication.admin import CustomUserAdmin
from authentication.models import CustomUser

admin_site.register(CustomUser, CustomUserAdmin)

