from django.utils import timezone
from decimal import Decimal

def calculate_final_price(base_price, user=None, discount=None):
    final_price = Decimal(str(base_price)) 
    
    if discount:
        discount_percent = Decimal(str(discount.discount_percent)) / Decimal(100)
        final_price *= (Decimal(1) - discount_percent)
    
    if user and user.birth_date:
        age = (timezone.now().date() - user.birth_date).days // 365
        if age >= 60:
            final_price *= Decimal('0.9')  
    
    return final_price.quantize(Decimal('0.00'))  