# Urban Style — Tienda de Ropa Online

Tienda de ropa online desarrollada con **Django 4.2+**, con carrusel de imágenes editable, variantes de productos por talle y color, integración con **MercadoPago**, sección de ofertas, y panel de administración completo. Lista para desplegar en **Render**.

---

## Características principales

- **Carrusel automático** en la página principal (editable desde el admin)
- **Productos con variantes**: talle y color, con control de stock por combinación
- **Sección de ofertas** para productos con descuento
- **Carrito de compras** con sesiones (sin necesidad de registro)
- **Checkout** con formulario de datos del cliente y elección de entrega
- **Integración con MercadoPago** para pagos online
- **Envío a domicilio** por correo o retiro acordado con el vendedor
- **Panel de administración Django** con todos los modelos editables
- **Textos del sitio editables** desde el admin (nombre, slogan, teléfono, redes sociales, etc.)
- **Botón flotante de WhatsApp** para contacto rápido
- **Sección de sugerencias/testimonios** con moderación desde el admin
- **Diseño responsive** (azul marino + naranja) compatible con móviles
- **Listo para producción** con WhiteNoise, Gunicorn y configuración para Render

---

## Instalación local

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/tienda-ropa.git
cd tienda-ropa
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus valores reales
```

Para desarrollo local, el archivo `.env` mínimo es:

```env
SECRET_KEY=cualquier-clave-secreta-larga
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 4. Aplicar migraciones y cargar datos de ejemplo

```bash
python manage.py migrate
python manage.py cargar_datos_iniciales
python manage.py createsuperuser
```

### 5. Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

Accedé a:
- **Tienda**: http://localhost:8000/
- **Admin**: http://localhost:8000/admin/

---

## Configuración de MercadoPago

1. Creá una cuenta en [MercadoPago Developers](https://www.mercadopago.com.ar/developers)
2. Obtené tu **Public Key** y **Access Token** (modo TEST para pruebas)
3. Ingresalos en el panel de administración: **Configuración del Sitio → MercadoPago**
   — O bien, configurá las variables de entorno:
   ```env
   MERCADOPAGO_PUBLIC_KEY=TEST-xxxxxxxx
   MERCADOPAGO_ACCESS_TOKEN=TEST-xxxxxxxx
   ```

---

## Despliegue en Render

### 1. Subir a GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/tu-usuario/tienda-ropa.git
git push -u origin main
```

### 2. Crear servicio en Render

1. Ir a [render.com](https://render.com) → **New Web Service**
2. Conectar con el repositorio de GitHub
3. Configurar:
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn tienda_ropa.wsgi --log-file -`
   - **Runtime**: Python 3

### 3. Variables de entorno en Render

En el panel de Render → **Environment**, agregar:

| Variable | Valor |
|---|---|
| `SECRET_KEY` | Clave secreta larga y aleatoria |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `tu-app.onrender.com` |
| `DATABASE_URL` | URL de PostgreSQL (Render provee una gratis) |
| `MERCADOPAGO_PUBLIC_KEY` | Tu Public Key de MercadoPago |
| `MERCADOPAGO_ACCESS_TOKEN` | Tu Access Token de MercadoPago |

### 4. Base de datos PostgreSQL en Render

1. En Render → **New PostgreSQL** → crear base de datos gratuita
2. Copiar la **Internal Database URL**
3. Pegarla como valor de `DATABASE_URL` en el servicio web

### 5. Archivos de media en producción

> **Importante**: Render no persiste archivos subidos entre deploys. Para producción se recomienda usar **Cloudinary** o **AWS S3** para almacenar imágenes. Para un uso básico, las imágenes cargadas desde el admin se perderán al redesplegar.

---

## Estructura del proyecto

```
tienda_ropa/
├── tienda/                     # App principal
│   ├── models.py               # Modelos: Producto, Variante, Pedido, etc.
│   ├── views.py                # Vistas: catálogo, carrito, checkout
│   ├── admin.py                # Panel de administración personalizado
│   ├── forms.py                # Formularios de pedido y sugerencias
│   ├── urls.py                 # URLs de la app
│   ├── context_processors.py   # Configuración global en templates
│   └── management/commands/
│       └── cargar_datos_iniciales.py
├── templates/tienda/           # Templates HTML
│   ├── base.html               # Template base con navbar y footer
│   ├── index.html              # Página principal con carrusel
│   ├── catalogo.html           # Listado de productos con filtros
│   ├── detalle_producto.html   # Detalle con selector de talle/color
│   ├── carrito.html            # Carrito de compras
│   ├── checkout.html           # Formulario de pedido
│   ├── pedido_confirmado.html  # Confirmación con link de pago
│   └── pedido_estado.html      # Estado del pago (éxito/error/pendiente)
├── static/                     # Archivos estáticos
├── media/                      # Imágenes subidas (no incluir en Git)
├── tienda_ropa/
│   ├── settings.py             # Configuración principal
│   ├── urls.py                 # URLs del proyecto
│   └── wsgi.py
├── requirements.txt
├── Procfile
├── build.sh
├── .env.example
└── README.md
```

---

## Panel de administración

Accedé a `/admin/` con el superusuario creado. Desde ahí podés:

- **Configuración del Sitio**: editar nombre, slogan, teléfono, redes sociales, info de envíos, credenciales de MercadoPago
- **Imágenes del Carrusel**: subir, ordenar y activar/desactivar imágenes del slider
- **Categorías**: crear y ordenar categorías de productos
- **Colores y Talles**: gestionar las opciones disponibles
- **Productos**: crear productos con imágenes, precios, variantes y stock
- **Pedidos**: ver y gestionar pedidos con sus ítems
- **Sugerencias**: moderar comentarios de clientes

---

## Webhook de MercadoPago

Para recibir notificaciones de pago en tiempo real, configurá en MercadoPago:

```
URL del webhook: https://tu-app.onrender.com/mp/webhook/
```

---

## Licencia

Este proyecto es de uso privado. Todos los derechos reservados.
