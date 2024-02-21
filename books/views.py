from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Book
from .serializers import BookSerializer

class BookList(generics.ListAPIView):
    """
    API endpoint to retrieve a list of all books in the library.
    """

    queryset = Book.objects.all()
    serializer_class = BookSerializer

class BookListByAuthor(generics.ListAPIView):
    """
    API endpoint to retrieve a list of all books by a specific author.
    """

    serializer_class = BookSerializer

    def get_queryset(self):
        """
        Returns a queryset of all books by a specific author.
        """
        author = self.kwargs['author']
        return Book.objects.filter(author=author)
    


class BorrowBookAPIView(generics.UpdateAPIView):
    """
    API endpoint to borrow a book.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def update(self, request, *args, **kwargs):
        # Get the book based on owl_id or title and author combination
        owl_id = request.data.get('owl_id')
        title = request.data.get('title')
        author = request.data.get('author')

        if owl_id:
            try:
                book = Book.objects.get(owl_id=owl_id)
            except Book.DoesNotExist:
                return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        elif title and author:
            try:
                book = Book.objects.get(title=title, author=author)
            except Book.DoesNotExist:
                return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Please provide owl_id or title and author combination"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the book is available
        if not book.available:
            return Response({"error": "This book is already borrowed"}, status=status.HTTP_400_BAD_REQUEST)

        # Update book availability and last borrowed date
        book.available = False
        book.last_borrowed_date = timezone.now()
        book.save()

        return Response({"message": "Book borrowed successfully"}, status=status.HTTP_200_OK)
