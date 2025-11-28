from django.urls import path
from .views import *

urlpatterns = [
    path('', products, name='products'),
    path("decision-analysis/", decision_analysis_api, name="decision_analysis_api"),
    # path("decision-analysis-page/", decision_analysis_page, name="decision_analysis_page"),
    path("decision-dashboard/", decision_dashboard, name="decision_dashboard"),
    path("quant-analysis/", quant_analysis_dashboard, name="quant_analysis_dashboard"),
    path("quant-analysis-api/", quant_analysis_api, name="quant_analysis_api"),
    # path("paper-analysis/", paper_analysis_dashboard, name="paper_analysis_dashboard"),
    # path("paper-analysis-api/", paper_analysis_api, name="paper_analysis_api"),
    path('content-analyzer/', content_analyzer_home, name='content_analyzer_home'),
    path('content-analyzer/history/', analysis_history, name='content_analysis_history'),
    path('content-analyzer/analysis/<int:analysis_id>/', content_analysis_results, name='content_analysis_results'),
    path('content-analyzer/analysis/<int:analysis_id>/download/<str:report_type>/', download_report, name='download_content_report'),
    path('content-analyzer/analysis/<int:analysis_id>/chat/', chat_with_ai, name='content_analysis_chat'),
    path('content-analyzer/analysis/<int:analysis_id>/chat/history/', get_chat_history, name='content_chat_history'),
    path('content-analyzer/analysis/<int:analysis_id>/delete/', delete_analysis, name='delete_content_analysis'),
]
