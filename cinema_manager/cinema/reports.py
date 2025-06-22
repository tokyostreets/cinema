from django.db.models import Sum, Count
from django.utils import timezone
from .models import Ticket
from datetime import datetime, timedelta

def generate_sales_report(start_date, end_date, report_type='daily'):
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    tickets = Ticket.objects.filter(
        purchase_time__date__gte=start_date,
        purchase_time__date__lte=end_date,
        is_paid=True
    )
    
    if report_type == 'daily':
        return generate_daily_report(tickets, start_date, end_date)
    elif report_type == 'weekly':
        return generate_weekly_report(tickets, start_date, end_date)
    elif report_type == 'monthly':
        return generate_monthly_report(tickets, start_date, end_date)
    elif report_type == 'by_movie':
        return generate_movie_report(tickets)
    elif report_type == 'by_hall':
        return generate_hall_report(tickets)
    else:
        return []

def generate_daily_report(tickets, start_date, end_date):
    report_data = []
    current_date = start_date
    
    while current_date <= end_date:
        daily_tickets = tickets.filter(purchase_time__date=current_date)
        total = daily_tickets.aggregate(total=Sum('price'), count=Count('id'))
        
        report_data.append((
            current_date.strftime('%d.%m.%Y'),
            total['count'] or 0,
            round(total['total'] or 0, 2)
        ))
        
        current_date += timedelta(days=1)
    
    return report_data

def generate_weekly_report(tickets, start_date, end_date):
    report_data = []
    current_date = start_date
    
    while current_date <= end_date:
        week_start = current_date
        week_end = min(current_date + timedelta(days=6), end_date)
        
        weekly_tickets = tickets.filter(
            purchase_time__date__gte=week_start,
            purchase_time__date__lte=week_end
        )
        
        total = weekly_tickets.aggregate(total=Sum('price'), count=Count('id'))
        
        report_data.append((
            f"{week_start.strftime('%d.%m')} - {week_end.strftime('%d.%m.%Y')}",
            total['count'] or 0,
            round(total['total'] or 0, 2)
        ))
        
        current_date += timedelta(days=7)
    
    return report_data

def generate_monthly_report(tickets, start_date, end_date):
    report_data = []
    current_date = start_date.replace(day=1)
    
    while current_date <= end_date:
        next_month = current_date.replace(day=28) + timedelta(days=4)
        month_end = (next_month - timedelta(days=next_month.day)).replace(day=1)
        month_end = min(month_end, end_date)
        
        monthly_tickets = tickets.filter(
            purchase_time__date__gte=current_date,
            purchase_time__date__lte=month_end
        )
        
        total = monthly_tickets.aggregate(total=Sum('price'), count=Count('id'))
        
        report_data.append((
            current_date.strftime('%B %Y'),
            total['count'] or 0,
            round(total['total'] or 0, 2)
        ))
        
        current_date = month_end + timedelta(days=1)
    
    return report_data

def generate_movie_report(tickets):
    report_data = []
    
    movie_stats = tickets.values('session__movie__title').annotate(
        total=Sum('price'),
        count=Count('id')
    ).order_by('-total')
    
    for stat in movie_stats:
        report_data.append((
            stat['session__movie__title'],
            stat['count'],
            round(stat['total'], 2)
        ))
    
    return report_data

def generate_hall_report(tickets):
    report_data = []
    
    hall_stats = tickets.values('session__hall__name').annotate(
        total=Sum('price'),
        count=Count('id')
    ).order_by('-total')
    
    for stat in hall_stats:
        report_data.append((
            stat['session__hall__name'],
            stat['count'],
            round(stat['total'], 2)
        ))
    
    return report_data