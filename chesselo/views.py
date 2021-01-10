from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django import forms
from .models import Elo, Match
from django.db.models import Q

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


# Start page
def index(request):
    context = {}
    form = UserRegisterForm()
    
    if request.user.is_authenticated:
        return HttpResponseRedirect("leaderboards")

    # User wants to login or register
    if request.method == "POST":
        # User wants to log in.
        login_username = request.POST.get("login_username", False)
        if login_username:
            login_username = login_username.lower()
            # If no password is supplied, make it an empty string so code doesn't error.
            password = request.POST.get("password", "")

            # Check correct username + password.
            user = authenticate(request, username=login_username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect("index")

            # Username + password doesnt exist.
            messages.add_message(request, messages.INFO, 'Credentials not correct.',)
            return HttpResponseRedirect("index")
        
        
        # User wants to register.
        else:
            if request.POST["username"]:
                new_post = request.POST.copy()
                
                new_post["username"] = new_post["username"].lower()
                print(new_post["username"])
            form = UserRegisterForm(new_post)
            # Register is succesfull.
            if form.is_valid():
                form.save()
                messages.add_message(request, messages.INFO, 'Account creation succesfull.',)

            # Register failed.
            else:
                messages.add_message(request, messages.INFO, 'Account creation failed',)
                context["show_register"] = True



    context["form"] = form
    return render(request, "login.html", context)

def leaderboards(request):
    context = {}
    
    # Check if logged in
    if not request.user.is_authenticated:
        messages.add_message(request, messages.INFO, 'Please log in.',)
        return HttpResponseRedirect("index")
    
    # Give elo rating if no rating yet.
    if not Elo.objects.filter(username = request.user.username):
        elo = Elo(username = request.user.username)
        elo.save()
    
    elos = Elo.objects.order_by('elo')[::-1]
    context["elo_list"] = elos

    match_list = Match.objects.order_by("match_datetime")[:10]
    context["match_list"] = match_list

    opponent_list = Elo.objects.all()
    context["opponents"] = opponent_list


    elo_score = Elo.objects.get(username = request.user.username)
    context["user_elo"] = int(elo_score.elo)
    context["logged_in"] = True
    context["lb"] = True
    return render(request, "main-page.html", context)

# Log-out user of logged in, return to login-page.
def logout_view(request): 
    
    # No need to log-out if not logged in.
    if request.user.is_authenticated:
        logout(request)
        messages.add_message(request, messages.INFO, 'Logged out',)
    
    return HttpResponseRedirect("index")


def pending(request):
    context = {}
    
    # Check if logged in
    if not request.user.is_authenticated:
        messages.add_message(request, messages.INFO, 'Please log in.',)
        return HttpResponseRedirect("index")

    username = request.user.username
    
    match_list = Match.objects.filter(Q(user_white=username) | Q(user_black=username), user_pending = request.user.username, accepted = False)[:20]
    context["pending_list"] = match_list

    outgoing_list = Match.objects.filter(Q(user_white=username) | Q(user_black=username), user_send = request.user.username, accepted = False)[:20]
    context["outgoing_list"] = outgoing_list





    context["pending"] = True
    context["logged_in"] = True
    elo_score = Elo.objects.get(username = request.user.username)
    context["user_elo"] = int(elo_score.elo)

    opponent_list = Elo.objects.all()
    context["opponents"] = opponent_list

    return render(request, "pending.html", context)

def account(request, username=False):
    context = {}

    # Check if logged in
    if not request.user.is_authenticated:
        messages.add_message(request, messages.INFO, 'Please log in.',)
        return HttpResponseRedirect("/index")

    if not username:
        # If logged in, go to that accounts profile.
        if request.user.is_authenticated:
            username = request.user.username
            url = "account/" + username
            return HttpResponseRedirect(url)
        
        # If not logged in return to login-page.
        return HttpResponseRedirect("/index")


    # Match history
    match_list = Match.objects.filter(Q(user_white=username) | Q(user_black=username))[:20]
    context["match_list"] = match_list
    # Create player statistics
    elo = Elo.objects.get(username=username)
    context["username"] = username
    context["wins"] = elo.wins
    context["losses"] = elo.losses
    context["account_elo"] = elo.elo
    context["ties"] = elo.ties
    total = elo.wins + elo.losses
    if total:
        context["winrate"] = elo.wins/(elo.wins + elo.losses)
    else:
        context["winrate"] = "None"

    opponent_list = Elo.objects.all()
    context["opponents"] = opponent_list



    context["account_page"] = True
    context["logged_in"] = True
    elo_score = Elo.objects.get(username = request.user.username)
    context["user_elo"] = int(elo_score.elo)

    return render(request, "account.html", context)

def add_match(request):

    # Check if logged in
    if not request.user.is_authenticated:
        messages.add_message(request, messages.INFO, 'Please log in.',)
        return HttpResponseRedirect("index")

    user1 = request.POST.get("user1")
    user2 = request.POST.get("user2")
    user1_color = request.POST.get("user1_color")
    user1_win = request.POST.get("user1_win")
    print(user1, user2, user1_color, user1_win)

    if user1_color == "white":
        username_white = user1
        username_black = user2
    
    elif user1_color == "black":
        username_black = user1
        username_white = user2
        if user1_win == "win":
            user1_win = "loss"
        if user1_win == "loss":
            user1_win = "win"
    
    white_win = user1_win

    match = Match(user_white = username_white, user_black = username_black, white_win = white_win, user_send = user1, user_pending = user2)
    match.save()
    messages.add_message(request, messages.INFO, 'Match request send.',)
    return HttpResponseRedirect("pending")

def accept(request):

    # Check if logged in
    if not request.user.is_authenticated:
        messages.add_message(request, messages.INFO, 'Please log in.',)
        return HttpResponseRedirect("index")

    match_id_accept = request.POST.get("match", "")
    match = Match.objects.get(id=match_id_accept)
    match.accepted = True
    match.save()

    user_white = match.user_white
    user_black = match.user_black
    white_elo = Elo.objects.get(username=user_white).elo
    black_elo = Elo.objects.get(username=user_black).elo

    win_dict = {"win": 1, "loss": 0, "tie": 0.5}
    win = win_dict[match.white_win]

    expected_white = 1/(1 + 10**((black_elo - white_elo) /400))
    expected_black = 1 - expected_white

    delta_elo_white = 32 * (win - expected_white)
    delta_elo_black = 32 * (abs(win-1) - expected_black)
    
    elo_white = Elo.objects.get(username = user_white)
    if match.white_win == "win":
        elo_white.wins += 1
    if match.white_win == "loss":
        elo_white.losses += 1
    if match.white_win == "tie":
        elo_white.ties += 1
    elo_white.elo += delta_elo_white
    elo_white.save()

    elo_black = Elo.objects.get(username = user_black)
    if match.white_win == "win":
        elo_black.losses += 1
    if match.white_win == "loss":
        elo_black.wins += 1
    if match.white_win == "tie":
        elo_black.ties += 1
    elo_black.elo += delta_elo_black
    elo_black.save()

    if delta_elo_white > 0:
        delta_elo_white = "+" + str(int(delta_elo_white))
    else:
        delta_elo_white = str(int(delta_elo_white))
    
    if delta_elo_black > 0:
        delta_elo_black = "+" + str(int(delta_elo_black))
    else:
        delta_elo_black = str(int(delta_elo_black))


    if request.user.username == user_white:
        messages.add_message(request, messages.INFO, f'Match accepted (You: {delta_elo_white}, {user_black}: {delta_elo_black})',)
    if request.user.username == user_black:
        messages.add_message(request, messages.INFO, f'Match accepted, (YOU: {delta_elo_black}, {user_white}: {delta_elo_white})',)

    return HttpResponseRedirect("pending")

def cancel(request):
    # Check if logged in
    if not request.user.is_authenticated:
        messages.add_message(request, messages.INFO, 'Please log in.',)
        return HttpResponseRedirect("index")

    match_id_cancel = request.POST.get("match", "")
    match = Match.objects.get(id=match_id_cancel)
    match.delete()
    
    return HttpResponseRedirect("pending")