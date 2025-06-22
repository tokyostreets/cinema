from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
import os

def movie_poster_path(instance, filename):
    return os.path.join('movie_posters', filename)

class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

class Movie(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    duration = models.PositiveIntegerField(verbose_name='Длительность (мин)')
    poster = models.ImageField(upload_to=movie_poster_path, verbose_name='Постер')
    age_rating = models.PositiveIntegerField(verbose_name='Возрастной рейтинг')
    genre = models.CharField(max_length=100, verbose_name='Жанр')
    director = models.CharField(max_length=255, verbose_name='Режиссер')
    release_date = models.DateField(verbose_name='Дата выхода')
    
    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'
    
    def __str__(self):
        return self.title

class Hall(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    seats_rows = models.PositiveIntegerField(verbose_name='Количество рядов')
    seats_per_row = models.PositiveIntegerField(verbose_name='Мест в ряду')
    description = models.TextField(blank=True, verbose_name='Описание')
    
    class Meta:
        verbose_name = 'Зал'
        verbose_name_plural = 'Залы'
    
    def __str__(self):
        return f"{self.name} ({self.seats_rows}x{self.seats_per_row})"
    
    @property
    def total_seats(self):
        return self.seats_rows * self.seats_per_row


class Session(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name='Фильм')
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, verbose_name='Зал')
    start_time = models.DateTimeField(verbose_name='Время начала')  
    end_time = models.DateTimeField(blank=True, null=True, verbose_name='Время окончания')
    base_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Базовая цена')
    
    class Meta:
        verbose_name = 'Сеанс'
        verbose_name_plural = 'Сеансы'
        ordering = ['start_time']
    
    def __str__(self):
        return f"{self.movie.title} - {self.start_time.strftime('%d.%m.%Y %H:%M')}"
    
    def save(self, *args, **kwargs):
        if not self.end_time and hasattr(self, 'movie'):
            if timezone.is_naive(self.start_time):
                self.start_time = timezone.make_aware(self.start_time)
            self.end_time = self.start_time + timedelta(minutes=self.movie.duration)
        super().save(*args, **kwargs)
    
    @property
    def is_past(self):
        if self.end_time:
            return self.end_time < timezone.now()
        return False
    

class Ticket(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, verbose_name='Сеанс')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    row = models.PositiveIntegerField(verbose_name='Ряд')
    seat = models.PositiveIntegerField(verbose_name='Место')
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Цена')
    purchase_time = models.DateTimeField(auto_now_add=True, verbose_name='Время покупки')
    is_paid = models.BooleanField(default=False, verbose_name='Оплачен')
    
    class Meta:
        verbose_name = 'Билет'
        verbose_name_plural = 'Билеты'
        unique_together = ('session', 'row', 'seat')
    
    def __str__(self):
        return f"Билет на {self.session} - ряд {self.row}, место {self.seat}"

class Discount(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    discount_percent = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name='Процент скидки'
    )
    code = models.CharField(max_length=20, unique=True, verbose_name='Код скидки')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    valid_from = models.DateTimeField(verbose_name='Действует с')
    valid_to = models.DateTimeField(verbose_name='Действует до')
    
    class Meta:
        verbose_name = 'Скидка'
        verbose_name_plural = 'Скидки'
    
    def __str__(self):
        return f"{self.name} ({self.discount_percent}%)"
    
    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.valid_from <= now <= self.valid_to