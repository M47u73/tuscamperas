from django.contrib import admin
from django.utils.html import format_html
from .models import (
    ConfiguracionSitio, ImagenCarrusel, Categoria, Color, Talle,
    Producto, ImagenProducto, VarianteStock, Pedido, ItemPedido, Sugerencia
)


# ──────────────────────────────────────────────
# CONFIGURACIÓN DEL SITIO
# ──────────────────────────────────────────────

@admin.register(ConfiguracionSitio)
class ConfiguracionSitioAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Identidad de la Tienda", {
            "fields": ("nombre_tienda", "slogan", "descripcion_hero")
        }),
        ("Contacto", {
            "fields": ("telefono", "whatsapp", "email")
        }),
        ("Entrega y Envíos", {
            "fields": ("direccion", "horario_atencion", "info_envio")
        }),
        ("Redes Sociales", {
            "fields": ("instagram", "facebook", "tiktok")
        }),
        ("Sección Ofertas", {
            "fields": ("titulo_ofertas", "descripcion_ofertas")
        }),
        ("Footer", {
            "fields": ("texto_footer",)
        }),
        ("MercadoPago", {
            "fields": ("mp_public_key", "mp_access_token"),
            "classes": ("collapse",),
            "description": "Ingresá las credenciales de MercadoPago para habilitar los pagos."
        }),
    )

    def has_add_permission(self, request):
        return not ConfiguracionSitio.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


# ──────────────────────────────────────────────
# CARRUSEL
# ──────────────────────────────────────────────

@admin.register(ImagenCarrusel)
class ImagenCarruselAdmin(admin.ModelAdmin):
    list_display = ("preview", "titulo", "orden", "activo")
    list_editable = ("orden", "activo")
    list_display_links = ("preview", "titulo")
    ordering = ("orden",)

    def preview(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" style="height:60px;border-radius:4px;" />', obj.imagen.url
            )
        return "—"
    preview.short_description = "Vista previa"


# ──────────────────────────────────────────────
# CATEGORÍAS
# ──────────────────────────────────────────────

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "slug", "orden", "activo")
    list_editable = ("orden", "activo")
    prepopulated_fields = {"slug": ("nombre",)}


# ──────────────────────────────────────────────
# COLORES Y TALLES
# ──────────────────────────────────────────────

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "muestra_color", "codigo_hex")

    def muestra_color(self, obj):
        return format_html(
            '<div style="width:30px;height:20px;background:{};border:1px solid #ccc;'
            'border-radius:3px;"></div>', obj.codigo_hex
        )
    muestra_color.short_description = "Color"


@admin.register(Talle)
class TalleAdmin(admin.ModelAdmin):
    list_display = ("nombre", "orden")
    list_editable = ("orden",)


# ──────────────────────────────────────────────
# PRODUCTOS
# ──────────────────────────────────────────────

class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 2
    fields = ("imagen", "color", "orden")


class VarianteStockInline(admin.TabularInline):
    model = VarianteStock
    extra = 3
    fields = ("talle", "color", "stock")


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "imagen_thumb", "nombre", "categoria", "precio", "precio_oferta",
        "en_oferta", "destacado", "activo"
    )
    list_editable = ("precio", "precio_oferta", "en_oferta", "destacado", "activo")
    list_display_links = ("imagen_thumb", "nombre")
    list_filter = ("categoria", "en_oferta", "destacado", "activo")
    search_fields = ("nombre", "descripcion")
    prepopulated_fields = {"slug": ("nombre",)}
    filter_horizontal = ("colores_disponibles", "talles_disponibles")
    inlines = [ImagenProductoInline, VarianteStockInline]
    fieldsets = (
        ("Información General", {
            "fields": ("nombre", "slug", "categoria", "descripcion_corta", "descripcion")
        }),
        ("Precios", {
            "fields": ("precio", "precio_oferta")
        }),
        ("Imagen Principal", {
            "fields": ("imagen_principal",)
        }),
        ("Variantes disponibles", {
            "fields": ("colores_disponibles", "talles_disponibles"),
            "description": "Seleccioná los colores y talles disponibles para este producto."
        }),
        ("Visibilidad", {
            "fields": ("destacado", "en_oferta", "activo")
        }),
    )

    def imagen_thumb(self, obj):
        if obj.imagen_principal:
            return format_html(
                '<img src="{}" style="height:50px;border-radius:4px;" />', obj.imagen_principal.url
            )
        return "—"
    imagen_thumb.short_description = "Imagen"


# ──────────────────────────────────────────────
# PEDIDOS
# ──────────────────────────────────────────────

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = (
        "nombre_producto", "talle", "color", "cantidad",
        "precio_unitario", "subtotal_display"
    )
    fields = (
        "nombre_producto", "talle", "color", "cantidad",
        "precio_unitario", "subtotal_display"
    )

    def subtotal_display(self, obj):
        return f"${obj.subtotal:,.2f}"
    subtotal_display.short_description = "Subtotal"

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        "id", "nombre", "email", "telefono", "tipo_entrega",
        "estado", "total_display", "creado"
    )
    list_editable = ("estado",)
    list_filter = ("estado", "tipo_entrega", "creado")
    search_fields = ("nombre", "email", "telefono")
    readonly_fields = (
        "nombre", "email", "telefono", "direccion", "ciudad", "codigo_postal",
        "tipo_entrega", "notas", "total", "mp_preference_id", "mp_payment_id",
        "mp_status", "creado", "actualizado"
    )
    inlines = [ItemPedidoInline]
    fieldsets = (
        ("Datos del Cliente", {
            "fields": (
                "nombre", "email", "telefono", "tipo_entrega",
                "direccion", "ciudad", "codigo_postal", "notas"
            )
        }),
        ("Estado del Pedido", {
            "fields": ("estado", "total")
        }),
        ("MercadoPago", {
            "fields": ("mp_preference_id", "mp_payment_id", "mp_status"),
            "classes": ("collapse",)
        }),
        ("Fechas", {
            "fields": ("creado", "actualizado"),
            "classes": ("collapse",)
        }),
    )

    def total_display(self, obj):
        return f"${obj.total:,.2f}"
    total_display.short_description = "Total"

    def has_add_permission(self, request):
        return False


# ──────────────────────────────────────────────
# SUGERENCIAS
# ──────────────────────────────────────────────

@admin.register(Sugerencia)
class SugerenciaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "mensaje_corto", "visible", "creado")
    list_editable = ("visible",)
    list_filter = ("visible",)
    readonly_fields = ("creado",)

    def mensaje_corto(self, obj):
        return obj.mensaje[:80] + ("..." if len(obj.mensaje) > 80 else "")
    mensaje_corto.short_description = "Mensaje"


# Personalización del admin
admin.site.site_header = "Panel de Administración — Tienda de Ropa"
admin.site.site_title = "Tienda de Ropa Admin"
admin.site.index_title = "Bienvenido al Panel de Administración"
