from django.db import models
from django.utils.text import slugify


# ──────────────────────────────────────────────
# CONFIGURACIÓN GENERAL DEL SITIO (textos editables)
# ──────────────────────────────────────────────

class ConfiguracionSitio(models.Model):
    """Todos los textos y datos del sitio editables desde el admin."""
    nombre_tienda = models.CharField(max_length=100, default="Mi Tienda de Ropa")
    slogan = models.CharField(max_length=200, default="Moda para todos los estilos")
    descripcion_hero = models.TextField(
        default="Encontrá las mejores camperas, remeras, buzos y pantalones.",
        help_text="Texto que aparece debajo del título en el carrusel principal."
    )
    # Contacto
    telefono = models.CharField(max_length=30, default="+54 9 11 0000-0000")
    whatsapp = models.CharField(max_length=30, default="+5491100000000",
                                help_text="Número con código de país, sin espacios ni guiones.")
    email = models.EmailField(default="tienda@ejemplo.com")
    # Dirección / Entrega
    direccion = models.CharField(max_length=200, default="Buenos Aires, Argentina")
    horario_atencion = models.CharField(max_length=200, default="Lunes a Viernes 9:00 - 18:00")
    info_envio = models.TextField(
        default=(
            "Enviamos por correo a todo el país. El costo de envío corre por cuenta del cliente. "
            "También podés coordinar retiro en punto acordado con el vendedor."
        ),
        help_text="Texto informativo sobre envíos que aparece en el sitio."
    )
    # Redes sociales
    instagram = models.URLField(blank=True, default="https://instagram.com/")
    facebook = models.URLField(blank=True, default="https://facebook.com/")
    tiktok = models.URLField(blank=True, default="")
    # Sección ofertas
    titulo_ofertas = models.CharField(max_length=100, default="Ofertas de la Semana")
    descripcion_ofertas = models.TextField(
        default="Aprovechá nuestros descuentos especiales en prendas seleccionadas.",
        blank=True
    )
    # Footer
    texto_footer = models.CharField(
        max_length=300, default="© 2025 Mi Tienda de Ropa. Todos los derechos reservados."
    )
    # MercadoPago
    mp_public_key = models.CharField(
        max_length=200, blank=True, default="",
        help_text="Public Key de MercadoPago (TEST o PROD)."
    )
    mp_access_token = models.CharField(
        max_length=200, blank=True, default="",
        help_text="Access Token de MercadoPago (TEST o PROD)."
    )

    class Meta:
        verbose_name = "Configuración del Sitio"
        verbose_name_plural = "Configuración del Sitio"

    def __str__(self):
        return self.nombre_tienda

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


# ──────────────────────────────────────────────
# CARRUSEL
# ──────────────────────────────────────────────

class ImagenCarrusel(models.Model):
    imagen = models.ImageField(upload_to="carrusel/", verbose_name="Imagen")
    titulo = models.CharField(max_length=150, blank=True, verbose_name="Título (opcional)")
    subtitulo = models.CharField(max_length=250, blank=True, verbose_name="Subtítulo (opcional)")
    orden = models.PositiveIntegerField(default=0, verbose_name="Orden")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Imagen del Carrusel"
        verbose_name_plural = "Imágenes del Carrusel"
        ordering = ["orden"]

    def __str__(self):
        return self.titulo or f"Imagen #{self.pk}"


# ──────────────────────────────────────────────
# CATEGORÍAS DE PRODUCTOS
# ──────────────────────────────────────────────

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to="categorias/", blank=True, null=True)
    orden = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


# ──────────────────────────────────────────────
# COLORES Y TALLES
# ──────────────────────────────────────────────

class Color(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    codigo_hex = models.CharField(
        max_length=7, default="#000000",
        help_text="Código hexadecimal, ej: #1e3a5f"
    )

    class Meta:
        verbose_name = "Color"
        verbose_name_plural = "Colores"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Talle(models.Model):
    nombre = models.CharField(max_length=10, unique=True, help_text="Ej: S, M, L, XL, 2XL, 3XL")
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Talle"
        verbose_name_plural = "Talles"
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre


# ──────────────────────────────────────────────
# PRODUCTOS
# ──────────────────────────────────────────────

class Producto(models.Model):
    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, null=True, related_name="productos"
    )
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    descripcion = models.TextField(blank=True)
    descripcion_corta = models.CharField(max_length=300, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_oferta = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Si tiene precio de oferta, ingresalo aquí."
    )
    imagen_principal = models.ImageField(upload_to="productos/", blank=True, null=True)
    colores_disponibles = models.ManyToManyField(Color, blank=True, related_name="productos")
    talles_disponibles = models.ManyToManyField(Talle, blank=True, related_name="productos")
    destacado = models.BooleanField(default=False, help_text="Aparece en la sección de destacados.")
    en_oferta = models.BooleanField(default=False, help_text="Aparece en la sección de ofertas.")
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["-creado"]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nombre)
            slug = base_slug
            n = 1
            while Producto.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def precio_actual(self):
        if self.precio_oferta:
            return self.precio_oferta
        return self.precio

    @property
    def tiene_descuento(self):
        return bool(self.precio_oferta and self.precio_oferta < self.precio)

    @property
    def porcentaje_descuento(self):
        if self.tiene_descuento:
            return int(100 - (self.precio_oferta / self.precio * 100))
        return 0


class ImagenProducto(models.Model):
    """Imágenes adicionales de un producto."""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="imagenes")
    imagen = models.ImageField(upload_to="productos/")
    color = models.ForeignKey(
        Color, on_delete=models.SET_NULL, null=True, blank=True,
        help_text="Asociá esta imagen a un color específico (opcional)."
    )
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Imagen del Producto"
        verbose_name_plural = "Imágenes del Producto"
        ordering = ["orden"]

    def __str__(self):
        return f"Imagen de {self.producto.nombre}"


class VarianteStock(models.Model):
    """Stock por combinación de producto + talle + color."""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="variantes")
    talle = models.ForeignKey(Talle, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Variante de Stock"
        verbose_name_plural = "Variantes de Stock"
        unique_together = ("producto", "talle", "color")

    def __str__(self):
        return (
            f"{self.producto.nombre} | {self.talle.nombre} | "
            f"{self.color.nombre} — Stock: {self.stock}"
        )


# ──────────────────────────────────────────────
# PEDIDOS
# ──────────────────────────────────────────────

class Pedido(models.Model):
    ESTADO_CHOICES = [
        ("pendiente", "Pendiente"),
        ("confirmado", "Confirmado"),
        ("en_preparacion", "En preparación"),
        ("enviado", "Enviado"),
        ("entregado", "Entregado"),
        ("cancelado", "Cancelado"),
    ]
    ENTREGA_CHOICES = [
        ("correo", "Envío por correo"),
        ("acordado", "Retiro en punto acordado"),
    ]

    # Datos del cliente
    nombre = models.CharField(max_length=150)
    email = models.EmailField()
    telefono = models.CharField(max_length=30)
    direccion = models.CharField(max_length=300, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    codigo_postal = models.CharField(max_length=20, blank=True)
    tipo_entrega = models.CharField(max_length=20, choices=ENTREGA_CHOICES, default="correo")
    notas = models.TextField(blank=True, help_text="Notas adicionales del cliente.")

    # Estado y totales
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="pendiente")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # MercadoPago
    mp_preference_id = models.CharField(max_length=200, blank=True)
    mp_payment_id = models.CharField(max_length=200, blank=True)
    mp_status = models.CharField(max_length=50, blank=True)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ["-creado"]

    def __str__(self):
        return f"Pedido #{self.pk} — {self.nombre} ({self.get_estado_display()})"

    def calcular_total(self):
        self.total = sum(item.subtotal for item in self.items.all())
        self.save(update_fields=["total"])


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    nombre_producto = models.CharField(max_length=200)  # snapshot del nombre
    talle = models.CharField(max_length=20)
    color = models.CharField(max_length=50)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Ítem del Pedido"
        verbose_name_plural = "Ítems del Pedido"

    def __str__(self):
        return f"{self.nombre_producto} ({self.talle} / {self.color}) x{self.cantidad}"

    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad


# ──────────────────────────────────────────────
# SUGERENCIAS / TESTIMONIOS
# ──────────────────────────────────────────────

class Sugerencia(models.Model):
    nombre = models.CharField(max_length=100)
    mensaje = models.TextField()
    visible = models.BooleanField(
        default=False,
        help_text="Marcar para mostrar públicamente en la página principal."
    )
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sugerencia / Testimonio"
        verbose_name_plural = "Sugerencias / Testimonios"
        ordering = ["-creado"]

    def __str__(self):
        return f"{self.nombre}: {self.mensaje[:60]}"
