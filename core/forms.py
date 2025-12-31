from django import forms
from .models import (
    TrainingCourse, TrainingModule, UserTrainingProgress, ModuleCompletion,
    Assessment, AssessmentQuestion, AssessmentOption, AssessmentAttempt, UserResponse,
    Office, OfficeHours, EmployeeDirectory
)


# ============================================================================
# TRAINING FORMS
# ============================================================================

class TrainingCourseForm(forms.ModelForm):
    """Form for creating/editing training courses (admin use)"""
    class Meta:
        model = TrainingCourse
        fields = ('title', 'description', 'difficulty', 'is_mandatory', 'order', 'estimated_duration_minutes', 'is_active')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Course title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Course description'
            }),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'is_mandatory': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'estimated_duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TrainingModuleForm(forms.ModelForm):
    """Form for creating/editing training modules"""
    class Meta:
        model = TrainingModule
        fields = ('course', 'title', 'description', 'content_type', 'order', 'video_url', 'pdf_file', 'text_content', 'duration_minutes', 'is_required')
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Module title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Module description'
            }),
            'content_type': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'video_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/watch?v=...'
            }),
            'pdf_file': forms.FileInput(attrs={'class': 'form-control'}),
            'text_content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Enter text content...'
            }),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# ============================================================================
# ASSESSMENT FORMS
# ============================================================================

class AssessmentForm(forms.ModelForm):
    """Form for creating/editing assessments"""
    class Meta:
        model = Assessment
        fields = ('title', 'description', 'total_questions', 'passing_score', 'randomize_questions', 'randomize_options', 'time_limit_minutes', 'is_mandatory', 'is_active')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Assessment title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Assessment description'
            }),
            'total_questions': forms.NumberInput(attrs={'class': 'form-control'}),
            'passing_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100
            }),
            'randomize_questions': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'randomize_options': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'time_limit_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_mandatory': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AssessmentQuestionForm(forms.ModelForm):
    """Form for creating/editing assessment questions"""
    class Meta:
        model = AssessmentQuestion
        fields = ('assessment', 'question_text', 'difficulty', 'order', 'explanation')
        widgets = {
            'assessment': forms.Select(attrs={'class': 'form-select'}),
            'question_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Question text'
            }),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'explanation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Explanation for the correct answer'
            }),
        }


class AssessmentOptionForm(forms.ModelForm):
    """Form for creating/editing assessment options"""
    class Meta:
        model = AssessmentOption
        fields = ('question', 'option_text', 'is_correct', 'order')
        widgets = {
            'question': forms.Select(attrs={'class': 'form-select'}),
            'option_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Option text'
            }),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class QuizForm(forms.Form):
    """
    Dynamic form for taking a quiz/assessment.
    Generated based on assessment questions.
    """
    def __init__(self, assessment, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get questions (randomized if enabled)
        questions = assessment.questions.all()
        if assessment.randomize_questions:
            from django.db.models import F
            questions = questions.order_by('?')
        
        # Create a field for each question
        for question in questions:
            options = question.options.all()
            
            # Randomize options if enabled
            if assessment.randomize_options:
                options = options.order_by('?')
            
            choices = [(option.id, option.option_text) for option in options]
            
            self.fields[f'question_{question.id}'] = forms.ChoiceField(
                label=question.question_text,
                choices=choices,
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                required=True
            )


# ============================================================================
# OFFICE & DIRECTORY FORMS
# ============================================================================

class OfficeForm(forms.ModelForm):
    """Form for creating/editing office locations"""
    class Meta:
        model = Office
        fields = ('name', 'address', 'city', 'state', 'postal_code', 'country', 'timezone', 'phone', 'email', 'is_active', 'order')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Office name'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State/Province'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Postal code'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country'
            }),
            'timezone': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1-555-0000'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'office@company.com'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class OfficeHoursForm(forms.ModelForm):
    """Form for creating/editing office hours"""
    class Meta:
        model = OfficeHours
        fields = ('office', 'day_of_week', 'is_open', 'opening_time', 'closing_time')
        widgets = {
            'office': forms.Select(attrs={'class': 'form-select'}),
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
            'is_open': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'opening_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'closing_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
        }


class EmployeeDirectoryForm(forms.ModelForm):
    """Form for creating/editing employee directory entries"""
    class Meta:
        model = EmployeeDirectory
        fields = ('user', 'title', 'department', 'office', 'phone', 'extension', 'is_active')
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Job title'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Department'
            }),
            'office': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1-555-0000'
            }),
            'extension': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1234'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
