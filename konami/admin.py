from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import (
    Tournament, Stage, Group, Player, Participant, Match,
    Profile, Favorite, Prediction, Comment, Like,
    Tag, NewsPost, Update, AIQueryLog,
)


# ---------------------------------------------------------------------
# Inlines
# ---------------------------------------------------------------------

class StageInline(admin.TabularInline):
    model = Stage
    extra = 0
    show_change_link = True


class GroupInline(admin.TabularInline):
    model = Group
    extra = 0


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"


# ---------------------------------------------------------------------
# Admin classes
# ---------------------------------------------------------------------

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "start_date", "end_date", "created_at")
    list_filter = ("status",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [StageInline]


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ("name", "tournament", "type", "order")
    list_filter = ("type", "tournament")
    search_fields = ("name", "tournament__name")
    inlines = [GroupInline]


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "stage")
    list_filter = ("stage__tournament",)
    search_fields = ("name", "stage__name")


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("name", "gamer_tag", "joined_at")
    search_fields = ("name", "gamer_tag")


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("player", "tournament", "group", "seed")
    list_filter = ("tournament", "group")
    search_fields = ("player__name", "player__gamer_tag")


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("__str__", "stage", "group", "status", "home_score", "away_score", "scheduled_at")
    list_filter = ("status", "stage__tournament", "stage")
    search_fields = ("home__player__name", "away__player__name")
    raw_id_fields = ("home", "away")  # helpful if you have many participants


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "player", "created_at")
    search_fields = ("user__username", "player__name")


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ("user", "match", "predicted_home", "predicted_away", "points_awarded", "created_at")
    list_filter = ("match__stage__tournament",)
    search_fields = ("user__username",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "target", "created_at")
    search_fields = ("user__username", "body")

    def target(self, obj):
        return obj.news_post or obj.match
    target.short_description = "On"


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("user", "news_post", "created_at")
    search_fields = ("user__username", "news_post__title")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ("title", "tournament", "author", "is_ai_generated", "published_at")
    list_filter = ("tournament", "is_ai_generated", "tags")
    search_fields = ("title", "body")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)


@admin.register(Update)
class UpdateAdmin(admin.ModelAdmin):
    list_display = ("body_truncated", "tournament", "match", "posted_at")
    list_filter = ("tournament",)
    search_fields = ("body",)

    def body_truncated(self, obj):
        return obj.body[:60] + "..." if len(obj.body) > 60 else obj.body
    body_truncated.short_description = "Update"


@admin.register(AIQueryLog)
class AIQueryLogAdmin(admin.ModelAdmin):
    list_display = ("question_truncated", "tournament", "user", "created_at")
    list_filter = ("tournament",)
    search_fields = ("question", "answer")

    def question_truncated(self, obj):
        return obj.question[:60] + "..." if len(obj.question) > 60 else obj.question
    question_truncated.short_description = "Question"


# ---------------------------------------------------------------------
# Integrate Profile with the built-in User admin
# ---------------------------------------------------------------------

# First unregister the default User admin
admin.site.unregister(User)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = BaseUserAdmin.inlines + (ProfileInline,)