from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing_page, name="landing"),
    path("staff-login/", views.staff_login, name="staff_login"),
    
    # Public views
    path("tournament/<slug:slug>/", views.tournament_detail, name="tournament_detail"),
    path("match/<int:pk>/", views.match_detail, name="match_detail"),
    path("match/<int:pk>/favorite/", views.toggle_favorite_match, name="toggle_favorite_match"),
    path("match/<int:pk>/comment/", views.add_match_comment, name="add_match_comment"),
    path("news/<slug:slug>/", views.news_detail, name="news_detail"),
    path("news/<slug:slug>/comment/", views.add_news_comment, name="add_news_comment"),
    path("news/<slug:slug>/like/", views.like_news_post, name="like_news_post"),

    # Admin Dashboard main tabs
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-dashboard/tournaments/", views.admin_tournaments, name="admin_tournaments"),
    path("admin-dashboard/matches/", views.admin_matches, name="admin_matches"),
    path("admin-dashboard/players/", views.admin_players, name="admin_players"),
    path("admin-dashboard/news-posts/", views.admin_news_posts, name="admin_news_posts"),
    path("admin-dashboard/live-updates/", views.admin_live_updates, name="admin_live_updates"),
    path("admin-dashboard/ai-queries/", views.admin_ai_queries, name="admin_ai_queries"),

    # Admin CRUD - Tournaments
    path("admin-dashboard/tournament/create/", views.create_tournament, name="create_tournament"),
    path("admin-dashboard/tournament/<int:pk>/edit/", views.edit_tournament, name="edit_tournament"),
    path("admin-dashboard/tournament/<int:pk>/delete/", views.delete_tournament, name="delete_tournament"),

    # Admin CRUD - Matches & Events
    path("admin-dashboard/match/create/", views.create_match, name="create_match"),
    path("admin-dashboard/match/<int:pk>/edit/", views.edit_match, name="edit_match"),
    path("admin-dashboard/match/<int:pk>/delete/", views.delete_match, name="delete_match"),
    path("admin-dashboard/match/<int:pk>/event/add/", views.add_match_event, name="add_match_event"),
    path("admin-dashboard/match-event/<int:pk>/delete/", views.delete_match_event, name="delete_match_event"),

    # AJAX helpers – dynamic dropdowns on create_match
    path("ajax/stages/<int:tournament_id>/", views.ajax_stages_for_tournament, name="ajax_stages"),
    path("ajax/groups/<int:stage_id>/", views.ajax_groups_for_stage, name="ajax_groups"),
    path("ajax/participants/<int:tournament_id>/", views.ajax_participants_for_tournament, name="ajax_participants"),

    # Admin CRUD - Players
    path("admin-dashboard/player/create/", views.create_player, name="create_player"),
    path("admin-dashboard/player/<int:pk>/edit/", views.edit_player, name="edit_player"),
    path("admin-dashboard/player/<int:pk>/delete/", views.delete_player, name="delete_player"),

    # Admin CRUD - News Posts
    path("admin-dashboard/news-post/create/", views.create_news_post, name="create_news_post"),
    path("admin-dashboard/news-post/<int:pk>/edit/", views.edit_news_post, name="edit_news_post"),
    path("admin-dashboard/news-post/<int:pk>/delete/", views.delete_news_post, name="delete_news_post"),

    # Admin CRUD - Live Updates
    path("admin-dashboard/live-update/create/", views.create_live_update, name="create_live_update"),
    path("admin-dashboard/live-update/<int:pk>/edit/", views.edit_live_update, name="edit_live_update"),
    path("admin-dashboard/live-update/<int:pk>/delete/", views.delete_live_update, name="delete_live_update"),

    # Admin CRUD - AI Queries
    path("admin-dashboard/ai-query/<int:pk>/delete/", views.delete_ai_query, name="delete_ai_query"),
]