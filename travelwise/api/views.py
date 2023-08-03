from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.http import JsonResponse
from django.contrib.auth.models import User
from http import HTTPStatus
import os
import openai
import json

OPENAI_KEY = os.environ['OPENAI_KEY']
OPENAI_MODEL = "gpt-3.5-turbo"

openai.api_key = OPENAI_KEY

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
    
    chat_completion = openai.ChatCompletion.create(
        model=OPENAI_MODEL, 
        messages=[
            { 
                'role': 'system', 
                'content': 'You are an assistant for organizing travel plans.',
            },
            {
                'role': 'user',
                'content': message,
            },
        ],
    )
    
    # StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    
    return JsonResponse({ 'message': chat_completion.choices[0].message.content })


def validateUser(request, username=None):
    if request.method == 'GET':
        if User.objects.filter(username=username).exists():
            return JsonResponse({"message": "bad"})
        
        return JsonResponse({"message": "good"})