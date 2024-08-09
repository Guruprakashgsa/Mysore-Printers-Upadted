from django.utils import timezone
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, name=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not name:
            raise ValueError('The Name field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, name=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user = self.create_user(email, password=None, name=name, **extra_fields)
        if password:
            user.password = make_password(password)
        user.save(using=self._db)
        return user
    
   

def validate_phonenumber(value):
    if len(value) != 10 or not value.isdigit():
        raise ValidationError(
            _('Phone number must be a 10-digit number.'),
            params={'value': value},
        )

class Userprofile(AbstractUser):
    ROLE_CHOICE = [
        ('admin', 'Admin'),
        ('superadmin', 'Super Admin'),
        ('executive', 'Executive'),
        ('agent', 'Agent'),
        ('DGIM', 'DGIM'),
        ('AGIM', 'AGIM'),
        ('manager', 'Manager'),
        ('LVD', 'LVD')
    ]
    name = models.CharField(max_length=200)
    agent_executive = models.CharField(max_length=100, null=True, blank=True)
    agent_executive_id = models.CharField(max_length=100, null=True, blank=True)
    users_name = models.CharField(max_length=100, null=True)
    password = models.CharField(max_length=128, blank=False, null=False)
    email = models.EmailField(unique=True, null=False, blank=False)
    phonenumber = models.CharField(max_length=10, validators=[validate_phonenumber])
    user_location = models.CharField(max_length=100)
    role = models.CharField(max_length=100, choices=ROLE_CHOICE, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    userID = models.IntegerField(unique=True)
    last_login = models.DateTimeField(_('last login'), blank=True, null=True)
    fcm_token = models.TextField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_image/', default='profile_image/default.jpg')

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    username = None

    def save(self, *args, **kwargs):
        if self.userID is None:
            last_user = Userprofile.objects.order_by('userID').last()
            if last_user:
                self.userID = last_user.userID + 1
            else:
                self.userID = 1
        super(Userprofile, self).save(*args, **kwargs)

    def __str__(self):
        return self.name or 'No Name'
    

class PaymentCollectionReport(models.Model):
    PAYMENT_CHOICE = [
        ('cheque', 'cheque'),
        ('cash', 'cash'),
        ('RTGS', 'RTGS'),
        ('NEFT', 'NEFT'),
        ('UPI', 'UPI'),
    ]
    agent_code = models.CharField(max_length=50, null=False)
    paymentmethod = models.CharField(max_length=50, choices=PAYMENT_CHOICE, blank=False)
    InstrumentNumber = models.IntegerField()
    AmountCollected = models.IntegerField()
    Executive = models.ForeignKey(Userprofile, on_delete=models.CASCADE)
    agent = models.CharField(max_length=50, null=False)
    Date = models.DateField(null=False, blank=False)


class AgentCollectionReport(models.Model):
    MONTH_CHOICES = [
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'), 
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),
    ]
    agent = models.CharField(max_length=100)
    month = models.CharField(max_length=10, choices=MONTH_CHOICES)
    bill_amount = models.DecimalField(max_digits=10, decimal_places=2)
    other_adjustment = models.DecimalField(max_digits=10, decimal_places=2)
    amount_collected = models.DecimalField(max_digits=10, decimal_places=2)
    total_dues = models.DecimalField(max_digits=10, decimal_places=2)
    balance_amount = models.DecimalField(max_digits=10, decimal_places=2)
    executive = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Collection Report for {self.agent} - {self.month}"
    
class TerritoryCollectionReport(models.Model):
    Executive = models.CharField(max_length=100)
    Territory = models.CharField(max_length=200)
    SalesEmployee = models.CharField(max_length=100)
    TotalDues = models.IntegerField()
    Balance = models.IntegerField()
    Collected = models.IntegerField()
    Collection = models.CharField(max_length=255)
    Date = models.DateField(timezone.now())


class PlantEdition(models.Model):
    PLANT_CHOICE = [
        # ('choose', 'choose'),
        ('Kumbalgodu(Bengaluru)', 'Kumbalgodu(Bengaluru)'),
        ('Kalaburagi(Gulbarga)', 'Kalaburagi(Gulbarga)'),
        ('Hosapete', 'Hosapete'),
        ('Dharwad(Hubballi)', 'Dharwad(Hubballi)'),
        ('Harihara(Davanagere)', 'Harihara(Davanagere)'),
        ('Mangaluru', 'Mangaluru'),
        ('Mysore', 'Mysore'),
    ]
    
    EDITION_CHOICE = [
        # ('choose', 'choose'),
        ('Bangalore city(BD)', 'BANGALORE CITY(BD)'),
        ('KOLAR/CHIKK/TUM(BD2)', 'KOLAR/CHIKK/TUM(BD2)'),
        ('Mysore city(YD)', 'MYSORE CITY(YD)'),
        ('Bangalore city edition(BP)', 'BANGALORE CITY EDITION(BP)'),
        ('Bangalore rural edition (BP1)', 'BANGALORE RURAL EDITION (BP1)'),
        ('Kolar dist edition(BP2)', 'KOLAR DIST EDITION'),
        ('Tumkur dist edition', 'TUMKUR DIST EDITION'),
        ('Mandya dist edition', 'MANDYA DIST EDITION'),
        ('chikkaballapur edition', 'CHIKKABALLAPUR EDITION'),
        ('ramanagara edition', 'RAMANAGARA EDITION'),
    ]
    user = models.ForeignKey(Userprofile, on_delete=models.DO_NOTHING)
    plant_description = models.CharField(max_length=50, choices=PLANT_CHOICE, blank=False, default='choose')
    edition_description = models.CharField(max_length=50, choices=EDITION_CHOICE, blank=False, default='choose')
    date = models.DateField()
    LPRtime = models.TimeField()

    def __str__(self):
        return f"{self.plant_description} - {self.edition_description}"

def get_current_date():
    return timezone.now().date()

class Location(models.Model):
    user = models.ForeignKey(Userprofile, on_delete=models.CASCADE)
    check_in_location = models.TextField()
    check_out_location = models.TextField(null=True, blank=True)
    check_in_time = models.DateTimeField()
    check_out_time = models.DateTimeField(null=True, blank=True)
    total_time = models.CharField(max_length=1000, null=True, blank=True)
    total_distance = models.CharField(max_length=1000, null=True, blank=True)
    locations_visited = models.TextField(null=True, blank=True)
    Date = models.DateField(default=get_current_date)  

    def __str__(self):
        return f"{self.user.name} - {self.check_in_location}"
    
class NetSale(models.Model):
    PUBLICATION_CHOICE = [
        ('DH','dh'),
        ('PV','pv'),
        ('Mayura', 'mayura'),
    ]
    Manager = models.CharField(max_length=255)
    AgentName = models.CharField(max_length=100)
    Territory = models.TextField()
    DropPoint = models.TextField()
    Total_net_sales = models.IntegerField()
    Executive = models.CharField(max_length=100)
    Publication = models.CharField(choices=PUBLICATION_CHOICE , max_length=255)
    Date = models.DateField(max_length=50)

class Notification(models.Model):
    ROLE_CHOICES = [
        ('all users', 'All Users'),
        ('superadmin', 'Super Admin'),
        ('executive', 'Executive'),
        ('agent', 'Agents'),
    ]
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('pending', 'Pending')
    ]
    notification_time = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=250, null=False, blank=False)
    content = models.TextField()
    notification_image = models.ImageField(upload_to='notifications/', null=True, blank=True)
    role = models.CharField(max_length=100, choices=ROLE_CHOICES, blank=False)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES)

class SupplyReport(models.Model):
    SEname = models.CharField(max_length=255)
    BPcode = models.BigIntegerField()
    Date = models.TextField()
    SumofPv =  models.CharField(max_length=255)
    RegionalManager = models.CharField(max_length=100)
    ManagerName = models.CharField(max_length=100)
    SumofDH = models.CharField(max_length=255)


# from django.db import models
# from App.models import Userprofile

class daily_working_summary(models.Model):
    Market_worked = models.TextField()
    Agents_visited = models.TextField()
    Institution_visited = models.IntegerField(null= True)
    Tasks_Accomplished = models.TextField(null= True)
    Date = models.CharField(max_length=11)
    Executive = models.ForeignKey(Userprofile, on_delete= models.DO_NOTHING)
    def __str__(self):
        return f"{self.user.name if self.user and self.user.name else 'No User'}"