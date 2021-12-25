from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView

from core.models import Item, OrderItem, Order, Address
from core.forms import CheckoutForm


class HomeView(ListView):
    """Основная страница со списком всех товаров на сайте."""

    model = Item
    template_name = 'home.html'
    context_object_name = 'items'
    paginate_by = 10


class CheckoutView(LoginRequiredMixin, View):
    """Вывод страницы с формой для оформления заказа."""""

    def get(self, *args, **kwargs):
        """Проверяем есть ли у пользователя действительный заказ, сохраненные адреса
        для доставки и выставления счета."""
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
        except Order.DoesNotExist:
            messages.warning(self.request, 'У вас нет активного заказа. Для начала добавте продукт в корзину.')
            return redirect('core:home')

        form = CheckoutForm()
        context = {
            'form': form,
            # 'couponform': CouponForm(),
            'order': order,
            'DISPLAY_COUPON_FORM': True
        }

        shipping_address_qs = Address.objects.filter(
            user=self.request.user,
            address_type='S',
            default=True
        )
        if shipping_address_qs.exists():
            context.update(
                {'default_shipping_address': shipping_address_qs[0]})

        billing_address_qs = Address.objects.filter(
            user=self.request.user,
            address_type='B',
            default=True
        )
        if billing_address_qs.exists():
            context.update(
                {'default_billing_address': billing_address_qs[0]})
        return render(self.request, 'checkout.html', context)

    def post(self, *args, **kwargs):
        """ """
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
        except Order.DoesNotExist:
            messages.warning('У вас нет активного заказа. Для начала добавте продукт в корзину.')
            return redirect('core:home')

        form = CheckoutForm(self.request.POST or None)
        if form.is_valid():

            if form.cleaned_data['use_default_shipping']:
                shipping_address = form.set_default_shipping_address(self.request.user, order)
            else:
                shipping_address = form.set_new_shipping_address(self.request.user, order)

            if form.cleaned_data['same_billing_address']:
                form.set_same_billing_address(shipping_address, order)
            elif form.cleaned_data['use_default_billing']:
                form.set_default_billing_address(self.request.user, order)
            else:
                # Пользователь ввел новый платежный адрес.
                form.set_new_billing_address(self.request.user, order)

            payment_option = form.cleaned_data.get('payment_option')

            # if payment_option == 'S':
            #     return redirect('core:payment', payment_option='stripe')
            # elif payment_option == 'P':
            #     return redirect('core:payment', payment_option='paypal')
            # else:
            #     messages.warning(
            #         self.request, "Invalid payment option selected")
            #     return redirect('core:checkout')
            messages.info(self.request, 'Успешно')
            return redirect('/')


class OrderSummaryView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            return render(self.request, 'order_summary.html', {'object': order})

        except Order.DoesNotExist:
            messages.error(self.request, 'You do not have an active order')
            return redirect('/')


class ItemDetailView(DetailView):
    model = Item
    template_name = 'product.html'
    context_object_name = 'item'


@login_required
def add_item_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)