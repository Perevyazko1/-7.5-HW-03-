from django.urls import path
# Импортируем созданные нами представления
from .views import NewsList, NewsDetail, NewsSearch, NewsCreate, NewsUpdate, NewsDelete, CategoryList, subscribe, \
   Profile, save_author, like_post_view

urlpatterns = [
   path('<int:pk>', NewsDetail.as_view()),
   path('<int:post_pk>/like', like_post_view, name='like-post'),
   path('search/', NewsSearch.as_view()),
   path('', NewsList.as_view(), name='news_list'),
   path('<int:pk>', NewsDetail.as_view(), name='news_detail'),
   path('create/', NewsCreate.as_view(), name='news_create'),
   path('<int:pk>/update/', NewsUpdate.as_view(), name='news_update'),
   path('<int:pk>/delete/', NewsDelete.as_view(), name='news_delete'),
   path('categories/<int:pk>/', CategoryList.as_view(), name='category_list'),
   path('categories/<int:pk>/subscribe', subscribe, name='subscribe'),
   path('profile/', Profile.as_view()),
   path('profile/author', save_author, name='new_author'),

]
