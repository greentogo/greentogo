from django.shortcuts import render


def payment(request):
    return render(request, 'index.html')

