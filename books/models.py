from django.db import models
from django.utils import timezone
from datetime import timedelta

class User(models.Model):
    """
    Represents a simplified user model with just a unique userid.
    """
    user_id = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return str(self.user_id)

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

    def can_be_borrowed(self, user):
        """Checks if the book can be borrowed by the given user, considering all rules."""
        if not self.is_returned():
            return False

        if self.is_popular_author():
            six_months_ago = timezone.now() - timedelta(days=6*30)  # Approximation of 6 months
            borrowed_books = BorrowHistory.objects.filter(
                user=user, 
                book__author=self.author,
                borrow_date__gte=six_months_ago,
            )
            if borrowed_books.exists():
                return False
        return True

    def is_returned(self):
        """Checks if the book is considered returned after 14 days, also updates the availability."""
        if self.available:
            return True
        # not available
        if self.last_borrowed and timezone.now() > self.last_borrowed + timedelta(days=14):
            self.available = True
            self.last_borrowed = None
            self.save(update_fields=['available', 'last_borrowed'])
            return True
        # less than 14 days
        return False
    

    def is_popular_author(self):
        """Determines if the book is by a popular author (name starts with 'J')."""
        return str(self.author).startswith('J')

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
        return f"{self.user.userid} borrowed {self.book.title}"
