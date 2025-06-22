from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count
from .models import Movie, Session, Hall, Ticket, Discount
from .forms import UserRegistrationForm, TicketBookingForm, DiscountApplyForm, SessionForm
from .reports import generate_sales_report
from .utils import calculate_final_price
import csv
from datetime import timedelta

def home(request):
    now = timezone.localtime()
    upcoming_sessions = Session.objects.filter(start_time__gte=now).order_by('start_time')[:10]
    movies = Movie.objects.all()
    
    context = {
        'upcoming_sessions': upcoming_sessions,
        'movies': movies,
    }
    return render(request, 'cinema/home.html', context)

def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    now = timezone.localtime()
    sessions = Session.objects.filter(movie=movie, start_time__gte=now).order_by('start_time')
    
    context = {
        'movie': movie,
        'sessions': sessions,
    }
    return render(request, 'cinema/movie_detail.html', context)

def session_detail(request, session_id):
    session = get_object_or_404(Session, pk=session_id)
    booked_seats = Ticket.objects.filter(session=session).values_list('row', 'seat')
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = TicketBookingForm(request.POST, session=session)
        discount_form = DiscountApplyForm(request.POST)
        
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.session = session
            ticket.user = request.user
            
            discount = None
            if discount_form.is_valid():
                discount_code = discount_form.cleaned_data['discount_code']
                try:
                    discount = Discount.objects.get(code=discount_code, is_active=True)
                except Discount.DoesNotExist:
                    pass
            
            ticket.price = calculate_final_price(session.base_price, request.user, discount)
            ticket.save()
            return redirect('profile')
    else:
        form = TicketBookingForm(session=session)
        discount_form = DiscountApplyForm()
    
    context = {
        'session': session,
        'form': form,
        'discount_form': discount_form,
        'booked_seats_as_strings': booked_seats,
        'rows_range': range(1, session.hall.seats_rows + 1),
        'seats_range': range(1, session.hall.seats_per_row + 1),
    }
    return render(request, 'cinema/session_detail.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'cinema/register.html', {'form': form})

@login_required
def profile(request):
    if not request.user.is_authenticated:
        return redirect('login') 
    
    try:
        user_tickets = Ticket.objects.filter(user=request.user).select_related(
            'session__movie',
            'session__hall'
        ).order_by('-purchase_time')
        
        context = {
            'tickets': user_tickets,
            'user': request.user 
        }
        return render(request, 'cinema/profile.html', context)
        
    except Exception as e:
        #(на продакшне logging)
        print(f"Error in profile view: {e}")
        return render(request, 'cinema/error.html', {'error': str(e)})

@staff_member_required
def manage_sessions(request):
    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_sessions')
    else:
        form = SessionForm()
    
    now = timezone.localtime()
    upcoming_sessions = Session.objects.filter(start_time__gte=now).order_by('start_time')
    past_sessions = Session.objects.filter(start_time__lt=now).order_by('-start_time')
    
    context = {
        'form': form,
        'upcoming_sessions': upcoming_sessions,
        'past_sessions': past_sessions,
    }
    return render(request, 'cinema/manage_sessions.html', context)

@staff_member_required
def sales_report(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        report_type = request.POST.get('report_type')
        
        report_data = generate_sales_report(start_date, end_date, report_type)
        
        if 'export_csv' in request.POST:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="sales_report_{start_date}_to_{end_date}.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Период', 'Количество билетов', 'Общая выручка'])
            
            for row in report_data:
                writer.writerow(row)
            
            return response
        
        context = {
            'report_data': report_data,
            'start_date': start_date,
            'end_date': end_date,
            'report_type': report_type,
        }
        return render(request, 'cinema/sales_report.html', context)
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    report_data = generate_sales_report(start_date, end_date, 'daily')
    
    context = {
        'report_data': report_data,
        'start_date': start_date,
        'end_date': end_date,
        'report_type': 'daily',
    }
    return render(request, 'cinema/sales_report.html', context)

def check_seat_availability(request, session_id):
    session = get_object_or_404(Session, pk=session_id)
    booked_seats = list(Ticket.objects.filter(session=session).values_list('row', 'seat'))
    return JsonResponse({'booked_seats': booked_seats})