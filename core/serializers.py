from rest_framework import serializers

from core.models import VehicleType, Mouvment, Invoice, InvoiceDetail


class VehicleTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = VehicleType
        fields = "__all__"


class InvoiceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceDetail
        fields = ['id','name','quantity','price_ht', 'price_tva', 'price_ttc']

class InvoiceSerializer(serializers.ModelSerializer):
    invoice_details = InvoiceDetailSerializer(many=True, read_only=True, source='invoicedetail_set')
    user_name = serializers.CharField(source='user.username' ,read_only=True)
    driver_name = serializers.CharField(source='mouvment.driver_name',read_only=True)

    class Meta:
        model = Invoice
        fields = "__all__"

class MouvmentUSerializer(serializers.ModelSerializer):

    type_vehicle_name = serializers.CharField(source="type_vehicule.name", read_only=True)
    sens  = serializers.CharField(source="type", read_only=True)
    invoice = InvoiceSerializer(data="invoice", read_only=True)

    class Meta:
        model = Mouvment

        fields = "__all__"

        read_only_fields = ['sens', 'invoice','user'
            , 'r_mouv']
class MouvmentCSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.first_name", read_only=True)
    first_name = serializers.CharField(source="user.username", read_only=True)
    type_vehicle_name = serializers.CharField(source="type_vehicule.name", read_only=True)
    sens  = serializers.CharField(source="type", read_only=True)


    class Meta:
        model = Mouvment
        fields = "__all__"
        read_only_fields = ['sens', 'invoice'
            , 'r_mouv']







