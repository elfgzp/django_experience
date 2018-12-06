from django.test import TestCase
from make_good_use_of_migrations import models


class BookTestCase(TestCase):
    def setUp(self):
        pass

    def test_book_data_init(self):
        queryset = models.Book.objects.all()
        self.assertEqual(queryset.count(), 3)
        for each in queryset:
            self.assertEqual(each.remark, None)
