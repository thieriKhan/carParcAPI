from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VehiculeTypeView, MouvmentView, MouvmentUpdateView, InvoiceView, DashboardView

router = DefaultRouter()
router.register(r'vehicle/type', VehiculeTypeView)



urlpatterns = [

    path('', include(router.urls)),
    path('mouvments/list/<op>', MouvmentView.as_view()),
    path('dashboard/', DashboardView.as_view()),
    path('invoices/list/<op>', InvoiceView.as_view()),
    path('mouvments/<pk>',MouvmentUpdateView.as_view()),

]