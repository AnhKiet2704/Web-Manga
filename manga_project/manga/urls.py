from django.urls import path
from . import views, crud_views

urlpatterns = [
    # Trang chủ
    path('', views.home, name='home'),

    # Chi tiết truyện
    path('manga/<slug:slug>/', views.manga_detail, name='manga_detail'),

    # Đọc truyện
    path('manga/<slug:manga_slug>/<path:chapter_slug>/', views.read_chapter, name='read_chapter'),
    # Tìm kiếm
    path('search/', views.search, name='search'),

    # Thể loại
    path('category/<slug:slug>/', views.category_view, name='category'),

    # Auth
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),

    # User
    path('user/profile/', views.profile, name='profile'),
    path('user/history/', views.reading_history, name='reading_history'),
    path('user/following/', views.following_list, name='following_list'),

    # Actions
    path('follow/<int:manga_id>/', views.follow_manga, name='follow_manga'),
    path('comment/<int:manga_id>/', views.add_comment, name='add_comment'),
    path('rate/<int:manga_id>/', views.rate_manga, name='rate_manga'),

    # ==================== CRUD ====================
    path('crud/manga/', crud_views.manga_list, name='crud_manga_list'),
    path('crud/manga/create/', crud_views.manga_create, name='crud_manga_create'),
    path('crud/manga/<int:manga_id>/update/', crud_views.manga_update, name='crud_manga_update'),
    path('crud/manga/<int:manga_id>/delete/', crud_views.manga_delete, name='crud_manga_delete'),

    path('crud/manga/<int:manga_id>/chapters/', crud_views.chapter_list, name='crud_chapter_list'),
    path('crud/manga/<int:manga_id>/chapter/create/', crud_views.chapter_create, name='crud_chapter_create'),
    path('crud/chapter/<int:chapter_id>/update/', crud_views.chapter_update, name='crud_chapter_update'),
    path('crud/chapter/<int:chapter_id>/delete/', crud_views.chapter_delete, name='crud_chapter_delete'),

    path('crud/category/', crud_views.category_list, name='crud_category_list'),
    path('crud/category/create/', crud_views.category_create, name='crud_category_create'),
    path('crud/category/<int:category_id>/update/', crud_views.category_update, name='crud_category_update'),
    path('crud/category/<int:category_id>/delete/', crud_views.category_delete, name='crud_category_delete'),

    path('crud/author/', crud_views.author_list, name='crud_author_list'),
    path('crud/author/create/', crud_views.author_create, name='crud_author_create'),
    path('crud/author/<int:author_id>/update/', crud_views.author_update, name='crud_author_update'),
    path('crud/author/<int:author_id>/delete/', crud_views.author_delete, name='crud_author_delete'),
]