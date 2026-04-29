from django import forms
from .models import Pedido, Sugerencia


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = [
            "nombre", "email", "telefono",
            "tipo_entrega", "direccion", "ciudad", "codigo_postal", "notas"
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control", "placeholder": "Tu nombre completo"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control", "placeholder": "tu@email.com"
            }),
            "telefono": forms.TextInput(attrs={
                "class": "form-control", "placeholder": "+54 9 11 0000-0000"
            }),
            "tipo_entrega": forms.Select(attrs={"class": "form-select", "id": "id_tipo_entrega"}),
            "direccion": forms.TextInput(attrs={
                "class": "form-control", "placeholder": "Calle y número"
            }),
            "ciudad": forms.TextInput(attrs={
                "class": "form-control", "placeholder": "Ciudad / Localidad"
            }),
            "codigo_postal": forms.TextInput(attrs={
                "class": "form-control", "placeholder": "Código postal"
            }),
            "notas": forms.Textarea(attrs={
                "class": "form-control", "rows": 3,
                "placeholder": "Notas adicionales para el vendedor (opcional)"
            }),
        }
        labels = {
            "nombre": "Nombre completo",
            "email": "Correo electrónico",
            "telefono": "Teléfono",
            "tipo_entrega": "Forma de entrega",
            "direccion": "Dirección",
            "ciudad": "Ciudad / Localidad",
            "codigo_postal": "Código postal",
            "notas": "Notas adicionales",
        }


class SugerenciaForm(forms.ModelForm):
    class Meta:
        model = Sugerencia
        fields = ["nombre", "mensaje"]
        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control", "placeholder": "Tu nombre"
            }),
            "mensaje": forms.Textarea(attrs={
                "class": "form-control", "rows": 4,
                "placeholder": "Escribí tu sugerencia, comentario o agradecimiento..."
            }),
        }
        labels = {
            "nombre": "Nombre",
            "mensaje": "Mensaje",
        }
