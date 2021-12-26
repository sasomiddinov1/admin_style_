from django.shortcuts import render, redirect
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from django.http import HttpResponseRedirect, FileResponse
from .models import Event, Venue
from .forms import VenueForm, EventForm
from django.http import HttpResponse
import csv
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from django.core.paginator import Paginator
# Create your views here.

def venue_pdf(request):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont('Helvetica', 14)

    # lines = [
    #     'This is line 1'
    #     'This is line 2'
    #     'This is line 3'
    # ]
    venues = Venue.objects.all()
    lines = []

    for venue in venues:
        lines.append(venue.name)
        lines.append(venue.address)
        lines.append(venue.zip_code)
        lines.append(venue.phone)
        lines.append(venue.web)
        lines.append(venue.email_address)
        lines.append(' ')
        lines.append('=========================')
        lines.append(' ')


    for line in lines:
        textob.textLine(line)

    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename='venue.pdf')


def venue_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=venues.csv'
    writer = csv.writer(response)
    venues = Venue.objects.all()
    writer.writerow(['Venue Name',  'Address', 'Zip Code', 'Phone', 'Web Address', 'Email'])
    for venue in venues:
        writer.writerow([venue.name, venue.address, venue.zip_code, venue.phone, venue.web, venue.email_address])
    return response

def venue_text(request):
    response = HttpResponse(content_type='text/plein')
    response['Content-Disposition'] = 'attachment; filename=venues.txt'
    venues = Venue.objects.all()

    lines = []

    for venue in venues:
        lines.append(f'{venue.name}\n {venue.address}\n {venue.zip_code}\n {venue.phone}\n {venue.web}\n {venue.email_address}\n')

    # lines = ['This is line 1\n'
    #          'This is line 2\n'
    #          'This is line 3\n'
    #
    #          ]

    response.writelines(lines)
    return response

def delete_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    venue.delete()
    return redirect('list-venues')

def delete_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    event.delete()
    return redirect('list-events')

def add_event(request):
    submitted = False
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/add_event?submitted=True')
    else:
        form = EventForm
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'add_event.html',
                  {"form": form, 'submitted': submitted})



def update_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    form = EventForm(request.POST or None, instance=event)
    if form.is_valid():
        form.save()
        return redirect('list-events')

    return render(request, 'update_event.html',
                  {'event': event,
                   'form': form
                   })



def update_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    form = VenueForm(request.POST or None, instance=venue)
    if form.is_valid():
        form.save()
        return redirect('list-venues')

    return render(request, 'update_venue.html',
                  {'venue': venue,
                   'form': form
                   })


def search_venues(request):
    if request.method == "POST":
        searched = request.POST["searched"]
        venues = Venue.objects.filter(name__contains=searched)
        return render(request, 'search_venues.html',
                     {'searched': searched,  'venues': venues})
    else:
        return render(request, 'search_venues.html', {})


def show_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    return render(request, 'show_venue.html',
                  {'venue': venue})



def list_venues(request):
    # venue_list = Venue.objects.all().order_by('name')
    venue_list = Venue.objects.all()

    p = Paginator(Venue.objects.all(), 3)
    page = request.GET.get('page')
    venues = p.get_page(page)
    nums = 'a' * venues.paginator.num_pages

    return render(request, 'venue.html',
                  {'venue_list': venue_list,
                   'venues': venues,
                   'nums': nums
                   })


def add_venue(request):
    submitted = False
    if request.method == "POST":
        form = VenueForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/add_venue? submitted=True')
    else:
        form = VenueForm
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'venue_add.html',
                  {"form": form, 'submitted': submitted})

def all_events(request):
    event_list = Event.objects.all().order_by('name')
    return render(request, 'event_list.html',
                  {'event_list': event_list})

def home(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
    name = "Khadjiya"
    month = month.capitalize()
    month_number = list(calendar.month_name).index(month)
    month_number = int(month_number)
    # create calendar
    cal = HTMLCalendar().formatmonth(year, month_number)
    now = datetime.now()
    current_year = now.year
    time = now.strftime('%I:%M %p')


    return render(request, 'home.html', {
        "name": name,
        "year": year,
        "month": month,
        "month_number": month_number,
        "cal": cal,
        "current_year": current_year,
        "time": time,
    })