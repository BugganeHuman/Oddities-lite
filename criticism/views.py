from django.shortcuts import render
from titles.models import Title
from users.models import User
def show_titles(request):
    user = User.objects.get(is_king=True)
    titles = Title.objects.filter(owner=user).order_by('-end_watch')
    context = {
        'titles' : titles
    }
    return render(request, 'criticism/title.html', context)

def sort_up(request):
    user = User.objects.get(is_king=True)
    titles = Title.objects.filter(owner=user).order_by('rating')
    context = {
        'titles' : titles
    }
    return render(request, 'criticism/title.html', context)

def sort_down(request):
    user = User.objects.get(is_king=True)
    titles = Title.objects.filter(owner=user).order_by('-rating')
    context = {
        'titles' : titles
    }
    return render(request, 'criticism/title.html', context)