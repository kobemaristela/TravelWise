from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required

# Create your views here.

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
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")

    form = UserCreationForm()

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
    return render(request, 'travel/create.html')