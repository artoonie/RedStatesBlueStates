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

    #title = forms.CharField(label='Title', max_length=128)
    #desc = forms.CharField(label='Description', max_length=1024)
    senators = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
        choices=getSenatorChoices)

class CombineForm(forms.Form):
    contactLists = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
        choices=getContactListChoices,
        label = "Choose which lists of senators to combine onto one map")
