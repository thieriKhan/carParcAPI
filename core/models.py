from enum import Enum

from django.conf import settings
from django.db import models

# Create your models here.

class TVA(models.Model):
    name = models.CharField(max_length=50)
    value = models.DecimalField(max_digits=4, decimal_places=2, default=19.25)


class Invoice(models.Model):
   mht = models.IntegerField()
   mtva = models.IntegerField()
   mttc = models.IntegerField()
   user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
   date_created = models.DateTimeField(auto_now_add=True)
   class Meta:
       permissions = [('view_dashboard', 'Can view dashboard')]

class LinePrice(models.Model):
    name = models.CharField(max_length=70)
    price = models.IntegerField()
    status = models.CharField(max_length=1)
    tva = models.ForeignKey(TVA, on_delete=models.CASCADE, null=False)

class InvoiceDetail(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    lp = models.ForeignKey(LinePrice, on_delete=models.CASCADE)
    tva = models.ForeignKey(TVA, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price_ht = models.IntegerField()
    price_ttc = models.IntegerField()
    price_tva = models.IntegerField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name +' '+ str(self.price_ttc)


class StatusEnum(Enum):
    IN = 'I', 'IN'
    OUT = 'O', 'OUT'

class VehicleType(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name
class Mouvment(models.Model):
    id_mouv = models.AutoField(primary_key=True)
    r_mouv = models.OneToOneField('self', on_delete=models.CASCADE, null=True, blank=True)
    type_vehicule = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    regis_num = models.CharField(max_length=50, null=False)
    brand_vehicule = models.CharField(max_length=50, null=True, blank=True)
    driver_name = models.CharField(max_length=50, null=False)
    id_card_num = models.CharField(max_length=50, null=False)
    is_stock = models.BooleanField(default=True, null=False, blank=False)
    comment = models.CharField(max_length=100, null=True, blank=True)
    invoice = models.OneToOneField(Invoice,on_delete=models.CASCADE, null=True, blank=True)


    type =  models.CharField(
        max_length=1,
        choices=[(tag.value[0], tag.value[1]) for tag in StatusEnum],
        default=StatusEnum.IN.value[0],
    )
    date_created = models.DateField(auto_now_add=True, blank=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return  self.driver_name +' '+ str(self.id_mouv)
