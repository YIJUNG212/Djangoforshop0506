# Serializers define the API representation.


from rest_framework import serializers#調用rest_framework裡的解析器serializers
from django.contrib.auth.models import User#調用django原生內部的User模組
class UserSerializer(serializers.HyperlinkedModelSerializer):
     # 下面這行將超級管理者權限關掉
    is_staff = serializers.ReadOnlyField()
    class Meta:
        model = User
        fields = ['id','url', 'username','password', 'email', 'is_staff']

###要加入VIPINFO的解析
from shopapp.models import VipInfodata
class VipInfoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=VipInfodata
        fields="__all__"

###加入購物車及其項目,加總等三份資料解析
from shopapp.models import ShoppingCart
class ShoppingCartSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=ShoppingCart
        fields="__all__"

from shopapp.models import CartItem
class CartItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=CartItem
        fields = ['cart', 'productName', 'subPrice', 'quantity', 'picId']
       # fields="__all__"

from shopapp.models import CartTotalPrice
class CartTotalPriceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=CartTotalPrice
        fields="__all__"