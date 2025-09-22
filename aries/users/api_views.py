from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.cache import cache
from django.conf import settings
from .models import Profile
from .serializers import UserSerializer, ProfileSerializer
from scripts import verify
from scripts.verify import MultiFieldAuthBackend
from threading import Thread
import json


class LoginAPIView(APIView):
    authentication_classes = []          
    permission_classes = [AllowAny]
    
    def post(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')
        
        print(f"[API] Login attempt for username: {username}")
        
        if not username or not password:
            print("[API] Missing username or password")
            return Response(
                {'error': 'Username and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Use custom authentication backend
        auth_backend = MultiFieldAuthBackend()
        user, error_code = auth_backend.custom_authenticate(request, username=username, password=password)
        
        print(f"[API] Authentication result - User: {user}, Error: {error_code}")
        
        if user and user.is_active:
            print(f"[API] User authenticated successfully: {user.username}")
            login(request, user)
            
            # Get or create profile
            profile, created = Profile.objects.get_or_create(user=user)
            print(f"[API] Profile {'created' if created else 'retrieved'}: {profile.id}")
            
            # Generate token (simple implementation)
            token = f"token_{user.id}_{user.username}"
            
            return Response({
                'success': True,
                'data': {
                    'user': UserSerializer(user).data,
                    'profile': ProfileSerializer(profile).data,
                    'token': token
                }
            })
        else:
            # Handle specific error codes
            error_messages = {
                'unverified': 'Account not verified. Please check your email for verification instructions.',
                'invalid': 'Invalid credentials',
                'admin_login_blocked': 'Admin login not allowed via API'
            }
            
            error_message = error_messages.get(error_code, 'Authentication failed')
            print(f"[API] Authentication failed: {error_message}")
            
            return Response(
                {'error': error_message}, 
                status=status.HTTP_401_UNAUTHORIZED
            )


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        data = request.data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        
        print(f"[API] Registration attempt for username: {username}, email: {email}")
        
        if not username or not email or not password:
            print("[API] Missing required fields for registration")
            return Response(
                {'error': 'Username, email and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(username=username).exists():
            print(f"[API] Username already exists: {username}")
            return Response(
                {'error': 'Username already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(email=email).exists():
            print(f"[API] Email already exists: {email}")
            return Response(
                {'error': 'Email already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            print(f"[API] Creating user: {username}")
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            print(f"[API] User created with ID: {user.id}")
            
            # Create profile
            profile = Profile.objects.create(user=user)
            print(f"[API] Profile created with ID: {profile.id}")
            
            # Send verification email
            print(f"[API] Sending verification email to: {email}")
            Thread(target=verify.send_verification, kwargs={
                "account": user, 
                "model_type": 'user', 
                "method": 'email'
            }).start()
            
            # Generate token
            token = f"token_{user.id}_{user.username}"
            
            print(f"[API] Registration successful for user: {username}")
            return Response({
                'success': True,
                'message': 'User created successfully. Please check your email for verification.',
                'data': {
                    'user': UserSerializer(user).data,
                    'profile': ProfileSerializer(profile).data,
                    'token': token
                },
                'verification_required': True
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"[API] Registration error: {e}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({'success': True})


class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
            return Response({
                'success': True,
                'data': {
                    'user': UserSerializer(request.user).data,
                    'profile': ProfileSerializer(profile).data
                }
            })
        except Profile.DoesNotExist:
            return Response(
                {'error': 'Profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            profile = Profile.objects.get(user=user)
            return Response({
                'success': True,
                'data': UserSerializer(user).data,
                'profile': ProfileSerializer(profile).data
            })
        except (User.DoesNotExist, Profile.DoesNotExist):
            return Response(
                {'error': 'User or profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def patch(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            if user != request.user:
                return Response(
                    {'error': 'Permission denied'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            profile = Profile.objects.get(user=user)
            
            # Update user fields
            if 'first_name' in request.data:
                user.first_name = request.data['first_name']
            if 'last_name' in request.data:
                user.last_name = request.data['last_name']
            if 'email' in request.data:
                user.email = request.data['email']
            user.save()
            
            # Update profile fields
            profile_serializer = ProfileSerializer(profile, data=request.data, partial=True)
            if profile_serializer.is_valid():
                profile_serializer.save()
                return Response({
                    'success': True,
                    'data': UserSerializer(user).data,
                    'profile': ProfileSerializer(profile).data
                })
            else:
                return Response(
                    {'error': profile_serializer.errors}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except (User.DoesNotExist, Profile.DoesNotExist):
            return Response(
                {'error': 'User or profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class FollowUserAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id):
        try:
            target_user = User.objects.get(id=user_id)
            if target_user == request.user:
                return Response(
                    {'error': 'Cannot follow yourself'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Add follow logic here (if you have a follow system)
            # For now, just return success
            return Response({'success': True})
            
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class VerificationPendingAPIView(APIView):
    """
    Show verification pending status.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'message': 'Please check your email for verification instructions',
            'status': 'pending'
        })


class VerifyEmailAPIView(APIView):
    """
    Verify email address for user registration.
    """
    permission_classes = [AllowAny]
    
    def get(self, request, model_type, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            if model_type == 'user':
                user.is_active = True
                user.save()
                return Response({
                    'success': True, 
                    'message': 'Email verified successfully'
                })
            else:
                return Response(
                    {'error': 'Invalid model type'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {'error': 'Invalid verification link'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class VerifyOTPAPIView(APIView):
    """
    Verify OTP for user registration.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        otp = request.data.get('otp')
        email = request.data.get('email')
        
        if not otp or not email:
            return Response(
                {'error': 'OTP and email are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check OTP in cache
        cached_otp = cache.get(f'user_otp_{email}')
        if cached_otp and cached_otp == otp:
            try:
                user = User.objects.get(email=email)
                user.is_active = True
                user.save()
                cache.delete(f'user_otp_{email}')
                return Response({
                    'success': True, 
                    'message': 'OTP verified successfully'
                })
            except User.DoesNotExist:
                return Response(
                    {'error': 'User not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            return Response(
                {'error': 'Invalid OTP'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class ResendVerificationAPIView(APIView):
    """
    Resend verification email.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response(
                {'error': 'Email is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                return Response(
                    {'error': 'Account is already verified'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            Thread(target=verify.send_verification, kwargs={
                "account": user, 
                "model_type": 'user', 
                "method": 'email'
            }).start()
            
            return Response({
                'success': True, 
                'message': 'Verification email sent'
            })
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class VerificationPendingAPIView(APIView):
    """
    Show verification pending status.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'message': 'Please check your email for verification instructions',
            'status': 'pending'
        })


class UnfollowUserAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id):
        try:
            target_user = User.objects.get(id=user_id)
            if target_user == request.user:
                return Response(
                    {'error': 'Cannot unfollow yourself'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Add unfollow logic here (if you have a follow system)
            # For now, just return success
            return Response({'success': True})
            
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class VerificationPendingAPIView(APIView):
    """
    Show verification pending status.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'message': 'Please check your email for verification instructions',
            'status': 'pending'
        })


class VerifyEmailAPIView(APIView):
    """
    Verify email address for user registration.
    """
    permission_classes = [AllowAny]
    
    def get(self, request, model_type, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            if model_type == 'user':
                user.is_active = True
                user.save()
                return Response({
                    'success': True, 
                    'message': 'Email verified successfully'
                })
            else:
                return Response(
                    {'error': 'Invalid model type'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {'error': 'Invalid verification link'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class VerifyOTPAPIView(APIView):
    """
    Verify OTP for user registration.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        otp = request.data.get('otp')
        email = request.data.get('email')
        
        if not otp or not email:
            return Response(
                {'error': 'OTP and email are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check OTP in cache
        cached_otp = cache.get(f'user_otp_{email}')
        if cached_otp and cached_otp == otp:
            try:
                user = User.objects.get(email=email)
                user.is_active = True
                user.save()
                cache.delete(f'user_otp_{email}')
                return Response({
                    'success': True, 
                    'message': 'OTP verified successfully'
                })
            except User.DoesNotExist:
                return Response(
                    {'error': 'User not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            return Response(
                {'error': 'Invalid OTP'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class ResendVerificationAPIView(APIView):
    """
    Resend verification email.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response(
                {'error': 'Email is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                return Response(
                    {'error': 'Account is already verified'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            Thread(target=verify.send_verification, kwargs={
                "account": user, 
                "model_type": 'user', 
                "method": 'email'
            }).start()
            
            return Response({
                'success': True, 
                'message': 'Verification email sent'
            })
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class VerificationPendingAPIView(APIView):
    """
    Show verification pending status.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'message': 'Please check your email for verification instructions',
            'status': 'pending'
        })
