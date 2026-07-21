from django import forms
from .models import Tournament, Match, Player, NewsPost, Update, MatchEvent

class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = [
            "name",
            "description",
            "status",
            "start_date",
            "end_date",
            "logo",
            "banner_image",
            "primary_color",
            "secondary_color",
            "accent_color",
        ]
        widgets = {
            "description": forms.Textarea(attrs={
                "rows": 3,
                "class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-3 text-white placeholder-neutral-500 focus:border-emerald-400 focus:outline-none transition text-sm"
            }),
            "name": forms.TextInput(attrs={
                "class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-3 text-white placeholder-neutral-500 focus:border-emerald-400 focus:outline-none transition text-sm"
            }),
            "status": forms.Select(attrs={
                "class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-3 text-white placeholder-neutral-500 focus:border-emerald-400 focus:outline-none transition text-sm"
            }),
            "start_date": forms.DateInput(attrs={
                "type": "date",
                "class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-3 text-white placeholder-neutral-500 focus:border-emerald-400 focus:outline-none transition text-sm"
            }),
            "end_date": forms.DateInput(attrs={
                "type": "date",
                "class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-3 text-white placeholder-neutral-500 focus:border-emerald-400 focus:outline-none transition text-sm"
            }),
            "primary_color": forms.TextInput(attrs={
                "type": "color",
                "class": "mt-1 h-12 w-full rounded-xl border border-white/10 bg-neutral-950 p-1 cursor-pointer focus:border-emerald-400 focus:outline-none transition"
            }),
            "secondary_color": forms.TextInput(attrs={
                "type": "color",
                "class": "mt-1 h-12 w-full rounded-xl border border-white/10 bg-neutral-950 p-1 cursor-pointer focus:border-emerald-400 focus:outline-none transition"
            }),
            "accent_color": forms.TextInput(attrs={
                "type": "color",
                "class": "mt-1 h-12 w-full rounded-xl border border-white/10 bg-neutral-950 p-1 cursor-pointer focus:border-emerald-400 focus:outline-none transition"
            }),
            "logo": forms.FileInput(attrs={
                "class": "mt-1 w-full text-sm text-neutral-400 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-white/10 file:text-white hover:file:bg-white/15 file:cursor-pointer"
            }),
            "banner_image": forms.FileInput(attrs={
                "class": "mt-1 w-full text-sm text-neutral-400 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-white/10 file:text-white hover:file:bg-white/15 file:cursor-pointer"
            }),
        }


class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = [
            "stage",
            "group",
            "home",
            "away",
            "round_name",
            "leg",
            "scheduled_at",
            "status",
            "venue",
            "home_score",
            "away_score",
            "home_shots",
            "away_shots",
            "home_shots_on_target",
            "away_shots_on_target",
            "home_possession",
            "away_possession",
            "home_fouls",
            "away_fouls",
            "home_corners",
            "away_corners",
            "home_yellow_cards",
            "away_yellow_cards",
            "home_red_cards",
            "away_red_cards",
        ]
        widgets = {
            "stage": forms.Select(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-2.5 text-white text-sm"}),
            "group": forms.Select(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-2.5 text-white text-sm"}),
            "home": forms.Select(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-2.5 text-white text-sm"}),
            "away": forms.Select(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-2.5 text-white text-sm"}),
            "round_name": forms.TextInput(attrs={"placeholder": "e.g. Matchday 1", "class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-2.5 text-white placeholder-neutral-500 text-sm"}),
            "leg": forms.NumberInput(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-2.5 text-white text-sm"}),
            "scheduled_at": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-2.5 text-white text-sm"}),
            "status": forms.Select(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-2.5 text-white text-sm"}),
            "venue": forms.TextInput(attrs={"placeholder": "Stadium/Arena Name", "class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-2.5 text-white placeholder-neutral-500 text-sm"}),
            
            "home_score": forms.NumberInput(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-2.5 text-white text-sm"}),
            "away_score": forms.NumberInput(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-2.5 text-white text-sm"}),
            
            "home_shots": forms.NumberInput(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-2 text-sm"}),
            "away_shots": forms.NumberInput(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-2 text-sm"}),
            "home_shots_on_target": forms.NumberInput(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-2 text-sm"}),
            "away_shots_on_target": forms.NumberInput(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-2 text-sm"}),
            "home_possession": forms.NumberInput(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-2 text-sm"}),
            "away_possession": forms.NumberInput(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-2 text-sm"}),
            "home_fouls": forms.NumberInput(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-2 text-sm"}),
            "away_fouls": forms.NumberInput(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-2 text-sm"}),
            "home_corners": forms.NumberInput(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-2 text-sm"}),
            "away_corners": forms.NumberInput(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-2 text-sm"}),
            "home_yellow_cards": forms.NumberInput(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-2 text-sm"}),
            "away_yellow_cards": forms.NumberInput(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-2 text-sm"}),
            "home_red_cards": forms.NumberInput(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-2 text-sm"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        home = cleaned_data.get("home")
        away = cleaned_data.get("away")
        
        if home and away and home == away:
            raise forms.ValidationError("Home and Away players must be different.")
        return cleaned_data



class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ["name", "gamer_tag", "avatar", "bio"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-3 text-white text-sm"}),
            "gamer_tag": forms.TextInput(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-3 text-white text-sm"}),
            "bio": forms.Textarea(attrs={"rows": 3, "class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-3 text-white text-sm"}),
            "avatar": forms.FileInput(attrs={"class": "mt-1 w-full text-sm text-neutral-400 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-white/10 file:text-white hover:file:bg-white/15 file:cursor-pointer"}),
        }


class NewsPostForm(forms.ModelForm):
    class Meta:
        model = NewsPost
        fields = ["tournament", "title", "slug", "body", "cover_image", "is_ai_generated"]
        widgets = {
            "tournament": forms.Select(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-3 text-white text-sm"}),
            "title": forms.TextInput(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-3 text-white text-sm"}),
            "slug": forms.TextInput(attrs={"placeholder": "Leave blank to autogenerate", "class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-3 text-white text-sm"}),
            "body": forms.Textarea(attrs={"rows": 6, "class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-3 text-white text-sm"}),
            "cover_image": forms.FileInput(attrs={"class": "mt-1 w-full text-sm text-neutral-400 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-white/10 file:text-white hover:file:bg-white/15 file:cursor-pointer"}),
            "is_ai_generated": forms.CheckboxInput(attrs={"class": "h-4 w-4 rounded border-white/10 bg-neutral-950 text-emerald-500 focus:ring-emerald-400 focus:ring-offset-neutral-900"}),
        }


class UpdateForm(forms.ModelForm):
    class Meta:
        model = Update
        fields = ["tournament", "match", "body"]
        widgets = {
            "tournament": forms.Select(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-3 text-white text-sm"}),
            "match": forms.Select(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-3 text-white text-sm"}),
            "body": forms.Textarea(attrs={"rows": 3, "class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-3 text-white text-sm"}),
        }


class MatchEventForm(forms.ModelForm):
    class Meta:
        model = MatchEvent
        fields = ["minute", "event_type", "player", "detail"]
        widgets = {
            "minute": forms.NumberInput(attrs={"min": 1, "max": 120, "class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-3 text-white text-sm"}),
            "event_type": forms.Select(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-3 text-white text-sm"}),
            "player": forms.Select(attrs={"class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-3 text-white text-sm"}),
            "detail": forms.TextInput(attrs={"placeholder": "e.g. Assist by GamerX / Reason for card", "class": "mt-1 w-full rounded-xl border border-white/10 bg-neutral-950 px-4 py-3 text-white text-sm"}),
        }
