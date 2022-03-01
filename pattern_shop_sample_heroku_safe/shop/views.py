from django.shortcuts import render,redirect
from django.contrib.auth.mixins import LoginRequiredMixin

#DjangoRESTFrameworkを使うため、django.viewsではなくrest_frameworkのviews.APIViewを継承してクラスを作る。これで、PUT,DELETE,PATCHメソッドを受け付ける。
from django.views import View
from rest_framework import views

from django.http.response import JsonResponse

from .models import Pattern,PatternRecipe
from .forms import PatternForm,PatternRecipeForm,ContactForm


#OR検索をするためのクエリビルダを使う
#参照:https://noauto-nolife.com/post/django-or-and-search/
from django.db.models import Q


#TODO:settings.pyに書いてあるDEFAULT_FROM_EMAILを参照するため、settings.pyをimport
from django.conf import settings
from django.core.mail import send_mail


#Djangoメッセージフレームワーク
from django.contrib import messages


class IndexView(views.APIView):

    def get(self, request, *args, **kwargs):

        #TODO:ここでメール送信をする。
        """
        subject = "ここに件名を入れる"
        message = "ここに本文を入れる"

        #運営からのメールであれば、このようにsettings.pyに書いてあるDEFAULT_FROM_EMAILを読み取り、セットする。
        #ユーザー間の送信であれば、ユーザーモデルからメールアドレスを参照する。
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [ "hoge@gmail.com" ]

        send_mail(subject, message, from_email, recipient_list)
        """

        patterns    = Pattern.objects.all()
        context     = { "patterns":patterns }

        return render(request,"shop/index.html",context)

index   = IndexView.as_view()


class PatternView(views.APIView):

    def get(self, request, *args, **kwargs):

        #ここはOR検索をするためクエリビルダを使う、|でOR検索、&でAND検索
        query       = Q(user=request.user.id) | Q(user=None)
        patterns    = Pattern.objects.filter(query).order_by("-dt")

        context     = { "patterns":patterns }

        return render(request,"shop/pattern.html",context)

pattern = PatternView.as_view()


#模様の保存、削除、編集を受け付ける。
class PatternModView(LoginRequiredMixin,views.APIView):

    def get(self, request, *args, **kwargs):


        #TODO:ここでメール認証を済ませていない場合は、認証ページへ行く
        from allauth.account.admin import EmailAddress

        emails   = EmailAddress.objects.all()

        print(emails)

        #この時、account_emailにアクセスしてないとNoneが返ってくる。
        email   = EmailAddress.objects.filter(user=request.user.id, email=request.user.email).first()

        if not email:
            print("メール認証ページへリダイレクト")
            return redirect("account_email")

        if email.verified:
            print("メール認証済み")
        else:
            print("メール未認証")
            print("メール認証ページへリダイレクト")
            return redirect("account_email")




        context     = {}

        #kwargsにpkがある場合は編集。ない場合は新規作成
        if "pk" in kwargs:
            #ここは自分が投稿したデータだけ、存在しない場合はリダイレクト
            context["pattern"] = Pattern.objects.filter(id=kwargs["pk"]).first()
            context["recipes"] = PatternRecipe.objects.filter(target=kwargs["pk"]).order_by("id")

        return render(request,"shop/pattern_mod.html",context)


    def post(self, request, *args, **kwargs):
        #模様の保存処理
        json    = { "error":True }

        #ユーザーIDの格納
        copied          = request.POST.copy()
        copied["user"]  = request.user.id

        #TODO:ここで無料ユーザーの場合は指定した個数制限(20個まで)


        #ここでもし管理者が投稿しようとした時、サンプルの模様として扱うため、userにはNoneを入れる(ifで分岐)

        print(copied)
        print(request.POST)


        form    = PatternForm(copied, request.FILES)
       
        #アーリーリターン(early return)
        if not form.is_valid():
            print("バリデーションNG")
            return JsonResponse(json)

        print("バリデーションOK")


        #保存するとき、保存したモデルオブジェクトのIDを入手。レシピ登録時に使う。
        pattern = form.save()
        target  = pattern.id

        #まずcolorとnumberがあるかチェック。なければNG
        if "color" not in request.POST or "number" not in request.POST:
            print("バリデーションNG")
            return JsonResponse(json)

        #colorとnumberはそれぞれリスト型なので、.getlist()メソッドを使って呼び出しする。普通にrequest.POST["color"]とすると、得られる値はひとつだけ。
        print(request.POST.getlist("color"))
        print(request.POST.getlist("number"))

        #colorとnumberがリストではない場合はNG
        if type(request.POST.getlist("color")) is not list and type(request.POST.getlist("number")) is not list:
            print("バリデーションNG")
            return JsonResponse(json)

        colors  = request.POST.getlist("color")
        numbers = request.POST.getlist("number")

        for ( color, number ) in zip( colors, numbers ):
            dic             = {}
            dic["color"]    = color
            dic["number"]   = number
            dic["target"]   = target
            dic["user"]     = request.user.id

            print(dic)
            
            form    = PatternRecipeForm(dic)

            if not form.is_valid():
                print("レシピバリデーションNG")
                continue

            print("レシピバリデーションOK")
            form.save()

        json["error"]   = False

        return JsonResponse(json)

    #ここで模様の編集をする
    def put(self, request, *args, **kwargs):
        json    = {"error":True}

        print(kwargs)

        if "pk" not in kwargs:
            return JsonResponse(json)

        pk  = kwargs["pk"]

        #特定のデータを編集する方法
        #https://noauto-nolife.com/post/django-models-delete-and-edit/

        #編集対象を指定
        target  = Pattern.objects.filter(id=pk).first()

        #ここでもしサンプルの模様を編集しようとする場合は、新規作成する

        copied          = request.POST.copy()
        copied["user"]  = request.user.id

        #編集対象を指定した上で、バリデーションをする。(もし編集する際、対象を上書きして編集するのであれば下記を、対象をそのまま残した状態で新規作成(コピー)するのであればinstanceを指定しない。)

        # if "新規作成編集" or "ユーザーがNone(サンプルの模様)":
        #   form    = PatternForm(copied, request.FILES)
        #else
        #   form    = PatternForm(copied, request.FILES, instance=target)


        form    = PatternForm(copied, request.FILES, instance=target)


        #レシピも同様に編集対象を特定してバリデーションをする。
        #編集対象のinstanceを指定するだけでPOSTと同じ処理が続くため、ここは一元化させたほうが良いかも知れない。

        #アーリーリターン(early return)
        if not form.is_valid():
            print("バリデーションNG")
            return JsonResponse(json)

        print("バリデーションOK")

        #保存するとき、保存したモデルオブジェクトのIDを入手。レシピ登録時に使う。
        pattern = form.save()
        target  = pattern.id


        #まずcolorとnumberがあるかチェック。なければNG
        if "color" not in request.POST or "number" not in request.POST:
            print("バリデーションNG")
            return JsonResponse(json)

        #colorとnumberがリストではない場合はNG
        if type(request.POST.getlist("color")) is not list and type(request.POST.getlist("number")) is not list:
            print("バリデーションNG")
            return JsonResponse(json)

        colors  = request.POST.getlist("color")
        numbers = request.POST.getlist("number")


        #レシピ登録で違うのはここだけ。ここでレシピの編集を行う直前、編集前のレシピは全て削除する。
        old_recipes = PatternRecipe.objects.filter(target=pk)
        old_recipes.delete()

        for ( color, number ) in zip( colors, numbers ):
            dic             = {}
            dic["color"]    = color
            dic["number"]   = number
            dic["target"]   = target
            dic["user"]     = request.user.id

            print(dic)
            
            form    = PatternRecipeForm(dic)

            if not form.is_valid():
                print("レシピバリデーションNG")
                continue

            print("レシピバリデーションOK")
            form.save()

        json["error"]   = False
        

        return JsonResponse(json)


    def delete(self, request, *args, **kwargs):

        json    = {"error":True}

        if "pk" not in kwargs:
            return JsonResponse(json)

        #TODO:削除対象の模様を特定して削除する(この時、リクエストを送信したユーザーIDと合致するかチェックする。)

        pattern = Pattern.objects.filter(id=kwargs["pk"],user=request.user.id).first()

        if not pattern:
            return JsonResponse(json)

        #これで削除する
        pattern.delete()
        print("削除")
        json["error"]   = False

        return JsonResponse(json)

pattern_mod = PatternModView.as_view()



#お問い合わせのビュー
class ContactView(views.APIView):

    def get(self, request, *args, **kwargs):
        #requestオブジェクトからIPアドレスとUAを取得してレンダリングさせる。
        #https://noauto-nolife.com/post/django-show-ip-ua-gateway/

        ip_list = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip_list:
            ip  = ip_list.split(',')[0]
        else:
            ip  = request.META.get('REMOTE_ADDR')

        if request.user.is_authenticated:
            email   = request.user.email
        else:
            email   = ""

        context             = {}
        context["ip"]       = ip
        context["email"]    = email

        return render(request,"shop/contact.html",context)

    def post(self, request, *args, **kwargs):

        ip_list = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip_list:
            ip  = ip_list.split(',')[0]
        else:
            ip  = request.META.get('REMOTE_ADDR')

        copied          = request.POST.copy()
        copied["ip"]    = ip

        #ログインしていない人はNoneが、ログインした人はid(UUID)が格納される
        copied["user"]  = request.user.id

        print(request.user.id)
        
        form    = ContactForm(copied)

        if form.is_valid():
            print("バリデーションOK")
            form.save()
            messages.success(request, "お問い合わせ承りました。")

        else:
            print("バリデーションNG")
            messages.error(request, "お問合わせの送信に失敗しました")

        return redirect("shop:contact")

contact = ContactView.as_view()


class SingleView(views.APIView):

    def get(self, request, *args, **kwargs):
        #ここで商品個別を表示
        pass

    def post(self, request, *args, **kwargs):
        #ここでカートに入れる。(Cartに記録する)
        pass


class CartView(views.APIView):
    def get(self, request, *args, **kwargs):
        #ここでカートの中身を表示(Cartを表示)
        pass

    def post(self, request, *args, **kwargs):
        #Cartの内容を元に記録
        #ここで配送先の住所をOrder,OrderDetail,OrderDetailPatternへ記録し、CheckoutViewへリダイレクト
        pass

class CheckoutView(views.APIView):

    #このビューのpkはOrderのid。これを元に支払いする金額、商品などを特定する。
    #ただし、リクエストしたユーザーとオーダーのuserが一致している事を確認するなどの対策必要
    def get(self, request, pk, *args, **kwargs):
        #注文内容と配送先を確認させ、決済をしてもらう。(Stripeを使用しない場合は、ここで振込先の銀行口座等を表示)
        #ここでStripeのセッションを作成。顧客に決済をさせる
        """
        具体的には
        - Stripeの秘密鍵をセットしてセッションを開始

        - items_listにカートの中身を全てセット
        - 成功時のURLをCheckoutSuccessViewへセット
        - 失敗時のURLをCheckoutErrorViewへセット
        """
        #ここでセッションを作った時、後に決済処理を特定するため、OrderモデルへStripeセッションID、payment_intentも記録する。
        pass


class CheckoutSuccessView(views.APIView):
    def get(self, request, pk, *args, **kwargs):
        pass

class CheckoutErrorView(views.APIView):
    def get(self, request, pk, *args, **kwargs):
        pass

