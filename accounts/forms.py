from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from django.forms.widgets import Select, Textarea, TextInput

from .models import (
    Message,
    Profile,
    Ticket,
    User,
)


class DateInput(forms.DateInput):
    input_type = 'date'


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email or Username',
            'autofocus': 'true',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
        })
    )


class SignUpForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    password2 = forms.CharField(required=True)
    accepted_terms = forms.BooleanField(required=True)

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'username', 'email', 'password', 'accepted_terms')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control', 'id': 'floatingInput',
            'placeholder': 'First Name', 'aria-describedby': 'nameHelp',
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control', 'id': 'floatingInput',
            'placeholder': 'Last Name', 'aria-describedby': 'nameHelp',
        })
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'id': 'name', 'placeholder': 'Username'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'id': 'email', 'placeholder': 'Email'})
        self.fields['password'].widget = forms.PasswordInput(attrs={
            'placeholder': 'Password', 'class': 'form form-control px-5', 'id': 'pass',
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password', 'class': 'form form-control px-5', 'id': 're_pass',
        })
        self.fields['accepted_terms'].widget.attrs.update({'class': 'custom-control-label'})

    def clean_email(self):
        return self.cleaned_data.get('email')

    def clean_username(self):
        return self.cleaned_data.get('username')

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        username = cleaned_data.get('username')
        
        has_error = False
        if email and get_user_model().objects.filter(email__iexact=email).exists():
            has_error = True
        if username and get_user_model().objects.filter(username__iexact=username).exists():
            has_error = True
            
        if has_error:
            raise forms.ValidationError('Please check the entered details and try again.')

        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password2')
        if p1 and p2:
            if p1 != p2:
                raise forms.ValidationError('Passwords do not match.')
            # Run Django's AUTH_PASSWORD_VALIDATORS against the submitted password.
            try:
                validate_password(p1, user=None)
            except DjangoValidationError as e:
                self.add_error('password', e)
        return cleaned_data


# Separate form for creating users — includes password field.
class CreateUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

    USER_ROLE_CHOICES = [
        ('', 'Choose Role'),
        ('admin', 'Admin'),
        ('mentee', 'Mentee'),
        ('mentor', 'Mentor'),
    ]
    user_role = forms.ChoiceField(
        choices=USER_ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='User Role',
    )

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'username', 'phone', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'First Name'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Last Name'})
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email'})
        self.fields['phone'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Phone number'})

    def clean_user_role(self):
        role = self.cleaned_data.get('user_role')
        if not role:
            raise forms.ValidationError('Please select a role.')
        return role

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        role = self.cleaned_data.get('user_role')
        user.is_admin = role == 'admin'
        user.is_mentor = role == 'mentor'
        user.is_mentee = role == 'mentee'
        # Admin-created accounts are pre-verified — no email link needed.
        user.is_verified = True
        if commit:
            user.save()
        return user


# Separate form for editing users — no password field to avoid plaintext overwrite.
class EditUserForm(forms.ModelForm):
    USER_ROLE_CHOICES = [
        ('', 'Choose Role'),
        ('admin', 'Admin'),
        ('mentee', 'Mentee'),
        ('mentor', 'Mentor'),
    ]
    user_role = forms.ChoiceField(
        choices=USER_ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='User Role',
    )

    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'username', 'phone', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'First Name'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Last Name'})
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email'})
        self.fields['phone'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Phone number'})
        if self.instance and self.instance.pk:
            if self.instance.is_admin:
                self.fields['user_role'].initial = 'admin'
            elif self.instance.is_mentor:
                self.fields['user_role'].initial = 'mentor'
            elif self.instance.is_mentee:
                self.fields['user_role'].initial = 'mentee'

    def clean_user_role(self):
        role = self.cleaned_data.get('user_role')
        if not role:
            raise forms.ValidationError('Please select a role.')
        return role

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data.get('user_role')
        user.is_admin = role == 'admin'
        user.is_mentor = role == 'mentor'
        user.is_mentee = role == 'mentee'
        if commit:
            user.save()
        return user


# Keep AddUserForm as an alias so existing imports don't break.
AddUserForm = CreateUserForm


class CompleteProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['address']


class UserProfileForm(forms.ModelForm):
    """Profile update form — email is intentionally excluded.

    Email changes require a separate verified flow to prevent account takeover
    via unverified email substitution + password reset.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'phone']
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'username': TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'phone': TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'address', 'date_of_birth', 'gender', 'profile_picture',
            'nationality', 'state_of_origin', 'current_city', 'current_state',
        ]
        widgets = {
            'address': Textarea(attrs={'class': 'form-control', 'placeholder': 'Address', 'rows': 3}),
            'date_of_birth': TextInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': Select(
                attrs={'class': 'form-control'},
                choices=[('', 'Select Gender'), ('Male', 'Male'), ('Female', 'Female')],
            ),
            'nationality': TextInput(attrs={'class': 'form-control', 'placeholder': 'Nationality'}),
            'state_of_origin': TextInput(attrs={'class': 'form-control', 'placeholder': 'State of Origin'}),
            'current_city': TextInput(attrs={'class': 'form-control', 'placeholder': 'City (e.g. Aba)'}),
            'current_state': TextInput(attrs={'class': 'form-control', 'placeholder': 'State (e.g. Abia)'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }


class PasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Old Password'})
        self.fields['new_password1'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'})
        self.fields['new_password2'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Re-Type Password'})


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['subject']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter ticket subject',
            })
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Type your message here',
                'rows': 3,
            })
        }


class TicketAssignmentForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(
            Q(is_admin=True) | Q(is_mentor=True)
        ),
        label='Assign To',
        empty_label='Choose a staff member',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = Ticket
        fields = ['assigned_to']