from datetime import datetime

from django.db import transaction
from django.db.models import Count, Sum
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication, BasicAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveUpdateDestroyAPIView, RetrieveUpdateAPIView, ListCreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import VehicleType, Mouvment, InvoiceDetail, LinePrice, Invoice
from core.serializers import VehicleTypeSerializer, InvoiceSerializer, MouvmentUSerializer, \
    MouvmentCSerializer
from rest_framework.views import APIView


# Create your views here.

class VehiculeTypeView(viewsets.ModelViewSet):
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer


class MouvmentView(ListCreateAPIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    # queryset = Mouvment.objects.all().order_by('-date_created')
    serializer_class = MouvmentCSerializer

    def get_queryset(self):
        ''''
        # op = 0 or else : all mouvments
        #  op = 1 : mouments in of the day
        #  op = 2 : mouments out of the day
        # op = 3 : mouments in stock
       '''
        today = datetime.now().date()
        op = int(self.kwargs.get('op'))

        if op == 1:
            print("1")

            query_set = Mouvment.objects.all().filter(type='I', date_created=today).order_by('-date_created')

        elif op == 2:

            query_set = Mouvment.objects.all().filter(type='O', date_created=today).order_by('-date_created')
        elif op == 3:

            query_set = Mouvment.objects.all().filter(type='I', is_stock=True).order_by('-date_created')
        else:

            query_set = Mouvment.objects.all().order_by('-date_created')

        return query_set


class InvoiceView(ListAPIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = InvoiceSerializer
    def get_queryset(self):
        ''''
        # op = 0 or else : all  invoices
        #  op = 1 : invoices of the day
        '''

        today = datetime.now().date()
        op = int(self.kwargs.get('op'))

        if op == 1:
            query_set = Invoice.objects.all().filter( date_created=today).order_by('-date_created')

        else:

            query_set = Invoice.objects.all().order_by('-date_created')

        return query_set


class MouvmentUpdateView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication, BasicAuthentication]
    permission_classes = []
    queryset = Mouvment.objects.all()



    def get(self, request, pk):
        instance = Mouvment.objects.filter(id_mouv=pk).first()


        serializer = MouvmentUSerializer(instance)
        print(serializer.data)
        if serializer.data.get('r_mouv') is None:
            return Response(serializer.data)
        else :
            invoice = Invoice.objects.filter(mouvment=serializer.data.get('r_mouv')).first()
            print(invoice)
            invoice_serializer  = InvoiceSerializer(invoice)

            return  Response(invoice_serializer.data)


    def put(self, request , pk):
        try:
            instance = Mouvment.objects.get(pk=pk)
            serializer = MouvmentUSerializer(instance, data=request.data )



            if(serializer.is_valid()):

                with transaction.atomic():


                    movement_type = serializer.validated_data.get('type')
                    print("type is : "+movement_type)

                    if movement_type == 'O' and instance.type == 'I':

                        # Create a new "OUT" movement from the "IN" movement
                        new_movement = Mouvment.objects.create(
                            type='O',
                            type_vehicule=instance.type_vehicule,

                            user=instance.user,
                            regis_num=instance.regis_num,
                            brand_vehicule=instance.brand_vehicule,
                            driver_name=instance.driver_name,
                            id_card_num=instance.id_card_num,
                            comment=instance.comment,

                        )

                        # generate a new Invoice object
                        invoice = Invoice.objects.create(
                            mht=0,  # Will be calculated
                            mtva=0,  # Will be calculated
                            mttc=0,  # Will be calculated
                            user=new_movement.user
                        )
                        new_movement.invoice = invoice

                        # generate invoice details
                        line_prices = LinePrice.objects.filter(status='A')
                        days_difference = (datetime.now().date() - instance.date_created).days
                        total_ht = 0
                        total_tva = 0
                        for lp in line_prices:
                            quantity = days_difference
                            price_ht = lp.price * quantity

                            price_tva = price_ht * (lp.tva.value / 100)
                            price_ttc = price_ht + price_tva
                            InvoiceDetail.objects.create(
                                lp=lp,
                                invoice=invoice,
                                tva=lp.tva,
                                name=lp.name + ' du ' + instance.date_created.strftime(
                                    "%Y-%m-%d") + ' au ' + datetime.now().strftime("%Y-%m-%d"),
                                quantity=quantity,
                                price_ht=price_ht,
                                price_ttc=price_ttc,
                                price_tva=price_tva
                            )
                            total_ht += price_ht
                            total_tva += price_tva

                        # update invoice

                        invoice.mht = total_ht
                        invoice.mtva = total_tva
                        invoice.mttc = total_ht + total_tva

                        invoice.save()
                        new_movement.save()

                        serializer.save(type='I', r_mouv=new_movement, is_stock=False)

                        # Serialize the invoice data
                        invoice_serializer = InvoiceSerializer(invoice)
                        print("invoice serializer is :")

                        print(invoice_serializer.data)
                        return Response(invoice_serializer.data, status=status.HTTP_200_OK)
                    elif movement_type == 'I':
                        raise ValidationError("Cannot change an 'OUT' movement to 'IN'.")
                    else:

                        raise ValidationError("No operation done.")


        except Mouvment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValidationError as error:

            return Response(error, status=status.HTTP_400_BAD_REQUEST)








class DashboardView(APIView):
    permission_classes = [IsAuthenticated]
    permission_required = 'core.view_dashboard'

    def get(self, request, *args, **kwargs):
        today = datetime.now().date()

        # Current number of movements 'IN' and 'OUT' in the current day
        movements_in_today = Mouvment.objects.filter(type='I', date_created=today).count()
        movements_out_today = Mouvment.objects.filter(type='O', date_created=today).count()
        stock_day = Mouvment.objects.filter( type='I',is_stock=True).count()

        # Total amount of all invoices in a day
        total_invoice_amount_today = Invoice.objects.filter(date_created__date=today).aggregate(total=Sum('mttc'))[
                                         'total'] or 0

        # Number of movements 'IN' and 'OUT' per month in the current year
        current_year = today.year
        movements_per_month = Mouvment.objects.filter(date_created__year=current_year).values('type',
                                                                                              'date_created__month').annotate(
            count=Count('id_mouv')).order_by('date_created__month')

        # Prepare the response data
        response_data = {
            'stock_day': stock_day,
            'movements_in': movements_in_today,
            'movements_out': movements_out_today,
            'total_invoice': total_invoice_amount_today,
            'movementsPerMonth': movements_per_month,
            'movements': map(lambda x: MouvmentCSerializer(x).data,
                             Mouvment.objects.all().order_by('-date_created')[:10]),
            'invoices': map(lambda x: InvoiceSerializer(x).data, Invoice.objects.all().order_by('-date_created')[:10]),
        }

        return Response(response_data)

# def post(self, request):
#     data = request.data
#     print(data)
#     return Response({"message": "success" }, status=status.HTTP_200_OK)
#
# def get(self, request):
#     data = request.data.get('data')
#     print(data)
#     return Response({"message": "success" }, status=status.HTTP_200_OK)
