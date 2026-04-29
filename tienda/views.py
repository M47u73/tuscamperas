import json
import mercadopago
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib import messages

from .models import (
    Producto, Categoria, ImagenCarrusel, Sugerencia,
    ConfiguracionSitio, Pedido, ItemPedido, VarianteStock
)
from .forms import PedidoForm, SugerenciaForm


# ──────────────────────────────────────────────
# HELPERS DE CARRITO
# ──────────────────────────────────────────────

def get_carrito(request):
    return request.session.get("carrito", {})


def save_carrito(request, carrito):
    request.session["carrito"] = carrito
    request.session.modified = True


def carrito_items_detail(carrito):
    """Devuelve lista de ítems del carrito con datos del producto."""
    items = []
    total = 0
    for key, item in carrito.items():
        try:
            producto = Producto.objects.get(pk=item["producto_id"])
            subtotal = float(producto.precio_actual) * item["cantidad"]
            total += subtotal
            items.append({
                "key": key,
                "producto": producto,
                "talle": item["talle"],
                "color": item["color"],
                "cantidad": item["cantidad"],
                "precio_unitario": float(producto.precio_actual),
                "subtotal": subtotal,
            })
        except Producto.DoesNotExist:
            pass
    return items, total


# ──────────────────────────────────────────────
# PÁGINA PRINCIPAL
# ──────────────────────────────────────────────

def index(request):
    config = ConfiguracionSitio.get()
    carrusel = ImagenCarrusel.objects.filter(activo=True).order_by("orden")
    destacados = Producto.objects.filter(destacado=True, activo=True)[:8]
    ofertas = Producto.objects.filter(en_oferta=True, activo=True)[:8]
    categorias = Categoria.objects.filter(activo=True).order_by("orden")
    sugerencias = Sugerencia.objects.filter(visible=True).order_by("-creado")[:6]
    form_sugerencia = SugerenciaForm()

    return render(request, "tienda/index.html", {
        "carrusel": carrusel,
        "destacados": destacados,
        "ofertas": ofertas,
        "categorias": categorias,
        "sugerencias": sugerencias,
        "form_sugerencia": form_sugerencia,
        "config": config,
    })


# ──────────────────────────────────────────────
# CATÁLOGO / LISTADO DE PRODUCTOS
# ──────────────────────────────────────────────

def catalogo(request):
    productos = Producto.objects.filter(activo=True)
    categorias = Categoria.objects.filter(activo=True).order_by("orden")

    categoria_slug = request.GET.get("categoria")
    busqueda = request.GET.get("q", "").strip()
    solo_ofertas = request.GET.get("ofertas") == "1"

    categoria_activa = None
    if categoria_slug:
        categoria_activa = get_object_or_404(Categoria, slug=categoria_slug, activo=True)
        productos = productos.filter(categoria=categoria_activa)

    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)

    if solo_ofertas:
        productos = productos.filter(en_oferta=True)

    return render(request, "tienda/catalogo.html", {
        "productos": productos,
        "categorias": categorias,
        "categoria_activa": categoria_activa,
        "busqueda": busqueda,
        "solo_ofertas": solo_ofertas,
    })


# ──────────────────────────────────────────────
# DETALLE DE PRODUCTO
# ──────────────────────────────────────────────

def detalle_producto(request, slug):
    producto = get_object_or_404(Producto, slug=slug, activo=True)
    talles = producto.talles_disponibles.all().order_by("orden")
    colores = producto.colores_disponibles.all().order_by("nombre")
    imagenes = producto.imagenes.all().order_by("orden")

    # Stock por variante para el JS
    variantes_stock = {}
    for v in producto.variantes.all():
        key = f"{v.talle_id}_{v.color_id}"
        variantes_stock[key] = v.stock

    relacionados = Producto.objects.filter(
        categoria=producto.categoria, activo=True
    ).exclude(pk=producto.pk)[:4]

    return render(request, "tienda/detalle_producto.html", {
        "producto": producto,
        "talles": talles,
        "colores": colores,
        "imagenes": imagenes,
        "variantes_stock_json": json.dumps(variantes_stock),
        "relacionados": relacionados,
    })


# ──────────────────────────────────────────────
# CARRITO
# ──────────────────────────────────────────────

@require_POST
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id, activo=True)
    talle = request.POST.get("talle", "").strip()
    color = request.POST.get("color", "").strip()
    cantidad = int(request.POST.get("cantidad", 1))

    if not talle or not color:
        messages.error(request, "Debés seleccionar talle y color antes de agregar al carrito.")
        return redirect("detalle_producto", slug=producto.slug)

    carrito = get_carrito(request)
    key = f"{producto_id}_{talle}_{color}"

    if key in carrito:
        carrito[key]["cantidad"] += cantidad
    else:
        carrito[key] = {
            "producto_id": producto_id,
            "talle": talle,
            "color": color,
            "cantidad": cantidad,
        }

    save_carrito(request, carrito)
    messages.success(request, f"¡{producto.nombre} agregado al carrito!")
    return redirect("ver_carrito")


def ver_carrito(request):
    carrito = get_carrito(request)
    items, total = carrito_items_detail(carrito)
    return render(request, "tienda/carrito.html", {
        "items": items,
        "total": total,
    })


@require_POST
def actualizar_carrito(request, key):
    carrito = get_carrito(request)
    cantidad = int(request.POST.get("cantidad", 1))
    if key in carrito:
        if cantidad <= 0:
            del carrito[key]
        else:
            carrito[key]["cantidad"] = cantidad
    save_carrito(request, carrito)
    return redirect("ver_carrito")


@require_POST
def eliminar_del_carrito(request, key):
    carrito = get_carrito(request)
    if key in carrito:
        del carrito[key]
    save_carrito(request, carrito)
    return redirect("ver_carrito")


# ──────────────────────────────────────────────
# CHECKOUT Y PEDIDO
# ──────────────────────────────────────────────

def checkout(request):
    carrito = get_carrito(request)
    if not carrito:
        messages.warning(request, "Tu carrito está vacío.")
        return redirect("ver_carrito")

    items, total = carrito_items_detail(carrito)
    config = ConfiguracionSitio.get()

    if request.method == "POST":
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.total = total
            pedido.save()

            for item in items:
                ItemPedido.objects.create(
                    pedido=pedido,
                    producto=item["producto"],
                    nombre_producto=item["producto"].nombre,
                    talle=item["talle"],
                    color=item["color"],
                    cantidad=item["cantidad"],
                    precio_unitario=item["precio_unitario"],
                )

            # Intentar crear preferencia de MercadoPago
            mp_init_point = None
            access_token = config.mp_access_token or settings.MERCADOPAGO_ACCESS_TOKEN
            if access_token:
                try:
                    sdk = mercadopago.SDK(access_token)
                    mp_items = []
                    for item in items:
                        mp_items.append({
                            "title": f"{item['producto'].nombre} ({item['talle']} / {item['color']})",
                            "quantity": item["cantidad"],
                            "unit_price": float(item["precio_unitario"]),
                            "currency_id": "ARS",
                        })

                    base_url = request.build_absolute_uri("/")
                    preference_data = {
                        "items": mp_items,
                        "payer": {
                            "name": pedido.nombre,
                            "email": pedido.email,
                            "phone": {"number": pedido.telefono},
                        },
                        "back_urls": {
                            "success": base_url + f"pedido/{pedido.pk}/confirmado/",
                            "failure": base_url + f"pedido/{pedido.pk}/error/",
                            "pending": base_url + f"pedido/{pedido.pk}/pendiente/",
                        },
                        "auto_return": "approved",
                        "external_reference": str(pedido.pk),
                    }
                    result = sdk.preference().create(preference_data)
                    preference = result.get("response", {})
                    pedido.mp_preference_id = preference.get("id", "")
                    pedido.save(update_fields=["mp_preference_id"])
                    mp_init_point = preference.get("init_point") or preference.get("sandbox_init_point")
                except Exception:
                    pass

            # Limpiar carrito
            request.session["carrito"] = {}
            request.session.modified = True

            return render(request, "tienda/pedido_confirmado.html", {
                "pedido": pedido,
                "items": items,
                "total": total,
                "mp_init_point": mp_init_point,
                "config": config,
            })
    else:
        form = PedidoForm()

    return render(request, "tienda/checkout.html", {
        "form": form,
        "items": items,
        "total": total,
        "config": config,
    })


def pedido_confirmado(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    # Actualizar estado si viene de MercadoPago
    payment_id = request.GET.get("payment_id", "")
    status = request.GET.get("status", "")
    if payment_id:
        pedido.mp_payment_id = payment_id
        pedido.mp_status = status
        if status == "approved":
            pedido.estado = "confirmado"
        pedido.save(update_fields=["mp_payment_id", "mp_status", "estado"])
    config = ConfiguracionSitio.get()
    return render(request, "tienda/pedido_estado.html", {
        "pedido": pedido,
        "estado_mp": status or "success",
        "config": config,
    })


def pedido_error(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    config = ConfiguracionSitio.get()
    return render(request, "tienda/pedido_estado.html", {
        "pedido": pedido,
        "estado_mp": "failure",
        "config": config,
    })


def pedido_pendiente(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    config = ConfiguracionSitio.get()
    return render(request, "tienda/pedido_estado.html", {
        "pedido": pedido,
        "estado_mp": "pending",
        "config": config,
    })


# ──────────────────────────────────────────────
# WEBHOOK MERCADOPAGO
# ──────────────────────────────────────────────

@csrf_exempt
def mp_webhook(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            if data.get("type") == "payment":
                payment_id = data["data"]["id"]
                config = ConfiguracionSitio.get()
                access_token = config.mp_access_token or settings.MERCADOPAGO_ACCESS_TOKEN
                if access_token:
                    sdk = mercadopago.SDK(access_token)
                    payment_info = sdk.payment().get(payment_id)
                    payment = payment_info.get("response", {})
                    external_ref = payment.get("external_reference")
                    status = payment.get("status")
                    if external_ref:
                        try:
                            pedido = Pedido.objects.get(pk=int(external_ref))
                            pedido.mp_payment_id = str(payment_id)
                            pedido.mp_status = status
                            if status == "approved":
                                pedido.estado = "confirmado"
                            pedido.save(update_fields=["mp_payment_id", "mp_status", "estado"])
                        except Pedido.DoesNotExist:
                            pass
        except Exception:
            pass
    return JsonResponse({"status": "ok"})


# ──────────────────────────────────────────────
# STOCK VÍA AJAX
# ──────────────────────────────────────────────

def stock_variante(request, producto_id):
    talle_id = request.GET.get("talle_id")
    color_id = request.GET.get("color_id")
    try:
        variante = VarianteStock.objects.get(
            producto_id=producto_id, talle_id=talle_id, color_id=color_id
        )
        stock = variante.stock
    except VarianteStock.DoesNotExist:
        stock = 0
    return JsonResponse({"stock": stock})


# ──────────────────────────────────────────────
# SUGERENCIAS
# ──────────────────────────────────────────────

@require_POST
def enviar_sugerencia(request):
    form = SugerenciaForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, "¡Gracias por tu mensaje! Lo revisaremos pronto.")
    else:
        messages.error(request, "Hubo un error. Por favor revisá los campos.")
    return redirect("index")
