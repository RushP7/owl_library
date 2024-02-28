from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from django.utils import timezone
from rest_framework import generics, status
from .models import Book
from .serializers import BookSerializer
from .models import BorrowHistory



class BookList(generics.ListAPIView):
    """
    API endpoint to retrieve a list of all books, filtered by author or availability.
    """
    serializer_class = BookSerializer

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('author', openapi.IN_QUERY, description="Filter by author", type=openapi.TYPE_STRING),
        openapi.Parameter('available', openapi.IN_QUERY, description="Filter by availability", type=openapi.TYPE_BOOLEAN)
    ])
    def get_queryset(self):
        """
        Optionally restricts the returned books to a given author,
        and filters on availability if requested.
        """
        queryset = Book.objects.all()
        author = self.request.query_params.get('author', None)
        available = self.request.query_params.get('available', None)

        if author is not None:
            queryset = queryset.filter(author__icontains=author)

        if available is not None:
            available = available.lower() in ['true', '1', 't']
            queryset = queryset.filter(available=available)

        return queryset



class BorrowBook(generics.UpdateAPIView):
    """
    API endpoint to borrow a book.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    # allow only patch method
    http_method_names = ['patch']

    def update(self, request, *args, **kwargs):
        # Get the book based on owl_id or title and author combination
        owl_id = request.data.get('owl_id')
        title = request.data.get('title')
        author = request.data.get('author')
        user = request.user

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
        
        recent_borrow = BorrowHistory.objects.filter(
            book=book, 
            user=user, 
            borrow_date__gte=timezone.now() - timezone.timedelta(days=90)
        ).exists()

        if recent_borrow:
            return Response({"error": "You have already borrowed this book in the last 90 days"}, status=status.HTTP_400_BAD_REQUEST)

        # Update book availability and last borrowed date
        book.available = False
        book.last_borrowed = timezone.now()
        book.save()

        return Response({"message": "Book borrowed successfully"}, status=status.HTTP_200_OK)
