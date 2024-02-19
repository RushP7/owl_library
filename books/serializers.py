from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for the Book model.

    Converts Book model instances into JSON representations.
    """

    class Meta:
        model = Book
        fields = ['title', 'author', 'owl_id', 'book_type']
