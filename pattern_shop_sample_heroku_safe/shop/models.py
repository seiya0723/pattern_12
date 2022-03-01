from django.db import models
from django.utils import timezone

#Djangoのもともとあったユーザーモデルと1対多を結ぶのではなく、カスタムしたユーザーモデルと1対多を結ぶ
#from django.contrib.auth.models import User
from django.conf import settings

from django.core.mail import send_mail

from django.core.validators import MinValueValidator,MaxValueValidator,RegexValidator


class Pattern(models.Model):

    class Meta:
        db_table = "pattern"

    title   = models.CharField(verbose_name="タイトル",max_length=30)
    dt      = models.DateTimeField(verbose_name="投稿日時",default=timezone.now)
    img     = models.ImageField(verbose_name="画像",upload_to="shop/pattern/")

    #ここに糸の太さを指定するフィールドを追加。糸の太さは1つしかないからPatternModelに記録。
    size    = models.IntegerField(verbose_name="糸の太さ",default=1,validators=[MinValueValidator(1),MaxValueValidator(10)])


    #userモデルと紐づくフィールド(nullはサンプルの模様を格納)
    #user    = models.ForeignKey(User, verbose_name="投稿者", on_delete=models.CASCADE, null=True,blank=True)

    #カスタムユーザーモデルと1対多を結ぶ
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="投稿者", on_delete=models.CASCADE, null=True,blank=True)

    def __str__(self):
        return self.title

class PatternRecipe(models.Model):

    #Patternモデルクラスと1対多のリレーションを作る。
    target      = models.ForeignKey(Pattern,verbose_name="対象の模様",on_delete=models.CASCADE)

    #colorフィールドは16進数カラーコードの正規表現を指定し、それのみ受け付ける
    #参照:https://noauto-nolife.com/post/django-models-regex-validate/
    color_regex = RegexValidator(regex=r'^#(?:[0-9a-fA-F]{6})$')
    color       = models.CharField(verbose_name="色",max_length=7,validators=[color_regex],default="#000000")

    number      = models.IntegerField(verbose_name="本数",default=1,validators=[MinValueValidator(1),MaxValueValidator(10)])

    #ここにコントローラの順番を記録するため、dtを記録する
    dt      = models.DateTimeField(verbose_name="投稿日時",default=timezone.now)
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="投稿者", on_delete=models.CASCADE, null=True,blank=True)

class Contact(models.Model):

    dt      = models.DateTimeField(verbose_name="お問い合わせ日時",default=timezone.now)
    subject = models.CharField(verbose_name="お問い合わせ件名",max_length=100)
    content = models.CharField(verbose_name="お問い合わせ内容",max_length=1000)
    
    #TODO:お問い合わせしてきた人のIPアドレスを記録する。
    #参照元:https://noauto-nolife.com/post/django-show-ip-ua-gateway/
    #参照元:https://noauto-nolife.com/post/django-same-user-operate-prevent/
    ip      = models.GenericIPAddressField(verbose_name="お問い合わせした人のIPアドレス")

    email   = models.EmailField(verbose_name="お問い合わせ送信先Email")
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="投稿者", on_delete=models.CASCADE, null=True,blank=True)


    def __str__(self):
        return self.subject


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        print("お問い合わせ承りました。")

        #TODO:ここにメール送信をする。

        subject = "お問い合わせ承りました"
        message = "お問い合わせ承りました\n\n" + "件名:" + self.subject + "\n本文:" + self.content 

        #運営からのメールであれば、このようにsettings.pyに書いてあるDEFAULT_FROM_EMAILを読み取り、セットする。
        #ユーザー間の送信であれば、ユーザーモデルからメールアドレスを参照する。
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [ self.email ]

        send_mail(subject, message, from_email, recipient_list)


class Product(models.Model):

    name    = models.CharField(verbose_name="商品名",max_length=100)
    price   = models.PositiveIntegerField(verbose_name="価格")


class Cart(models.Model):

    dt      = models.DateTimeField(verbose_name="カートに追加された日時",default=timezone.now)
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="カートに入れた人", on_delete=models.CASCADE)

    product = models.ForeignKey(Product, verbose_name="商品", on_delete=models.CASCADE)
    pattern = models.ForeignKey(Pattern, verbose_name="商品に貼り付ける模様", on_delete=models.CASCADE)
    amount  = models.IntegerField(verbose_name="商品の個数", default=1, validators=[MinValueValidator(1)] )

    #TODO:顧客がカートに入れた時CartFormでバリデーションしてこのCartモデルに追加する
    #TODO:注文した時にカート内のデータを全て消して対処。orderedは無くても良い。レコードを削除して対処する。
    #ordered = models.BooleanField(verbose_name="注文済み",default=False)
    

class Order(models.Model):

    dt          = models.DateTimeField(verbose_name="注文日時",default=timezone.now)
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="注文した人", on_delete=models.CASCADE)

    paid        = models.DateTimeField(verbose_name="支払い確認日時",null=True,blank=True)
    deliverd    = models.DateTimeField(verbose_name="配送処理日時",null=True,blank=True)

    #TODO:配送先モデルを作って、ユーザーは配送先を選ぶ、ビューはそれを受け取り、下記の住所に複写する。(途中で書き換えられないように)
    prefecture  = models.CharField(verbose_name="配送先の都道府県",max_length=100)
    city        = models.CharField(verbose_name="市町村",max_length=100)
    address     = models.CharField(verbose_name="番地・部屋番号",max_length=100)


class OrderDetail(models.Model):

    order           = models.ForeignKey(Order, verbose_name="注文", on_delete=models.CASCADE)

    product_price   = models.PositiveIntegerField(verbose_name="注文したときの商品の価格")
    product_name    = models.PositiveIntegerField(verbose_name="注文時の商品の名前")

    pattern_img     = models.ImageField(verbose_name="画像",upload_to="shop/pattern/")
    pattern_size    = models.IntegerField(verbose_name="注文時の糸の太さ",default=1,validators=[MinValueValidator(1),MaxValueValidator(10)])

    amount          = models.IntegerField(verbose_name="商品の個数", default=1, validators=[MinValueValidator(1)] )


class OrderDetailPattern(models.Model):

    #対象の注文
    order_detail    = models.ForeignKey(Order,verbose_name="注文(1種類に対しての注文)",on_delete=models.CASCADE)

    color_regex     = RegexValidator(regex=r'^#(?:[0-9a-fA-F]{6})$')
    color           = models.CharField(verbose_name="色",max_length=7,validators=[color_regex],default="#000000")
    number          = models.IntegerField(verbose_name="本数",default=1,validators=[MinValueValidator(1),MaxValueValidator(10)])

    #ここにコントローラの順番を記録するため、dtを記録する
    dt          = models.DateTimeField(verbose_name="投稿日時",default=timezone.now)




"""

    dt      = models.DateTimeField(verbose_name="注文日時",default=timezone.now)
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="カートに入れた人", on_delete=models.CASCADE)

    product_price   = models.PositiveIntegerField(verbose_name="決済したときの商品の価格")
    product         = models.ForeignKey(Product, verbose_name="商品", on_delete=models.CASCADE)
    amount          = models.IntegerField(verbose_name="商品の個数", default=1, validators=[MinValueValidator(1)] )

    paid    = models.BooleanField(verbose_name="支払い確認済み",default=False)

    prefectures = models.CharField(verbose_name="配送先の都道府県",max_length=100)
    city        = models.CharField(verbose_name="市町村",max_length=100)
    address     = models.CharField(verbose_name="番地・部屋番号",max_length=100)

    #TODO:ここの2つは1対多で繋がっていると後から値が変わった時、問題が起こる。
    #例えば、顧客がカートに入れて、決済した時100円だったとする。管理者が支払い済みかどうかチェックする時、商品の値段が120円になっていると、決済されていないと誤認されかねない。
    #そのため、流動性のある情報(商品の価格、配送先の住所、貼り付ける模様など)は必ず、1対多で紐付かないフィールドに個別に格納しておいたほうがよい。
    
    #この支払い済みの編集処理は、必ず管理サイトにて、管理者が入金を確認した上で、チェックを入れる。
    #こちらも同様にsaveメソッドが働いて、配送モデルに複写される。


#注文されたときのパターンレシピ
class OrderPatternRecipe(models.Model):

    #対象の注文
    target      = models.ForeignKey(Order,verbose_name="注文",on_delete=models.CASCADE)

    color_regex = RegexValidator(regex=r'^#(?:[0-9a-fA-F]{6})$')
    color       = models.CharField(verbose_name="色",max_length=7,validators=[color_regex],default="#000000")
    number      = models.IntegerField(verbose_name="本数",default=1,validators=[MinValueValidator(1),MaxValueValidator(10)])

    #ここにコントローラの順番を記録するため、dtを記録する
    dt          = models.DateTimeField(verbose_name="投稿日時",default=timezone.now)
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="投稿者", on_delete=models.CASCADE, null=True,blank=True)


#決済は終わっていて、商品を作って配送し始める段階のモデル
class Delivery(models.Model):

    dt      = models.DateTimeField(verbose_name="追加日時",default=timezone.now)
    order   = models.ForeignKey(Order, verbose_name="配送対象の注文", on_delete=models.CASCADE)
    delivered   = models.BooleanField(verbose_name="配送済み",default=False)

"""
