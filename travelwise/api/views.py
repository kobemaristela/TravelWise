from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.http import JsonResponse
from http import HTTPStatus
import os
import openai
import json
from .models import Activities, TravelPlans
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
        return JsonResponse({ 'error': 'Response body is not UTF-8' }, status=HTTPStatus.BAD_REQUEST)
     
    request_json = None
    try:  
        request_json = json.loads(request_body)
    except:
        return JsonResponse({ 'error': 'Response body is not JSON' }, status=HTTPStatus.BAD_REQUEST)
        
    message = request_json.get('message')
    if message is None:
        return JsonResponse({ 'error': 'Missing "message" field' }, status=HTTPStatus.BAD_REQUEST)
     
    # Prevent OpenAI API calls when testing
    # return JsonResponse({ 'message': 'Test Response' })
    
    def create_activity(start_time, end_time, note=None):
        start_time = datetime.datetime.fromisoformat(start_time)
        end_time = datetime.datetime.fromisoformat(end_time)
        
        Activities.objects.create(
            start_time=start_time,
            end_time=end_time,
            note=note,
            plan=TravelPlans.objects.get(pk=1),
        )
    
    
    messages = [
        { 
            'role': 'system', 
            'content': 'You are an assistant for organizing travel plans.',
        },
        {
            'role': 'user',
            'content': message,
        },
    ]
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
    
    # StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    return JsonResponse({ 'message': response_message.content })
