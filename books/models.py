from django.db import models
from django.utils import timezone

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

    TYPE_CHOICES = [
        ('PB', 'Paperback'),
        ('HC', 'Hardcover'),
        ('HM', 'Handmade'),
    ]
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    owl_id = models.CharField(max_length=255, unique=True)
    book_type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    available = models.BooleanField(default=True)
    last_borrowed = models.DateTimeField(null=True)
    
    def __str__(self):
        return str(self.title)