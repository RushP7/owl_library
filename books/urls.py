from django.urls import path
from .views import BookList, BookListByAuthor

urlpatterns = [
    path('books/', BookList.as_view(), name='book-list'),
    path('books/<str:author>/', BookListByAuthor.as_view(), name='book-list-by-author'),
]
