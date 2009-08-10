from django.db import models
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_str
from django.contrib.auth.models import User

from control_panel.customize import CountryField

class Customer(models.Model):
    # account details
    name = models.CharField(_('Customer Name'),max_length = 255)
    expiration_date = models.DateField(blank=True, null=True)
    service_name = models.CharField(max_length = 200,  blank=True)
    service_cost = models.PositiveIntegerField(default=0, blank=True, null=True)
    contract_id = models.CharField(max_length = 32, blank=True)
    status = models.SmallIntegerField(choices=(
        (0, 'Inactive'),
        (1, 'Active'),
    ),  default=False)
    
    created_date = models.DateTimeField(_('Creation date'), blank=True, null=True)

    # contact details
    website = models.URLField(verify_exists=False, blank=True)
    address = models.CharField(max_length = 200,  blank=True)
    first_name = models.CharField(max_length = 200,  blank=True)
    last_name = models.CharField(max_length = 200,  blank=True)
    phone_number = models.CharField(max_length = 200,  blank=True)
    email = models.EmailField(_('e-mail address'), max_length=255)
    country = CountryField(default='VN')

    #bank account
    bank = models.CharField(max_length = 200, blank=True)
    account_number = models.CharField(max_length = 200, blank=True)
    account_name = models.CharField(max_length = 200, blank=True)

    # primary key
    id = models.AutoField(_('Customer Id'),primary_key=True)    
        
    user = models.ForeignKey(User, blank=True, null=True)
    
    ##  products ->* Product

    def __unicode__(self):
        return self.name
    
    def set_password(self, password):
        self.user.set_password(password)
        self.user.save()
    
    __str__ = __unicode__

class Product(models.Model):
    customer = models.ForeignKey('Customer')
    name = models.CharField(_('Product name'),max_length=255)
    prices = models.ManyToManyField('PricePolicy', through='Pricing')
    discounts = models.ManyToManyField('Discount', through='Discounting')
    
    created_date = models.DateField(_('Creation date'), blank=True, null=True)
    
    api_key = models.CharField(max_length=255)
    user_secret = models.CharField(max_length=10)
    active = models.BooleanField()

    '''
    status = models.SmallIntegerField(choices=(
        (0, 'Inactive'),
        (1, 'Active'),
    )
,  default=1, blank=True, null=True)
    '''

    def customer_id(self):
        return '%d' % self.customer.id
    
    def customer_name(self):
        return self.customer.name

    def command(self):
        return ' <select id="id_command_%d" onchange = "onChangeEventHanlder(%d)"> \
            <option selected="selected" value="">---------</option> \
            <option value="1">Active</option>  \
            <option value="0">Deactive</option></select> ' % (self.id, self.id)
    command.allow_tags = True

    def __unicode__(self):
        return self.api_key

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')


class Pricing(models.Model):
    product = models.ForeignKey('Product')
    price_policy = models.ForeignKey('PricePolicy')
    effective_date = models.DateField()

    def __unicode__(self):
        return _('%(policy_name)s from %(start_date)s') % {
            'policy_name': self.price_policy.name,
            'start_date': self.effective_date,
        }

    class Meta:
        ordering = ('effective_date',)


class PricePolicy(models.Model):
    name = models.CharField(max_length=255)
##  products ->* Product
    base_price = models.DecimalField(max_digits=5, decimal_places=2)
    has_levels = models.PositiveSmallIntegerField(default=0)
##  price_levels ->* PriceLevel
    
    def __unicode__(self):
        return self.name
    __str__ = __unicode__

    @property
    def total_levels(self):
        return self.has_levels + 1
        
    @property
    def currency_base_price(self):
        return _('%.2f USD') % self.base_price


class PriceLevel(models.Model):
    price_policy = models.ForeignKey('PricePolicy')
    volume_threshold = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ('volume_threshold',)


class Discount(models.Model):
    name = models.CharField(max_length=255)
    discount_class = models.CharField(max_length=255)
    # Indicate the discount is applicable to all customer without
    # explicitely assigning it to them
    is_global = models.BooleanField()
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    
    def __unicode__(self):
        return self.name
    __str__ = __unicode__
        
class Discounting(models.Model):
    product = models.ForeignKey('Product')
    discount_object = models.ForeignKey('Discount')
    
    def __unicode__(self):
        return _('%(discount_name)s from %(start_date)s to %(end_date)s') % {
            'discount_name': self.discount_object.name,
            'start_date': self.effective_start_date,
            'end_date': self.effective_end_date,
        }
    __str__ = __unicode__

    @property
    def discount(self):
        if self.discount_object.discount_class == self.discount_object.__class__.__name__:
            return self.discount_object
        else:
            return getattr(self.discount_object, self.discount_object.discount_class.lower())

    effective_start_date = models.DateField()
    effective_end_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ('effective_start_date', 'effective_end_date',)


class VolumeDiscount(Discount):
    volume = models.PositiveIntegerField()

# This is actually a simple discount
#class FixedDiscount(Discount):
#    pass
    
class SeasonDiscount(Discount):
    start_date = models.DateField()
    end_date = models.DateField()
    
# Maybe add a periodic discount using rrules in dateutils
# class PeriodicDiscount(Discount):
#     ...


# Importing signals
import control_panel.signals
