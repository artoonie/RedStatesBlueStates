from django import forms
from django.utils.safestring import mark_safe
from .models import Senator, ContactList

def getContactListChoices():
    def c2t(c):
        return mark_safe(
            "<strong><a href=\"%s\">%s</a></strong><br/>"\
            "<em>%s</em><br/><br/>"\
            "Senators: %s<br/>"\
            "Unique ID: %s<br/><br/><br/><br/>" % \
            (c.fbUrl, c.title, c.description,
             ', '.join([s.lastName for s in c.senators.all()]), c.uid))
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
        label="Title",
        help_text=mark_safe("<br/><em>Which senators are included in this list?</em>"),
        label_suffix=mark_safe("<br/>"),
        required=True)

    description = forms.CharField(
        label="Description",
        label_suffix=mark_safe("<br/>"),
        widget=forms.Textarea(attrs={"rows": 5, "cols": 35}),
        help_text="<br/>Call to action: what should people tell their friends "
                  "to tell their senators. Markdown allowed: **bold**, "
                  "[link](http://url).<br/>"
                  "<a onClick=\"toggleCheetsheet()\">[markdown cheatsheet]</a>",
        required=True)
    senators = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
        choices=getSenatorChoices)

class CombineForm(forms.Form):
    contactLists = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
        choices=getContactListChoices,
        label = "Choose which lists of senators to combine onto one map")
