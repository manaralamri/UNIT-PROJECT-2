from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Profile_Seller, Profile_User
from django.db import transaction
def user_sign_up(request: HttpRequest):
    
    if request.method == 'POST':
        try:
            new_user = User.objects.create_user(username=request.POST["username"],password=request.POST["password"],email=request.POST["email"], first_name=request.POST["first_name"], last_name=request.POST["last_name"])            
            new_user.save()
             #create profile after user save 
            profile = Profile_User(
                user=new_user,
                address=request.POST.get("address", ""),
                postal_code=request.POST.get("postal_code", ""),
                phone_number=request.POST.get("phone_number", ""),
                city=request.POST.get("city", ""),
                avatar=request.FILES.get("avatar", "images/avatars/avatar.webp"))
            profile.save()


            messages.success(request, "Registered User Successfuly", "alert-success")
            return redirect("accounts:sign_in")
        
        except Exception as e:
            messages.error(request, "Couldn't register user. Try again", "alert-danger")
            print(e)


    
    return render(request, "accounts/user_signup.html", {})





def seller_sign_up(request: HttpRequest):
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                new_user = User.objects.create_user(username=request.POST["username"],password=request.POST["password"],email=request.POST["email"], first_name=request.POST["first_name"], last_name=request.POST["last_name"])            
                new_user.save()
                profile = Profile_Seller(
                    user=new_user,
                    CR=request.POST['CR'],
                    CR_image=request.FILES['CR_image'],
                    avatar=request.FILES.get('avatar', Profile_Seller.avatar.field.get_default()),
                    twitch_link=request.POST.get('twitch_link', '')
                )
                profile.save()
                print(profile)
                messages.success(request, "Registered User Successfuly", "alert-success")
                return redirect("accounts:sign_in")
        
        except Exception as e:
            messages.error(request, "Couldn't register user. Try again", "alert-danger")
            print(e)


    
    return render(request, "accounts/seller_signup.html", {})


def sign_in(request:HttpRequest):
    if request.method == "POST":
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            messages.success(request,"Logged in successfuly", "alert-success" )
            return redirect(request.GET.get("next", "/"))



        else:
            messages.error(request, "Invalid username or password", "alert-danger")

    



    return render(request, "accounts/signin.html")




def log_out(request: HttpRequest):

    logout(request)
    messages.success(request, "logged out successfully", "alert-warning")
    return redirect(request.GET.get("next", "/"))

#def user_profile_view(request:HttpRequest, user_name):
#    try:
#        user = User.objects.get(username=user_name)
#        if not Profile_User.objects.filter(user=user).first():
#            new_profile = Profile_User(user=user)
#            new_profile.save()
#
#    
#    except Exception as e:
#        print(e)
#        return render(request, '404.html')
#    return render(request, 'accounts/user_profile.html', {'user':user})
#
#def seller_profile_view(request:HttpRequest, user_name):
#    try:
#        user = User.objects.get(username=user_name)
#        # whay one get profile user from Model name 
#        #profile:Profile = user.profile
#        if not Profile_Seller.objects.filter(user=user).first():
#            new_profile = Profile_Seller(user=user)
#            new_profile.save()
#
#
#        # whay to get user from anther whay from objects.get
#        # profile = Profile.objects.get(user=user)
#
#    
#    except Exception as e:
#        print(e)
#        return render(request, '404.html')
#    return render(request, 'accounts/seller_profile.html', {'user':user})

def profile_view(request: HttpRequest, user_name):
    try:
        user = User.objects.get(username=user_name)
        
        if Profile_Seller.objects.filter(user=user).exists():
            profile = Profile_Seller.objects.get(user=user)
            template = 'accounts/seller_profile.html'
        else:
            profile, created = Profile_User.objects.get_or_create(user=user)
            template = 'accounts/user_profile.html'
    
    except User.DoesNotExist:
        return render(request, '404.html')

    return render(request, template, {'user': user, 'profile': profile})


#def update_user_profile(request:HttpRequest):
#    if not request.user.is_authenticated:
#        messages.warning(request, 'Only registered users can update profile', 'alert-warning')
#        return redirect('accounts:sign_in')
#    if request.method == 'POST':
#        try:
#            with transaction.atomic():
#                 user:User = request.user# هنا مايحتاج اجلبة من الداتا بيز objects.get
#                 user.first_name = request.POST['first_name']
#                 user.last_name = request.POST['last_name']
#                 user.email = request.POST['email']
#                 user.save()
#
#                 profile:Profile_User = user
#                 if 'avatar' in request.FILES: Profile_User.avatar = request.FILES['avatar']
#         
#                 profile.save()
#            messages.success(request, 'Profile updated successfully', 'alert-success')
#        except Exception as e:
#            messages.error(request, "Couldn't Profile updated ", "alert-danger")
#            print(e)
#    return render(request, 'accounts/update_profile.html')

def update_user_profile(request: HttpRequest):
    if not request.user.is_authenticated:
        messages.warning(request, 'Only registered users can update profile', 'alert-warning')
        return redirect('accounts:sign_in')

    if request.method == 'POST':
        try:
            with transaction.atomic():
                user: User = request.user
                user.first_name = request.POST['first_name']
                user.last_name = request.POST['last_name']
                user.email = request.POST['email']
                user.save()

                profile: Profile_User = user.profile_user  
                if 'avatar' in request.FILES:
                    profile.avatar = request.FILES['avatar']  
                profile.address = request.POST.get('address', profile.address)  
                profile.city = request.POST.get('city', profile.city)  
                profile.postal_code = request.POST.get('postal_code', profile.postal_code)  
                profile.phone_number = request.POST.get('phone_number', profile.phone_number) 

                profile.save() 

            messages.success(request, 'Profile updated successfully', 'alert-success')
        except Exception as e:
            messages.error(request, "Couldn't update profile", "alert-danger")
            print(e)

    return render(request, 'accounts/update_profile.html')

#def update_profile_view(request:HttpRequest):
#    if request.method == 'POST':
#        with transaction.atomic():
#            user = request.user
#            user.first_name = request.POST['first_name']
#            user.last_name = request.POST['last_name']
#            user.email = request.POST['email']
#            user.save()
#            if Profile_Seller.objects.filter(user=user).exists():
#                    profile = Profile_Seller.objects.get(user=user)
#            else:
#                    profile, _ = Profile_User.objects.get_or_create(user=user)



            

#def update_profile_view(request: HttpRequest, user_name):
#    try:
#        user = User.objects.get(useername = user_name)
#        # تحقق مما إذا كان المستخدم بائعًا أو مستخدمًا عاديًا  
#        if Profile_Seller.objects.filter(user=user).exists():
#            profile = Profile_Seller.objects.get(user=user)
#            template = 'accounts/update_seller_profile.html'
#    except User.DoesNotExist:
#         return render(request, '404.html')
#
#