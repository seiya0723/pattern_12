from django.contrib import admin
from django.utils.html import format_html

from .models import Pattern,PatternRecipe,Contact,Product,Cart,Order,OrderDetail,OrderDetailPattern

class PatternAdmin(admin.ModelAdmin):

    list_display    = [ "title","dt","size","format_img","user" ]

    def format_img(self,obj):
        if obj.img:
            return format_html('<img src="{}" alt="画像" style="width:15rem">', obj.img.url)

    format_img.short_description    = Pattern.img.field.verbose_name
    format_img.empty_value_display  = "画像なし"



class PatternRecipeAdmin(admin.ModelAdmin):

    #一覧に表示させる内容
    list_display    = [ "target","color","number","dt","user" ]

class ContactAdmin(admin.ModelAdmin):

    #一覧に表示させる内容
    list_display    = [ "dt","subject","content","ip","user" ]


class ProductAdmin(admin.ModelAdmin):
    pass

class CartAdmin(admin.ModelAdmin):
    pass

class OrderAdmin(admin.ModelAdmin):
    pass

class OrderDetailAdmin(admin.ModelAdmin):
    pass

class OrderDetailPatternAdmin(admin.ModelAdmin):
    pass


admin.site.register(Pattern,PatternAdmin)
admin.site.register(PatternRecipe,PatternRecipeAdmin)
admin.site.register(Contact,ContactAdmin)

admin.site.register(Product,ProductAdmin)
admin.site.register(Cart,CartAdmin)
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderDetail,OrderDetailAdmin)
admin.site.register(OrderDetailPattern,OrderDetailPatternAdmin)

