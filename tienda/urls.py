from django.urls import path
from . import views

urlpatterns = [
    # Páginas principales
    path("", views.index, name="index"),
    path("catalogo/", views.catalogo, name="catalogo"),
    path("producto/<slug:slug>/", views.detalle_producto, name="detalle_producto"),

    # Carrito
    path("carrito/", views.ver_carrito, name="ver_carrito"),
    path("carrito/agregar/<int:producto_id>/", views.agregar_al_carrito, name="agregar_al_carrito"),
    path("carrito/actualizar/<str:key>/", views.actualizar_carrito, name="actualizar_carrito"),
    path("carrito/eliminar/<str:key>/", views.eliminar_del_carrito, name="eliminar_del_carrito"),

    # Checkout y pedidos
    path("checkout/", views.checkout, name="checkout"),
    path("pedido/<int:pedido_id>/confirmado/", views.pedido_confirmado, name="pedido_confirmado"),
    path("pedido/<int:pedido_id>/error/", views.pedido_error, name="pedido_error"),
    path("pedido/<int:pedido_id>/pendiente/", views.pedido_pendiente, name="pedido_pendiente"),

    # MercadoPago webhook
    path("mp/webhook/", views.mp_webhook, name="mp_webhook"),

    # AJAX
    path("api/stock/<int:producto_id>/", views.stock_variante, name="stock_variante"),

    # Sugerencias
    path("sugerencia/", views.enviar_sugerencia, name="enviar_sugerencia"),
]
