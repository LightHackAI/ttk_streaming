from django.contrib.auth.decorators import login_required
from django.shortcuts import render



@login_required
def player_page(request):
    return render(request, 'player/player_page.html')
