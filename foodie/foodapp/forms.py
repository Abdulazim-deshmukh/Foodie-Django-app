from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import Orders


# ============================================================
# ORDER FORM
# ============================================================

class OrderForm(forms.ModelForm):
    """
    Form used during checkout to collect delivery information.
    """

    class Meta:
        model = Orders

        fields = [
            "name",
            "address",
            "city",
            "state",
            "pincode",
            "phoneno",
        ]

        labels = {
            "name": "Full Name",
            "address": "Street Address",
            "city": "City",
            "state": "State",
            "pincode": "PIN Code",
            "phoneno": "Phone Number",
        }

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your full name",
                    "autocomplete": "name",
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your complete address",
                    "rows": 3,
                    "autocomplete": "street-address",
                }
            ),

            "city": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your city",
                    "autocomplete": "address-level2",
                }
            ),

            "state": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your state",
                    "autocomplete": "address-level1",
                }
            ),

            "pincode": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter PIN code",
                    "min": "100000",
                    "max": "999999",
                    "inputmode": "numeric",
                    "autocomplete": "postal-code",
                }
            ),

            "phoneno": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter phone number",
                    "inputmode": "numeric",
                    "autocomplete": "tel",
                }
            ),
        }


# ============================================================
# REGISTRATION FORM
# ============================================================

class RegistrationForm(forms.Form):
    """
    Form used to create a new Foodie customer account.
    """

    name = forms.CharField(
        max_length=50,
        label="Full Name",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your full name",
                "autocomplete": "name",
            }
        )
    )

    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your email address",
                "autocomplete": "email",
            }
        )
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Create a password",
                "autocomplete": "new-password",
            }
        ),
        validators=[validate_password],
    )

    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm your password",
                "autocomplete": "new-password",
            }
        )
    )

    def clean_name(self):
        """
        Clean and validate the customer's name.
        """

        name = self.cleaned_data["name"].strip()

        if not name:
            raise forms.ValidationError(
                "Please enter your name."
            )

        return name

    def clean_email(self):
        """
        Normalize the email address and make sure
        it is not already registered.
        """

        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(
            username=email
        ).exists():

            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email

    def clean(self):
        """
        Make sure both password fields match.
        """

        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get(
            "confirm_password"
        )

        if (
            password
            and confirm_password
            and password != confirm_password
        ):

            raise forms.ValidationError(
                "Passwords do not match."
            )

        return cleaned_data