from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from django.apps import apps

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
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect("home")

    form = AuthenticationForm()

    return render(request, 'accounts/login.html', {"form": form})


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
        
    return render(request, 'travel/create.html', {
        'messages': messages,
        'activities': activities,
    })