from django.urls import path
from . import views

urlpatterns = [
    path('books/', views.BookList.as_view(), name='book-list'),
    path('books/borrow/', views.BorrowBook.as_view(), name='borrow-book'),
    path('books/return/', views.ReturnBook.as_view(), name='return-book'),
]
