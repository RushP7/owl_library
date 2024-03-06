from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from datetime import timedelta
from ..models import Book, User, BorrowHistory

class BorrowBookAPITestCase(APITestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create(user_id="user123")
        self.user2 = User.objects.create(user_id="user456")

        # Create books with different scenarios
        self.book_available = Book.objects.create(title="Available Book", author="Author One", owl_id="ID1", book_type="PB", available=True)
        self.book_recently_borrowed = Book.objects.create(title="Recently Borrowed", author="Author Two", owl_id="ID2", book_type="HC", available=False, last_borrowed=timezone.now() - timedelta(days=1))
        self.book_unavaiilable_gte_14 = Book.objects.create(title="Unavailable but older than 14 days Book", author="Author Three", owl_id="ID3", book_type="HM", available=False, last_borrowed=timezone.now() - timedelta(days=15))
        self.book_special_author = Book.objects.create(title="Special Author Book", author="J.K. Rowling", owl_id="ID4", book_type="HM", available=True, last_borrowed=timezone.now() - timedelta(days=10))
        self.book_special_author_under_6months = Book.objects.create(title="Recently Borrowed Special Author", author="J Author", owl_id="ID5", book_type="PB", available=True, last_borrowed=timezone.now() - timedelta(days=10))
        self.book_unborrwed_special_author_under_6months = Book.objects.create(title="Recently Borrowed Special Author (not borrowed)", author="J Author", owl_id="ID6", book_type="PB", available=True, last_borrowed=timezone.now() - timedelta(days=10))
        # self.book_special_author_recent = Book.objects.create(title="Recently Borrowed Special Author", author="J.Author", owl_id="ID4", book_type="PB", available=True, last_borrowed=timezone.now() - timedelta(days=10))


        # borrow history for book by special author borrowed less than 6 months ago
        BorrowHistory.objects.create(user=self.user1, book=self.book_special_author_under_6months, borrow_date=timezone.now() - timedelta(days=160))
        # borrow history for book by special author borrowed more than 6 months ago
        BorrowHistory.objects.create(user=self.user2, book=self.book_special_author, borrow_date=timezone.now() - timedelta(days=190))

    
    """BASIC TESTS"""

    def test_borrow_available_book(self):
        data = {"user_id": self.user1.user_id, "owl_id": self.book_available.owl_id}
        response = self.client.patch(reverse('borrow-book'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book_available.refresh_from_db()
        self.assertFalse(self.book_available.available)
        self.assertTrue(self.book_available.last_borrowed)

    def test_borrow_nonexistent_user(self):
        data = {"user_id": "NonexistentID", "owl_id": self.book_available.owl_id}
        response = self.client.patch(reverse('borrow-book'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_borrow_nonexistent_book(self):
        data = {"user_id": self.user1.user_id, "owl_id": "NonexistentID"}
        response = self.client.patch(reverse('borrow-book'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



    """TESTS BASED ON BORROW AND RETURN RULES"""
    
    def test_borrow_recently_borrowed_book(self):
        data = {"user_id": self.user1.user_id, "owl_id": self.book_recently_borrowed.owl_id}
        response = self.client.patch(reverse('borrow-book'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # borrow book that is unavailable and borrowed more than 14 days ago
    def test_borrow_unavailable_gte_14_book(self):
        data = {"user_id": self.user1.user_id, "owl_id": self.book_unavaiilable_gte_14.owl_id}
        response = self.client.patch(reverse('borrow-book'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book_unavaiilable_gte_14.refresh_from_db()
        self.assertFalse(self.book_unavaiilable_gte_14.available)

    # borrow book by special author that has never been borrowed
    def test_borrow_special_author_book(self):
        data = {"user_id": self.user1.user_id, "owl_id": self.book_special_author.owl_id}
        response = self.client.patch(reverse('borrow-book'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book_special_author.refresh_from_db()
        self.assertFalse(self.book_special_author.available)

    # user1 try to borrow book by special author that user1 borrowed less than 6 months ago
    def test_borrow_special_author_under_6months_book(self):
        data = {"user_id": self.user1.user_id, "owl_id": self.book_special_author_under_6months.owl_id}
        response = self.client.patch(reverse('borrow-book'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # user1 try to borrow book by special author that user1 has not borrowed but has borrwed another book by special author less than 6 months ago
    def test_borrow_special_author_under_6months_book_not_borrowed(self):
        data = {"user_id": self.user1.user_id, "owl_id": self.book_unborrwed_special_author_under_6months.owl_id}
        response = self.client.patch(reverse('borrow-book'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # user2 try to borrow book by special author that user2 borrowed more than 6 months ago 
    def test_borrow_special_author_book_borrowed_more_than_6months_ago(self):
        data = {"user_id": self.user2.user_id, "owl_id": self.book_special_author.owl_id}
        response = self.client.patch(reverse('borrow-book'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book_special_author.refresh_from_db()
        self.assertFalse(self.book_special_author.available)