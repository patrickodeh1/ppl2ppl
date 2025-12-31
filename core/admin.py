from django.contrib import admin
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
# TRAINING ADMIN
# ============================================================================

class TrainingModuleInline(admin.TabularInline):
    model = TrainingModule
    extra = 0
    fields = ('order', 'title', 'content_type', 'duration_minutes', 'is_required')
    ordering = ['order']


@admin.register(TrainingCourse)
class TrainingCourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'is_mandatory', 'total_modules', 'order', 'is_active')
    list_filter = ('difficulty', 'is_mandatory', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    ordering = ['order']
    inlines = [TrainingModuleInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'difficulty', 'is_mandatory')
        }),
        ('Content Management', {
            'fields': ('total_modules', 'estimated_duration_minutes', 'order')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(TrainingModule)
class TrainingModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'content_type', 'order', 'duration_minutes', 'is_required')
    list_filter = ('course', 'content_type', 'is_required', 'created_at')
    search_fields = ('title', 'course__title')
    ordering = ['course', 'order']
    fieldsets = (
        ('Basic Information', {
            'fields': ('course', 'title', 'description', 'content_type', 'order')
        }),
        ('Content', {
            'fields': ('video_url', 'pdf_file', 'text_content')
        }),
        ('Metadata', {
            'fields': ('duration_minutes', 'is_required')
        }),
    )


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


@admin.register(ModuleCompletion)
class ModuleCompletionAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'is_completed', 'time_spent_minutes', 'started_at')
    list_filter = ('is_completed', 'module__course', 'started_at')
    search_fields = ('user__email', 'module__title')
    readonly_fields = ('started_at',)


# ============================================================================
# ASSESSMENT ADMIN
# ============================================================================

class AssessmentOptionInline(admin.TabularInline):
    model = AssessmentOption
    extra = 0
    fields = ('order', 'option_text', 'is_correct')
    ordering = ['order']


class AssessmentQuestionInline(admin.TabularInline):
    model = AssessmentQuestion
    extra = 0
    fields = ('order', 'question_text', 'difficulty')
    ordering = ['order']


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'total_questions', 'passing_score', 'is_mandatory', 'is_active')
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


@admin.register(AssessmentQuestion)
class AssessmentQuestionAdmin(admin.ModelAdmin):
    list_display = ('assessment', 'order', 'question_text', 'difficulty')
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


@admin.register(AssessmentOption)
class AssessmentOptionAdmin(admin.ModelAdmin):
    list_display = ('question', 'order', 'option_text', 'is_correct')
    list_filter = ('question__assessment', 'is_correct')
    search_fields = ('option_text', 'question__question_text')
    ordering = ['question', 'order']


class UserResponseInline(admin.TabularInline):
    model = UserResponse
    extra = 0
    fields = ('question', 'selected_option', 'is_correct')
    readonly_fields = ('question', 'selected_option', 'is_correct')
    can_delete = False


@admin.register(AssessmentAttempt)
class AssessmentAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'assessment', 'score_percentage', 'passed', 'status', 'started_at')
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


@admin.register(UserResponse)
class UserResponseAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_option', 'is_correct')
    list_filter = ('is_correct', 'attempt__assessment')
    search_fields = ('attempt__user__email', 'question__question_text')
    readonly_fields = ('attempt', 'question', 'answered_at')


# ============================================================================
# CERTIFICATION ADMIN
# ============================================================================

@admin.register(UserCertification)
class UserCertificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_certified', 'certification_date', 'expires_at')
    list_filter = ('is_certified', 'certification_date')
    search_fields = ('user__email', 'user__full_name')
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


# ============================================================================
# OFFICE SCHEDULE ADMIN
# ============================================================================

class OfficeHoursInline(admin.TabularInline):
    model = OfficeHours
    extra = 0
    fields = ('day_of_week', 'is_open', 'opening_time', 'closing_time')
    ordering = ['day_of_week']


@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'timezone', 'is_active', 'order')
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


@admin.register(OfficeHours)
class OfficeHoursAdmin(admin.ModelAdmin):
    list_display = ('office', 'day_of_week', 'is_open', 'opening_time', 'closing_time')
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


@admin.register(EmployeeDirectory)
class EmployeeDirectoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'department', 'office', 'phone', 'is_active')
    list_filter = ('office', 'department', 'is_active')
    search_fields = ('user__email', 'user__full_name', 'title', 'department')
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
