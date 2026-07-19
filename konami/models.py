from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone


# ---------------------------------------------------------------------------
# Tournament structure
# ---------------------------------------------------------------------------

class Tournament(models.Model):
    STATUS_CHOICES = [
        ("upcoming", "Upcoming"),
        ("active", "Active"),
        ("completed", "Completed"),
    ]

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="upcoming")

    logo = models.ImageField(upload_to="tournaments/logos/", blank=True, null=True)
    banner_image = models.ImageField(upload_to="tournaments/banners/", blank=True, null=True)
    primary_color = models.CharField(max_length=7, default="#1D9E75")    # hex codes, e.g. #1D9E75
    secondary_color = models.CharField(max_length=7, default="#0F6E56")
    accent_color = models.CharField(max_length=7, default="#F2A623")

    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Stage(models.Model):
    TYPE_CHOICES = [
        ("league", "League"),
        ("groups", "Groups"),
        ("knockout", "Knockout"),
    ]

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="stages")
    name = models.CharField(max_length=120)                 # e.g. "Group stage", "Knockout stage"
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    order = models.PositiveSmallIntegerField(default=1)      # sequence within the tournament
    config = models.JSONField(default=dict, blank=True)      # legs, group_count, points_per_win, has_third_place...

    class Meta:
        ordering = ["tournament", "order"]

    def __str__(self):
        return f"{self.tournament.name} — {self.name}"


class Group(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name="groups")
    name = models.CharField(max_length=60)                   # e.g. "Group A"

    def __str__(self):
        return f"{self.stage} — {self.name}"


class Player(models.Model):
    """A persistent identity — the same player can enter multiple tournaments over time."""
    name = models.CharField(max_length=100)
    gamer_tag = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to="players/avatars/", blank=True, null=True)
    bio = models.TextField(blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.gamer_tag or self.name


class Participant(models.Model):
    """One player's entry into one specific tournament. Match points here, not at Player directly."""
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="participants")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="entries")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, related_name="participants", blank=True, null=True)
    seed = models.PositiveSmallIntegerField(blank=True, null=True)

    class Meta:
        unique_together = ("tournament", "player")

    def __str__(self):
        return f"{self.player} in {self.tournament}"


class Match(models.Model):
    """A record of a result the admin logs after the fact — not a live/playable match."""
    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("completed", "Completed"),
        ("postponed", "Postponed"),
    ]

    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name="matches")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, related_name="matches", blank=True, null=True)

    home = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name="home_matches")
    away = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name="away_matches")

    round_name = models.CharField(max_length=60, blank=True)   # "Matchday 3", "Quarter-final"
    leg = models.PositiveSmallIntegerField(default=1)          # 1 or 2, for two-legged knockout ties

    home_score = models.PositiveSmallIntegerField(blank=True, null=True)
    away_score = models.PositiveSmallIntegerField(blank=True, null=True)

    scheduled_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="scheduled")

    class Meta:
        ordering = ["scheduled_at"]

    # Inside class Match(models.Model):
    def __str__(self):
        home_tag = self.home.player.gamer_tag or self.home.player.name
        away_tag = self.away.player.gamer_tag or self.away.player.name
        return f"{home_tag} vs {away_tag} ({self.round_name})"


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to="profiles/", blank=True, null=True)
    bio = models.TextField(blank=True)

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        USER = "user", "Normal User"

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
    )

    def __str__(self):
        return self.user.username


class Favorite(models.Model):
    """A fan following a specific player."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "player")


# ---------------------------------------------------------------------------
# Engagement — predictions, comments, likes
# ---------------------------------------------------------------------------

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="predictions")
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="predictions")
    predicted_home = models.PositiveSmallIntegerField()
    predicted_away = models.PositiveSmallIntegerField()
    points_awarded = models.PositiveSmallIntegerField(default=0)   # filled in once the match goes final
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "match")

    def __str__(self):
        return f"{self.user} predicts {self.predicted_home}-{self.predicted_away} for {self.match}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    news_post = models.ForeignKey("NewsPost", on_delete=models.CASCADE, related_name="comments", blank=True, null=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="comments", blank=True, null=True)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user}: {self.body[:40]}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    news_post = models.ForeignKey("NewsPost", on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "news_post")


# ---------------------------------------------------------------------------
# Content — news & the live update feed
# ---------------------------------------------------------------------------

class Tag(models.Model):
    name = models.CharField(max_length=40, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class NewsPost(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="news_posts")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="news_posts", null=True)
    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    body = models.TextField()
    cover_image = models.ImageField(upload_to="news/covers/", blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name="news_posts", blank=True)
    is_ai_generated = models.BooleanField(default=False)
    published_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Update(models.Model):
    """Short ticker-style entries — 'Player A beat Player B 3-1' — no full article needed."""
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="updates")
    match = models.ForeignKey(Match, on_delete=models.SET_NULL, related_name="updates", blank=True, null=True)
    body = models.CharField(max_length=280)
    posted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-posted_at"]

    def __str__(self):
        return self.body[:60]


# ---------------------------------------------------------------------------
# AI
# ---------------------------------------------------------------------------

class AIQueryLog(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.SET_NULL, related_name="ai_queries", blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="ai_queries", blank=True, null=True)
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.question[:60]