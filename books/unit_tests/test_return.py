from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from datetime import timedelta
from ..models import Book, User, BorrowHistory

class ReturnBookAPITestCase(APITestCase):
    def setUp(self):
        current_time = timezone.now()

        self.user1 = User.objects.create(user_id="user123")
        self.user2= User.objects.create(user_id="user456")
        
        self.book = Book.objects.create(title="Borrowed Book", author="Author One", owl_id="ID1", book_type="PB", available=False, last_borrowed=current_time - timedelta(days=7))
        self.available_book = Book.objects.create(title="Available Book", author="Author Two", owl_id="ID2", book_type="HC", available=True, last_borrowed=current_time - timedelta(days=15))
    

        BorrowHistory.objects.create(user=self.user1, book=self.book, borrow_date=current_time - timedelta(days=7), returned=False)
        BorrowHistory.objects.create(user=self.user2, book=self.available_book, borrow_date=current_time - timedelta(days=15), returned=False)

       

    def test_return_borrowed_book(self):
        data = {"user_id": self.user1.user_id, "owl_id": self.book.owl_id}
        response = self.client.patch(reverse('return-book'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertTrue(self.book.available)
        borrow_entry = BorrowHistory.objects.get(user=self.user1, book=self.book)
        self.assertTrue(borrow_entry.returned)

    def test_return_already_available_book(self):
        data = {"user_id": self.user1.user_id, "owl_id": self.available_book.owl_id}
        response = self.client.patch(reverse('return-book'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_return_book_not_borrowed_by_user(self):
        data = {"user_id": self.user2.user_id, "owl_id": self.book.owl_id}
        response = self.client.patch(reverse('return-book'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self

    def test_return_nonexistent_book(self):
        data = {"user_id": self.user1.user_id, "owl_id": "NonexistentID"}
        response = self.client.patch(reverse('return-book'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_return_book_with_nonexistent_user(self):
        data = {"user_id": "nonexistentUser", "owl_id": self.book.owl_id}
        response = self.client.patch(reverse('return-book'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # return book that was already automatically returned after 14 days
    def test_return_book_automatically_returned(self):
        data = {"user_id": self.user2.user_id, "owl_id": self.available_book.owl_id}
        response = self.client.patch(reverse('return-book'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        borrow_entry = BorrowHistory.objects.get(user=self.user2, book=self.available_book)
        self.assertTrue(borrow_entry.returned)
       
    