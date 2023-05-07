from django.db import models


# Create your models here.
#新增VIP的MODEL
class VipInfodata(models.Model):
    cname=models.CharField(max_length=50,null=False)
    cemail=models.EmailField(max_length=50,null=False)
    cpasswd=models.CharField(max_length=50,null=False)
    cphone=models.CharField(max_length=50,null=False)
    cBirthday=models.DateField(null=True)
    cAddr=models.CharField(max_length=50,null=True)
 #新建購物車存放資訊
from django.contrib.auth.models import User#調用django原生內部的User模組
class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

#因為一個購物車裡會有很多不同
class CartItem(models.Model):
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE, related_name='items')
    productName=models.CharField(max_length=50,null=False)
    subPrice= models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    picId=models.PositiveIntegerField()

class CartTotalPrice(models.Model):
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE, related_name='total_price')
    total=models.PositiveIntegerField()