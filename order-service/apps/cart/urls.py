from django.urls import path
from . import views

urlpatterns = [
    # GET    /api/v1/cart/{user_id}/
    path("<str:user_id>/",
         views.view_cart,
         name="view-cart"),

    # POST   /api/v1/cart/{user_id}/add/
    path("<str:user_id>/add/",
         views.add_item,
         name="add-item"),

    # DELETE /api/v1/cart/{user_id}/remove/{product_id}/
    path("<str:user_id>/remove/<str:product_id>/",
         views.remove_item,
         name="remove-item"),

    # PATCH  /api/v1/cart/{user_id}/update/{product_id}/
    path("<str:user_id>/update/<str:product_id>/",
         views.update_item,
         name="update-item"),

    # DELETE /api/v1/cart/{user_id}/clear/
    path("<str:user_id>/clear/",
         views.clear_user_cart,
         name="clear-cart"),
]