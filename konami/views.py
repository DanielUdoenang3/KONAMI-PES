import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse

from .models import Tournament, Update, NewsPost, Player, Match, AIQueryLog, MatchEvent, FavoriteMatch, Comment, Like, Stage, Participant
from .forms import TournamentForm, MatchForm, PlayerForm, NewsPostForm, UpdateForm, MatchEventForm
from .standings import calculate_standings


# ---------------------------------------------------------------------------
# Decorators
# ---------------------------------------------------------------------------

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("staff_login")
        if request.user.is_staff or request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
            return view_func(request, *args, **kwargs)
        messages.error(request, "You do not have permission to view the Admin Dashboard.")
        return redirect("landing")
    return _wrapped_view


# ---------------------------------------------------------------------------
# Public Pages
# ---------------------------------------------------------------------------

def landing_page(request):
    context = {
        "tournaments": Tournament.objects.exclude(status="completed").order_by("-start_date")[:6],
        "latest_updates": Update.objects.select_related("tournament").order_by("-posted_at")[:6],
        "latest_news": NewsPost.objects.select_related("tournament").order_by("-published_at")[:3],
        "tournament_count": Tournament.objects.count(),
        "player_count": Player.objects.count(),
        "match_count": Match.objects.filter(status="completed").count(),
    }
    return render(request, "landing.html", context)


def staff_login(request):
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'admin')):
        return redirect("admin_dashboard")

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        if user.is_staff or user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'admin'):
            login(request, user)
            return redirect("admin_dashboard")
        messages.error(request, "This account doesn't have admin access.")

    return render(request, "staff_login.html", {"form": form})


def tournament_detail(request, slug):
    tournament = get_object_or_404(Tournament, slug=slug)
    standings = calculate_standings(tournament)
    
    # Group matches by round_name (Matchday)
    matches_qs = Match.objects.filter(tournament=tournament).select_related("home__player", "away__player").order_by("scheduled_at")
    matchdays = {}
    for m in matches_qs:
        md_name = m.round_name or "General Fixtures"
        if md_name not in matchdays:
            matchdays[md_name] = []
        matchdays[md_name].append(m)

    participants = Participant.objects.filter(tournament=tournament).select_related("player")
    news_posts = NewsPost.objects.filter(tournament=tournament).order_by("-published_at")

    context = {
        "tournament": tournament,
        "standings": standings,
        "matchdays": matchdays,
        "participants": participants,
        "news_posts": news_posts,
    }
    return render(request, "tournament_detail.html", context)


def match_detail(request, pk):
    match = get_object_or_404(Match.objects.select_related("home__player", "away__player", "stage", "tournament"), pk=pk)
    events = match.events.select_related("player").order_by("minute", "created_at")
    comments = Comment.objects.filter(match=match).select_related("user").order_by("-created_at")
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = FavoriteMatch.objects.filter(user=request.user, match=match).exists()

    context = {
        "match": match,
        "events": events,
        "comments": comments,
        "is_favorited": is_favorited,
    }
    return render(request, "match_detail.html", context)


@login_required
def toggle_favorite_match(request, pk):
    match = get_object_or_404(Match, pk=pk)
    fav_qs = FavoriteMatch.objects.filter(user=request.user, match=match)
    if fav_qs.exists():
        fav_qs.delete()
        messages.success(request, f"Removed {match} from your favorites.")
    else:
        FavoriteMatch.objects.create(user=request.user, match=match)
        messages.success(request, f"Favorited {match}! You will receive simulated notifications on goal updates.")
    return redirect("match_detail", pk=pk)


def news_detail(request, slug):
    post = get_object_or_404(NewsPost.objects.select_related("tournament", "author"), slug=slug)
    comments = Comment.objects.filter(news_post=post).select_related("user").order_by("-created_at")
    likes_count = post.likes.count()
    is_liked = False
    if request.user.is_authenticated:
        is_liked = post.likes.filter(user=request.user).exists()

    context = {
        "post": post,
        "comments": comments,
        "likes_count": likes_count,
        "is_liked": is_liked,
    }
    return render(request, "news_detail.html", context)


@login_required
def add_news_comment(request, slug):
    post = get_object_or_404(NewsPost, slug=slug)
    body = request.POST.get("body")
    if body:
        Comment.objects.create(user=request.user, news_post=post, body=body)
        messages.success(request, "Comment posted successfully.")
    return redirect("news_detail", slug=slug)


@login_required
def add_match_comment(request, pk):
    match = get_object_or_404(Match, pk=pk)
    body = request.POST.get("body")
    if body:
        Comment.objects.create(user=request.user, match=match, body=body)
        messages.success(request, "Comment posted successfully.")
    return redirect("match_detail", pk=pk)


@login_required
def like_news_post(request, slug):
    post = get_object_or_404(NewsPost, slug=slug)
    like_qs = post.likes.filter(user=request.user)
    if like_qs.exists():
        like_qs.delete()
        messages.success(request, "Post unliked.")
    else:
        post.likes.create(user=request.user)
        messages.success(request, "Post liked.")
    return redirect("news_detail", slug=slug)


# ---------------------------------------------------------------------------
# Admin Dashboard main lists
# ---------------------------------------------------------------------------

@admin_required
def admin_dashboard(request):
    context = {
        "active_tab": "overview",
        "total_tournaments": Tournament.objects.count(),
        "active_tournaments": Tournament.objects.filter(status="active").order_by("-start_date"),
        "upcoming_tournaments": Tournament.objects.filter(status="upcoming").order_by("-start_date"),
        "total_players": Player.objects.count(),
        "total_matches": Match.objects.count(),
        "completed_matches": Match.objects.filter(status="completed").count(),
        "recent_matches": Match.objects.select_related("home__player", "away__player", "stage", "tournament").order_by("-scheduled_at")[:8],
        "recent_ai_queries": AIQueryLog.objects.select_related("user", "tournament").order_by("-created_at")[:6],
        "recent_updates": Update.objects.select_related("tournament").order_by("-posted_at")[:6],
        "recent_news": NewsPost.objects.select_related("tournament").order_by("-published_at")[:6],
    }
    return render(request, "admin_dashboard.html", context)


@admin_required
def admin_tournaments(request):
    tournaments = Tournament.objects.all().order_by("-start_date")
    return render(request, "admin/tournaments.html", {
        "tournaments": tournaments,
        "active_tab": "tournaments",
    })


@admin_required
def admin_matches(request):
    matches = Match.objects.select_related("home__player", "away__player", "stage", "tournament").order_by("-scheduled_at")
    return render(request, "admin/matches.html", {
        "matches": matches,
        "active_tab": "matches",
    })


@admin_required
def admin_players(request):
    players = Player.objects.all().order_by("-joined_at")
    return render(request, "admin/players.html", {
        "players": players,
        "active_tab": "players",
    })


@admin_required
def admin_news_posts(request):
    news_posts = NewsPost.objects.select_related("tournament", "author").order_by("-published_at")
    return render(request, "admin/news_posts.html", {
        "news_posts": news_posts,
        "active_tab": "news_posts",
    })


@admin_required
def admin_live_updates(request):
    updates = Update.objects.select_related("tournament", "match").order_by("-posted_at")
    return render(request, "admin/live_updates.html", {
        "updates": updates,
        "active_tab": "live_updates",
    })


@admin_required
def admin_ai_queries(request):
    queries = AIQueryLog.objects.select_related("tournament", "user").order_by("-created_at")
    return render(request, "admin/ai_queries.html", {
        "queries": queries,
        "active_tab": "ai_queries",
    })


# ---------------------------------------------------------------------------
# Admin CRUD - Tournaments
# ---------------------------------------------------------------------------

@admin_required
def create_tournament(request):
    if request.method == "POST":
        form = TournamentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Tournament created successfully!")
            return redirect("admin_tournaments")
    else:
        form = TournamentForm()
    return render(request, "create_tournament.html", {"form": form, "active_tab": "tournaments"})


@admin_required
def edit_tournament(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    
    # Get all players
    all_players = Player.objects.all().order_by("name")
    # Get current participant player IDs
    current_player_ids = set(Participant.objects.filter(tournament=tournament).values_list("player_id", flat=True))
    
    if request.method == "POST":
        form = TournamentForm(request.POST, request.FILES, instance=tournament)
        if form.is_valid():
            tournament = form.save()
            
            # Update participants
            selected_player_ids = [int(pid) for pid in request.POST.getlist("participants") if pid.isdigit()]
            
            # Players to add
            to_add = [pid for pid in selected_player_ids if pid not in current_player_ids]
            # Players to remove
            to_remove = [pid for pid in current_player_ids if pid not in selected_player_ids]
            
            for pid in to_add:
                Participant.objects.create(tournament=tournament, player_id=pid)
            Participant.objects.filter(tournament=tournament, player_id__in=to_remove).delete()
            
            messages.success(request, f"Tournament '{tournament.name}' updated successfully.")
            return redirect("admin_tournaments")
    else:
        form = TournamentForm(instance=tournament)
        
    return render(request, "admin/edit_tournament.html", {
        "form": form,
        "tournament": tournament,
        "all_players": all_players,
        "current_player_ids": current_player_ids,
        "active_tab": "tournaments"
    })


@admin_required
def delete_tournament(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    if request.method == "POST":
        tournament.delete()
        messages.success(request, "Tournament deleted successfully.")
        return redirect("admin_tournaments")
    return render(request, "admin/delete_confirm.html", {"object": tournament, "title": "Delete Tournament", "back_url": "admin_tournaments", "active_tab": "tournaments"})


# ---------------------------------------------------------------------------
# Admin CRUD - Matches
# ---------------------------------------------------------------------------

@admin_required
def create_match(request):
    """Tournament-scoped match creator with dynamic dropdown support."""
    tournaments = Tournament.objects.all().order_by("name")
    selected_tournament_id = request.POST.get("tournament_id") or request.GET.get("tournament_id")
    selected_tournament = None
    stages = Stage.objects.none()
    participants = Participant.objects.none()

    if selected_tournament_id:
        selected_tournament = Tournament.objects.filter(pk=selected_tournament_id).first()
        if selected_tournament:
            stages = Stage.objects.filter(tournament=selected_tournament).order_by("order")
            participants = Participant.objects.filter(tournament=selected_tournament).select_related("player").order_by("player__name")

    if request.method == "POST":
        form = MatchForm(request.POST)
        # Restrict querysets to selected tournament so form validation passes
        if selected_tournament:
            form.fields["stage"].queryset = stages
            form.fields["home"].queryset = participants
            form.fields["away"].queryset = participants
        if not selected_tournament:
            form.add_error(None, "You must select a tournament first.")
        if form.is_valid():
            match = form.save(commit=False)
            match.tournament = selected_tournament
            match.save()
            messages.success(request, "Match created successfully!")
            # Auto-create Live Update if match is active from the start
            if match.status == "active":
                Update.objects.create(
                    tournament=match.tournament or (match.stage.tournament if match.stage else None),
                    match=match,
                    body=f"LIVE NOW: {match.home_name} vs {match.away_name} is underway at {match.venue or 'PES Arena'}!"
                )
            return redirect("admin_matches")
    else:
        form = MatchForm()
        if selected_tournament:
            form.fields["stage"].queryset = stages
            form.fields["home"].queryset = participants
            form.fields["away"].queryset = participants
        else:
            form.fields["stage"].queryset = Stage.objects.none()
            form.fields["home"].queryset = Participant.objects.none()
            form.fields["away"].queryset = Participant.objects.none()

    return render(request, "admin/create_match.html", {
        "form": form,
        "tournaments": tournaments,
        "selected_tournament": selected_tournament,
        "participants_json": json.dumps([
            {"id": p.id, "label": f"{p.player.gamer_tag or p.player.name} ({p.player.name})"}
            for p in participants
        ]),
        "active_tab": "matches",
    })


# AJAX helpers for dynamic dropdowns
@admin_required
def ajax_stages_for_tournament(request, tournament_id):
    stages = Stage.objects.filter(tournament_id=tournament_id).values("id", "name")
    return JsonResponse({"stages": list(stages)})


@admin_required
def ajax_groups_for_stage(request, stage_id):
    from .models import Group
    groups = Group.objects.filter(stage_id=stage_id).values("id", "name")
    return JsonResponse({"groups": list(groups)})


@admin_required
def ajax_participants_for_tournament(request, tournament_id):
    parts = Participant.objects.filter(tournament_id=tournament_id).select_related("player")
    data = [{"id": p.id, "label": f"{p.player.gamer_tag or p.player.name} ({p.player.name})"} for p in parts]
    return JsonResponse({"participants": data})


@admin_required
def edit_match(request, pk):
    match = get_object_or_404(Match, pk=pk)
    events = match.events.select_related("player").order_by("minute", "created_at")
    
    if request.method == "POST":
        old_status = match.status
        form = MatchForm(request.POST, instance=match)
        if form.is_valid():
            match = form.save()
            messages.success(request, "Match scores and stats updated successfully.")
            
            # Handle automatic status transition tickers
            if match.status != old_status:
                if match.status == 'active':
                    Update.objects.create(
                        tournament=match.tournament or (match.stage.tournament if match.stage else None),
                        match=match,
                        body=f"KICK-OFF: {match.home_name} vs {match.away_name} is now underway at {match.venue or 'PES Arena'}!"
                    )
                elif match.status == 'completed':
                    Update.objects.create(
                        tournament=match.tournament or (match.stage.tournament if match.stage else None),
                        match=match,
                        body=f"FULL TIME: {match.home_name} {match.home_score} : {match.away_score} {match.away_name}! Final result logged."
                    )
            return redirect("admin_matches")
    else:
        form = MatchForm(instance=match)
    
    # Prepare MatchEventForm for inline event logging
    event_form = MatchEventForm()
    # Filter event form players to only home/away participants to avoid selecting unrelated players
    player_ids = [pid for pid in [match.home_player_id, match.away_player_id] if pid]
    event_form.fields['player'].queryset = Player.objects.filter(id__in=player_ids)

    return render(request, "admin/edit_match.html", {
        "form": form,
        "match": match,
        "events": events,
        "event_form": event_form,
        "active_tab": "matches",
    })


@admin_required
def delete_match(request, pk):
    match = get_object_or_404(Match, pk=pk)
    if request.method == "POST":
        match.delete()
        messages.success(request, "Match deleted successfully.")
        return redirect("admin_matches")
    return render(request, "admin/delete_confirm.html", {"object": match, "title": "Delete Match", "back_url": "admin_matches", "active_tab": "matches"})


@admin_required
def add_match_event(request, pk):
    match = get_object_or_404(Match, pk=pk)
    if request.method == "POST":
        form = MatchEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.match = match
            event.save()
            messages.success(request, "Event logged to match timeline.")
            
            # Auto-score calculation
            if event.event_type == 'goal':
                if match.home_player_id and event.player_id == match.home_player_id:
                    match.home_score = (match.home_score or 0) + 1
                elif match.away_player_id and event.player_id == match.away_player_id:
                    match.away_score = (match.away_score or 0) + 1
                match.save()
            elif event.event_type == 'own_goal':
                if match.home_player_id and event.player_id == match.home_player_id:
                    match.away_score = (match.away_score or 0) + 1
                elif match.away_player_id and event.player_id == match.away_player_id:
                    match.home_score = (match.home_score or 0) + 1
                match.save()

            # Create Live update
            body = f"Event: {event.minute}' - {event.get_event_type_display()} by {event.player.name}!"
            if event.event_type in ['goal', 'own_goal']:
                body = f"GOAL! {event.player.name} ({event.minute}') - {match.home_name} {match.home_score} : {match.away_score} {match.away_name}!"
            
            Update.objects.create(
                tournament=match.tournament or (match.stage.tournament if match.stage else None),
                match=match,
                body=body
            )

            # Trigger push notification simulation for favorites
            favs = FavoriteMatch.objects.filter(match=match)
            if favs.exists():
                users = ", ".join([f.user.username for f in favs])
                messages.info(request, f"[PUSH ALERT SIMULATOR] Sent Google Chrome notifications to: {users} - '{body}'")

    return redirect("edit_match", pk=pk)


@admin_required
def delete_match_event(request, pk):
    event = get_object_or_404(MatchEvent, pk=pk)
    match = event.match
    
    # Reverse score calculation if deleting goal
    if event.event_type == 'goal':
        if match.home_player_id and event.player_id == match.home_player_id:
            match.home_score = max(0, (match.home_score or 1) - 1)
        elif match.away_player_id and event.player_id == match.away_player_id:
            match.away_score = max(0, (match.away_score or 1) - 1)
        match.save()
    elif event.event_type == 'own_goal':
        if match.home_player_id and event.player_id == match.home_player_id:
            match.away_score = max(0, (match.away_score or 1) - 1)
        elif match.away_player_id and event.player_id == match.away_player_id:
            match.home_score = max(0, (match.home_score or 1) - 1)
        match.save()

    event.delete()
    messages.success(request, "Event removed from match timeline.")
    return redirect("edit_match", pk=match.pk)


# ---------------------------------------------------------------------------
# Admin CRUD - Players
# ---------------------------------------------------------------------------

@admin_required
def create_player(request):
    if request.method == "POST":
        form = PlayerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Player registered successfully!")
            return redirect("admin_players")
    else:
        form = PlayerForm()
    return render(request, "admin/create_player.html", {"form": form, "active_tab": "players"})


@admin_required
def edit_player(request, pk):
    player = get_object_or_404(Player, pk=pk)
    if request.method == "POST":
        form = PlayerForm(request.POST, request.FILES, instance=player)
        if form.is_valid():
            form.save()
            messages.success(request, f"Player profile '{player.name}' updated successfully.")
            return redirect("admin_players")
    else:
        form = PlayerForm(instance=player)
    return render(request, "admin/edit_player.html", {"form": form, "player": player, "active_tab": "players"})


@admin_required
def delete_player(request, pk):
    player = get_object_or_404(Player, pk=pk)
    if request.method == "POST":
        player.delete()
        messages.success(request, "Player profile deleted.")
        return redirect("admin_players")
    return render(request, "admin/delete_confirm.html", {"object": player, "title": "Delete Player Profile", "back_url": "admin_players", "active_tab": "players"})


# ---------------------------------------------------------------------------
# Admin CRUD - News Posts
# ---------------------------------------------------------------------------

@admin_required
def create_news_post(request):
    if request.method == "POST":
        form = NewsPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "News post published!")
            return redirect("admin_news_posts")
    else:
        form = NewsPostForm()
    return render(request, "admin/create_news_post.html", {"form": form, "active_tab": "news_posts"})


@admin_required
def edit_news_post(request, pk):
    post = get_object_or_404(NewsPost, pk=pk)
    if request.method == "POST":
        form = NewsPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "News post updated.")
            return redirect("admin_news_posts")
    else:
        form = NewsPostForm(instance=post)
    return render(request, "admin/edit_news_post.html", {"form": form, "post": post, "active_tab": "news_posts"})


@admin_required
def delete_news_post(request, pk):
    post = get_object_or_404(NewsPost, pk=pk)
    if request.method == "POST":
        post.delete()
        messages.success(request, "News post deleted.")
        return redirect("admin_news_posts")
    return render(request, "admin/delete_confirm.html", {"object": post, "title": "Delete News Post", "back_url": "admin_news_posts", "active_tab": "news_posts"})


# ---------------------------------------------------------------------------
# Admin CRUD - Live Updates
# ---------------------------------------------------------------------------

@admin_required
def create_live_update(request):
    if request.method == "POST":
        form = UpdateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Live update ticker posted.")
            return redirect("admin_live_updates")
    else:
        form = UpdateForm()
    return render(request, "admin/create_live_update.html", {"form": form, "active_tab": "live_updates"})


@admin_required
def edit_live_update(request, pk):
    update = get_object_or_404(Update, pk=pk)
    if request.method == "POST":
        form = UpdateForm(request.POST, instance=update)
        if form.is_valid():
            form.save()
            messages.success(request, "Live update ticker updated.")
            return redirect("admin_live_updates")
    else:
        form = UpdateForm(instance=update)
    return render(request, "admin/edit_live_update.html", {"form": form, "update": update, "active_tab": "live_updates"})


@admin_required
def delete_live_update(request, pk):
    update = get_object_or_404(Update, pk=pk)
    if request.method == "POST":
        update.delete()
        messages.success(request, "Live update ticker deleted.")
        return redirect("admin_live_updates")
    return render(request, "admin/delete_confirm.html", {"object": update, "title": "Delete Live Update", "back_url": "admin_live_updates", "active_tab": "live_updates"})


# ---------------------------------------------------------------------------
# Admin CRUD - AI Queries
# ---------------------------------------------------------------------------

@admin_required
def delete_ai_query(request, pk):
    query = get_object_or_404(AIQueryLog, pk=pk)
    if request.method == "POST":
        query.delete()
        messages.success(request, "AI query log deleted.")
        return redirect("admin_ai_queries")
    return render(request, "admin/delete_confirm.html", {"object": query, "title": "Delete AI Query Log", "back_url": "admin_ai_queries", "active_tab": "ai_queries"})