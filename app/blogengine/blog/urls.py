from django.urls import path
from .views import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import RedirectView

"""
Для каждой функции нужен свой url для выполнения этой функции, а также имя которое позже будет использоваться в html
Поведение новых путей такое же, как и написанные тобой выше
В путь передайтся (если это нужно) какой-то аргумент, который будет отображаться в адрессной строке и этот же аргумент
будет для функции, которая выполняется при переходе на этот путь
"""

urlpatterns = [
    path('', RedirectView.as_view(url='/date_down')),
    path('<str:pk>', posts_list, name='posts_list_url'),
    path('tags/', tags_list, name='tags_list_url'),
    path('post/create/', PostCreate.as_view(), name='post_create_url'),
    path('tag/create/', TagCreate.as_view(), name='tag_create_url'),
    path('post/<str:slug>/', PostDetail.as_view(), name='post_detail_url'),
    path('tag/<str:slug>/', TagDetail.as_view(), name='tag_detail_url'),
    path('tag/<str:slug>/update/', TagUpdate.as_view(), name='tag_update_url'),
    path('post/<str:slug>/update/', PostUpdate.as_view(), name='post_update_url'),
    path('tag/<str:slug>/delete/', TagDelete.as_view(), name='tag_delete_url'),
    path('post/<str:slug>/delete/', PostDelete.as_view(), name='post_delete_url'),
    path('delete/<int:id>/<str:slug>/', PostDetail.comment_delete, name='comments-delete'),
    path('delete/<int:id>/<str:author_post>/', PostDetail.comment_delete, name='comments-delete-profile'),
    path('download_txt/<str:slug>/', download_file_txt, name='download_txt'),
    path('download_pdf/<str:slug>/', download_file_pdf, name='download_pdf'),
    path('post/<str:slug>/addlike/', add_like, name='add_like'),
    path('post/<str:slug>/adddislike/', add_dislike, name='add_dislike'),
    path('post/<str:slug>/rating/', rating_sum, name='rating'),
    path('profile/<str:author_post>/', profile, name='profile'),
    path('profile/<str:author_post>/addlike/', add_like_prof, name='add_like_prof'),
    path('profile/<str:author_post>/adddislike/', add_dislike_prof, name='add_dislike_prof'),
    path('profile/<str:author_post>/rating/', rating_sum_prof, name='rating_prof'),
    path('favorites/', AddArticleToFavorites.as_view(), name='add_to_favorites'),
    path('favorites_profile/', AddProfileToFavorites.as_view(), name='add_to_favorites_profile'),
    path('favorites/<str:author_post>', render_favorite, name='favorites')
]

# Нужно для отображения в адрессной строке номрмального пути , где хранятся картинки и статические файлы
urlpatterns += staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
