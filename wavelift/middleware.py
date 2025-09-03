# middleware.py
from django.shortcuts import render,redirect

class Custom404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Print actual status code
        #print(f"Middleware Status Code: {response.status_code}")

        # Custom 404 handling
        if response.status_code == 404:
            return redirect('pagenotfound_url')


        return response