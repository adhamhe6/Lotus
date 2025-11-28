from django import forms
import json

class PaperAnalysisForm(forms.Form):
    ANALYSIS_TYPE_CHOICES = [
        ('summary', 'Paper Summary'),
        ('draft', 'Document Draft'),
        ('qa', 'Q&A Analysis'),
        ('system', 'Custom Prompt'),
    ]
    
    LANGUAGE_CHOICES = [
        ('ar', 'Arabic'),
        ('en', 'English'), 
        ('fr', 'French'),
    ]
    
    file = forms.FileField(
        label="Upload PDF (Optional)",
        required=False,
        help_text="Upload a PDF file for analysis"
    )
    text_content = forms.CharField(
        label="Or Enter Text Manually",
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 8, 
            'placeholder': 'Paste your scientific paper text here...',
            'style': 'font-family: monospace;'
        }),
        help_text="Enter text directly if you don't have a PDF file"
    )
    language = forms.ChoiceField(
        label="Language",
        choices=LANGUAGE_CHOICES,
        initial='en',
        help_text="Select the language for the analysis output"
    )
    analysis_type = forms.ChoiceField(
        label="Task Type",
        choices=ANALYSIS_TYPE_CHOICES,
        initial='summary',
        help_text="Choose the type of analysis to perform"
    )
    question = forms.CharField(
        label="Question",
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your question about the paper...'
        }),
        help_text="Required for Q&A analysis"
    )
    document_spec = forms.CharField(
        label="Document Specifications (JSON)",
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4, 
            'placeholder': '{\n  "DOCUMENT_TYPE": "Scientific Report",\n  "TARGET_AUDIENCE": "Researchers",\n  "TONE": "formal"\n}',
            'style': 'font-family: monospace; font-size: 0.9em;'
        }),
        help_text="JSON format for document specifications in draft mode"
    )
    custom_prompt = forms.CharField(
        label="Custom Prompt",
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Enter your custom instructions for the AI...'
        }),
        help_text="Required for custom prompt analysis"
    )

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        text_content = cleaned_data.get('text_content')
        analysis_type = cleaned_data.get('analysis_type')
        
        # Validate that either file or text is provided
        if not file and not text_content:
            raise forms.ValidationError("Either upload a PDF file or enter text content.")
        
        # Validate file type if provided
        if file and not file.name.endswith('.pdf'):
            raise forms.ValidationError("Only PDF files are allowed.")
        
        # Validate required fields based on analysis type
        if analysis_type == 'qa' and not cleaned_data.get('question'):
            raise forms.ValidationError("Question is required for Q&A analysis.")
        
        if analysis_type == 'system' and not cleaned_data.get('custom_prompt'):
            raise forms.ValidationError("Custom prompt is required for system analysis.")
        
        # Validate document_spec JSON if provided
        document_spec = cleaned_data.get('document_spec')
        if document_spec:
            try:
                json.loads(document_spec)
            except json.JSONDecodeError as e:
                raise forms.ValidationError(f"Document specifications must be valid JSON format: {str(e)}")
        
        return cleaned_data
    


