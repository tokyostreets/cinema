from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Ticket, Session

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)
    birth_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'phone', 'birth_date']

class TicketBookingForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['row', 'seat']
    
    def __init__(self, *args, **kwargs):
        self.session = kwargs.pop('session', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        row = cleaned_data.get('row')
        seat = cleaned_data.get('seat')
        
        if row and seat and self.session:
            if row > self.session.hall.seats_rows or seat > self.session.hall.seats_per_row:
                raise forms.ValidationError("Указано несуществующее место")
            
            if Ticket.objects.filter(session=self.session, row=row, seat=seat).exists():
                raise forms.ValidationError("Это место уже занято")
        
        return cleaned_data

class DiscountApplyForm(forms.Form):
    discount_code = forms.CharField(max_length=20, label='Код скидки')

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['movie', 'hall', 'start_time', 'base_price']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }