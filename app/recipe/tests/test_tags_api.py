from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe
from recipe.serializers import TagSerializer
from decimal import Decimal


TAGS_URL = reverse("recipe:tag-list")


def detail_url(tag_id):
    return reverse("recipe:tag-detail", args=[tag_id])


def create_user(email="test@asd.om", password="some123"):
    return get_user_model().objects.create_user(email, password)


class TagsAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()

        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        Tag.objects.create(user=self.user, name="abc")
        Tag.objects.create(user=self.user, name="def")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_limited_to_user(self):
        user2 = create_user("email@user2.com", "asom124")

        Tag.objects.create(user=user2, name="fruity")
        tag = Tag.objects.create(user=self.user, name="com asd")

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], tag.name)
        self.assertEqual(res.data[0]["id"], tag.id)

    def test_update_tag(self):
        tag = Tag.objects.create(user=self.user, name="asd")

        payload = {"name": "dessert"}

        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()

        self.assertEqual(tag.name, payload["name"])

    def test_delete_tag(self):
        tag = Tag.objects.create(user=self.user, name="breakfast")

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(user=self.user).exists())

    def test_filter_tags_assigned_to_recipes(self):
        tag1 = Tag.objects.create(user=self.user, name="breakfast")
        tag2 = Tag.objects.create(user=self.user, name="lunch")

        recipe = Recipe.objects.create(
            title="title 1", time_minutes=4, price=Decimal("12.2"), user=self.user
        )

        recipe.tags.add(tag1)
        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_uniq(self):
        tag = Tag.objects.create(user=self.user, name="breakfast")

        Tag.objects.create(user=self.user, name="lunch")

        rec1 = Recipe.objects.create(
            title="title 1", time_minutes=4, price=Decimal("12.2"), user=self.user
        )
        rec2 = Recipe.objects.create(
            title="title 2", time_minutes=14, price=Decimal("12.2"), user=self.user
        )

        rec1.tags.add(tag)
        rec2.tags.add(tag)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        self.assertEqual(len(res.data), 1)
