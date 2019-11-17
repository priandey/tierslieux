from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from django.db.utils import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from .forms import SigninForm, EditProfileForm
from .models import CustomUser


def sign_in(request):
    '''
    Sign In view
    '''

    form = SigninForm(request.POST or None)
    if form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        try:
            new_user = CustomUser.objects.create_user(email, password)
            new_user.save()
            if not isinstance(request.user, AnonymousUser):
                user = authenticate(request, username=email, password=password)
                login(request, user)
            return redirect('home')
        except IntegrityError:
            duplicate_email = True
    else:
        validForm = False

    return render(request, 'user/signin.html', locals())


def log_in(request):
    '''
    Log in view
    '''

    form = SigninForm(request.POST or None)

    if form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request=request, user=user)
            return redirect("private_locations")
        else:
            logged = False

    return render(request, 'user/login.html', locals())


def log_out(request):
    '''
    Log out view
    '''

    logout(request)
    return redirect("home")


@login_required(login_url='/user/login/')
def profile(request):
    return render(request, "user/userprofile.html", locals())


@login_required(login_url='/user/login/')
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = EditProfileForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['password'])
            user.save()
            response = redirect('userprofile')
        else:
            response = render(request, 'user/edit_profile.html', {
                'form': form,
                'error': True,
            })
    else:
        form = EditProfileForm()
        response = render(request, 'user/edit_profile.html', {'form': form})
    return response

@login_required(login_url='/user/login')
def delete_profile(request):
    if request.method == 'POST':
        user = request.user.pk
        logout(request)
        CustomUser.objects.get(pk=user).delete()
    return redirect('home', permanent=True)