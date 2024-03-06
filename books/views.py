from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from django.utils import timezone
from rest_framework import generics, status
from .models import Book
from .serializers import BookSerializer
from .models import BorrowHistory, User
from django.shortcuts import get_object_or_404
from datetime import timedelta



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
        queryset = Book.objects.all()
        author = self.request.query_params.get('author', None)
        available = self.request.query_params.get('available', None)

        if author is not None:
            queryset = queryset.filter(author__icontains=author)

        if available is not None:
            available = available.lower() in ['true', '1', 't']
            if available:
                queryset = [book for book in queryset if book.is_returned()]
            else:
                queryset = [book for book in queryset if not book.is_returned()]

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
        user_id = request.data.get('user_id')

        # verify userid
        user = get_object_or_404(User, user_id=user_id)

        if owl_id:
            book = get_object_or_404(Book, owl_id=owl_id)
        elif title and author:
            try:
                book = Book.objects.get(title=title, author=author)
            except Book.DoesNotExist:
                return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Please provide owl_id or title and author combination"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the book can be borrowed
        if not book.can_be_borrowed(user):
            return Response({"error": "This book cannot be borrowed based on the borrowing rules."}, status=status.HTTP_400_BAD_REQUEST)
        

        # Update book availability and last borrowed date
        current_date = timezone.now() # var ensures that the time is consistent between the book and borrow history objects
        book.available = False
        book.last_borrowed = current_date
        book.save()

        # Log the borrow history
        BorrowHistory.objects.create(user=user, book=book, borrow_date=current_date)

        return Response({"message": "Book borrowed successfully"}, status=status.HTTP_200_OK)
    


class ReturnBook(generics.UpdateAPIView):
    """
    API endpoint to return a borrowed book.
    """

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    # allow only patch method
    http_method_names = ['patch']

    def update(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        owl_id = request.data.get('owl_id')

        # Validate user
        user = get_object_or_404(User, user_id=user_id)

        # Validate book
        book = get_object_or_404(Book, owl_id=owl_id)
           
        #retrieve users borrow history
        try:
            borrow_history = BorrowHistory.objects.get(user=user, book=book, borrow_date=book.last_borrowed)
        except BorrowHistory.DoesNotExist:
            return Response({"error": "This book is not currently borrowed by this user"}, status=status.HTTP_400_BAD_REQUEST)
        
        if borrow_history.returned:
            return Response({"error": "This book was already returned"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Mark the book as available
        book.available = True
        book.last_borrowed = None
        book.save()

        # Log the return history
        borrow_history.returned = True
        borrow_history.save()

        return Response({"message": "Book returned successfully"}, status=status.HTTP_200_OK)
    
class BookAvailabilityView(generics.ListAPIView):
    """
    API endpoint to check when a user can next borrow a specific book.
    """
    
    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        owl_id = request.query_params.get('owl_id')

        # Validate user and book
        user = get_object_or_404(User, user_id=user_id)
        book = get_object_or_404(Book, owl_id=owl_id)
        
        # If the book can be borrowed now
        if book.can_be_borrowed(user):
            return Response({"message": "Book can be borrowed now."})

        # For books by popular authors that cannot be borrowed now
        if book.is_popular_author():
            last_borrowed = BorrowHistory.objects.filter(user=user, book__author=book.author).latest('borrow_date').borrow_date
            next_available_date = last_borrowed + timedelta(days=6*30)  # 6 months
            message = "Book can be borrowed on or after {}".format(next_available_date.date())
            return Response({"message": message})

        # For books currently borrowed by someone else
        if not book.available:
            # Assuming book will be returned in 14 days from the last borrowed date
            next_available_date = book.last_borrowed + timedelta(days=14)
            message = "Book can be borrowed on or after {}".format(next_available_date.date())
            return Response({"message": message})

        return Response({"error": "Unable to determine availability."}, status=status.HTTP_400_BAD_REQUEST)