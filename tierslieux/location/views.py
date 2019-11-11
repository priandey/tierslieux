from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from userlocations.models import UserFavorite
from .models import Location, Status, VolunteerBase, VolunteeringRequest
from .forms import LocationForm, StatusForm

def location_detail(request, slug):
    location = Location.objects.get(slug=slug)
    statuses = Status.objects.filter(location=location).order_by('-open_date')
    last_status = Status.objects.filter(location=location).last()
    if last_status:
        opened = last_status.is_opened

    if request.user.is_authenticated:
        user = request.user
        if user == location.moderator:
            disclaimer = "Vous êtes modérateur de ce lieu"
            location_mod = True

        for entry in VolunteerBase.objects.filter(location=location):
            if user == entry.volunteer:
                if entry.volunteering_request.validated:
                    disclaimer = "Vous êtes bénévole sur ce lieu"

        if UserFavorite.objects.filter(location=location, user=user):
            is_favorite = True

        return render(request, 'location/location_detail_logged.html', locals())
    else:
        return render(request, 'location/location_detail_common.html', locals())


@login_required(login_url='/user/login/')
def location_creation(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            new_location = form.save(commit=False)
            new_location.moderator = request.user
            new_location.save()
            return HttpResponseRedirect('/')
    else:
        form = LocationForm()
    return render(request, 'location/location_creation.html', locals())

@login_required(login_url='/user/login/')
def require_volunteering(request, slug):
    location = Location.objects.get(slug=slug)
    requesting_user = request.user
    moderator = location.moderator

    sent_request = VolunteeringRequest.objects.create(
            sender=requesting_user,
            receiver=moderator,
            validated=False,
    ) #Creating a new request

    VolunteerBase.objects.create(
            volunteer=requesting_user,
            location=location,
            is_active=False,
            volunteering_request=sent_request
    ) #Creating a new entry for the location in the volunteer base
    return redirect('location', slug=location.slug)

@login_required(login_url='/user/login/')
def add_status(request, slug):
    location = Location.objects.get(slug=slug)
    if VolunteerBase.objects.filter(location=location, volunteer=request.user) or request.user == location.moderator:
        if request.method == 'POST':
            form = StatusForm(request.POST)
            if form.is_valid():
                new_status = form.save(commit=False)
                new_status.volunteer = request.user
                new_status.location = Location.objects.get(slug=slug)
                new_status.save()
                return redirect('location', permanent=True, slug=slug)
        else:
            form = StatusForm()
            location = slug
            return render(request, 'location/status_declaration.html', locals())

@login_required(login_url='/user/login/')
def close_status(request, slug):
    location = Location.objects.get(slug=slug)
    if VolunteerBase.objects.filter(location=location, volunteer=request.user) or request.user == location.moderator:
            Status.objects.filter(location=location).last().close()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

#TODO : location_edition view for moderator


def search_location(request):
    if request.POST:
        searchterm = request.POST['research']
        location = get_object_or_404(Location, name=searchterm)
        print(location.name)
        return redirect('location', slug=location.slug)
