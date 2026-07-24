from django.test import TestCase
from django.utils import timezone

from django.contrib.auth import get_user_model

from links.models import Link
from analytics.models import Click
from analytics.tasks import record_click_task

User = get_user_model()


class RecordClickTaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="taskuser",
            email="task@example.com",
            password="pw123",
        )
        self.link = Link.objects.create(
            owner=self.user,
            original_url="https://www.example.com",
            short_code="task1",
            is_active=True,
        )

    def test_record_click_creates_click_and_increments_count(self):
        """Calling record_click_task directly should create a Click and bump click_count."""
        initial_count = self.link.click_count

        record_click_task(
            link_id=self.link.id,
            ip="8.8.8.8",
            raw_user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        )

        clicks = Click.objects.filter(url=self.link)
        self.assertEqual(clicks.count(), 1)

        click = clicks.first()
        self.assertEqual(click.ip_address, "8.8.8.8")
        self.assertIsNotNone(click.country)
        self.assertIsNotNone(click.city)
        self.assertIsNotNone(click.device_type)
        self.assertIsNotNone(click.browser)

        self.link.refresh_from_db()
        self.assertEqual(self.link.click_count, initial_count + 1)