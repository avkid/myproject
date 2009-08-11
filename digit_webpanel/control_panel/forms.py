from django.template import Context, loader
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.http import int_to_base36
from django.forms.util import ErrorList
from django.contrib.admin.widgets import AdminDateWidget, AdminSplitDateTime
from django.contrib.auth.models import User

import datetime

from control_panel.models import *
from control_panel.customize import CustomModelChoiceField

from django.utils.thread_support import currentThread 

class CustomerCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and password.
    """
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^\w+$',
        help_text = _("Required. 30 characters or fewer. Alphanumeric characters only (letters, digits and underscores)."),
        error_message = _("This value must contain only letters, numbers and underscores."))
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput)
    
    expiration_date = forms.DateField(initial = (datetime.date.today()  + datetime.timedelta(days=365)), widget=AdminDateWidget, required=False)
    
    class Meta:
        model = Customer
        fields = ("username","email",'name', 'expiration_date', 'service_name','service_cost', 'contract_id','status','country',
        'website','address','first_name','last_name','phone_number','bank','account_number','account_name',)
    
    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(_("A customer with that username already exists."))

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    def save(self, commit=True):
        customer = super(CustomerCreationForm, self).save(commit=False)
        
        if commit:
            user = User.objects.create_user(self.clean_username(), '', self.clean_password2())
            user.is_active = self.cleaned_data['status'] == 1
            user.save()
                        
            customer.created_date = datetime.datetime.now()
            
            customer.user = user
            
            if customer.expiration_date == None:
                customer.expiration_date = (datetime.date.today()  + datetime.timedelta(days=365))
            
            customer.save()
        return customer
    
class CustomerChangeForm(forms.ModelForm):
    id = forms.CharField(label=_("Customer Id"))
    
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^\w+$',
        help_text = _("Required. 30 characters or fewer. Alphanumeric characters only (letters, digits and underscores)."),
        error_message = _("This value must contain only letters, numbers and underscores."),
        )
    
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput,
        help_text=_("Use the <a style=\"text-decoration:underline\" href=\"password/\">change password form</a> to change customer password."),
        )
    
    created_date = forms.CharField(label=_("Creation date"))

    def __init__(self,*args, **kwargs):
        customer = kwargs['instance']
        kwargs['initial'] = {'username': customer.user,'password':customer.user.password,'customer_id':customer.id}
        super(CustomerChangeForm, self).__init__(*args, **kwargs)
    
    def clean_username(self):
        username = self.cleaned_data["username"]
        customer_id = self.cleaned_data["id"]
        try:
            User.objects.get(username=username)
            customer = Customer.objects.get(id=customer_id)
            if username == customer.user.username:
                return username    
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(_("A customer with that username already exists."))
    
    def save(self, commit=True):
        username = self.cleaned_data['username']
        customer = super(CustomerChangeForm, self).save(commit=False)
        customer.user.username = username
        customer.user.is_active = self.cleaned_data['status'] == 1
        customer.user.save()
        
        if customer.status == 0:
            qs = Product.objects.filter(customer=customer)
            for p in qs:
                p.active = 0
                p.save()
        
        return customer
    
    class Meta:
        model = Customer
        
class AdminPasswordChangeForm(forms.Form):
    """
    A form used to change the password of a user in the admin interface.
    """
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password (again)"), widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(AdminPasswordChangeForm, self).__init__(*args, **kwargs)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    def save(self, commit=True):
        """
        Saves the new password.
        """
        self.user.set_password(self.cleaned_data["password1"])
        if commit:
            self.user.save()
        return self.user

class ProductChangeForm(forms.ModelForm):
    
    def clean_customer(self):
        cid =  self.cleaned_data['customer']
        customer = Customer.objects.get(id=cid)
        return customer
    
    def save(self, commit=True):
        product = super(ProductChangeForm, self).save(commit=False)
        
        if product.customer.status == 0:
            product.active = 0
            product.save()
        
        return product
    
    def __init__(self,*args, **kwargs):
        choices=[ (o.id,str(o)) for o in Customer.objects.filter(status=1)]
        choices.insert(0,('','---------'))
        try:
            product = kwargs['instance']
            if product.customer.status == 0:
                choices.append((product.customer.id, str(product.customer)))
        except:
            pass
        
        super(ProductChangeForm, self).__init__(*args, **kwargs)
        
        self.fields['customer'] = forms.ChoiceField( choices = choices)

    class Meta:
        model = Product


