from venv import logger
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer, RegisterSerializer
from rest_framework.permissions import AllowAny




# views.py
from rest_framework import generics
from .models import User
from .serializers import UserSerializer

class UserListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            data = request.data
            serializer = RegisterSerializer(data=data)  
            


            if not serializer.is_valid():
                return Response({
                    'data': serializer.errors,
                    'message': 'Something went wrong..',
                }, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()
            user.is_verified = False
            user.save()

            return Response({
                'data': {},
                'message': 'User registered successfully.',
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print('e:',e)
            return Response({   
                'data': {},  
                'message': 'Something went wrong..',
            }, status=status.HTTP_400_BAD_REQUEST)
        


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = request.data
            serializer = LoginSerializer(data=data)
         
            if not serializer.is_valid():
                return Response({
                    'data': serializer.errors,
                    'message': 'Validation failed.',
                }, status=status.HTTP_400_BAD_REQUEST)

            res = serializer.get_jwt_token(serializer.validated_data)
            return Response({
                'data': res['data'],
                'message': res['message'],
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            logger.error(f'error is loginview:{traceback.format_exc()}')
            print(f"Unexpected Error: {e}")
            return Response({
                'data': {},
                'message': 'Something went wrong.',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

