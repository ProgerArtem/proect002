from django.conf.urls import include, url
from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.show_categories),
    path('register/', views.register),
    path('settings/', views.settings),
    path('index/', views.index),
    path('logout/', views.logout_request),
    path('login/', views.login_request),
    path('look_profile/<profile>', views.look_profile, name='look_profile'),
    path('profile/', views.profile, name = "user_profile"),
    path('smotri_profile/', views.smotri_profile, name = "user_smotri_profile"),
    path('search_post/', views.search_post, name="search_post"),
    path('add_post/', views.add_post, name="add_post"),
    path('post_like/<int:pk>', views.like_post, name="like_post"),
    path('post_dislike/<int:pk>', views.dislikes_post, name="dislike_post"),
    path('main_page/', views.main_page, name="categories"),
    path('<single_slug>/', views.single_slug, name="slug_url"),

    
]

urlpatterns+= static(settings.STATIC_URL,
                     document_root=settings.STATIC_ROOT)
print (urlpatterns)
