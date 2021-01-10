from django.db import models

# Create your models here.

# Elo of user
class Elo(models.Model):
    username = models.CharField(max_length=64)
    elo = models.FloatField(default=1100)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    ties = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.username}: {self.elo}"

# Matches played by users
class Match(models.Model):
    user_white = models.CharField(max_length=64)
    user_black = models.CharField(max_length=64)
    
    # "win", "lose" or "tie"
    white_win = models.CharField(max_length=64)

    # Gets set auto when object created.
    match_datetime = models.DateTimeField(auto_now_add=True)

    # Gets set auto when object saved/edited.
    user_send = models.CharField(max_length=64)
    user_pending = models.CharField(max_length=64)
    accepted = models.BooleanField(default=False)

    def __str__(self):
            return f"{self.user_white}(white) VS {self.user_black}(black): {self.white_win} for white"