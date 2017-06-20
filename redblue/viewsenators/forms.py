from django import forms
from .models import Senator, ContactList

def getSenatorChoices():
    def s2t(s): return "[%s] %s, %s" % (s.state.name, s.firstName, s.lastName)
    return sorted([(s.id, s2t(s)) for s in Senator.objects.all()],
                   key=lambda x: x[1])

class ChooseForm(forms.ModelForm):
    class Meta:
        model = ContactList
        fields = ['title', 'description', 'senators']

    #title = forms.CharField(label='Title', max_length=128)
    #desc = forms.CharField(label='Description', max_length=1024)
    senators = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
        choices=getSenatorChoices)
