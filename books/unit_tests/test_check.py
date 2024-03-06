from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from datetime import timedelta
from ..models import Book, User, BorrowHistory

class BookAvailabilityAPITestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create(user_id="user123")
        self.user2 = User.objects.create(user_id="user456")
        
        
        # Book available for borrowing
        self.book_available = Book.objects.create(
            title="Available Book",
            author="Author Three",
            owl_id="AV1",
            book_type="HM",
            available=True
        )

    def test_immediately_borrowable_book(self):
        # Assuming an endpoint that updates/checks something about borrowing availability
        data = {"user_id": self.user1.user_id, "owl_id": self.book_available.owl_id}
        response = self.client.get(reverse('book-availability'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)