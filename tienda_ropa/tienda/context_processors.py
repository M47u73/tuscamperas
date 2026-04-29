from .models import ConfiguracionSitio


def configuracion_global(request):
    """Inyecta la configuración del sitio en todos los templates."""
    config = ConfiguracionSitio.get()
    return {
        "config": config,
        "carrito_count": sum(
            item.get("cantidad", 0)
            for item in request.session.get("carrito", {}).values()
        ),
    }
