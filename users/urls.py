from django.urls import path, include
from . import views

urlpatterns = [
    path('create/', views.create_account, name = 'create_account'),
    path('is_username_available/<str:username>', views.is_username_available, name = 'is_username_available'),
    path('username/', views.update_username, name = 'update_username'),
    path('logout/', views.logout_user, name = 'logout_user'),
    path('login/', views.login_user, name = 'login_user'),
    path('upload-image/', views.upload_image, name='upload_image'),
    path('interests/', views.add_your_interest, name='add_your_interest'),
    path('add-interest/<str:interest>', views.add_interest, name='add_interest'),
    path('del-interest/<str:interest>', views.del_interest, name='del_interest'),
    path("account/delete", views.delete_user, name="delete_user"),
    path("account/update", views.update_account, name="update_account"),
    path("account/update/username", views.change_username, name="change_username"),
    path("account/update/password", views.change_password, name="change_password"),
    path("account/update/image", views.change_image, name="change_image"),
    path("account/update/interest", views.change_interest, name="change_interest"),

]