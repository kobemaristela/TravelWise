import requests
import openai
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.contrib.auth.decorators import login_required
from django.apps import apps
from django.conf import settings
from .forms import RegisterForm


TravelPlan = apps.get_model('api', 'TravelPlan')
ChatMessage = apps.get_model('api', 'ChatMessage')
Activity = apps.get_model('api', 'Activity')
Profile = apps.get_model('frontend', 'Profile')

# Helper Functions
def create_profile_picture(request):
    OPENAI_MODEL = "gpt-3.5-turbo"
    openai.api_key = settings.OPENAI_KEY

    prompt = f'''Generate a LinkedIn headshot for senior professional {request.user.get_full_name()}. 
            Portray confidence and approachability through his expression, wearing business attire suitable for his industry. 
            Attain well-lit, focused shot with a clean, professional background. 
            This is crucial for {request.user.first_name}'s credible online presence.'''

    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="512x512"
    )
    image_url = response['data'][0]['url']

    profile, _ = Profile.objects.get_or_create(user=request.user)
    profile.profile_picture = image_url
    profile.save()


def landing(request):
    return render(request, "index.html")


@login_required(login_url="landing")
def home(request):
    try:
        recent_plan = TravelPlan.objects.filter(author=request.user).latest('last_modified')
    except TravelPlan.DoesNotExist:
        return redirect("plan")

    return redirect(f"/create/?id={recent_plan.pk}")


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

        try:
            response = requests.post('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
                'secret': settings.CLOUDFLARE_SECRET_KEY,
                'response': token
            }, timeout=5, verify=True)
            response.raise_for_status()

        except requests.HTTPError as err:
            form.add_error(None, err)
            return render(request, 'accounts/login.html', {"form": form})

        except requests.Timeout as err:
            form.add_error(None, err)
            return render(request, 'accounts/login.html', {"form": form})

        results = response.json()
        if not results['success']:
            form.add_error(None, "Invalid CAPTCHA Token")
            return render(request, 'accounts/login.html', {"form": form})

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
            'id': stored_activity.pk,
            'start_time': stored_activity.start_time.isoformat(),
            'end_time': stored_activity.end_time.isoformat(),
            'note': stored_activity.note,
            'link': stored_activity.link,
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
        if request.POST.get('first_name') != request.user.first_name or request.user.last_name != request.POST.get('last_name'):
            request.user.first_name = request.POST.get('first_name')
            request.user.last_name = request.POST.get('last_name')
            request.user.save()

            create_profile_picture(request)

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
