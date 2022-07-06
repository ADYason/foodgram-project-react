from django.db import models

from users.models import User


class Tags(models.Model):
    name = models.CharField(
        max_length=200,
    )
    color = models.CharField(
        max_length=7,
    )
    slug = models.SlugField(
        max_length=7,
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'
        ordering = ['name']


class Ingredients(models.Model):
    name = models.CharField(
        max_length=200,
    )
    measurement_unit = models.CharField(
        max_length=200,
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(
        max_length=200,
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        related_name='ingredient_recipe'
    )
    tags = models.ManyToManyField(
        Tags,
        related_name='tag_recipe'
    )
    image = models.ImageField(
        'Картинка',
        blank=True
    )
    text = models.TextField()
    cooking_time = models.IntegerField()

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ['id']

    def __str__(self):
        return self.name


class Favorites(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Users favorite',
        on_delete=models.CASCADE,
        related_name='user_favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Users favorite',
        on_delete=models.SET_NULL,
        related_name='recipe_favorites',
        null=True
    )

    class Meta:
        verbose_name = 'изранное'
        ordering = ['id']

    def __str__(self):
        return self.user


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Users shopping cart',
        on_delete=models.CASCADE,
        related_name='user_shoppingcart'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Users shopping cart',
        on_delete=models.SET_NULL,
        null=True,
        related_name='recipe_shoppingcart'
    )

    class Meta:
        verbose_name = 'корзина'
        ordering = ['id']

    def __str__(self):
        return self.user


class RecipeTags(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.SET_NULL,
        null=True,
    )
    tag = models.ForeignKey(
        Tags,
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        verbose_name = 'recipes-tags'
        ordering = ['id']

    def __str__(self):
        return self.recipe


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recipe_to_ingredient'
    )
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.SET_NULL,
        null=True,
        related_name='needamount'
    )
    amount = models.IntegerField()

    class Meta:
        verbose_name = 'recipes-ingredients'
        ordering = ['id']

    def __str__(self):
        return self.recipe
