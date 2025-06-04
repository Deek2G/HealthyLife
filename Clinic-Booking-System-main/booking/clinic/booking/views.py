from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from datetime import datetime, timedelta
from .models import *
from django.contrib import messages
from .forms import AppointmentForm
from django.core.mail import send_mail

def index(request):
    return render(request, "index.html",{})

def about(request):
    return render(request, 'about.html')

def booking(request):
    # Calling 'validWeekday' Function to Loop days you want in the next 21 days:
    weekdays = validWeekday(22)

    # Remove today's date from the weekdays list if it exists:
    today = datetime.now().strftime('%Y-%m-%d')
    weekdays = [day for day in weekdays if day != today]

    # Only show the days that are not full:
    validateWeekdays = isWeekdayValid(weekdays)

    if request.method == 'POST':
        service = request.POST.get('service')
        day = request.POST.get('day')
        doctor = request.POST.get('doctor')  # Capture the selected doctor

        if not service or not doctor:
            messages.success(request, "Please Select A Service and Doctor!")
            return redirect('booking')

        # Store day, service, and doctor in django session:
        request.session['day'] = day
        request.session['service'] = service
        request.session['doctor'] = doctor

        return redirect('bookingSubmit')

    return render(request, 'booking.html', {
        'weekdays': weekdays,
        'validateWeekdays': validateWeekdays,
    })

def bookingSubmit(request):
    user = request.user
    times = [
        "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM", "1:00 PM", "1:30 PM", "2:00 PM", "2:30 PM", "3:00 PM", "3:30 PM", "4:00 PM", "4:30 PM", "5:00 PM", "5:30 PM"
    ]
    today = datetime.now()
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=21)
    strdeltatime = deltatime.strftime('%Y-%m-%d')
    maxDate = strdeltatime

    # Get stored data from django session:
    day = request.session.get('day')
    service = request.session.get('service')
    doctor = request.session.get('doctor')  # Get the selected doctor

    # Only show the time of the day that has not been selected before:
    hour = checkTime(times, day)
    if request.method == 'POST':
        time = request.POST.get("time")
        date = dayToWeekday(day)

        if service and doctor:
            if minDate <= day <= maxDate:
                if date in ['Monday', 'Wednesday', 'Friday']:
                    if Appointment.objects.filter(day=day).count() < 11:
                        if Appointment.objects.filter(day=day, time=time).count() < 1:
                            Appointment.objects.get_or_create(
                                user=user,
                                service=service,
                                doctor=doctor,  # Save the selected doctor
                                day=day,
                                time=time,
                            )
                            messages.success(request, "Appointment Saved!")
                            return redirect('index')
                        else:
                            messages.success(request, "The Selected Time Has Been Reserved Before!")
                    else:
                        messages.success(request, "The Selected Day Is Full!")
                else:
                    messages.success(request, "The Selected Date Is Incorrect")
            else:
                messages.success(request, "The Selected Date Isn't In The Correct Time Period!")
        else:
            messages.success(request, "Please Select A Service and Doctor!")

    return render(request, 'bookingSubmit.html', {
        'times': hour,
    })

def userPanel(request):
    user = request.user
    appointments = Appointment.objects.filter(user=user).order_by('day', 'time')
    return render(request, 'userPanel.html', {
        'user':user,
        'appointments':appointments,
    })

def userUpdate(request, id):
    appointment = Appointment.objects.get(pk=id)
    userdatepicked = appointment.day
    today = datetime.today()
    minDate = today.strftime('%Y-%m-%d')

    # 24h condition for allowing editing:
    delta24 = (userdatepicked).strftime('%Y-%m-%d') >= (today + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Loop to get valid weekdays, and filter out today:
    weekdays = validWeekday(22)

    # Remove today's date from the weekdays list if it exists:
    weekdays = [day for day in weekdays if day != minDate]

    # Only show the days that are not full:
    validateWeekdays = isWeekdayValid(weekdays)

    if request.method == 'POST':
        service = request.POST.get('service')
        day = request.POST.get('day')

        # Store day and service in django session:
        request.session['day'] = day
        request.session['service'] = service

        return redirect('userUpdateSubmit', id=id)

    return render(request, 'userUpdate.html', {
        'weekdays': weekdays,
        'validateWeekdays': validateWeekdays,
        'delta24': delta24,
        'id': id,
    })

    

    if request.method == 'POST':
        service = request.POST.get('service')
        day = request.POST.get('day')

        # Store day and service in django session:
        request.session['day'] = day
        request.session['service'] = service

        return redirect('userUpdateSubmit', id=id)


    return render(request, 'userUpdate.html', {
            'weekdays':weekdays,
            'validateWeekdays':validateWeekdays,
            'delta24': delta24,
            'id': id,
        })

def userUpdateSubmit(request, id):
    user = request.user
    times = [
        "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM", "1:00 PM", "1:30 PM", "2:00 PM", "2:30 PM", "3:00 PM", "3:30 PM", "4:00 PM", "4:30 PM", "5:00 PM", "5:30 PM"
    ]
    today = datetime.now()
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=21)
    strdeltatime = deltatime.strftime('%Y-%m-%d')
    maxDate = strdeltatime

    day = request.session.get('day')
    service = request.session.get('service')
    
    # Only show the time of the day that has not been selected before and the time he is editing:
    hour = checkEditTime(times, day, id)
    appointment = Appointment.objects.get(pk=id)
    userSelectedTime = appointment.time
    if request.method == 'POST':
        time = request.POST.get("time")
        date = dayToWeekday(day)

        if service != None:
            if day <= maxDate and day >= minDate:
                if date == 'Monday' or date == 'Wednesday' or date == 'Friday':
                    if Appointment.objects.filter(day=day).count() < 11:
                        if Appointment.objects.filter(day=day, time=time).count() < 1 or userSelectedTime == time:
                            Appointment.objects.filter(pk=id).update(
                                user = user,
                                service = service,
                                day = day,
                                time = time,
                            ) 
                            messages.success(request, "Appointment Edited!")
                            return redirect('index')
                        else:
                            messages.success(request, "The Selected Time Has Been Reserved Before!")
                    else:
                        messages.success(request, "The Selected Day Is Full!")
                else:
                    messages.success(request, "The Selected Date Is Incorrect")
            else:
                    messages.success(request, "The Selected Date Isn't In The Correct Time Period!")
        else:
            messages.success(request, "Please Select A Service!")
        return redirect('userPanel')


    return render(request, 'userUpdateSubmit.html', {
        'times':hour,
        'id': id,
    })

def staffPanel(request):
    today = datetime.today()
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=31)
    strdeltatime = deltatime.strftime('%Y-%m-%d')
    maxDate = strdeltatime

    # Query for today's appointments (filtering appointments with today's date)
    today_items = Appointment.objects.filter(day=minDate).order_by('time')

    # Query for upcoming appointments (filtering appointments with dates after today)
    upcoming_items = Appointment.objects.filter(day__gt=minDate).order_by('day', 'time')

    return render(request, 'staffPanel.html', {
        'today_items': today_items,
        'upcoming_items': upcoming_items,
    })


def delete_appointment(request, appointment_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to delete this appointment.")
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.delete()
    return redirect('staffPanel')

def edit_appointment(request, appointment_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to edit this appointment.")

    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('staffPanel')
    else:
        form = AppointmentForm(instance=appointment)

    return render(request, 'edit_appointment.html', {'form': form})


def dayToWeekday(x):
    z = datetime.strptime(x, "%Y-%m-%d")
    y = z.strftime('%A')
    return y

def validWeekday(days):
    # Loop days you want in the next 21 days:
    today = datetime.now()
    weekdays = []
    for i in range (0, days):
        x = today + timedelta(days=i)
        y = x.strftime('%A')
        if y == 'Monday' or y == 'Wednesday' or y == 'Friday':
            weekdays.append(x.strftime('%Y-%m-%d'))
    return weekdays

def isWeekdayValid(x):
    validateWeekdays = []
    for j in x:
        if Appointment.objects.filter(day=j).count() < 10:
            validateWeekdays.append(j)
    return validateWeekdays

def checkTime(times, day):
    # Only show the time of the day that has not been selected before:
    x = []
    for k in times:
        if Appointment.objects.filter(day=day, time=k).count() < 1:
            x.append(k)
    return x

def checkEditTime(times, day, id):
    # Only show the time of the day that has not been selected before:
    x = []
    appointment = Appointment.objects.get(pk=id)
    time = appointment.time
    for k in times:
        if Appointment.objects.filter(day=day, time=k).count() < 1 or time == k:
            x.append(k)
    return x

def cancelAppointment(request, appointment_id):
    # Get the appointment or return 404 if it doesn't exist
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if the user owns the appointment
    if appointment.user != request.user:
        return HttpResponseForbidden("You cannot cancel this appointment.")
    
    # Delete the appointment
    appointment.delete()
    messages.success(request, "Appointment cancelled successfully.")
    return redirect('userPanel')
