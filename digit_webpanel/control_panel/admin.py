from django.http import HttpResponse
from django.contrib import admin
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext, ugettext_lazy as _
from django import template
from django.utils.html import escape
from django.template import RequestContext

import datetime

import re

from control_panel.forms import *

from apikeygen import APIKeygen
from control_panel.models import *
from control_panel.customize import ReadOnlyAdminFields


class CustomerAdmin(ReadOnlyAdminFields, admin.ModelAdmin):
    
    #class Media:
    #    js = ("jquery/jquery-1.3.2.min.js",)

    add_form = CustomerCreationForm
    form = CustomerChangeForm
    change_password_form = AdminPasswordChangeForm
    
    fieldsets = (
        ('Account details ', {
            'fields': ('name','id','created_date','expiration_date','status', 'service_name','service_cost', 'contract_id','country', )
        }),
        ('Contact details', {
            'fields': ('website','address','first_name','last_name','phone_number','email', )
        }),
        ("Customer's bank account details", {
            'fields': ('bank','account_number','account_name',)
        }),
        
        ('Log in account', {
            'fields': ('username', 'password')
        }),
    )
    
    list_display = ('id', 'name','username', 'created_date', 'expiration_date', 'status', 'service_name', 'service_cost','contract_id', )
    list_display_links = ('name','username')
    list_filter = ( 'status',  )
    search_fields = ( 'name',  )
    ordering = ('name',)
    filter_horizontal = ()

    readonly = ('id','created_date')
    
    def __call__(self, request, url):
        # this should not be here, but must be due to the way __call__ routes
        # in ModelAdmin.
        if url is None:
            return self.changelist_view(request)
        if url.endswith('password'):
            return self.user_change_password(request, url.split('/')[0])
        if url.endswith('check'):
            return self.check_view(request, url)
        if request.method == 'POST' and "_cancel_add" in request.POST:
                return HttpResponseRedirect('../')
        return super(CustomerAdmin, self).__call__(request, url)
    
    def check_view(self, request, url):
        res = 0
        username = request.GET['name']
        try:
            user = User.objects.get(username=username)
            try:
                customer = Customer.objects.get(user=user)
                try:
                    if (int)(url.split('/')[0]) == customer.id:
                        res = 1
                except ValueError:
                    res = 0
            except Customer.DoesNotExist:
                res = 0
                
        except User.DoesNotExist:
            res = 1
                
        #check regular expression
        if re.match(r'^\w+$',username) == None:
            res = 0
        
        return HttpResponse("%d" % res)
        
    def add_view(self, request):
        if request.method == 'POST':
            form = self.add_form(request.POST)
            if form.is_valid():
                new_user = form.save()
                msg = _('The %(name)s "%(obj)s" was added successfully.') % {'name': 'customer', 'obj': new_user}
                self.log_addition(request, new_user)
                if "_addanother" in request.POST:
                    request.user.message_set.create(message=msg)
                    return HttpResponseRedirect(request.path)
                elif "_continue" in request.POST:
                    request.user.message_set.create(message="%s %s" % (msg, 'You may edit it again below.'))
                    return HttpResponseRedirect('../%s/' % new_user.customer_id)
                elif '_popup' in request.REQUEST:
                    return self.response_add(request, new_user)
                else:
                    request.user.message_set.create(message=msg )
                    return HttpResponseRedirect('../')
        else:
            form = self.add_form()
        
        return render_to_response('admin/control_panel/customer/add_form.html', {
            'title': _('Add Customer'),
            'form': form,
            'is_popup': '_popup' in request.REQUEST,
            'add': True,
            'change': False,
            'has_add_permission': True,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_file_field': False,
            'has_absolute_url': False,
            'auto_populated_fields': (),
            'opts': self.model._meta,
            'save_as': False,
            'username_help_text': _("Use the <a href=\"password/\">change password form</a>."),
            'root_path': self.admin_site.root_path,
            'app_label': self.model._meta.app_label,
            'show_cancel': True,
        }, context_instance=template.RequestContext(request))
    
    def user_change_password(self, request, id):
        if not request.user.has_perm('auth.change_user'):
            raise PermissionDenied
        user = get_object_or_404(self.model, pk=id)
        if request.method == 'POST':
            if "_cancel" in request.POST:
                return HttpResponseRedirect('..')
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                new_user = form.save()
                msg = ugettext('Password changed successfully.')
                request.user.message_set.create(message=msg)
                return HttpResponseRedirect('..')
        else:
            form = self.change_password_form(user)
        return render_to_response('admin/control_panel/customer/change_password.html', {
            'title': _('Change password: %s') % escape(user.name),
            'form': form,
            'is_popup': '_popup' in request.REQUEST,
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
            'root_path': self.admin_site.root_path,
        }, context_instance=RequestContext(request))
        
    def has_delete_permission(self, request, obj=0):
        return False

class PriceLevelInline(admin.TabularInline):
    model = PriceLevel
    
class PricePolicyAdmin(admin.ModelAdmin):
    list_display = ('name', 'currency_base_price', 'total_levels',)
    exclude = ('has_levels',)
    inlines = [
        PriceLevelInline,
    ]

class DiscountAdminBase(admin.ModelAdmin):
    exclude = ('discount_class',)

class DiscountAdmin(DiscountAdminBase):
    def queryset(self, request):
        return super(DiscountAdmin, self).queryset(request).filter(discount_class__exact=Discount.__name__)

    def has_change_permission(self, request, obj=None):
        if obj and Discount.__name__ != obj.discount_class:
            return False
        return super(DiscountAdmin, self).has_change_permission(request, obj)
        
class DiscountingInline(admin.TabularInline):
    model = Discounting

class PricingInline(admin.TabularInline):
    model = Pricing
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    
    form = ProductChangeForm
    
    fieldsets = (
        ('Product Info ', {
            'fields': ('name','customer','api_key','user_secret','active')
        }),
    )
    
    list_display = ( 'customer_id', 'customer','name','api_key','user_secret','active','created_date',)
    list_display_links = ('name',)
    list_filter = ( 'active','created_date', )
    search_fields = ('customer__customer_name',)
    ordering = ('customer',)

    inlines = [
        PricingInline,
        DiscountingInline,
    ]

    def __call__(self, request, url):
        if('generate' in request.get_full_path()):
            return self.generate_view(request)
        '''
        # to remove active/deactive command
        if( 'activate' in request.get_full_path()):
            return self.active_view(request)
        '''
        if request.method == 'POST' and "_cancel_add" in request.POST:
            return HttpResponseRedirect('../')
        return super(ProductAdmin, self).__call__(request, url)
        
    def add_view(self, request):
        respone = super(ProductAdmin,self).add_view(request)
        prolist = Product.objects.filter(created_date=None)
                
        for product in prolist:
            product.created_date = datetime.date.today()
            product.save()
        return respone

    def generate_view(self, request):
        res = APIKeygen.gen_apikey()
        return HttpResponse("%s %s" % res)

    '''
    # to remove active/deactive command
    def active_view(self, request):
        product = Product.objects.get(id = request.GET['id'])
        msg = _('The status of %(name)s "%(obj)s" was updated successfully.') % {'name': 'api-key', 'obj': product}
        self.log_addition(request, product)

        product.active = (request.GET['val'] == '1')
        
        product.save()
        request.user.message_set.create(message=msg )
        return HttpResponseRedirect('../');
    '''

    def has_delete_permission(self, request, obj=0):
        return False

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(PricePolicy, PricePolicyAdmin)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(VolumeDiscount, DiscountAdminBase)
admin.site.register(SeasonDiscount, DiscountAdminBase)
