from django import forms
from .models import Contact, ContactReply, SiteSettings, MentorshipApplication, SponsorshipTier, SponsorshipInquiry, VolunteerApplication

class MentorshipApplicationForm(forms.ModelForm):
    # Overridden as a standalone field so we get CheckboxSelectMultiple
    # and can validate/join the list before saving.
    tech_interests = forms.MultipleChoiceField(
        choices=MentorshipApplication.TECH_FIELD_CHOICES,
        widget=forms.CheckboxSelectMultiple(),
        label='What tech field are you most interested in pursuing?',
        error_messages={'required': 'Please select at least one tech field.'},
    )
    agreed_to_terms = forms.BooleanField(
        label=(
            'I understand that this is a free program, and I agree to actively '
            'participate, complete assignments, and follow the program\u2019s guidelines.'
        ),
        error_messages={'required': 'You must agree to the program guidelines to apply.'},
    )

    class Meta:
        model = MentorshipApplication
        fields = [
            'full_name', 'email', 'address', 'phone_number', 'country',
            'python_community_member', 'python_community_name',
            'experience_level', 'programming_experience',
            'mentorship_stream', 'tech_interests',
            'reason_for_joining', 'schedule_commitment', 'device_access',
            'referral_source', 'referral_other', 'questions_concerns', 'agreed_to_terms',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your full name as it should appear on your certificate'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your current address'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +234 811 589 7450'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Nigeria'}),
            'python_community_member': forms.RadioSelect(),
            'python_community_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Black Python Devs, PyData Nairobi'}),
            'experience_level': forms.RadioSelect(),
            'programming_experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe any programming experience you have. If a complete beginner, leave this blank.'}),
            'mentorship_stream': forms.RadioSelect(),
            'reason_for_joining': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Share your goals, what you hope to gain, and why this opportunity is important to you. (100\u2013200 words)'}),
            'schedule_commitment': forms.RadioSelect(),
            'device_access': forms.RadioSelect(),
            'referral_source': forms.RadioSelect(),
            'referral_other': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Please specify'}),
            'questions_concerns': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Feel free to ask anything about the program structure, schedule, or requirements.'}),
        }
        labels = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'address': 'Address',
            'phone_number': 'Phone Number (with Country Code)',
            'country': 'Country of Residence',
            'python_community_member': 'Are you a member of a Python community?',
            'python_community_name': 'If yes, which community?',
            'experience_level': 'What is your current level of experience with Python?',
            'programming_experience': 'What is your experience with programming in general? (Optional)',
            'mentorship_stream': 'Choose the stream of mentorship you are interested in',
            'reason_for_joining': 'Why do you want to join this mentorship program?',
            'schedule_commitment': 'Are you able to commit to virtual classes 3 times per week (Mon, Wed, Fri \u2014 1.5 hrs each) for 5 months?',
            'device_access': 'Do you have access to a reliable internet connection and a device for virtual classes and coding?',
            'referral_source': 'How did you hear about this program?',
            'referral_other': 'Please specify',
            'questions_concerns': 'Do you have any questions or concerns about the program? (Optional)',
        }



    def clean(self):
        cleaned = super().clean()
        
        # Enforce max length on TextFields
        max_lengths = {
            'programming_experience': 3000,
            'reason_for_joining': 3000,
            'questions_concerns': 3000,
        }
        for field, max_len in max_lengths.items():
            val = cleaned.get(field, '')
            if len(val) > max_len:
                self.add_error(field, f'This field is too long. Maximum {max_len} characters.')

        if cleaned.get('python_community_member') == 'yes' and not cleaned.get('python_community_name', '').strip():
            self.add_error('python_community_name', 'Please indicate which Python community you are a member of.')
        if cleaned.get('referral_source') == 'other' and not cleaned.get('referral_other', '').strip():
            self.add_error('referral_other', 'Please specify how you heard about us.')
        return cleaned



class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Message subject'
            }),
            'message': forms.Textarea(attrs={'maxlength': '5000', 
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Type your message here...'
            }),
        }
        labels = {
            'name': 'Full Name',
            'email': 'Email Address',
            'phone': 'Phone Number',
            'subject': 'Subject',
            'message': 'Your Message'
        }



class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = [
            'site_name',
            'support_email',
            'support_phone',
            'whatsapp_number',
            'address',
            'working_hours',
            'facebook_url',
            'twitter_url',
            'instagram_url',
            'linkedin_url',
            'youtube_url',
            'interview_booking_link',
        ]


class ContactReplyForm(forms.ModelForm):
    class Meta:
        model = ContactReply
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reply subject'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Your reply...'}),
        }



class SponsorshipTierForm(forms.ModelForm):
    class Meta:
        model = SponsorshipTier
        fields = ['name', 'price_display', 'description', 'features', 'is_recommended', 'icon_class', 'bg_class', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price_display': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. ₦150,000 (~$90)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'features': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 8,
                'placeholder': 'Logo on website & certificates\nBrand tagged in 24 sponsor posts\nMention in final impact report',
            }),
            'is_recommended': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'icon_class': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fas fa-medal'}),
            'bg_class': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'bronze-bg'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class SponsorshipInquiryForm(forms.ModelForm):
    class Meta:
        model = SponsorshipInquiry
        fields = ['company_name', 'contact_person', 'email', 'whatsapp_number', 'tier', 'message']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+234...'}),
            'tier': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class SponsorshipDashboardForm(forms.ModelForm):
    class Meta:
        model = SponsorshipInquiry
        fields = ['company_name', 'contact_person', 'email', 'whatsapp_number', 'tier', 'message', 'status', 'internal_notes']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control'}),
            'tier': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'internal_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class VolunteerApplicationForm(forms.ModelForm):
    areas_of_expertise = forms.MultipleChoiceField(
        choices=VolunteerApplication.EXPERTISE_CHOICES,
        widget=forms.CheckboxSelectMultiple(),
        label='Areas of Expertise',
        error_messages={'required': 'Please select at least one area of expertise.'},
    )

    class Meta:
        model = VolunteerApplication
        fields = [
            'full_name', 'email', 'phone_number', 'country',
            'linkedin_profile', 'github_profile',
            'role_interest', 'role_other',
            'job_title_company', 'years_of_experience',
            'areas_of_expertise', 'professional_bio',
            'motivation', 'hours_per_week', 'evening_availability', 'commitment_length',
            'cv_resume', 'additional_comments'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number / WhatsApp'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country of Residence'}),
            'linkedin_profile': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/...'}),
            'github_profile': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/... (Optional)'}),
            'role_interest': forms.RadioSelect(),
            'role_other': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Please specify if Other'}),
            'job_title_company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Current Job Title & Company/Organization'}),
            'years_of_experience': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 5 years'}),
            'professional_bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Brief Professional Bio (150–300 words)'}),
            'motivation': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Why do you want to volunteer with the From Zero to Hero Program?'}),
            'hours_per_week': forms.RadioSelect(),
            'evening_availability': forms.RadioSelect(),
            'commitment_length': forms.RadioSelect(),
            'cv_resume': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
            'additional_comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any questions or additional comments?'}),
        }

    def clean(self):
        cleaned = super().clean()

        # Enforce max length on TextFields (no model-level limit)
        max_lengths = {
            'professional_bio': 5000,
            'motivation': 5000,
            'additional_comments': 3000,
        }
        for field, max_len in max_lengths.items():
            val = cleaned.get(field, '')
            if len(val) > max_len:
                self.add_error(field, f'This field is too long. Maximum {max_len} characters.')

        if cleaned.get('role_interest') == 'other' and not cleaned.get('role_other', '').strip():
            self.add_error('role_other', 'Please specify your role interest.')

        return cleaned