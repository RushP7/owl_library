from django.test import TestCase, Client
from django.urls import reverse
from .models import Book
from .serializers import BookSerializer

class BookList(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('book-list')
        self.author1 = 'Author 1'
        self.author2 = 'Author 2'
        self.book1 = Book.objects.create(title='Book 1', author=self.author1, owl_id='123', book_type='PB')
        self.book2 = Book.objects.create(title='Book 2', author=self.author2, owl_id='456', book_type='HC')
        self.book3 = Book.objects.create(title='Book 3', author=self.author1, owl_id='789', book_type='HM')
        self.book4 = Book.objects.create(title='Book 4', author=self.author2, owl_id='101', book_type='HC')

    def test_get_all_books(self):
        """
        Test retrieving a list of all books in the library.

        1. Sends a GET request to the book-list API endpoint and asserts that the response
           status code is 200 (OK)
        2. Compares the serialized data returned in the response with the data obtained 
           from querying all books in the database.
        """

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        self.assertEqual(response.data, serializer.data)
    
    def test_get_books_by_author(self):
        """
        Test retrieving a list of all books by a specific author.

        1. Sends a GET request to the book-list-by-author API endpoint and asserts that the response
           status code is 200 (OK)
        2. Compares the serialized data returned in the response with the data obtained 
           from querying all books by a specific author in the database.
        """

        url = reverse('book-list-by-author', kwargs={'author': self.book1.author})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        books = Book.objects.filter(author=self.author1)
        serializer = BookSerializer(books, many=True)
        self.assertEqual(response.data, serializer.data)