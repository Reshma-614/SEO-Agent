# chatbot/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot_home, name='chatbot_home'),  # Home page for the chatbot
    path('summary/', views.chatbot_summary, name='chatbot_summary'),  # API endpoint for the summary
    path("generate_pdf/", views.generate_pdf, name="generate_pdf"),
]
