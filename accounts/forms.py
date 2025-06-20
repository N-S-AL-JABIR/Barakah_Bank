from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .constants import ACCOUNT_TYPE, GENDER_CHOICES
from .models import UserAccount, UserAddress


class UserRegistrationForm(UserCreationForm):
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    gender = forms.ChoiceField(choices=GENDER_CHOICES)
    street = forms.CharField(max_length=100)
    city = forms.CharField(max_length=50)
    zip_code = forms.CharField(max_length=20)
    country = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
            "first_name",
            "last_name",
            "account_type",
            "birth_date",
            "gender",
            "street",
            "city",
            "zip_code",
            "country",
        ]

    def save(self, commit=True):
        our_user = super().save(commit=False)
        if commit == True:
            our_user.save()
            account_type = self.cleaned_data["account_type"]
            birth_date = self.cleaned_data["birth_date"]
            gender = self.cleaned_data["gender"]
            street = self.cleaned_data["street"]
            city = self.cleaned_data["city"]
            zip_code = self.cleaned_data["zip_code"]
            country = self.cleaned_data["country"]

            UserAccount.objects.create(
                user=our_user,
                account_type=account_type,
                birth_date=birth_date,
                gender=gender,
                account_no=799700 + our_user.id,
            )
            UserAddress.objects.create(
                user=our_user,
                street=street,
                city=city,
                zip_code=zip_code,
                country=country,
            )
            return our_user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": (
                        "form-control "  # Bootstrap class for inputs
                        "w-100 "  # full width
                        "bg-light "  # light background (similar to bg-gray-200)
                        "text-secondary "  # similar to text-gray-700
                        "border "  # border
                        "rounded "  # rounded corners
                        "py-2 px-3 "  # padding y & x
                        "focus:outline-none "  # no outline on focus (optional)
                        "focus:bg-white "  # change bg to white on focus (needs custom CSS or ignore)
                        "focus:border-primary"  # bootstrap primary border on focus (needs custom CSS or ignore)
                    )
                }
            )


class UserUpdateForm(forms.ModelForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    gender = forms.ChoiceField(choices=GENDER_CHOICES)
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    street = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    zip_code = forms.IntegerField()
    country = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {
                    "class": (
                        "form-control "  # Bootstrap class for inputs
                        "w-100 "  # full width
                        "bg-light "  # light background (similar to bg-gray-200)
                        "text-secondary "  # similar to text-gray-700
                        "border "  # border
                        "rounded "  # rounded corners
                        "py-2 px-3 "  # padding y & x
                        "focus:outline-none "  # no outline on focus (optional)
                        "focus:bg-white "  # change bg to white on focus (needs custom CSS or ignore)
                        "focus:border-primary"  # bootstrap primary border on focus (needs custom CSS or ignore)
                    )
                }
            )

        if self.instance:
            try:
                user_account = self.instance.account
                user_address = self.instance.address
            except UserAccount.DoesNotExist:
                user_account = None
                user_address = None

            if user_account:
                self.fields["account_type"].initial = user_account.account_type
                self.fields["gender"].initial = user_account.gender
                self.fields["birth_date"].initial = user_account.birth_date
                self.fields["street"].initial = user_address.street
                self.fields["city"].initial = user_address.city
                self.fields["zip_code"].initial = user_address.zip_code
                self.fields["country"].initial = user_address.country

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()

            user_account, created = UserAccount.objects.get_or_create(user=user)
            user_address, created = UserAddress.objects.get_or_create(user=user)

            user_account.account_type = self.cleaned_data["account_type"]
            user_account.gender = self.cleaned_data["gender"]
            user_account.birth_date = self.cleaned_data["birth_date"]
            user_account.save()

            user_address.street = self.cleaned_data["street"]
            user_address.city = self.cleaned_data["city"]
            user_address.zip_code = self.cleaned_data["zip_code"]
            user_address.country = self.cleaned_data["country"]
            user_address.save()

        return user
