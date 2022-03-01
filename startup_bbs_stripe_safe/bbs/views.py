from django.shortcuts import render,redirect

from django.views import View
from .models import Topic,Order
from .forms import OrderSetForm,OrderPaidForm

import stripe
from django.conf import settings


from django.urls import reverse_lazy

#移行後バージョン
class IndexView(View):

    def get(self, request, *args, **kwargs):
        context = {}

        #ここはGETメソッドで実行する内容？

        #ここでStripeのセッションを作る、セッションは作られているため、このあと決済処理を実装させる。
        # https://dashboard.stripe.com/account から企業名を入れていないとエラーが出る点に注意
        # 自分の名前をローマ字で入れておく。

        #セッションを開始するため、秘密鍵をセットする。
        stripe.api_key = settings.STRIPE_API_KEY

        session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                
                #顧客が購入する商品(実践ではここにカートに入れた商品を格納)
                line_items=[{
                    'price_data': {
                        'currency': 'jpy',
                        'product_data': {
                            'name': 'T-shirt',
                            },
                        'unit_amount': 2000,
                        },

                    'quantity': 1,
                    }],
                
                mode='payment',

                #TODO:reverse_lazyと.build_absolute_uri()でリダイレクト先を指定
                #https://stackoverflow.com/questions/2345708/how-can-i-get-the-full-absolute-url-with-domain-in-django

                #決済成功した後のリダイレクト先
                #success_url='http://127.0.0.1:8000/checkout/',
                success_url=request.build_absolute_uri(reverse_lazy("bbs:checkout")) + "?session_id={CHECKOUT_SESSION_ID}",

                #成功時のリダイレクト先のパラメータとしてセッションIDを含むように指定して、成功時のビューではそのセッションIDに紐づく注文が本当に決済完了しているかStripeに問い合わせてチェックする。
                #参照:https://stripe.com/docs/payments/checkout/custom-success-page

                #決済キャンセルしたときのリダイレクト先
                #cancel_url='http://127.0.0.1:8000/',
                cancel_url=request.build_absolute_uri(reverse_lazy("bbs:index")),
                )


        print(request.build_absolute_uri(reverse_lazy("bbs:checkout")))

        #print(session)

        context["session"]      = session
        
        #この公開鍵を使ってテンプレート上のJavaScriptにセットする。顧客が入力する情報を暗号化させるための物
        context["public_key"]   = settings.STRIPE_PUBLISHABLE_KEY

        #このStripeのセッションIDをテンプレート上のJavaScriptにセットする。上記のビューで作ったセッションを顧客に渡して決済させるための物
        context["session_id"]   = session["id"]

        #ここでOrderモデルへsession["id"]を記録しておく。
        data    = { "user":request.user.id,
                    "session_id":session["id"],
                    }

        form    = OrderSetForm(data)

        if form.is_valid():
            print("注文を保存。")
            form.save()

        print(session["id"])

        return render(request,"bbs/index.html",context)

    def post(self, request, *args, **kwargs):

        posted  = Topic( comment = request.POST["comment"] )
        posted.save()

        return redirect("bbs:index")

index   = IndexView.as_view()


class CheckoutView(View):

    def get(self, request, *args, **kwargs):

        stripe.api_key = settings.STRIPE_API_KEY

        #ここでセッションIDを元に顧客情報を参照。決済しているかをチェックする。存在しないセッションIDを入力した場合、ここで例外エラーが出る。(出来ればtry文でサーバーが落ちないようにしたほうが良いかと)
        if "session_id" not in request.GET:
            return redirect("bbs:index")

        #ここでセッションの存在チェック(存在しないセッションIDを適当に入力した場合、ここでエラーが出る。)
        try:           
            session     = stripe.checkout.Session.retrieve(request.GET["session_id"])
            print(session)
        except:
            return redirect("bbs:index")

        try:
            #ここで決済完了かどうかチェックできる。(何らかの方法でセッションIDを取得し、URLに直入力した場合、ここでエラーが出る。)
            customer    = stripe.Customer.retrieve(session.customer)
            print(customer)
        except:
            return redirect("bbs:index")


        #ここでリクエストしてきたユーザーが、決済したユーザー(indexで記録した注文のユーザー)と一致するかどうかチェックした上で、決済完了した注文内容を表示する。

        order   = Order.objects.filter(session_id=request.GET["session_id"], user=request.user.id).first()

        import datetime
        data    = {"paid": datetime.datetime.now() }
        form    = OrderPaidForm(data,instance=order)

        if not form.is_valid():
            print("NG")
            return redirect("bbs:index")


        #支払い日時が指定されていないときだけ指定する。(この条件分岐がないと、既に支払いした人がもう一度ページにアクセスすることで支払い日時が変わってしまう。)
        if not order.paid:
            print("このユーザーの決済は完了しました。")
            form.save()

            #TODO:ここでカート内の削除も同時にやっておく。

        print("決済完了")
        #TODO:出来ればこのページは注文完了のレンダリングを
        return redirect("bbs:index")


checkout    = CheckoutView.as_view()


"""
#レガシーバージョン

class IndexView(View):

    def get(self, request, *args, **kwargs):
        context = {}

        #顧客がチェックアウトセッションを作るようにHTML側で仕立てる
        context["topics"]   = Topic.objects.all()

        context['data_key'] = settings.STRIPE_PUBLISHABLE_KEY
        context['data_amount']      = 30000 
        context['data_name']        = "テスト決済"
        context['data_description'] = "ご注文を決済します"
        context['data_currency'] =  'JPY'


        return render(request,"bbs/index.html",context)

    def post(self, request, *args, **kwargs):

        posted  = Topic( comment = request.POST["comment"] )
        posted.save()

        return redirect("bbs:index")

index   = IndexView.as_view()


class CheckoutView(View):

    def post(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_API_KEY
        token = request.POST['stripeToken']

        #決済処理
        try:
            #トークンを元に決済を実行する
            charge = stripe.Charge.create(
                amount= 30000,
                currency='JPY',
                source=token,
                description='テスト決済完了',
            )
            context = { "charge":charge }

            print("決済完了")

        except stripe.error.CardError as e:

            #決済が失敗した場合の処理
            print("失敗しました。")

        return redirect("bbs:index")


checkout    = CheckoutView.as_view()
"""
