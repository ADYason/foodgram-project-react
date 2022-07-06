from django.contrib import admin

from .models import Favorites, Ingredients, Recipe, ShoppingCart, Tags


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
        return Favorites.objects.filter(recipe=obj).count()

    def ingredients(self, obj):
        return "\n".join([a.name for a in obj.ingredient_recipe.all()])

    def tags(self, obj):
        return "\n".join([a.name for a in obj.tag_recipe.all()])


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
admin.site.register(Tags, TagsAdmin)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favorites, FavoritesAdmin)
