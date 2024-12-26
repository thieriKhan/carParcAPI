from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from rest_framework.generics import CreateAPIView
from rest_framework.utils import json
from rest_framework.views import APIView
from django.contrib.auth.models import  Group
from rest_framework.response import Response
from rest_framework import status

from .models import User
from .serializers import SignupSerializer, LoginSerializer, UserSerializer, GroupSerializer, TokenSerializer, \
    OTPVerificationSerializer
from rest_framework.authtoken.models import Token
from rest_framework import viewsets
from rest_framework import permissions
from django.db import transaction


class SignupAPIView(APIView):
    """This api will handle signup"""
    permission_classes = ()
    authentication_classes = ()
    serializer_class = SignupSerializer
    def post(self,request):
            serializer = SignupSerializer(data = request.data)
            if serializer.is_valid():
                    """If the validation success, it will created a new user."""
                    with transaction.atomic():
                        user = serializer.save()

                        print("after refresh token is ________________")
                        res = { 'status' : status.HTTP_201_CREATED}
                        return Response(res , status = status.HTTP_201_CREATED)
            res = { 'status' : status.HTTP_400_BAD_REQUEST, 'data' : serializer.errors}
            return Response(res, status = status.HTTP_400_BAD_REQUEST)



class LoginAPIView(APIView):
    """This api will handle login and return token for authenticate user."""
    permission_classes = ()
    authentication_classes = ()
    serializer_class = LoginSerializer
    def post(self,request):
            serializer = LoginSerializer(data = request.data)
            if serializer.is_valid():
                    username = serializer.validated_data["username"]
                    password = serializer.validated_data["password"]
                    user = authenticate(request, username=username, password=password)
                    if user is not None:
                        """We are retreiving the token for authenticated user."""




                        data = UserSerializer(user, context={'request': request})


                        response = {
                               "status": status.HTTP_200_OK,
                               "message": "success",

                                "data":data.data


                               }
                        return Response(response, status = status.HTTP_200_OK)
                    else :
                        response = {
                               "status": status.HTTP_401_UNAUTHORIZED,
                               "message": "Utilisateur ou mot de passe incorrect",
                               }
                        return Response(response, status = status.HTTP_401_UNAUTHORIZED)
            response = {
                 "status": status.HTTP_400_BAD_REQUEST,
                 "message": "bad request",
                 "data": serializer.errors
                 }
            return Response(response, status = status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = get_user_model().objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]



class OTPVerificationView(APIView):
    serializer_class = OTPVerificationSerializer
    permission_classes = []
    authentication_classes = []
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            step = serializer.validated_data['step']
            otp = serializer.validated_data['otp']

            user = User.objects.filter(password_reset_tokens__key=otp).first()
            if user:
                if step == 2:
                    new_password = serializer.validated_data['new_password']
                    user.check_password(new_password)
                    user.set_password(new_password)
                    user.save()
                    user.password_reset_tokens.all().delete()
                    return Response({'message': 'Password changed successfully', "statut":"OK"}, status=status.HTTP_200_OK)
                elif step ==1:
                    return Response({'message': 'OTP was is ok', "statut":"OK"}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'OTP is not ok', "statut":"NOK"}, status=status.HTTP_400_BAD_REQUEST)


        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

