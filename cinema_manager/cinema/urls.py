from django.urls import path
from . import views

app_name = 'cinema'  

urlpatterns = [
    path('', views.home, name='home'),
    path('movies/<int:movie_id>/', views.movie_detail, name='movie_detail'),  
    path('sessions/<int:session_id>/', views.session_detail, name='session_detail'),  
    path('sessions/<int:session_id>/check_seats/', views.check_seat_availability, name='check_seat_availability'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    
    # Staff-only URLs
    path('manage/sessions/', views.manage_sessions, name='manage_sessions'),
    path('reports/sales/', views.sales_report, name='sales_report'),
]