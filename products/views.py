import io
import json
import base64
import requests
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from django.conf import settings

from .tools.analysis_tool import perform_analysis, perform_categorical_analysis, generate_plot
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import *
from .models import *

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.files.base import ContentFile
from django.utils import timezone

from .analysis_utils import *

def products(request):
    # Get the active product
    product = Product.objects.filter(is_active=True).first()
    
    # Get all related data
    features = Feature.objects.filter(is_active=True, product=product)
    process_steps = ProcessStep.objects.all()
    benefits = Benefit.objects.all()
    testimonials = Testimonial.objects.filter(is_active=True)
    
    # Group features by category
    feature_categories = {}
    for feature in features:
        if feature.category not in feature_categories:
            feature_categories[feature.category] = []
        feature_categories[feature.category].append(feature)
    
    context = {
        'product': product,
        'features': features,
        'process_steps': process_steps,
        'benefits': benefits,
        'testimonials': testimonials,
        'feature_categories': feature_categories,
    }
    
    return render(request, 'products/products.html', context)


#==============================================analytics code==============================

# ---------------------------
# Helpers: parsing & sim
# ---------------------------
def parse_params(raw, decision):
    if pd.isna(raw):
        raise ValueError(f"Missing params for decision '{decision}'")
    s = str(raw)
    try:
        return json.loads(s)
    except Exception:
        # try replacing single quotes with double quotes
        try:
            return json.loads(s.replace("'", '"'))
        except Exception as e:
            raise ValueError(f"Invalid params JSON for '{decision}': {e}")

def draw_distribution_values(distribution, params, runs):
    dist = distribution.strip().lower()
    if dist == "normal":
        return np.random.normal(params["mean"], params["std"], runs)
    elif dist == "uniform":
        return np.random.uniform(params["low"], params["high"], runs)
    elif dist == "triangular":
        return np.random.triangular(params["left"], params["mode"], params["right"], runs)
    elif dist == "beta":
        scale = params.get("scale", 1)
        return np.random.beta(params["a"], params["b"], runs) * scale
    elif dist == "exponential":
        return np.random.exponential(params["scale"], runs)
    elif dist == "lognormal":
        return np.random.lognormal(params["mean"], params["sigma"], runs)
    elif dist == "poisson":
        return np.random.poisson(params["lam"], runs)
    elif dist == "gamma":
        return np.random.gamma(params["shape"], params["scale"], runs)
    elif dist in ("chi-square", "chisquare", "chi2"):
        return np.random.chisquare(params["df"], runs)
    elif dist == "binomial":
        return np.random.binomial(params["n"], params["p"], runs)
    else:
        raise ValueError(f"Unsupported distribution '{distribution}'")

def run_simulation_dataframe(df, n_simulations=1000):
    """
    Returns a DataFrame with columns: decision, value, success
    (concatenated for all decisions)
    """
    frames = []
    has_group = "group" in df.columns
    for _, row in df.iterrows():
        decision = str(row["decision"])
        distribution = str(row["distribution"])
        params = parse_params(row["params"], decision)
        p_success = float(row["success_prob"])
        if not (0 <= p_success <= 1):
            raise ValueError(f"success_prob must be between 0 and 1 (decision '{decision}')")
        values = draw_distribution_values(distribution, params, n_simulations)
        successes = np.random.binomial(1, p_success, n_simulations)
        d = {"decision": [decision]*n_simulations, "value": values, "success": successes}
        if has_group:
            group_val = row.get("group", None)
            d["group"] = [group_val]*n_simulations
        frames.append(pd.DataFrame(d))
    if not frames:
        return pd.DataFrame(columns=["decision","value","success"])
    return pd.concat(frames, ignore_index=True)

def summarize_results(results_df):
    agg_dict = {
        "expected_value": ("value", "mean"),
        "success_rate": ("success", "mean"),
        "avg_cost": ("value", "median"),
        "std_value": ("value", "std"),
        "min_value": ("value", "min"),
        "max_value": ("value", "max"),
        "n_obs": ("value", "count"),
    }
    if "group" in results_df.columns:
        agg_dict["group"] = ("group", "first")
    summary = results_df.groupby("decision").agg(**agg_dict).reset_index()
    # Make numeric columns plain python types for JSON
    for col in ["expected_value","success_rate","avg_cost","std_value","min_value","max_value"]:
        if col in summary.columns:
            summary[col] = summary[col].astype(float)
    return summary

# ---------------------------
# Chart helper: matplotlib -> base64
# ---------------------------
def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return f"data:image/png;base64,{img_b64}"

def make_ecdf_plot(df, decisions):
    fig, ax = plt.subplots(figsize=(6,4))
    for d in decisions:
        vals = np.sort(df[df["decision"]==d]["value"].values)
        if vals.size == 0:
            continue
        y = np.arange(1, len(vals)+1) / len(vals)
        ax.step(vals, y, where="post", label=d)
    ax.set_xlabel("Value")
    ax.set_ylabel("Cumulative Probability")
    ax.set_title("ECDF")
    ax.legend()
    return fig_to_base64(fig)

def make_hist_plot(df, decisions):
    fig, ax = plt.subplots(figsize=(6,4))
    for d in decisions:
        vals = df[df["decision"]==d]["value"].values
        ax.hist(vals, bins=30, alpha=0.5, label=d)
    ax.set_xlabel("Value")
    ax.set_ylabel("Count")
    ax.set_title("Histogram")
    ax.legend()
    return fig_to_base64(fig)

def make_box_plot(df, decisions):
    fig, ax = plt.subplots(figsize=(6,4))
    data = [df[df["decision"]==d]["value"].values for d in decisions]
    ax.boxplot(data, labels=decisions, showfliers=False)
    ax.set_xlabel("Decision")
    ax.set_ylabel("Value")
    ax.set_title("Boxplot")
    return fig_to_base64(fig)

def make_success_bar(summary_df):
    fig, ax = plt.subplots(figsize=(6,4))
    ax.bar(summary_df["decision"], summary_df["success_rate"])
    ax.set_xlabel("Decision")
    ax.set_ylabel("Success Rate")
    ax.set_title("Success Rate by Decision")
    return fig_to_base64(fig)

def make_scatter_ev_sr(summary_df):
    fig, ax = plt.subplots(figsize=(6,4))
    ax.scatter(summary_df["expected_value"], summary_df["success_rate"])
    for _, row in summary_df.iterrows():
        ax.text(row["expected_value"], row["success_rate"], str(row["decision"]))
    ax.set_xlabel("Expected Value")
    ax.set_ylabel("Success Rate")
    ax.set_title("EV vs Success Rate")
    return fig_to_base64(fig)

# ---------------------------
# API endpoint (curl/external)
# ---------------------------
@csrf_exempt
def decision_analysis_api(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST requests are allowed.")

    if "file" not in request.FILES:
        return HttpResponseBadRequest("CSV file is required (key='file').")

    runs = int(request.POST.get("runs", 1000))
    file = request.FILES["file"]

    try:
        df = pd.read_csv(file)
    except Exception as e:
        return HttpResponseBadRequest(f"Invalid CSV file: {e}")

    required_cols = {"decision", "distribution", "params", "success_prob"}
    if not required_cols.issubset(df.columns):
        return HttpResponseBadRequest(f"CSV must contain columns: {required_cols}")

    # run simulation (we use aggregated summary to keep API light)
    results_df = run_simulation_dataframe(df, n_simulations=int(runs))
    summary = summarize_results(results_df)

    results = summary.to_dict(orient="records")

    run_record = DecisionAnalysisRun.objects.create(
        uploaded_file=file,
        result_json=results,
    )

    return JsonResponse({
        "run_id": run_record.id,
        "run_at": run_record.run_at.isoformat(),
        "results": results,
    })

# ---------------------------
# Dashboard page (form + results)
# ---------------------------
def decision_dashboard(request):
    context = {"summary_table_html": None, "images": None, "error": None}
    if request.method == "POST":
        file = request.FILES.get("file")
        runs = int(request.POST.get("runs", 1000))
        if not file:
            context["error"] = "Please upload a CSV file."
            return render(request, "products/decision_dashboard.html", context)

        try:
            df = pd.read_csv(file)
        except Exception as e:
            context["error"] = f"Invalid CSV: {e}"
            return render(request, "products/decision_dashboard.html", context)

        required_cols = {"decision", "distribution", "params", "success_prob"}
        if not required_cols.issubset(df.columns):
            context["error"] = f"CSV must contain columns: {required_cols}"
            return render(request, "products/decision_dashboard.html", context)

        try:
            results_df = run_simulation_dataframe(df, n_simulations=runs)
            summary_df = summarize_results(results_df)

            # Save run
            run_record = DecisionAnalysisRun.objects.create(
                uploaded_file=file,
                result_json=summary_df.to_dict(orient="records"),
            )

            # Build HTML table for summary
            context["summary_table_html"] = summary_df.to_html(
                index=False, classes="table table-striped", float_format="%.3f"
            )

            # Generate charts
            decisions = summary_df["decision"].tolist()
            images = {
                "ecdf": make_ecdf_plot(results_df, decisions),
                "hist": make_hist_plot(results_df, decisions),
                "box": make_box_plot(results_df, decisions),
                "success_bar": make_success_bar(summary_df),
                "ev_sr": make_scatter_ev_sr(summary_df),
            }
            context["images"] = images
            context["run_id"] = run_record.id
            context["run_at"] = run_record.run_at
        except Exception as e:
            context["error"] = str(e)

    return render(request, "products/decision_dashboard.html", context)

#============================================analysis code====================================================

# Import your analysis functions (make sure they're in the same directory)
try:
    from .tools.analysis_tool import perform_analysis, perform_categorical_analysis, generate_plot, generate_bar_plot
except ImportError:
    # Fallback imports - you'll need to integrate the actual functions
    def perform_analysis(df, x_col, y_col, lang='en'):
        # Mock implementation - replace with actual function
        correlation = np.corrcoef(df[x_col], df[y_col])[0,1]
        if np.isnan(correlation):
            correlation = 0.0
        p_value = 0.001 if abs(correlation) > 0.5 else 0.5
        
        # Generate mock plot
        plt.figure(figsize=(8, 5))
        plt.scatter(df[x_col], df[y_col], alpha=0.5)
        plt.title(f"{x_col} vs {y_col}")
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        
        interpretation = f"Correlation: {correlation:.3f}, p-value: {p_value:.3f}"
        return correlation, p_value, buf, interpretation

    def perform_categorical_analysis(df, cat_col, y_col, lang='en'):
        # Mock implementation - replace with actual function
        summary_df = df.groupby(cat_col)[y_col].agg(['count', 'mean']).reset_index()
        summary_df.columns = [cat_col, 'Count', f'Mean {y_col}']
        
        # Generate mock plot
        plt.figure(figsize=(8, 5))
        df.groupby(cat_col)[y_col].mean().plot(kind='bar')
        plt.title(f"Mean {y_col} by {cat_col}")
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        
        interpretation = f"Analysis of {cat_col} vs {y_col}"
        return summary_df, buf, interpretation

def quant_analysis_dashboard(request):
    context = {
        'form': QuantAnalysisForm(),
        'numeric_results': [],
        'categorical_results': [],
        'error': None,
        'has_results': False
    }

    if request.method == "POST":
        form = QuantAnalysisForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            y_var = form.cleaned_data['y_variable']
            language = form.cleaned_data['language']
            
            try:
                # Read and validate data
                df = pd.read_csv(file)
                
                if y_var not in df.columns:
                    context['error'] = f"Column '{y_var}' not found in the CSV file. Available columns: {', '.join(df.columns)}"
                    return render(request, 'products/quant_analysis_dashboard.html', context)
                
                # Validate that Y variable is numeric
                if not np.issubdtype(df[y_var].dtype, np.number):
                    context['error'] = f"Target variable '{y_var}' must be numeric for quantitative analysis."
                    return render(request, 'products/quant_analysis_dashboard.html', context)
                
                # Identify variable types
                numeric_cols = [col for col in df.select_dtypes(include=np.number).columns 
                               if col != y_var and df[col].nunique() > 1]
                categorical_cols = [col for col in df.select_dtypes(include=['object']).columns 
                                   if col != y_var and 2 <= df[col].nunique() <= 20]
                
                # Perform numeric analyses
                numeric_results = []
                # In the numeric analysis section of your views.py
                for x_col in numeric_cols[:10]:
                    try:
                        r_val, p_val, plot_buffer, interpretation = perform_analysis(
                            df, x_col, y_var, lang=language
                        )
                        plot_base64 = base64.b64encode(plot_buffer.getvalue()).decode('utf-8')
                        numeric_results.append({
                            'x_variable': x_col,
                            'correlation': r_val,
                            'correlation_abs': abs(r_val),  # Add this line
                            'p_value': p_val,
                            'plot': plot_base64,
                            'interpretation': interpretation
                        })
                    except Exception as e:
                        print(f"Error analyzing {x_col}: {e}")
                        continue
                
                # Perform categorical analyses
                categorical_results = []
                for cat_col in categorical_cols[:10]:  # Limit to first 10
                    try:
                        summary_df, plot_buffer, interpretation = perform_categorical_analysis(
                            df, cat_col, y_var, lang=language
                        )
                        if summary_df is not None:
                            plot_base64 = base64.b64encode(plot_buffer.getvalue()).decode('utf-8')
                            # Convert DataFrame to HTML for display
                            summary_html = summary_df.to_html(
                                classes='table table-striped', 
                                index=False, 
                                float_format='%.3f'
                            )
                            categorical_results.append({
                                'category_variable': cat_col,
                                'summary_table': summary_html,
                                'plot': plot_base64,
                                'interpretation': interpretation
                            })
                    except Exception as e:
                        print(f"Error analyzing categorical {cat_col}: {e}")
                        continue
                
                # Save analysis run
                run_record = QuantAnalysisRun.objects.create(
                    uploaded_file=file,
                    y_variable=y_var,
                    language=language
                )
                
                context.update({
                    'form': form,
                    'numeric_results': numeric_results,
                    'categorical_results': categorical_results,
                    'has_results': True,
                    'y_variable': y_var,
                    'run_id': run_record.id,
                    'run_at': run_record.run_at,
                    'language': language
                })
                
            except Exception as e:
                context['error'] = f"Error processing file: {str(e)}"
        else:
            context['error'] = "Please correct the errors in the form."
    
    return render(request, 'products/quant_analysis_dashboard.html', context)

@csrf_exempt
def quant_analysis_api(request):
    """API endpoint for quantitative analysis"""
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST requests allowed")
    
    if 'file' not in request.FILES:
        return HttpResponseBadRequest("CSV file is required")
    
    file = request.FILES['file']
    y_var = request.POST.get('y_variable')
    language = request.POST.get('language', 'en')
    
    if not y_var:
        return HttpResponseBadRequest("y_variable parameter is required")
    
    try:
        df = pd.read_csv(file)
        if y_var not in df.columns:
            return HttpResponseBadRequest(f"Column '{y_var}' not found in CSV")
        
        # Perform analysis (similar to dashboard but return JSON)
        results = {
            'numeric_analyses': [],
            'categorical_analyses': []
        }
        
        # Add your analysis logic here...
        
        run_record = QuantAnalysisRun.objects.create(
            uploaded_file=file,
            y_variable=y_var,
            language=language
        )
        
        return JsonResponse({
            'run_id': run_record.id,
            'results': results
        })
        
    except Exception as e:
        return HttpResponseBadRequest(f"Analysis error: {str(e)}")
    

#========================================paper=================

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
    

#========================simple test content_analyzer====================
@login_required
def test_perplexity_api(request):
    """Test view to verify Perplexity API connection"""
    if request.method == 'POST':
        test_message = request.POST.get('test_message', 'Hello, are you working?')
        
        try:
            response = chat_with_perplexity(test_message)
            
            return JsonResponse({
                'status': 'success',
                'test_message': test_message,
                'api_response': response,
                'api_key_set': bool(settings.PERPLEXITY_API_KEY)
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': str(e)
            })
    
    return render(request, 'content_analyzer/test_api.html')
#========================content_analyzer====================

@login_required
def content_analyzer_home(request):
    """Main content analyzer dashboard"""
    analyses = ContentAnalysis.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    if request.method == 'POST':
        form = ContentAnalysisForm(request.POST, request.FILES)
        if form.is_valid():
            # Create analysis
            analysis = form.save(commit=False)
            analysis.user = request.user
            analysis.save()
            
            # Handle file uploads
            files = request.FILES.getlist('files')
            file_contents = {}
            
            for file in files:
                # Save file to database
                file_type = 'text'
                if file.name.endswith('.pdf'):
                    file_type = 'pdf'
                elif file.name.endswith(('.xlsx', '.xls')):
                    file_type = 'excel'
                elif file.name.endswith('.csv'):
                    file_type = 'csv'
                
                analysis_file = AnalysisFile.objects.create(
                    analysis=analysis,
                    file=file,
                    file_name=file.name,
                    file_type=file_type
                )
                
                # Extract text content
                try:
                    file_content = extract_text_from_file(file, file.name)
                    file_contents[file.name] = file_content
                except Exception as e:
                    analysis.error_message = str(e)
                    analysis.save()
                    return render(request, 'content_analyzer/error.html', {
                        'error': str(e),
                        'analysis': analysis
                    })
            
            # Perform analysis
            try:
                keywords = analysis.get_keywords_list()
                include_synonyms = analysis.analysis_type == 'words_synonyms'
                
                results = analyze_content(file_contents, keywords, include_synonyms)
                
                # Save results
                analysis.file_contents_json = file_contents
                analysis.results_json = results
                analysis.is_completed = True
                analysis.save()
                
                return redirect('content_analysis_results', analysis_id=analysis.id)
                
            except Exception as e:
                analysis.error_message = str(e)
                analysis.save()
                return render(request, 'content_analyzer/error.html', {
                    'error': str(e),
                    'analysis': analysis
                })
    else:
        form = ContentAnalysisForm()
    
    return render(request, 'content_analyzer/home.html', {
        'form': form,
        'analyses': analyses
    })

@login_required
def content_analysis_results(request, analysis_id):
    """Display analysis results with AI insights"""
    analysis = get_object_or_404(ContentAnalysis, id=analysis_id, user=request.user)
    
    if not analysis.is_completed:
        return render(request, 'content_analyzer/error.html', {
            'error': 'Analysis not completed yet',
            'analysis': analysis
        })
    
    results = analysis.get_results()
    file_contents = analysis.get_file_contents()
    
    # Get AI insights for the analysis
    ai_insights = None
    if results and results.get('summary'):
        try:
            # Create a summary prompt for AI insights
            keywords_summary = ", ".join([f"{item['keyword']} ({item['count']} occurrences)" 
                                        for item in results['summary'][:5]])
            
            insight_prompt = f"""
            Based on this keyword analysis: {keywords_summary}
            Total files analyzed: {results.get('total_files', 0)}
            
            Please provide brief insights about:
            1. The most prominent themes
            2. Any interesting patterns in keyword distribution
            3. Suggestions for further analysis
            """
            
            ai_insights = chat_with_perplexity(insight_prompt)
        except Exception as e:
            # Don't fail the whole page if AI insights fail
            ai_insights = f"AI insights temporarily unavailable: {str(e)}"
    
    return render(request, 'content_analyzer/results.html', {
        'analysis': analysis,
        'results': results,
        'file_contents': file_contents,
        'ai_insights': ai_insights
    })

# @login_required
# def download_report(request, analysis_id, report_type):
#     """Download analysis report"""
#     analysis = get_object_or_404(ContentAnalysis, id=analysis_id, user=request.user)
    
#     if not analysis.is_completed:
#         return HttpResponse("Analysis not completed", status=400)
    
#     results = analysis.get_results()
#     language = analysis.report_language
    
#     try:
#         if report_type == 'pdf':
#             buffer = create_pdf_report(results, language)
#             response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
#             response['Content-Disposition'] = f'attachment; filename="content_analysis_{analysis.id}_{language}.pdf"'
            
#         elif report_type == 'excel':
#             buffer = create_excel_report(results, language)
#             response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#             response['Content-Disposition'] = f'attachment; filename="content_analysis_{analysis.id}_{language}.xlsx"'
            
#         elif report_type == 'csv':
#             buffer = create_csv_report(results, language)
#             response = HttpResponse(buffer.getvalue(), content_type='text/csv')
#             response['Content-Disposition'] = f'attachment; filename="content_analysis_{analysis.id}_{language}.csv"'
            
#         else:
#             return HttpResponse("Invalid report type", status=400)
        
#         # Save report record
#         report = GeneratedReport.objects.create(
#             analysis=analysis,
#             report_type=report_type,
#             language=language
#         )
        
#         # For now, we're generating on-the-fly, so we don't save the file
#         # In production, you might want to save the file to the report_file field
        
#         return response
        
#     except Exception as e:
#         return HttpResponse(f"Error generating report: {str(e)}", status=500)

# @login_required
# @require_POST
# @csrf_exempt
# def chat_with_ai(request, analysis_id):
#     """Chat with AI about analysis"""
#     analysis = get_object_or_404(ContentAnalysis, id=analysis_id, user=request.user)
    
#     message = request.POST.get('message', '').strip()
#     if not message:
#         return JsonResponse({'error': 'No message provided'}, status=400)
    
#     try:
#         # Get conversation history
#         chat_history = []
#         previous_messages = ChatMessage.objects.filter(analysis=analysis).order_by('created_at')
#         for msg in previous_messages:
#             chat_history.append({
#                 "role": msg.role,
#                 "content": msg.content
#             })
        
#         # Save user message
#         user_message = ChatMessage.objects.create(
#             analysis=analysis,
#             role='user',
#             content=message
#         )
        
#         # Get AI response
#         response = chat_with_perplexity(message, chat_history)
        
#         # Save AI response
#         ai_message = ChatMessage.objects.create(
#             analysis=analysis,
#             role='assistant',
#             content=response
#         )
        
#         return JsonResponse({
#             'user_message': message,
#             'ai_response': response,
#             'timestamp': timezone.now().isoformat()
#         })
        
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)

# @login_required
# def get_chat_history(request, analysis_id):
#     """Get chat history for an analysis"""
#     analysis = get_object_or_404(ContentAnalysis, id=analysis_id, user=request.user)
    
#     messages = ChatMessage.objects.filter(analysis=analysis).order_by('created_at')
    
#     chat_data = []
#     for msg in messages:
#         chat_data.append({
#             'role': msg.role,
#             'content': msg.content,
#             'timestamp': msg.created_at.isoformat()
#         })
    
#     return JsonResponse({'messages': chat_data})

# @login_required
# def analysis_history(request):
#     """View analysis history"""
#     analyses = ContentAnalysis.objects.filter(user=request.user).order_by('-created_at')
    
#     return render(request, 'content_analyzer/history.html', {
#         'analyses': analyses
#     })

# @login_required
# def delete_analysis(request, analysis_id):
#     """Delete an analysis"""
#     analysis = get_object_or_404(ContentAnalysis, id=analysis_id, user=request.user)
    
#     if request.method == 'POST':
#         analysis.delete()
#         return redirect('content_analysis_history')
    
#     return render(request, 'content_analyzer/confirm_delete.html', {
#         'analysis': analysis
#     })


# #=================updated to use local ai============
# @login_required
# @require_POST
# @csrf_exempt
# def chat_with_ai(request, analysis_id):
#     """Chat with local AI about analysis - No external API needed"""
#     analysis = get_object_or_404(ContentAnalysis, id=analysis_id, user=request.user)
    
#     message = request.POST.get('message', '').strip()
#     if not message:
#         return JsonResponse({'error': 'No message provided'}, status=400)
    
#     try:
#         # Get analysis results
#         analysis_results = analysis.get_results()
        
#         # Get conversation history for context (though our local AI doesn't use it heavily)
#         conversation_history = []
#         previous_messages = ChatMessage.objects.filter(analysis=analysis).order_by('created_at')
#         for msg in previous_messages:
#             conversation_history.append({
#                 "role": msg.role,
#                 "content": msg.content
#             })
        
#         # Save user message
#         user_message = ChatMessage.objects.create(
#             analysis=analysis,
#             role='user',
#             content=message
#         )
        
#         # Get local AI response
#         from .analysis_utils import local_ai_chat
#         response = local_ai_chat(message, analysis_results, conversation_history)
        
#         # Save AI response
#         ai_message = ChatMessage.objects.create(
#             analysis=analysis,
#             role='assistant',
#             content=response
#         )
        
#         return JsonResponse({
#             'user_message': message,
#             'ai_response': response,
#             'timestamp': timezone.now().isoformat()
#         })
        
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)