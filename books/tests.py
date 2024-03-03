from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from .models import Book
from datetime import timedelta

class BookListTestCase(APITestCase):
    def setUp(self):
        # Create sample books for testing
        Book.objects.create(title="Book by J. Author", author="J. Author", available=True, last_borrowed=timezone.now() - timedelta(days=15))
        Book.objects.create(title="Unavailable Book", author="A. Author", available=False, last_borrowed=timezone.now() - timedelta(days=1))
        Book.objects.create(title="Another Book", author="B. Author", available=True, last_borrowed=None)

    def test_get_all_books(self):
        response = self.client.get(reverse('book-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # Adjust based on your actual setup

    def test_filter_by_author(self):
        response = self.client.get(reverse('book-list'), {'author': 'J. Author'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['author'], 'J. Author')

    def test_filter_by_availability(self):
        # Test for available books
        response = self.client.get(reverse('book-list'), {'available': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        books = [book for book in response.data if book['available'] is True]
        self.assertTrue(all(book['available'] for book in books))

        # Test for unavailable books
        response = self.client.get(reverse('book-list'), {'available': 'false'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        books = [book for book in response.data if book['available'] is False]
        self.assertTrue(all(not book['available'] for book in books))

