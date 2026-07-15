from django.test import TestCase
from django.contrib.auth import get_user_model

from links.models import Link
from links.services import create_short_link
from links.utils import generate_short_code

User = get_user_model()


class ShortCodeCollisionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')

    def test_generated_short_codes_are_unique(self):
        links = []
        for i in range(1000):
            link = create_short_link(
                owner=self.user,
                original_url=f'https://example.com/{i}',
            )
            links.append(link.short_code)

        self.assertEqual(len(links), len(set(links)))