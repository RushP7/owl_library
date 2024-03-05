from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from datetime import timedelta
from ..models import Book, User

class BookListAPITestCase(APITestCase):
    def setUp(self):
        #available and not borrowed
        Book.objects.create(title="Book One", author="J.K. Rowling", owl_id="ID1", book_type="PB", available=True, last_borrowed=timezone.now() - timedelta(days=90))
        # not available and borrowed less than 14 days ago
        Book.objects.create(title="Book Two", author="Author Two", owl_id="ID2", book_type="HC", available=False, last_borrowed=timezone.now() - timedelta(days=1))
        #available and not borrowed
        Book.objects.create(title="Book Three", author="Author Three", owl_id="ID3", book_type="HM", available=True)
        # not available but borrowed more than 14 days ago
        Book.objects.create(title="Book Four", author="J.K. Rowling", owl_id="ID4", book_type="PB", available=False, last_borrowed=timezone.now() - timedelta(days=90))

    def test_get_all_books(self):
        response = self.client.get(reverse('book-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_filter_by_author(self):
        response = self.client.get(reverse('book-list'), {'author': 'J.K. Rowling'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(book['author'] == 'J.K. Rowling' for book in response.data))
        self.assertEqual(len(response.data), 2)

    def test_filter_by_availability(self):
        # Test for available books
        response = self.client.get(reverse('book-list'), {'available': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(book['available'] for book in response.data if book))
        self.assertEqual(len(response.data), 3)
        # Test for unavailable books
        response = self.client.get(reverse('book-list'), {'available': 'false'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(not book['available'] for book in response.data if book))
        self.assertEqual(len(response.data), 1)
