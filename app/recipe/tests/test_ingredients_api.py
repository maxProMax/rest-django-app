from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe
from recipe.serializers import IngredientSerializer

from decimal import Decimal


INGREDIENTS_URL = reverse("recipe:ingredient-list")


def detail_url(ingredient_id):
    return reverse("recipe:ingredient-detail", args=[ingredient_id])


def create_user(email="test@asd.om", password="some123"):
    return get_user_model().objects.create_user(email, password)


class PublicIngredientsAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsTagsAPITests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()

        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        Ingredient.objects.create(user=self.user, name="abc")
        Ingredient.objects.create(user=self.user, name="def")

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_limited_to_user(self):
        user2 = create_user("email@user2.com", "asom124")

        Ingredient.objects.create(user=user2, name="salt")
        ingredient = Ingredient.objects.create(user=self.user, name="pepper")

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], ingredient.name)
        self.assertEqual(res.data[0]["id"], ingredient.id)

    def test_update_ingredient(self):
        ingredient = Ingredient.objects.create(user=self.user, name="asd")

        payload = {"name": "coriander"}

        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()

        self.assertEqual(ingredient.name, payload["name"])

    def test_delete_tag(self):
        ingredient = Ingredient.objects.create(user=self.user, name="coriander")

        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(user=self.user).exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        int1 = Ingredient.objects.create(user=self.user, name="apples")
        int2 = Ingredient.objects.create(user=self.user, name="turkey")

        recipe = Recipe.objects.create(
            title="title 1", time_minutes=4, price=Decimal("12.2"), user=self.user
        )

        recipe.ingredients.add(int1)
        res = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})

        s1 = IngredientSerializer(int1)
        s2 = IngredientSerializer(int2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_uniq(self):
        ing = Ingredient.objects.create(user=self.user, name="eggs")

        Ingredient.objects.create(user=self.user, name="abc")

        rec1 = Recipe.objects.create(
            title="title 1", time_minutes=4, price=Decimal("12.2"), user=self.user
        )
        rec2 = Recipe.objects.create(
            title="title 2", time_minutes=14, price=Decimal("12.2"), user=self.user
        )

        rec1.ingredients.add(ing)
        rec2.ingredients.add(ing)

        res = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})

        self.assertEqual(len(res.data), 1)
