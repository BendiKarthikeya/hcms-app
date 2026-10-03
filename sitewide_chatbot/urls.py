from django.urls import path

from . import views

app_name = "sitewide_chatbot"

urlpatterns = [
    path("api/chat/", views.chat_api, name="chat"),
    path("api/health/", views.health, name="health"),
]
