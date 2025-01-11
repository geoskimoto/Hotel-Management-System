from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from userauths.models import User, Profile
from userauths.forms import UserRegisterForm, MemberApplicationForm

# Create your views here.

def RegisterView(request, *args, **kwargs):
    if request.user.is_authenticated:
        messages.warning(request, f"Hey {request.user.username}, you are already logged in")
        return redirect('hotel:index')   

    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        form.save()
        full_name = form.cleaned_data.get('full_name')
        phone = form.cleaned_data.get('phone')
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')

        user = authenticate(email=email, password=password)
        login(request, user)

        messages.success(request, f"Hi {request.user.username}, your account have been created successfully.")

        profile = Profile.objects.get(user=request.user)
        profile.full_name = full_name
        profile.phone = phone
        profile.save()

        return redirect('hotel:index')
    
    context = {'form':form}
    return render(request, 'userauths/sign-up.html', context)

def LoginView(request):
    # if request.user.is_authenticated:
    #     return redirect('hotel:index')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)

            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "You are Logged In")
                return redirect('hotel:index')
            else:
                messages.error(request, 'Username or password does not exit.')
        
        except:
            messages.error(request, 'User does not exist')

    return HttpResponseRedirect("/")

def loginViewTemp(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in")
        return redirect('hotel:index')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)

            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "You are Logged In")
                # return redirect()
                next_url = request.GET.get("next", 'hotel:index')
                return redirect(next_url)
                
            else:
                messages.error(request, 'Username or password does not exit.')
        
        except:
            messages.error(request, 'User does not exist')

    return render(request, "userauths/sign-in.html")



def LogoutView(request):
    logout(request)
    messages.success(request, 'You have been logged out')
    return redirect("userauths:sign-in")


def membership_application(request):
    if request.method == 'POST':
        form = MemberApplicationForm(request.POST)
        if form.is_valid():
            form.save()  # Save the data to the database
            return redirect('success')  # Redirect to a success page
    else:
        form = MemberApplicationForm()

    return render(request, 'userauths/membership_application.html', {'form': form})

    # Class-based version of the same member_application function from above:
    # class MemberApplicationView(FormView):
    #     template_name = 'your_template_name.html'
    #     form_class = MemberApplicationForm
    #     success_url = reverse_lazy('success')  # Redirect after successful submission

    #     def form_valid(self, form):
    #         form.save()  # Save the form data to the database
    #         return super().form_valid(form)
