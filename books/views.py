from rest_framework import generics
from .models import Book
from .serializers import BookSerializer

class BookList(generics.ListAPIView):
    """
    API endpoint to retrieve a list of all books in the library.

    Inherits from ListAPIView provided by Django REST Framework.
    """

    queryset = Book.objects.all()
    serializer_class = BookSerializer

class BookListByAuthor(generics.ListAPIView):
    """
    API endpoint to retrieve a list of all books by a specific author.

    Inherits from ListAPIView provided by Django REST Framework.
    """

    serializer_class = BookSerializer

    def get_queryset(self):
        """
        Returns a queryset of all books by a specific author.
        """
        author = self.kwargs['author']
        return Book.objects.filter(author=author)
