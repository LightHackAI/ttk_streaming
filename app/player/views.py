from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


@login_required
def admin_panel(request):
    if request.user.role != 'admin':
        return redirect('player:player_page')
    return render(request, 'player/admin_panel.html')


def player_page(request):
    return render(request, 'player/player_page.html')
