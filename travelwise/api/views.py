from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.http import JsonResponse
from http import HTTPStatus
import os
import openai

OPENAI_KEY = os.environ['OPENAI_KEY']
OPENAI_MODEL = "gpt-3.5-turbo"

openai.api_key = OPENAI_KEY

# @csrf_exempt
def chat(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid Method'}, status=HTTPStatus.METHOD_NOT_ALLOWED)
     
    # Prevent OpenAI API calls when testing
    return JsonResponse({ 'message': 'Test Response' })
    
    chat_completion = openai.ChatCompletion.create(
        model=OPENAI_MODEL, 
        messages=[
            { "role": "system", "content": "You are an assistant for organizing travel plans. Start by asking the user where they want to go." },
        ],
    )
    
    # StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    
    return JsonResponse({ 'message': chat_completion.choices[0].message.content })