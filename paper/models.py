from django.db import models

class PaperAnalysisRun(models.Model):
    LANGUAGE_CHOICES = [
        ('ar', 'Arabic'),
        ('en', 'English'),
        ('fr', 'French'),
    ]
    
    ANALYSIS_TYPE_CHOICES = [

        ('summary', 'Summary'),
        ('draft', 'Draft'),
        ('qa', 'Q&A'),
        ('system', 'System'),
    ]
    
    uploaded_file = models.FileField(upload_to='paper_analysis/', null=True, blank=True)
    text_content = models.TextField(null=True, blank=True)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')
    analysis_type = models.CharField(max_length=10, choices=ANALYSIS_TYPE_CHOICES, default='summary')
    question = models.TextField(null=True, blank=True)  # For Q&A type
    document_spec = models.JSONField(null=True, blank=True)  # For draft type
    custom_prompt = models.TextField(null=True, blank=True)  # For system type
    result_text = models.TextField(null=True, blank=True)
    run_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Paper Analysis - {self.analysis_type} ({self.language}) at {self.run_at}"
    

