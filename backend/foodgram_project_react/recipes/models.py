from django.db import models
from django.core.validators import MinValueValidator

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Имя'
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=7,
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Имя'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
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
        verbose_name='Имя'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    image = models.ImageField(
        'Картинка',
        blank=True,
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(0), ],
        verbose_name='Время готовки'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['id']

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Юзер',
        on_delete=models.CASCADE,
        related_name='user_favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.SET_NULL,
        related_name='recipe_favorites',
        null=True
    )

    class Meta:
        verbose_name = 'Изранное'
        verbose_name_plural = 'Множество объектов избранного'
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='favorite_unique')
        ]

    def __str__(self):
        return self.user


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Юзер',
        on_delete=models.CASCADE,
        related_name='user_shoppingcart'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.SET_NULL,
        null=True,
        related_name='recipe_shoppingcart'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Множество объектов корзины'
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='shopping_cart_unique')
        ]

    def __str__(self):
        return self.user


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Рецепт'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Теги'
    )

    class Meta:
        verbose_name = 'Рецепт-Теги'
        verbose_name_plural = 'Множество объектов Рецепт-Теги'
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'tag'],
                                    name='recipe_tag_unique')
        ]

    def __str__(self):
        return self.recipe


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recipe_to_ingredient',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.SET_NULL,
        null=True,
        related_name='needamount',
        verbose_name='ингредиент'
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(0), ]
    )

    class Meta:
        verbose_name = 'Рецепт-Ингредиенты'
        verbose_name_plural = 'Множество объектов Рецепт-Ингредиенты'
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(fields=['ingredient', 'recipe'],
                                    name='recipe_ingredient_unique')
        ]

    def __str__(self):
        return self.recipe
