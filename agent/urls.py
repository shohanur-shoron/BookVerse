from django.urls import path
from . import views

urlpatterns = [
    path('agent/initiate/', views.initiate_nlp_processing, name='initiate_nlp_processing'),
    path('stream/<uuid:stream_id>/', views.stream_nlp_results, name='stream_nlp_results'),
    path('', views.agent_chat_page, name='agent_chat_page'),
]