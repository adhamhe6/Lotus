from django.urls import path
from .views import *

urlpatterns = [
    path("paper-analysis/", paper_analysis_dashboard, name="paper_analysis_dashboard"),
]
