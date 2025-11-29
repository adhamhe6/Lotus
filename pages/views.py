from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'pages/home.html')

def about(request):
    return render(request, 'pages/about.html')

def contact(request):
    if request.method == 'POST':
        # Add your contact form processing logic here
        # You can integrate with Django's email sending functionality
        pass
    return render(request, 'pages/contact.html')

def services(request):
    return render(request, 'pages/services.html')

def industries(request):
    return render(request, 'pages/industries.html')

def resources(request):
    return render(request, 'pages/resources.html')

def design_your_tool(request):
    if request.method == 'POST':
        # Process the custom tool request form
        # You can save to database, send email, etc.
        pass
    return render(request, 'pages/design_your_tool.html')

def executive_team(request):
    return render(request, 'pages/executive_team.html')

def newsroom(request):
    return render(request, 'pages/newsroom.html')

def careers(request):
    return render(request, 'pages/careers.html')

def pricing(request):
    return render(request, 'pages/pricing.html')

def blog(request):
    return render(request, 'pages/blog.html')

def privacy_policy(request):
    return render(request, 'pages/privacy_policy.html')

def terms_of_service(request):
    return render(request, 'pages/terms_of_service.html')

def data_protection(request):
    return render(request, 'pages/data_protection.html')