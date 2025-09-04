# middleware.py
from django.shortcuts import render,redirect,HttpResponse

class Custom404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Custom  handling
        if response.status_code == 404:
            return redirect('pagenotfound_url')
        elif response.status_code == 500:
            return redirect('server_error_url')


        return response
    
