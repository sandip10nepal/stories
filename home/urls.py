from .views import *
from django.urls import path, include
from . import views

urlpatterns = [
    path("", home, name="home"),
    path("home", home, name="home"),
    path("publish", publish, name="publish"),
    path("account", account, name="account"),
    path("login", login_page, name="login_page"),
    path("logout_page", logout_page, name="logout_page"),
    path('category/<slug:name>/', views.category_detail, name='category_detail'),
    path("profile/<str:username>/", profile, name="profile"),
    path('dictionary/', dictionary, name='dictionary'),
    path('content/<slug:id>/', readmore, name='readmore'),
    path('submit_rating/', views.submit_rating, name='submit_rating'),
    path('follow_user/<str:username>/', views.follow_user, name='follow_user'),
    path('search/', search, name='search'),
     ]
