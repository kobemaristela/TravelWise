from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages as dj_msg
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.conf import settings
from http import HTTPStatus
import openai
import json
from .models import Activity, TravelPlan, ChatMessage
import datetime

OPENAI_MODEL = "gpt-3.5-turbo"
openai.api_key = settings.OPENAI_KEY

OPENAI_FUNCTIONS = [
    {
        'name': 'create_activity',
        'description': 'Create a travel activity for a user.',
        'parameters': {
            'type': 'object',
            'properties': {
                'start_time': {
                    'type': 'string',
                    'description': 'The start ISO 8601 UTC date time of the event',
                },
                'end_time': {
                    'type': 'string',
                    'description': 'The end ISO 8601 UTC date time of the event',
                },
                'note': {
                    'type': 'string',
                    'description': 'A description of the activity',
                },
            },
            'required': [
                'start_time', 
                'end_time'
            ],
        },
    },
    {
        'name': 'delete_activity',
        'description': 'Delete a travel activity for a user.',
        'parameters': {
            'type': 'object',
            'properties': {
                'id': {
                    'type': 'integer',
                    'description': 'The id of the activity to be deleted',
                }
            },
            'required': [
                'id',
            ],
        },
    },
    {
        'name': 'update_activity',
        'description': 'Update the parameters for an activity.',
        'parameters': {
            'type': 'object',
            'properties': {
                'id': {
                    'type': 'integer',
                    'description': 'The id of the activity to be updated',
                },
                'start_time': {
                    'type': 'string',
                    'description': 'The new start ISO 8601 UTC date time of the event',
                },
                'end_time': {
                    'type': 'string',
                    'description': 'The new end ISO 8601 UTC date time of the event',
                },
                'note': {
                    'type': 'string',
                    'description': 'The new description of the activity',
                },
            },
            'required': [
                'id',
            ],
        },
    },
]

def chat(request):
    if request.method != 'POST':
        return JsonResponse({ 'error': 'Invalid Method' }, status=HTTPStatus.METHOD_NOT_ALLOWED)
        
    if not request.user.is_authenticated:
        return JsonResponse({ 'error': 'Unauthorized' }, status=HTTPStatus.UNAUTHORIZED)
      
    request_body = None
    try:
        request_body = request.body.decode('utf-8')
    except:
        return JsonResponse({ 'error': 'Request body is not UTF-8' }, status=HTTPStatus.BAD_REQUEST)
     
    request_json = None
    try:  
        request_json = json.loads(request_body)
    except:
        return JsonResponse({ 'error': 'Request body is not JSON' }, status=HTTPStatus.BAD_REQUEST)
        
    message = request_json.get('message')
    if message is None:
        return JsonResponse({ 'error': 'Missing "message" field' }, status=HTTPStatus.BAD_REQUEST)
    plan_id = request_json.get('planId')
    if message is None:
        return JsonResponse({ 'error': 'Missing "planId" field' }, status=HTTPStatus.BAD_REQUEST)
        
    travel_plan = TravelPlan.objects.filter(pk=plan_id, author=request.user).first()
    
    if travel_plan is None:
        return JsonResponse({ 'error': 'Missing travel plan' }, status=HTTPStatus.NOT_FOUND)
          
    # Prevent OpenAI API calls when testing
    # return JsonResponse({ 'message': 'Test Response' })
    
    response = {
        'activities': {
            'created': None,
            'deleted': None,
            'modified': None,
        },
    }
    response_activity_created = None
    
    def create_activity(function_arguments, response):        
        start_time = function_arguments.get('start_time')
        end_time = function_arguments.get('end_time')
        note = function_arguments.get('note')
        
        start_time = datetime.datetime.fromisoformat(start_time)
        end_time = datetime.datetime.fromisoformat(end_time)
        
        activity = Activity.objects.create(
            start_time=start_time,
            end_time=end_time,
            note=note,
            plan=travel_plan,
        )
        
        response['activities']['created'] = {
            'id': activity.pk,
            'start_time': activity.start_time,
            'end_time': activity.end_time,
            'note': activity.note,
        }
        
        return f'Created activity with id \"{activity.pk}\"'
        
    def delete_activity(function_arguments, response):
        id = function_arguments.get('id')
        
        id = int(id)
        
        Activity.objects.filter(pk=id, plan=travel_plan).delete()
        
        response['activities']['deleted'] = id
        
        return f'Deleted activity with id \"{id}\"'
        
    def update_activity(function_arguments, response):
        id = function_arguments.get('id')
        start_time = function_arguments.get('start_time')
        end_time = function_arguments.get('end_time')
        note = function_arguments.get('note')
        
        message = f'Updated activity with id \"{id}\"'
        
        activity = Activity.objects.filter(pk=id, plan=travel_plan).first()
        if activity is None:
            return f'Activity with id \"{id}\" does not exist'
        
        if start_time is not None:
            activity.start_time = start_time
            message += f', Start Time set to {start_time}'
        if end_time is not None:
            activity.end_time = end_time
            message += f', End Time set to {end_time}'
        if note is not None:
            activity.note = note
            message += f', Note set to {note}'
        activity.save()
        
        response['activities']['modified'] = {
            'id': activity.pk,
            'start_time': activity.start_time,
            'end_time': activity.end_time,
            'note': activity.note,
        }
        
        return message
        
    messages = [
        { 
            'role': 'system', 
            'content': 'You are an assistant for organizing travel plans.',
        },
    ]
    
    for stored_message in ChatMessage.objects.filter(plan=travel_plan).order_by('time'):
        messageDict = {
            'role': stored_message.user,
            'content': stored_message.msg,
        }
        
        if stored_message.user == 'function':
            messageDict['name'] = stored_message.function_name
            
        messages.append(messageDict)
    
    messages.append({
        'role': 'user',
        'content': message,
    })
        
    chat_completion = openai.ChatCompletion.create(
        model=OPENAI_MODEL, 
        messages=messages,
        functions=OPENAI_FUNCTIONS,
        function_call="auto",
    )
    response_message = chat_completion.choices[0].message
    
    function_message = None
    
    response_message_function_call = response_message.get('function_call')
    if response_message_function_call is not None:
        function_table = {
            'create_activity': create_activity,
            'delete_activity': delete_activity,
            'update_activity': update_activity,
        }
        
        function_name = response_message_function_call['name']
        function = function_table[function_name]
        function_arguments = json.loads(response_message_function_call['arguments'])
        
        function_response = function(function_arguments, response)
        messages.append(response_message)
        
        function_message = {
            'role': 'function',
            'name': function_name,
            'content': function_response, # TODO: Return errors here as well.
        }
        messages.append(function_message)
        
        chat_completion = openai.ChatCompletion.create(
            model=OPENAI_MODEL, 
            messages=messages,
            functions=OPENAI_FUNCTIONS,
            function_call="auto",
        )
        response_message = chat_completion.choices[0].message
        
    ChatMessage(
        time=datetime.datetime.now(), 
        user='user', 
        msg=message, 
        plan=travel_plan
    ).save()
    
    response_messages = []
    
    if function_message is not None:
        ChatMessage(
            time=datetime.datetime.now(), 
            user='function', 
            msg=function_message['content'], 
            function_name=function_message['name'], 
            plan=travel_plan
        ).save()
        response_messages.append({
            'role': 'function',
            'content': function_message['content'],
        })
    ChatMessage(
        time=datetime.datetime.now(), 
        user='assistant', 
        msg=response_message.content, 
        plan=travel_plan
    ).save()
    response_messages.append({
        'role': 'assistant',
        'content': response_message.content,
    })
    response['messages'] = response_messages
    
    # StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    
    return JsonResponse(response)


@login_required(login_url="landing")
def plan(request):
    if request.method == 'GET':
        new_travel_plan = TravelPlan(name='WIP', author=request.user, note='WIP')
        new_travel_plan.save()
    
        return redirect(f"/create/?id={new_travel_plan.pk}")

    
def validateUser(request, username=None):
    if request.method == 'GET':
        if User.objects.filter(username=username).exists():
            return JsonResponse({"message": "bad"})
        
        return JsonResponse({"message": "good"})


@login_required(login_url="landing")
def delete_plan(request, plan_id):
    if request.method == 'GET':
        try:
            TravelPlan.objects.get(pk=plan_id, author=request.user).delete()
        except Exception:
            dj_msg.error(request, "Plan was not deleted" )

        return redirect("history")
        
