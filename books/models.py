from django.db import models

class Book(models.Model):
    """
    Represents a book in the library.

    Attributes:
        title (str): The title of the book.
        author (str): The author of the book.
        owl_id (str): The unique ID of the book.
        book_type (str): The type of the book (e.g., 'PB' for Paperback).
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

    def __str__(self):
        return str(self.title)
