from django.contrib import admin

from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'name',
        'ingredients',
        'tags',
        'image',
        'text',
        'cooking_time',
        'favorites_count'
    )
    search_fields = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'

    def favorites_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    def ingredients(self, obj):
        return "\n".join([a for a in obj.values(
            'recipe_to_ingredient__ingredient__name'
        )])

    def tags(self, obj):
        return "\n".join([a for a in obj.values(
            'recipe_to_tag__tag__name'
        )])


class TagsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug'
    )
    empty_value_display = '-пусто-'


class IngredientsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = ('name', )
    empty_value_display = '-пусто-'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe'
    )
    empty_value_display = '-пусто-'


class FavoritesAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe'
    )
    empty_value_display = '-пусто-'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagsAdmin)
admin.site.register(Ingredient, IngredientsAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favorite, FavoritesAdmin)
