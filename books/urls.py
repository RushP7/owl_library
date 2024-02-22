from django.urls import path
from . import views

urlpatterns = [
    path('books/', views.BookList.as_view(), name='book-list'),
    path('books/<str:author>/', views.BookListByAuthor.as_view(), name='book-list-by-author'),
    path('books/borrow/', views.BorrowBook.as_view(), name='borrow-book'),
]
