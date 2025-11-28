from django.shortcuts import render
from .models import *
from .forms import *
import requests
import json

def perform_paper_analysis(file=None, text_content=None, language='en', analysis_type='summary', 
                          question=None, document_spec=None, custom_prompt=None):
    """
    Connect to the FastAPI backend for paper analysis
    """
    # FastAPI endpoint URL - adjust this to match your FastAPI server
    API_URL = "http://localhost:800/process-text"  # Change this to your FastAPI server URL
    
    # Prepare the form data
    data = {
        "language": language,
        "type": analysis_type,
    }
    
    # Add optional fields if provided
    if text_content:
        data["text"] = text_content
    if question:
        data["question"] = question
    if custom_prompt:
        data["prompt"] = custom_prompt
    if document_spec:
        data["document_spec"] = json.dumps(document_spec)
    
    # Prepare files for upload
    files = {}
    if file:
        files = {"file": file}
    
    try:
        # Make request to FastAPI backend
        response = requests.post(API_URL, data=data, files=files, stream=True, timeout=60)
        
        if response.status_code == 200:
            # Stream and combine the response chunks
            full_result = ""
            for line in response.iter_lines():
                if line:
                    try:
                        obj = json.loads(line.decode("utf-8"))
                        chunk = obj.get("chunk", "")
                        full_result += chunk
                    except json.JSONDecodeError:
                        continue
            
            return full_result
        else:
            return f"Error: API returned status code {response.status_code}\n{response.text}"
            
    except requests.exceptions.RequestException as e:
        return f"Error connecting to AI service: {str(e)}\n\nPlease ensure the Paper AI backend is running on localhost:8000"

def paper_analysis_dashboard(request):
    context = {
        'form': PaperAnalysisForm(),
        'result': None,
        'error': None,
        'has_results': False
    }

    if request.method == "POST":
        form = PaperAnalysisForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Prepare data for the analysis
                file = request.FILES.get('file')
                text_content = form.cleaned_data['text_content']
                language = form.cleaned_data['language']
                analysis_type = form.cleaned_data['analysis_type']
                question = form.cleaned_data.get('question')
                document_spec = form.cleaned_data.get('document_spec')
                custom_prompt = form.cleaned_data.get('custom_prompt')

                # Convert document_spec to dict if provided
                document_spec_dict = None
                if document_spec:
                    try:
                        document_spec_dict = json.loads(document_spec)
                    except json.JSONDecodeError as e:
                        context['error'] = f"Invalid JSON in document specifications: {str(e)}"
                        return render(request, 'products/paper_analysis_dashboard.html', context)

                # Call the actual FastAPI backend
                result_text = perform_paper_analysis(
                    file=file,
                    text_content=text_content,
                    language=language,
                    analysis_type=analysis_type,
                    question=question,
                    document_spec=document_spec_dict,
                    custom_prompt=custom_prompt
                )

                # Save the run
                run_record = PaperAnalysisRun.objects.create(
                    uploaded_file=file,
                    text_content=text_content,
                    language=language,
                    analysis_type=analysis_type,
                    question=question,
                    document_spec=document_spec_dict,
                    custom_prompt=custom_prompt,
                    result_text=result_text
                )

                context.update({
                    'form': form,
                    'result': result_text,
                    'has_results': True,
                    'run_id': run_record.id,
                    'run_at': run_record.run_at,
                    'analysis_type': analysis_type,
                    'language': language
                })

            except Exception as e:
                context['error'] = f"Error processing analysis: {str(e)}"
        else:
            context['error'] = "Please correct the errors in the form."

    return render(request, 'products/paper_analysis_dashboard.html', context)
    

