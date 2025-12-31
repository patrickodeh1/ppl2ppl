from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from authentication.models import CustomUser


# ============================================================================
# TRAINING MODULE MODELS
# ============================================================================

class TrainingCourse(models.Model):
    """
    Main training course container.
    Sequential learning curriculum with video, PDF, and text modules.
    """
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    is_active = models.BooleanField(default=True)
    is_mandatory = models.BooleanField(default=True, help_text="Must be completed before certification")
    
    # Ordering and sequencing
    order = models.PositiveIntegerField(default=0, help_text="Display order in course list")
    
    # Content metadata
    total_modules = models.PositiveIntegerField(default=0, editable=False)
    estimated_duration_minutes = models.PositiveIntegerField(default=0, help_text="Estimated total time in minutes")
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Training Course"
        verbose_name_plural = "Training Courses"
    
    def __str__(self):
        return self.title
    
    def update_module_count(self):
        """Update total module count from related modules"""
        self.total_modules = self.modules.count()
        self.save()


class TrainingModule(models.Model):
    """
    Individual learning modules (videos, PDFs, text content).
    Each module is sequential within a course.
    """
    CONTENT_TYPE_CHOICES = [
        ('video', 'Video'),
        ('pdf', 'PDF Document'),
        ('text', 'Text Content'),
        ('mixed', 'Mixed Content'),
    ]
    
    course = models.ForeignKey(TrainingCourse, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    
    # Ordering within course
    order = models.PositiveIntegerField(default=0)
    
    # Content storage
    video_url = models.URLField(blank=True, help_text="URL for video content (e.g., YouTube, Vimeo)")
    pdf_file = models.FileField(upload_to='training/pdfs/%Y/%m/', blank=True)
    text_content = models.TextField(blank=True)
    
    # Metadata
    duration_minutes = models.PositiveIntegerField(default=0, help_text="Duration in minutes for video")
    is_required = models.BooleanField(default=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['course', 'order', 'id']
        unique_together = ('course', 'order')
        verbose_name = "Training Module"
        verbose_name_plural = "Training Modules"
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class UserTrainingProgress(models.Model):
    """
    Track user progress through training courses and modules.
    Records completion status and timestamps.
    """
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('locked', 'Locked'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='training_progress')
    course = models.ForeignKey(TrainingCourse, on_delete=models.CASCADE)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    progress_percentage = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'course')
        ordering = ['-updated_at']
        verbose_name = "User Training Progress"
        verbose_name_plural = "User Training Progress"
    
    def __str__(self):
        return f"{self.user.email} - {self.course.title} ({self.status})"
    
    def mark_started(self):
        """Mark course as started"""
        if self.status == 'not_started':
            self.status = 'in_progress'
            self.started_at = timezone.now()
            self.save()
    
    def mark_completed(self):
        """Mark course as completed"""
        self.status = 'completed'
        self.progress_percentage = 100
        self.completed_at = timezone.now()
        self.save()
    
    def update_progress(self, percentage):
        """Update progress percentage"""
        self.progress_percentage = min(100, max(0, percentage))
        if self.status == 'not_started' and percentage > 0:
            self.status = 'in_progress'
            self.started_at = timezone.now()
        self.save()


class ModuleCompletion(models.Model):
    """
    Track completion of individual modules by users.
    Links users to specific modules they've completed.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='module_completions')
    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE, related_name='user_completions')
    
    # Time tracking
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent_minutes = models.PositiveIntegerField(default=0)
    
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('user', 'module')
        ordering = ['-completed_at']
        verbose_name = "Module Completion"
        verbose_name_plural = "Module Completions"
    
    def __str__(self):
        return f"{self.user.email} - {self.module.title}"
    
    def mark_completed(self, time_spent=0):
        """Mark module as completed"""
        self.is_completed = True
        self.completed_at = timezone.now()
        self.time_spent_minutes = time_spent
        self.save()


# ============================================================================
# ASSESSMENT MODULE MODELS
# ============================================================================

class Assessment(models.Model):
    """
    Assessment/Quiz configuration.
    Set passing threshold (85%), randomization options, etc.
    """
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Passing threshold
    passing_score = models.PositiveIntegerField(
        default=85,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Minimum percentage score to pass (default: 85%)"
    )
    
    # Question settings
    total_questions = models.PositiveIntegerField(help_text="Total number of questions in assessment")
    randomize_questions = models.BooleanField(
        default=True,
        help_text="Randomize question order for each user"
    )
    randomize_options = models.BooleanField(
        default=True,
        help_text="Randomize answer options for each question"
    )
    
    # Time settings
    time_limit_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Optional time limit in minutes"
    )
    
    # Control
    is_active = models.BooleanField(default=True)
    is_mandatory = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Assessment"
        verbose_name_plural = "Assessments"
    
    def __str__(self):
        return self.title


class AssessmentQuestion(models.Model):
    """
    Individual quiz questions with multiple choice options.
    """
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    
    # Question metadata
    explanation = models.TextField(blank=True, help_text="Explanation shown after answering")
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['assessment', 'order']
        unique_together = ('assessment', 'order')
    
    def __str__(self):
        return f"{self.assessment.title} - Q{self.order}"


class AssessmentOption(models.Model):
    """
    Multiple choice options for each question.
    Only one should be marked as correct.
    """
    question = models.ForeignKey(AssessmentQuestion, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['question', 'order']
        unique_together = ('question', 'order')
    
    def __str__(self):
        return f"{self.question.question_text[:50]} - {self.option_text[:30]}"


class AssessmentAttempt(models.Model):
    """
    Track each user's assessment attempt.
    Records score, timestamp, and whether they passed.
    """
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assessment_attempts')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    
    # Scoring
    total_questions = models.PositiveIntegerField()
    correct_answers = models.PositiveIntegerField(default=0)
    score_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Certification status
    passed = models.BooleanField(default=False)
    
    # Time tracking
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    time_taken_minutes = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Assessment Attempt"
        verbose_name_plural = "Assessment Attempts"
    
    def __str__(self):
        return f"{self.user.email} - {self.assessment.title} ({self.score_percentage}%)"
    
    def calculate_score(self):
        """Calculate percentage score from correct answers"""
        if self.total_questions > 0:
            self.score_percentage = (self.correct_answers / self.total_questions) * 100
            self.passed = self.score_percentage >= self.assessment.passing_score
        self.save()
    
    def submit(self):
        """Submit the assessment"""
        self.status = 'submitted'
        self.submitted_at = timezone.now()
        self.save()


class UserResponse(models.Model):
    """
    Track individual question responses during an assessment attempt.
    Records which option user selected for each question.
    """
    attempt = models.ForeignKey(AssessmentAttempt, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(AssessmentQuestion, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(AssessmentOption, on_delete=models.CASCADE, null=True, blank=True)
    
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('attempt', 'question')
    
    def __str__(self):
        return f"{self.attempt.user.email} - Q{self.question.order}"


# ============================================================================
# CERTIFICATION MODEL
# ============================================================================

class UserCertification(models.Model):
    """
    Certification status for users.
    Updated when user passes assessment with score >= 85%.
    This gates access to Office Schedule and other features.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='certification')
    
    is_certified = models.BooleanField(default=False)
    certification_date = models.DateTimeField(null=True, blank=True)
    
    # Track passing attempt
    passing_attempt = models.ForeignKey(AssessmentAttempt, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Expiration (optional - for recurring certifications)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Optional expiration date for certification")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Certification"
        verbose_name_plural = "User Certifications"
    
    def __str__(self):
        status = "Certified" if self.is_certified else "Not Certified"
        return f"{self.user.email} - {status}"
    
    def certify(self, attempt):
        """Mark user as certified"""
        self.is_certified = True
        self.certification_date = timezone.now()
        self.passing_attempt = attempt
        self.save()


# ============================================================================
# OFFICE SCHEDULE MODELS
# ============================================================================

class Office(models.Model):
    """
    Physical office locations.
    Supports multiple branches with timezone info.
    """
    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='USA')
    
    # Timezone for schedule display
    timezone = models.CharField(
        max_length=50,
        default='America/New_York',
        help_text="IANA timezone for this office (e.g., America/New_York)"
    )
    
    # Contact
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Office"
        verbose_name_plural = "Offices"
    
    def __str__(self):
        return f"{self.name} ({self.city})"


class OfficeHours(models.Model):
    """
    Operating hours for each office.
    Supports different schedules for different days.
    """
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name='hours')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    
    is_open = models.BooleanField(default=True)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('office', 'day_of_week')
        ordering = ['office', 'day_of_week']
        verbose_name = "Office Hours"
        verbose_name_plural = "Office Hours"
    
    def __str__(self):
        day_name = dict(self.DAY_CHOICES)[self.day_of_week]
        if self.is_open:
            return f"{self.office.name} - {day_name}: {self.opening_time} - {self.closing_time}"
        return f"{self.office.name} - {day_name}: Closed"


class EmployeeDirectory(models.Model):
    """
    Employee directory for admin interface.
    Contains communication links (SMS, phone).
    Only visible to certified users and admins.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='directory_entry')
    
    # Professional info
    title = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=255, blank=True)
    office = models.ForeignKey(Office, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Communication
    phone = models.CharField(max_length=20, blank=True)
    extension = models.CharField(max_length=10, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Employee Directory"
        verbose_name_plural = "Employee Directory"
    
    def __str__(self):
        return f"{self.user.full_name} - {self.title or 'Staff'}"
