from django import forms
from django.utils.safestring import mark_safe
from .models import Senator, ContactList

def getContactListChoices():
    def c2t(c):
        return mark_safe(
            "<strong><a href=\"./?lists=%s\">%s</a></strong><br/>"\
            "<em>%s</em><br/>"\
            "Senators: %s<br/><br/>" % \
            (c.slug, c.title, c.description,
             ', '.join([s.lastName for s in c.senators.all()])))
    return reversed([(s.id, c2t(s)) for s in ContactList.objects.filter(public=True)])

def getSenatorChoices():
    def s2t(s): return "[%s] %s, %s" % (s.state.name, s.lastName, s.firstName)
    return sorted([(s.id, s2t(s)) for s in Senator.objects.all()],
                   key=lambda x: x[1])

class ChooseForm(forms.ModelForm):
    class Meta:
        model = ContactList
        fields = ['title', 'description', 'public', 'senators']

    title = forms.CharField(
        label="Name your Call to Action",
        help_text=mark_safe("<br/><em>Briefly describe the cause. For example: \"Fight the AHCA\"</em><br/><br/>"),
        label_suffix=mark_safe("<br/>"),
        required=True)

    description = forms.CharField(
        label="Longer description and call script",
        label_suffix=mark_safe("<br/>"),
        widget=forms.Textarea(attrs={"rows": 5, "cols": 35}),
        help_text="<br/>What should people tell their friends "
                  "to tell their senators. Markdown allowed. "
                  "<a onClick=\"toggleCheetsheet()\">[markdown cheatsheet]</a><br/><br/>",
        required=True)

    public = forms.BooleanField(
        label = "Make public?",
        label_suffix = "",
        required = False,
        initial = 1,
        help_text="<br/>If checked, this will show up in \"View public calls to actions\" <br/><br/>")

    senators = forms.MultipleChoiceField(
        widget  = forms.CheckboxSelectMultiple,
        choices = getSenatorChoices)

class CombineForm(forms.Form):
    contactLists = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
        choices=getContactListChoices,
        label = "")
