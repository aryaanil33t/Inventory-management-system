from django.urls import path

from . import views

urlpatterns = [

    path('admin-login/',views.AdminLoginView.as_view(),name='admin-login'),

    path('logout/',views.LogoutView.as_view(),name='logout'),

    path('user-login/',views.UserLoginView.as_view(),name='user-login'),

    path('phone-otp/',views.PhoneOTPView.as_view(),name='phone-otp'),

    path('signup/',views.SignUpView.as_view(),name='signup'),

    path('signup-otp-veriy/',views.SignUpOTPVerifyView.as_view(),name='signup-otp-verify'),

    path('add-user-name/',views.UserNameView.as_view(),name='add-user-name'),
    
]