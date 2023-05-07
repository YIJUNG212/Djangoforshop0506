from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User #不意外,這模組還是要調用
from rest_framework import viewsets#調用viewsets
from shopapp.serializers import UserSerializer#調用解析器
from rest_framework.permissions import AllowAny,IsAuthenticated#調用權限模組
from rest_framework import serializers#調用rest_framework裡的解析器serializers
#權限問題要導入
from rest_framework.exceptions import PermissionDenied
from rest_framework import permissions
#密碼問題要引入
# from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.hashers import make_password#密碼加密這個模組要調用




class UserViewSet(viewsets.ModelViewSet):
    #下面這兩行就能調用ModelViewSet模組裡的CRUD,只是要針對客製化內容再覆寫
    queryset = User.objects.all()
    serializer_class = UserSerializer

    permission_classes = [AllowAny]
    authentication_classes = [JWTAuthentication] 
    
     
    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff:
                # 只有管理者可以查詢全部
                return User.objects.all()
            else:
                # 其他使用者只能用filter查自己
                return User.objects.filter(pk=user.pk)
        # 當未登入時,就什麼都沒得查
        return User.objects.none()
    def list(self, request, *args, **kwargs):
        
        if not request.user.is_authenticated:
            # 當還沒登入時，可以使用創造帳號功能
            return self.create(request, *args, **kwargs)
        else:
            return super().list(request, *args, **kwargs)
    def perform_create(self, serializer):
         # 當創建用戶時，會將密碼加密
        serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
        serializer.save()

    def perform_update(self, serializer):
        # 更新時的規範
        user = self.request.user
        if user == serializer.instance or user.is_staff:
            # 使用者自己或管理者時更新時,都可以存檔,而且密碼是加密的

            serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
            serializer.save()
        else:
            #當不是上述使用者,則顯示你沒有權利更新
            raise PermissionDenied("You don't have permission to update this user.")

    def perform_destroy(self, instance):
        # 刪除權限區域
        user = self.request.user
        if user == instance:
            #使用者本身不能刪帳號
            raise PermissionDenied("You don't have permission to delete your own account.")
        elif user.is_staff:
            # 管理者可以刪所有人帳號
            instance.delete()
        else:
            raise PermissionDenied("You don't have permission to delete this user.")
##****************************************************************************************
##加入需要的vipinfo
from shopapp.models import VipInfodata
from shopapp.serializers import VipInfoSerializer
class VipInfoViewSet(viewsets.ModelViewSet):
    queryset = VipInfodata.objects.all()
    serializer_class = VipInfoSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication] 


#########加入購物車的view,理論上只要加驗證就好,基本CRUD應該都要可以執行.自己對自己購物車要能掌控全部
from shopapp.models import ShoppingCart
from shopapp.serializers import ShoppingCartSerializer
class ShoppingCartViewSet(viewsets.ModelViewSet):
    #下面這兩行就能調用ModelViewSet模組裡的CRUD,只是要針對客製化內容再覆寫
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    #加入驗證的部份
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication] 
    def get_queryset(self):
        user = self.request.user  # 获取当前请求的用户
        return ShoppingCart.objects.filter(user=user)
#########加入購物車的 ITEM　view
from shopapp.models import CartItem
from shopapp.serializers import CartItemSerializer
#status 跟response要import
from rest_framework.response import Response
from rest_framework import status
#要加入QueryDict的套件,import
from django.http import QueryDict
###要回應JSON格式的話,要import這個
from django.http import HttpResponse, JsonResponse


class CartItemViewSet(viewsets.ModelViewSet):
    ####律定格式範圍#####
    def parse_form_data(self, data):
        # 將非 JSON 格式的 POST 請求轉成 QueryDict 格式
        if isinstance(data, QueryDict):
            # 如果已經是 QueryDict 格式，就直接返回
            return data

        # 取得請求標頭中的 Content-Type 值
        content_type = self.request.META.get('CONTENT_TYPE', '').split(';')[0].lower()

        # 如果 Content-Type 為 application/x-www-form-urlencoded，則使用 QueryDict 解析
        if content_type == 'application/x-www-form-urlencoded':
            return QueryDict(data)

        # 如果 Content-Type 為 multipart/form-data，則使用 request.POST 解析
        elif content_type == 'multipart/form-data':
            return self.request.POST

        # 其他情況，就直接返回原始請求數據
        else:
            return data
    ####律定格式範圍#####
    #下面這兩行就能調用ModelViewSet模組裡的CRUD,只是要針對客製化內容再覆寫
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
        #加入驗證的部份
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication] 

    def create(self, request, *args, **kwargs):
        # 取得POST資料
        data = request.data
        # 如果data是一個list，則迭代每一筆dict資料，分別創建CartItem物件
        if isinstance(data, list):
            cart_items = []
            for item_data in data:
                serializer = self.get_serializer(data=item_data)
                serializer.is_valid(raise_exception=False)
                cart_item = serializer.save()
                cart_items.append(cart_item)

            # 將回應資料轉換成 JSONArray 格式
            serializer = self.get_serializer(cart_items, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # 如果data是一個dict，則執行原本的create方法
        else:
            return super().create(request, *args, **kwargs)


#########加入購物車的 Total　view
from shopapp.models import CartTotalPrice
from shopapp.serializers import CartTotalPriceSerializer
class CartTotalPriceViewSet(viewsets.ModelViewSet):
    #下面這兩行就能調用ModelViewSet模組裡的CRUD,只是要針對客製化內容再覆寫
    queryset = CartTotalPrice.objects.all()
    serializer_class = CartTotalPriceSerializer
        #加入驗證的部份
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]