from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('services/', views.services, name='services'),
    path('industries/', views.industries, name='industries'),
    path('resources/', views.resources, name='resources'),
    path('design-your-tool/', views.design_your_tool, name='design_your_tool'),
    path('executive-team/', views.executive_team, name='executive_team'),
    path('newsroom/', views.newsroom, name='newsroom'),
    path('careers/', views.careers, name='careers'),
    path('pricing/', views.pricing, name='pricing'),
    path('blog/', views.blog, name='blog'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('data-protection/', views.data_protection, name='data_protection'),
]