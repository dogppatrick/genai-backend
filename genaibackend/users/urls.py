from django.urls import path

from .views import (LoginView, user_detail_view, user_redirect_view,
                    user_update_view)

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<int:pk>/", view=user_detail_view, name="detail"),
    path("api-login/", view=LoginView.as_view(), name="front-end-login"),
]
