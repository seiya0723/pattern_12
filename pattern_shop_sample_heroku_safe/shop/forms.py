from django import forms 
from .models import Pattern,PatternRecipe,Contact,Product,Cart #,Order,OrderDetail,OrderDetailPattern

class PatternForm(forms.ModelForm):

    class Meta:
        model   = Pattern
        fields  = [ "title","img","size","user" ]

class PatternRecipeForm(forms.ModelForm):

    class Meta:
        model   = PatternRecipe
        fields  = [ "target","color","number","user" ]

class ContactForm(forms.ModelForm):
    class Meta:
        model   = Contact
        fields  = [ "subject","content","ip","user","email" ]


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        print("フォームクラスの後処理")

class CartForm(forms.ModelForm):
    class Meta:
        model   = Cart
        fields  = [ "user","product","pattern","amount" ]



#ユーザーモデルを編集するフォームを作る
from users.models import CustomUser

#ここでカスタムユーザーモデルを継承したフォームクラスを作る。下記は姓名を受け付け、それだけを編集する。フォームクラス
class CustomUserForm(forms.ModelForm):
    class Meta:
        model   = CustomUser
        fields  = [ "first_name","last_name" ]
    
#views.pyにて
"""
from users.models import CustomUser

user    = CustomUser.objects.filter(id=request.user.id)

form    = CustomUserForm(request.POST, instance=user)

if form.is_valid():
    form.save()
"""



"""

#顧客がカートに追加した時に使うフォーム
class CartAddForm(forms.ModelForm):
    class Meta:
        model   = Cart
        fields  = [ "user","product","pattern","amount" ]

#顧客が注文した時に格納するフォーム(注文済みにチェックを入れる。)
class CartOrderForm(forms.ModelForm):
    class Meta:
        model   = Cart
        fields  = [ "user","pattern","ordered" ]

    #注文した時、注文モデルへ複写する。
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

"""
    
