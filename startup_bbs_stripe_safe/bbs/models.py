from django.db import models

from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator,MaxValueValidator,RegexValidator


class Topic(models.Model):

    class Meta:
        db_table = "topic"

    comment     = models.CharField(verbose_name="コメント",max_length=2000)

    def __str__(self):
        return self.comment


class Product(models.Model):

    name    = models.CharField(verbose_name="商品名",max_length=100)
    price   = models.PositiveIntegerField(verbose_name="価格")


class Cart(models.Model):

    dt      = models.DateTimeField(verbose_name="カートに追加された日時",default=timezone.now)
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="カートに入れた人", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="商品", on_delete=models.CASCADE)
    amount  = models.IntegerField(verbose_name="商品の個数", default=1, validators=[MinValueValidator(1)] )

class Order(models.Model):

    dt          = models.DateTimeField(verbose_name="注文日時",default=timezone.now)
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="注文した人", on_delete=models.CASCADE)
    paid        = models.DateTimeField(verbose_name="支払い確認日時",null=True,blank=True)

    #TODO:セッションIDの桁数不明につき取り急ぎ文字数制限のないTextFieldで
    session_id  = models.TextField(verbose_name="StripeセッションID")

    
