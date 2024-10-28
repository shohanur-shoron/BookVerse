from django.urls import path
from users import views, api

urlpatterns = [
    path('create-account/', views.create_account, name='create_account'),
    path('is-username-available/<str:username>', api.is_username_available, name='is_username_available'),
    path('update-username', views.update_username, name='update_username'),
    path('upload-image', views.upload_image, name='upload_image'),
    path('add-interest/<str:interest>', api.add_interest, name='add_interest'),
    path('del-interest/<str:interest>', api.del_interest, name='del_interest'),
    path('login', views.login_user, name="login_user"),
    path('logout', views.logout_user, name="logout_user"),
    path('add_interest', views.add_interest, name="add_interest"),
    path('search-suggestions', api.search_items, name='search_items'),
]