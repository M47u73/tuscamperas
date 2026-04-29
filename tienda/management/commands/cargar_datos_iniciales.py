"""
Comando para cargar datos de ejemplo en la tienda.
Uso: python manage.py cargar_datos_iniciales
"""
from django.core.management.base import BaseCommand
from tienda.models import (
    ConfiguracionSitio, Categoria, Color, Talle,
    Producto, ImagenCarrusel, VarianteStock
)
import os
from django.core.files import File
from pathlib import Path


class Command(BaseCommand):
    help = "Carga datos iniciales de ejemplo para la tienda de ropa."

    def handle(self, *args, **kwargs):
        self.stdout.write("Cargando configuración del sitio...")
        config = ConfiguracionSitio.get()
        config.nombre_tienda = "Urban Style"
        config.slogan = "Moda para todos los estilos"
        config.telefono = "+54 9 11 0000-0000"
        config.whatsapp = "+5491100000000"
        config.email = "contacto@urbanstyle.com"
        config.instagram = "https://instagram.com/urbanstyle"
        config.facebook = "https://facebook.com/urbanstyle"
        config.save()
        self.stdout.write(self.style.SUCCESS("  ✓ Configuración guardada"))

        # Categorías
        self.stdout.write("Cargando categorías...")
        cats = [
            ("Camperas", "camperas", 1),
            ("Remeras", "remeras", 2),
            ("Buzos", "buzos", 3),
            ("Pantalones", "pantalones", 4),
        ]
        cat_objs = {}
        for nombre, slug, orden in cats:
            cat, _ = Categoria.objects.get_or_create(
                slug=slug, defaults={"nombre": nombre, "orden": orden}
            )
            cat_objs[slug] = cat
        self.stdout.write(self.style.SUCCESS("  ✓ Categorías cargadas"))

        # Colores
        self.stdout.write("Cargando colores...")
        colores_data = [
            ("Negro", "#1a1a1a"),
            ("Azul marino", "#1e3a5f"),
            ("Gris", "#808080"),
            ("Verde oliva", "#6b7c3a"),
            ("Rojo", "#c0392b"),
            ("Blanco", "#f5f5f5"),
            ("Beige", "#c8a97e"),
            ("Verde", "#27ae60"),
        ]
        color_objs = {}
        for nombre, hex_code in colores_data:
            color, _ = Color.objects.get_or_create(
                nombre=nombre, defaults={"codigo_hex": hex_code}
            )
            color_objs[nombre] = color
        self.stdout.write(self.style.SUCCESS("  ✓ Colores cargados"))

        # Talles
        self.stdout.write("Cargando talles...")
        talles_data = [
            ("S", 1), ("M", 2), ("L", 3), ("XL", 4),
            ("2XL", 5), ("3XL", 6), ("4XL", 7),
        ]
        talle_objs = {}
        for nombre, orden in talles_data:
            talle, _ = Talle.objects.get_or_create(
                nombre=nombre, defaults={"orden": orden}
            )
            talle_objs[nombre] = talle
        self.stdout.write(self.style.SUCCESS("  ✓ Talles cargados"))

        # Productos de ejemplo
        self.stdout.write("Cargando productos de ejemplo...")
        productos_data = [
            {
                "nombre": "Campera Deportiva con Capucha",
                "categoria": "camperas",
                "descripcion_corta": "Campera liviana ideal para actividades al aire libre.",
                "descripcion": (
                    "Campera deportiva con capucha ajustable, cierre metálico y bolsillos laterales. "
                    "Confeccionada en tela rompeviento, perfecta para el día a día."
                ),
                "precio": 35000,
                "precio_oferta": None,
                "destacado": True,
                "en_oferta": False,
                "colores": ["Negro", "Gris", "Verde oliva"],
                "talles": ["S", "M", "L", "XL", "2XL", "3XL"],
                "imagen": "campera_deportiva.jpg",
            },
            {
                "nombre": "Campera de Invierno Térmica",
                "categoria": "camperas",
                "descripcion_corta": "Campera inflada con forro térmico y piel interior.",
                "descripcion": (
                    "Campera de invierno con relleno de pluma sintética, capucha desmontable "
                    "y forro interior con piel. Ideal para los días más fríos."
                ),
                "precio": 65000,
                "precio_oferta": 52000,
                "destacado": True,
                "en_oferta": True,
                "colores": ["Negro", "Azul marino", "Gris", "Verde"],
                "talles": ["L", "XL", "2XL", "3XL", "4XL"],
                "imagen": "campera_invierno.jpg",
            },
            {
                "nombre": "Remera Básica Algodón",
                "categoria": "remeras",
                "descripcion_corta": "Remera de algodón 100%, cuello redondo.",
                "descripcion": (
                    "Remera básica de algodón peinado, suave al tacto y de larga duración. "
                    "Disponible en múltiples colores para combinar con cualquier look."
                ),
                "precio": 12000,
                "precio_oferta": 9500,
                "destacado": False,
                "en_oferta": True,
                "colores": ["Negro", "Blanco", "Gris", "Azul marino", "Rojo"],
                "talles": ["S", "M", "L", "XL", "2XL"],
                "imagen": None,
            },
            {
                "nombre": "Buzo con Capucha Fleece",
                "categoria": "buzos",
                "descripcion_corta": "Buzo canguro con capucha y bolsillo frontal.",
                "descripcion": (
                    "Buzo de algodón con interior de felpa, capucha con cordón y bolsillo canguro. "
                    "Cómodo y abrigado para el uso diario."
                ),
                "precio": 28000,
                "precio_oferta": None,
                "destacado": True,
                "en_oferta": False,
                "colores": ["Negro", "Azul marino", "Gris", "Rojo"],
                "talles": ["S", "M", "L", "XL", "2XL", "3XL"],
                "imagen": None,
            },
            {
                "nombre": "Pantalón Cargo Jogger",
                "categoria": "pantalones",
                "descripcion_corta": "Pantalón cargo con elástico y bolsillos laterales.",
                "descripcion": (
                    "Pantalón jogger estilo cargo con elástico en cintura y tobillo, "
                    "bolsillos laterales y traseros. Cómodo y versátil."
                ),
                "precio": 22000,
                "precio_oferta": 18000,
                "destacado": False,
                "en_oferta": True,
                "colores": ["Negro", "Beige", "Gris", "Azul marino"],
                "talles": ["S", "M", "L", "XL", "2XL"],
                "imagen": None,
            },
        ]

        media_root = Path(__file__).resolve().parent.parent.parent.parent / "media" / "productos"

        for pdata in productos_data:
            if Producto.objects.filter(nombre=pdata["nombre"]).exists():
                self.stdout.write(f"  — '{pdata['nombre']}' ya existe, omitiendo.")
                continue

            producto = Producto(
                nombre=pdata["nombre"],
                categoria=cat_objs[pdata["categoria"]],
                descripcion_corta=pdata["descripcion_corta"],
                descripcion=pdata["descripcion"],
                precio=pdata["precio"],
                precio_oferta=pdata.get("precio_oferta"),
                destacado=pdata["destacado"],
                en_oferta=pdata["en_oferta"],
                activo=True,
            )

            # Imagen
            if pdata.get("imagen"):
                img_path = media_root / pdata["imagen"]
                if img_path.exists():
                    with open(img_path, "rb") as f:
                        producto.imagen_principal.save(pdata["imagen"], File(f), save=False)

            producto.save()

            # Colores y talles
            for nombre_color in pdata["colores"]:
                if nombre_color in color_objs:
                    producto.colores_disponibles.add(color_objs[nombre_color])
            for nombre_talle in pdata["talles"]:
                if nombre_talle in talle_objs:
                    producto.talles_disponibles.add(talle_objs[nombre_talle])

            # Stock de ejemplo
            for nombre_color in pdata["colores"]:
                for nombre_talle in pdata["talles"]:
                    if nombre_color in color_objs and nombre_talle in talle_objs:
                        VarianteStock.objects.get_or_create(
                            producto=producto,
                            talle=talle_objs[nombre_talle],
                            color=color_objs[nombre_color],
                            defaults={"stock": 10},
                        )

            self.stdout.write(f"  ✓ '{producto.nombre}' creado")

        # Carrusel
        self.stdout.write("Cargando imágenes del carrusel...")
        carrusel_dir = Path(__file__).resolve().parent.parent.parent.parent / "media" / "carrusel"
        carrusel_data = [
            ("carrusel_1.jpg", "Camperas Deportivas", "Livianas y resistentes para cada aventura", 1),
            ("carrusel_2.jpg", "Camperas de Invierno", "El calor que necesitás en los días fríos", 2),
            ("carrusel_3.jpg", "Buzos y Hoodies", "Comodidad y estilo para el día a día", 3),
            ("carrusel_4.jpg", "Remeras Básicas", "Colores que combinan con todo", 4),
            ("carrusel_5.jpg", "Pantalones", "Estilo y comodidad en cada movimiento", 5),
            ("carrusel_6.jpg", "Camperas Bomber", "Estilo urbano para cada ocasión", 6),
        ]
        for filename, titulo, subtitulo, orden in carrusel_data:
            img_path = carrusel_dir / filename
            if img_path.exists() and not ImagenCarrusel.objects.filter(titulo=titulo).exists():
                carrusel_img = ImagenCarrusel(titulo=titulo, subtitulo=subtitulo, orden=orden, activo=True)
                with open(img_path, "rb") as f:
                    carrusel_img.imagen.save(filename, File(f), save=True)
                self.stdout.write(f"  ✓ Imagen '{titulo}' cargada")

        self.stdout.write(self.style.SUCCESS("\n¡Datos iniciales cargados correctamente!"))
        self.stdout.write("Ahora podés crear un superusuario con: python manage.py createsuperuser")
