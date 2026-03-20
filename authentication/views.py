from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from .models import Profile,OTP,TempOTP
from inventory.utils import generate_otp,send_otp,delete_otp_obj
from .forms import AdminLoginForm,PhoneForm,VerifyOTPForm,SignUpPhoneForm,AddUserNameForm

class AdminLoginView(View):

    template = 'authentication/login.html'

    form_class = AdminLoginForm

    def get(self,request,*args,**kwargs):

        form = self.form_class()

        data = {'form':form}

        return render(request,self.template,context=data)
    
    def post(self,request,*args,**kwargs):

        form = self.form_class(request.POST)

        data = {}

        if form.is_valid():

            email = form.cleaned_data.get('email')

            password = form.cleaned_data.get('password')

            user = authenticate(username=email,password=password)

            if user :

                login(request,user)

                return redirect('dashboard')
            
            data.update({'error':'Invalid username or password'})

        data.update({'form':form})

        return render(request,self.template,context=data)
    
class LogoutView(View):

    def get(self,request,*args,**kwargs):

        logout(request)

        return redirect('dashboard')
    
class UserLoginView(View):

    template = 'authentication/phone.html'

    form_class = PhoneForm

    def get(self,request,*args,**kwargs):

        form = self.form_class()

        data = {'form':form}

        return render(request,self.template,context=data)
    
    def post(self,request,*args,**kwargs):

        form = self.form_class(request.POST)

        if form.is_valid():

            phone = form.cleaned_data.get('phone')

            request.session['phone'] = phone

            return redirect('phone-otp')
        
        data = {'form':form}

        return render(request,self.template,context=data)
    
class PhoneOTPView(View):

    template = 'authentication/otp.html'

    form_class = VerifyOTPForm

    def get(self,request,*args,**kwargs):

        form = self.form_class()

        otp =  generate_otp()

        phone = request.session.get('phone')

        profile = Profile.objects.get(phone=phone)

        otp_obj,_ = OTP.objects.get_or_create(profile=profile)

        otp_obj.otp = otp

        otp_obj.save()

        send_otp(phone,otp)

        otp_time = timezone.now().timestamp()

        request.session['otp_time'] = otp_time

        remaining_time = 300

        data = {'form':form,'phone':phone,'remaining_time':remaining_time}

        return render(request,self.template,context=data)
    
    def post(self,request,*args,**kwargs):

        form = self.form_class(request.POST)

        if form.is_valid():

            user_otp = form.cleaned_data.get('otp')

            phone = request.session.get('phone')

            profile = Profile.objects.get(phone=phone)

            otp_obj = OTP.objects.get(profile=profile)

            otp_time = request.session.get('otp_time')

            time_now =  timezone.now().timestamp()

            time_difference = time_now-otp_time

            remaining_time = max(0,300-time_difference)

            if time_difference > 300 :
                 
                 error = 'OTP Expired Request a New One'  

            elif user_otp == otp_obj.otp :

                login(request,profile)  

                request.session.pop('phone')

                request.session.pop('otp_time')       
                
                return redirect('dashboard')
            
            else :

                error = 'Invalid OTP'

        data = {'form':form,'error':error,'remaining_time':remaining_time}

        return render(request,self.template,context=data)
    

class SignUpView(View):

    template = 'authentication/signup.html'

    form_class = SignUpPhoneForm

    def get(self,request,*args,**kwargs):

        form = self.form_class()

        data = {'form':form}

        return render(request,self.template,context=data)

    def post(self,request,*args,**kwargs):

        form = self.form_class(request.POST)

        if form.is_valid():

            phone = form.cleaned_data.get('phone')

            request.session['phone'] = phone

            return redirect('signup-otp-verify')

        data = {'form':form}

        return render(request,self.template,context=data)
    
class SignUpOTPVerifyView(View):

    template = 'authentication/otp.html'

    form_class = VerifyOTPForm

    def get(self,request,*args,**kwargs):

        form = self.form_class()

        otp =  generate_otp()

        phone = request.session.get('phone')

        otp_obj = TempOTP.objects.create(phone=phone,otp=otp)

        send_otp(phone,otp)

        otp_time = timezone.now().timestamp()

        request.session['otp_time'] = otp_time

        remaining_time = 300

        data = {'form':form,'phone':phone,'remaining_time':remaining_time}

        return render(request,self.template,context=data)
    
    def post(self,request,*args,**kwargs):

        form = self.form_class(request.POST)

        if form.is_valid():

            user_otp = form.cleaned_data.get('otp')

            phone = request.session.get('phone')

            otp_obj = TempOTP.objects.get(phone=phone)

            otp_time = request.session.get('otp_time')

            time_now =  timezone.now().timestamp()

            time_difference = time_now-otp_time

            remaining_time = max(0,300-time_difference)

            if time_difference > 300 :
                 
                 error = 'OTP Expired Request a New One'  

                 delete_otp_obj(otp_obj)


            elif user_otp == otp_obj.otp :

                profile = Profile.objects.create_user(phone=phone,username=phone,role='User') 
                
                return redirect('add-user-name')
            
            else :

                error = 'Invalid OTP'

        data = {'form':form,'error':error,'remaining_time':remaining_time}

        return render(request,self.template,context=data)


class UserNameView(View):

    template = 'authentication/add-name.html'

    form_class = AddUserNameForm

    def get(self,request,*args,**kwargs):

        form = self.form_class()

        data = {'form':form}

        return render(request,self.template,context=data)
    
    def post(self,request,*args,**kwargs):

        form = self.form_class(request.POST)

        if form.is_valid():

            phone = request.session.get('phone')

            profile = Profile.objects.get(phone=phone)

            name = form.cleaned_data.get('name')
            
            profile.first_name = name 

            profile.save()

            return redirect('user-login')
        
        data = {'form':form}

        return render(request,self.template,context=data)