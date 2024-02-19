from django.db import models

class Book(models.Model):
    TYPE_CHOICES = [
        ('PB', 'Paperback'),
        ('HC', 'Hardcover'),
        ('HM', 'Handmade'),
    ]
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    owl_id = models.CharField(max_length=255, unique=True)
    book_type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    def __str__(self):
        return str(self.title)
