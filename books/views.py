from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
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
    

class BorrowBook(generics.UpdateAPIView):
    """
    API endpoint to borrow a book.

    Inherits from UpdateAPIView provided by Django REST Framework.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def update(self, request, *args, **kwargs):
        book = self.get_object()

        # Check if the book is available
        if not book.available:
            return Response({"error": "This book is already borrowed"}, status=status.HTTP_400_BAD_REQUEST)

        # Update book availability and last borrowed date  
        book.available = False
        book.last_borrowed_date = timezone.now()
        book.save()

        return Response({"message": "Book borrowed successfully"}, status=status.HTTP_200_OK)
