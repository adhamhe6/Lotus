from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
import json


class Product(models.Model):
    name = models.CharField(max_length=200)
    tagline = models.CharField(max_length=300)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Feature(models.Model):
    FEATURE_CATEGORIES = [
        ('import', 'Import'),
        ('organize', 'Organize'),
        ('explore', 'Explore'),
        ('collaborate', 'Collaborate'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='features')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=FEATURE_CATEGORIES)
    icon = models.CharField(max_length=100, help_text="Font Awesome icon class")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.product.name} - {self.title}"

class ProcessStep(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)
    icon = models.CharField(max_length=100)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Benefit(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Testimonial(models.Model):
    author = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    content = models.TextField()
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author} - {self.rating} stars"

#==============analytics tool=======================
class DecisionAnalysisRun(models.Model):
    uploaded_file = models.FileField(upload_to='decision_runs/')
    result_json = models.JSONField()
    run_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Decision Run at {self.run_at.strftime('%Y-%m-%d %H:%M')}"
    
#================analysis tool====================
class QuantAnalysisRun(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('ar', 'Arabic'),
    ]
    
    uploaded_file = models.FileField(upload_to='quant_uploads/')
    y_variable = models.CharField(max_length=128)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')
    result_json = models.JSONField(null=True, blank=True)
    run_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quant Analysis - {self.y_variable} ({self.language}) at {self.run_at}"

#================= Scientific Paper AI Tool =================

#========================================content_analyzer==


class ContentAnalysis(models.Model):
    ANALYSIS_TYPES = [
        ('words_only', 'Words Only'),
        ('words_synonyms', 'Words with Synonyms'),
    ]
    
    LANGUAGES = [
        ('en', 'English'),
        ('ar', 'Arabic'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default="Content Analysis")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Analysis parameters
    analysis_type = models.CharField(max_length=20, choices=ANALYSIS_TYPES, default='words_only')
    report_language = models.CharField(max_length=10, choices=LANGUAGES, default='en')
    keywords = models.TextField(help_text="Comma-separated keywords")
    
    # Results storage
    results_json = models.JSONField(null=True, blank=True)
    file_contents_json = models.JSONField(null=True, blank=True)
    
    # Status
    is_completed = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    def get_keywords_list(self):
        """Convert comma-separated keywords to list"""
        return [k.strip() for k in self.keywords.split(',') if k.strip()]
    
    def get_file_contents(self):
        """Get file contents from JSON"""
        if self.file_contents_json:
            return self.file_contents_json
        return {}
    
    def get_results(self):
        """Get analysis results from JSON"""
        if self.results_json:
            return self.results_json
        return {}
    
    class Meta:
        ordering = ['-created_at']


class AnalysisFile(models.Model):
    FILE_TYPES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('text', 'Text'),
    ]
    
    analysis = models.ForeignKey(ContentAnalysis, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='content_analysis/')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.file_name
    
    def save(self, *args, **kwargs):
        if not self.file_name:
            self.file_name = self.file.name
        super().save(*args, **kwargs)


class ChatMessage(models.Model):
    analysis = models.ForeignKey(ContentAnalysis, on_delete=models.CASCADE, related_name='chat_messages')
    role = models.CharField(max_length=20, choices=[('user', 'User'), ('assistant', 'Assistant')])
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']


class GeneratedReport(models.Model):
    REPORT_TYPES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ]
    
    analysis = models.ForeignKey(ContentAnalysis, on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES)
    report_file = models.FileField(upload_to='content_reports/')
    language = models.CharField(max_length=10, choices=ContentAnalysis.LANGUAGES)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.analysis.name} - {self.get_report_type_display()} - {self.language}"
