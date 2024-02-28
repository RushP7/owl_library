from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Book(models.Model):
    """
    Represents a book in the library.

    Attributes:
        title (str): The title of the book.
        author (str): The author of the book.
        owl_id (str): The unique ID of the book.
        book_type (str): The type of the book (e.g., 'PB' for Paperback).
        available (bool): Whether the book is available to borrow.
        last_borrowed (datetime): The date and time the book was last borrowed.
    """

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    owl_id = models.CharField(max_length=255, unique=True)
    book_type = models.CharField(max_length=2, choices=[('PB', 'Paperback'), ('HC', 'Hardcover'), ('HM', 'Handmade')])
    available = models.BooleanField(default=True)
    last_borrowed = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

class BorrowHistory(models.Model):
    """
    Represents the history of a book being borrowed.

    Attributes:
        user (User): The user who borrowed the book.
        book (Book): The book that was borrowed.
        borrow_date (datetime): The date and time the book was borrowed.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrow_history')
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    borrow_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title}"
