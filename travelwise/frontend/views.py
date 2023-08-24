import requests
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.contrib.auth.decorators import login_required
from django.apps import apps
from .forms import RegisterForm
from django.conf import settings


TravelPlan = apps.get_model('api', 'TravelPlan')
ChatMessage = apps.get_model('api', 'ChatMessage')
Activity = apps.get_model('api', 'Activity')

def landing(request):
    return render(request, "index.html")


@login_required(login_url="landing")
def home(request):
    return render(request, 'travel/home.html')


def register(request):
    # Authenticated User
    if request.user.is_authenticated:
        return redirect('home')
    
    # Unauthenticated User
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")

    form = RegisterForm()

    return render(request, 'accounts/register.html', {"form": form})


def login_view(request):
    # Authenticated User
    if request.user.is_authenticated:
        return redirect('home')

    # Unauthenticated User
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        token = request.POST.get('cf-turnstile-response')

        # Missing CAPTCHA Token
        if not token:
            form.add_error(None, "CAPTCHA Token Missing")
            return render(request, 'accounts/login.html', {"form": form})

        response = requests.post('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
            'secret': settings.CLOUDFLARE_SECRET_KEY,
            'response': token
        }, timeout=5, verify=True)
        
        results = response.json()

        print(results)
        if not results.success:   # Checks if there is a response and response is True
            print("I'm in")
            form.add_error(None, "Invalid CAPTCHA Token")
            return render(request, 'accounts/login.html', {"form": form})

        print("I'm out")
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect("home")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {"form": form})   # Catches form errors


@login_required(login_url="landing")
def logout_view(request):
    logout(request)
    return redirect("landing")
    
    
@login_required(login_url="landing")
def create_plan(request):
    travel_plan_id = request.GET.get('id')
    if travel_plan_id is None:
        return redirect('home')
        
    travel_plan = TravelPlan.objects.filter(pk=travel_plan_id, author=request.user).first()
    if travel_plan is None:
        return redirect('home')
        
    activities = []
    for stored_activity in Activity.objects.filter(plan=travel_plan).order_by('start_time'):
        activities.append({
            'start_time': stored_activity.start_time,
            'end_time': stored_activity.end_time,
            'note': stored_activity.note,
        })
        
    messages = []
    for stored_message in ChatMessage.objects.filter(plan=travel_plan).order_by('time'):
        messages.append({
            'role': stored_message.user,
            'content': stored_message.msg,
        })
    
    travel_plan.save()  # Updates last_modified time

    return render(request, 'travel/create.html', {
        'messages': messages,
        'activities': activities,
    })


@login_required(login_url="landing")
def history_view(request):
    if request.method == 'GET':
        travel_plans = []
        for travel_plan in TravelPlan.objects.filter(author=request.user):
            travel_plans.append({
                'id': travel_plan.id,
                'completed': travel_plan.completed,
            })
        
        
        return render(request, 'travel/history.html', {
            'travel_plans': travel_plans})


@login_required(login_url="landing")
def profile_view(request):
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        request.user.save()

        if not request.POST.get('new_password') and not request.POST.get('new_password'):
            return render(request, 'accounts/profile.html', {'form': {}})

        data = {
            'new_password1': request.POST.get('new_password'),
            'new_password2': request.POST.get('confirm_password')
        }

        form = SetPasswordForm(user=request.user, data=data)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("profile")

        return render(request, 'accounts/profile.html', {'form': form})  # Returns form error

    return render(request, 'accounts/profile.html')
