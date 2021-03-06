from django.urls import path

from core.views import (
    CheckoutView, HomeView, ItemDetailView,
    add_item_to_cart, remove_from_cart, OrderSummaryView,
    remove_single_item_from_cart, PaymentView, AddCouponView,
    ProductsView, RequestRefundView, SearchView
)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('category/<int:id>', ProductsView.as_view(), name='products-by-category'),
    path('search/', SearchView.as_view(), name='search'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),
    path('add-to-cart/<slug>/', add_item_to_cart, name='add-to-cart'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-single-item-from-cart/<slug>/', remove_single_item_from_cart, name='remove-single-item-from-cart'),
]
