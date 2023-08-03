from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.http import JsonResponse
from django.contrib.auth.models import User
from http import HTTPStatus
import os
import openai
import json
from .models import Activity, TravelPlan, ChatMessage
import datetime

OPENAI_KEY = os.environ['OPENAI_KEY']
OPENAI_MODEL = "gpt-3.5-turbo"

openai.api_key = OPENAI_KEY

OPENAI_FUNCTIONS = [
    {
        'name': 'create_activity',
        'description': 'Create a travel activity for a user.',
        'parameters': {
            'type': 'object',
            'properties': {
                'start_time': {
                    'type': 'string',
                    'description': 'The start ISO 8601 date time of the event',
                },
                'end_time': {
                    'type': 'string',
                    'description': 'The end ISO 8601 date time of the event',
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
    
    def create_activity(start_time, end_time, note=None):
        start_time = datetime.datetime.fromisoformat(start_time)
        end_time = datetime.datetime.fromisoformat(end_time)
        
        Activity.objects.create(
            start_time=start_time,
            end_time=end_time,
            note=note,
            plan=travel_plan,
        )
        
    messages = [
        { 
            'role': 'system', 
            'content': 'You are an assistant for organizing travel plans.',
        }
    ]
    
    for stored_message in ChatMessage.objects.filter(plan=travel_plan).order_by('time'):
        messages.append({
            'role': stored_message.user,
            'content': stored_message.msg,
        })
    
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
    
    response_message_function_call = response_message.get('function_call')
    if response_message_function_call is not None:
        function_table = {
            'create_activity': create_activity,
        }
        
        function_name = response_message_function_call['name']
        function = function_table[function_name]
        function_arguments = json.loads(response_message_function_call['arguments'])
        
        function_response = function(
            start_time=function_arguments.get('start_time'),
            end_time=function_arguments.get('end_time'),
            note=function_arguments.get('note'),
        )
        messages.append(response_message)
        messages.append(
            {
                'role': 'function',
                'name': function_name,
                'content': 'ok', # TODO: Use function_response, return errors here as well.
            }
        )
        
        chat_completion = openai.ChatCompletion.create(
            model=OPENAI_MODEL, 
            messages=messages,
            functions=OPENAI_FUNCTIONS,
            function_call="auto",
        )
        response_message = chat_completion.choices[0].message
        
    ChatMessage(time=datetime.datetime.now(), user='user', msg=message, plan=travel_plan).save()
    ChatMessage(time=datetime.datetime.now(), user='assistant', msg=response_message.content, plan=travel_plan).save()
    
    # StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    return JsonResponse({ 'message': response_message.content })

def plan(request):
    if not request.user.is_authenticated:
        return JsonResponse({ 'error': 'Unauthorized' }, status=HTTPStatus.UNAUTHORIZED)
        
    if request.method != 'POST':
        return JsonResponse({ 'error': 'Invalid Method' }, status=HTTPStatus.METHOD_NOT_ALLOWED)
        
    new_travel_plan = TravelPlan(name='WIP', author=request.user, note='WIP')
    new_travel_plan.save()
    
    return JsonResponse({ 'planId': new_travel_plan.pk })


def validateUser(request, username=None):
    if request.method == 'GET':
        if User.objects.filter(username=username).exists():
            return JsonResponse({"message": "bad"})
        
        return JsonResponse({"message": "good"})

