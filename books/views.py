from rest_framework import generics
from .models import Book
from .serializers import BookSerializer

class BookListAPIView(generics.ListAPIView):
    """
    API endpoint to retrieve a list of all books in the library.

    Inherits from ListAPIView provided by Django REST Framework.
    """

    queryset = Book.objects.all()
    serializer_class = BookSerializer
