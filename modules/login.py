"""
Pantalla de Inicio de Sesión y Autenticación Oficial
Puesto de Comando Estratégico Operacional del Estado Portuguesa
"""
import os
import flet as ft
from components.theme import (
    COLOR_NAVY_DARK,
    COLOR_NAVY_MEDIUM,
    COLOR_ELECTRIC_BLUE,
    COLOR_ELECTRIC_LIGHT,
    COLOR_SURFACE_WHITE,
    COLOR_SURFACE_ELEVATED,
    COLOR_BG_LIGHT,
    COLOR_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    COLOR_STATUS_RED,
    COLOR_STATUS_GREEN
)
from data.auth_manager import AuthManager
from data.state import AppState

def build_login_view(page: ft.Page, on_login_success) -> ft.Control:
    """Construye la vista de autenticación oficial con validación SHA-256."""
    state = AppState()
    auth_mgr = AuthManager()

    # Campos de Entrada Oficiales
    username_field = ft.TextField(
        label="Usuario Institucional",
        hint_text="ej: master1, analista1, gobernador",
        prefix_icon=ft.Icons.ACCOUNT_CIRCLE_ROUNDED,
        border_radius=10,
        text_size=13,
        autofocus=True,
        border_color=COLOR_BORDER,
        color=COLOR_TEXT_PRIMARY,
        label_style=ft.TextStyle(color=COLOR_TEXT_MUTED),
        bgcolor="#F8FAFC"
    )

    password_field = ft.TextField(
        label="Contraseña",
        hint_text="Ingrese su clave de acceso",
        prefix_icon=ft.Icons.LOCK_ROUNDED,
        password=True,
        can_reveal_password=True,
        border_radius=10,
        text_size=13,
        border_color=COLOR_BORDER,
        color=COLOR_TEXT_PRIMARY,
        label_style=ft.TextStyle(color=COLOR_TEXT_MUTED),
        bgcolor="#F8FAFC"
    )

    # Contenedor de Error Dinámico (Rojo claro institucional)
    error_text = ft.Text(
        "",
        color="#B91C1C",
        size=12,
        weight=ft.FontWeight.W_500
    )
    error_container = ft.Container(
        content=ft.Row(
            spacing=8,
            controls=[
                ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, color="#DC2626", size=18),
                ft.Container(content=error_text, expand=True)
            ]
        ),
        padding=10,
        bgcolor="#FEF2F2",
        border_radius=10,
        border=ft.Border.all(1, "#FCA5A5"),
        visible=False
    )

    def do_login(e=None):
        uname = (username_field.value or "").strip()
        pwd = (password_field.value or "").strip()

        if not uname or not pwd:
            error_text.value = "Por favor ingrese su usuario institucional y contraseña."
            error_container.visible = True
            page.update()
            return

        success, user, msg = auth_mgr.authenticate(uname, pwd)

        if success and user:
            # Validar cuenta activa
            if not user.get("activo", True):
                error_text.value = "Cuenta desactivada por la Coordinación Master. Contacte al administrador."
                error_container.visible = True
                page.update()
                return

            # Validar perfil y permisos institucionales
            user_role = (user.get("rol") or "").upper()
            if user_role not in ["MASTER", "ANALISTA", "EJECUTIVO"]:
                error_text.value = f"Perfil de usuario '{user_role}' no autorizado en el sistema."
                error_container.visible = True
                page.update()
                return

            error_container.visible = False
            password_field.value = ""
            state.login_user(user)
            state.is_authenticated = True
            on_login_success()
        else:
            error_text.value = msg or "Credenciales inválidas. Verifique su usuario y contraseña."
            error_container.visible = True
            page.update()

    # Permitir inicio de sesión al presionar Enter en cualquiera de los campos
    username_field.on_submit = do_login
    password_field.on_submit = do_login

    # Insignia de Seguridad Institucional
    security_badge = ft.Container(
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=6,
            controls=[
                ft.Icon(ft.Icons.LOCK_OUTLINE_ROUNDED, size=13, color=COLOR_TEXT_MUTED),
                ft.Text(
                    "Autenticación Segura SHA-256 • Acceso Oficial PCEO",
                    size=10.5,
                    weight=ft.FontWeight.W_500,
                    color=COLOR_TEXT_MUTED
                )
            ]
        ),
        padding=ft.Padding.symmetric(vertical=4)
    )

    # Logo Institucional Oficial PCEO (Dimensiones ampliadas: 180x130)
    logo_institucional = (
        ft.Container(
            content=ft.Image(src="logo_pceo.png", width=180, height=130),
            alignment=ft.Alignment(0, 0),
            padding=ft.Padding.only(top=4, bottom=2)
        )
        if os.path.exists("assets/logo_pceo.png")
        else ft.Container(
            content=ft.Icon(
                ft.Icons.ACCOUNT_BALANCE_ROUNDED,
                size=44,
                color="#FFFFFF"
            ),
            width=72,
            height=72,
            border_radius=36,
            bgcolor=COLOR_NAVY_DARK,
            alignment=ft.Alignment(0, 0),
            border=ft.Border.all(3, COLOR_ELECTRIC_BLUE)
        )
    )

    login_card = ft.Container(
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
            controls=[
                # Escudo o Isotipo Institucional
                logo_institucional,

                # Títulos Institucionales
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=3,
                    controls=[
                        ft.Text(
                            "GOBERNACIÓN DE PORTUGUESA",
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_ELECTRIC_LIGHT,
                            style=ft.TextStyle(letter_spacing=1.5)
                        ),
                        ft.Text(
                            "Puesto de Comando Estratégico Operacional del Estado Portuguesa",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_TEXT_PRIMARY,
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Text(
                            "Sistema Integrado de Seguimiento Operativo (SIGSO)",
                            size=12,
                            color=COLOR_TEXT_MUTED,
                            text_align=ft.TextAlign.CENTER
                        ),
                    ]
                ),

                ft.Divider(color=COLOR_BORDER, height=1),

                # Formulario de Acceso
                ft.Column(
                    spacing=12,
                    controls=[
                        username_field,
                        password_field,
                        error_container
                    ]
                ),

                # Botón de Inicio de Sesión
                ft.FilledButton(
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=8,
                        tight=True,
                        controls=[
                            ft.Text("Ingresar al Tablero de Control", size=14, weight=ft.FontWeight.BOLD),
                            ft.Icon(ft.Icons.ARROW_FORWARD_ROUNDED, size=18)
                        ]
                    ),
                    style=ft.ButtonStyle(
                        bgcolor=COLOR_ELECTRIC_BLUE,
                        color="#FFFFFF",
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.Padding.symmetric(vertical=16)
                    ),
                    width=380,
                    on_click=do_login
                ),

                # Insignia de seguridad criptográfica
                security_badge,

                # Pie Institucional
                ft.Text(
                    "PORTUGUESA EL COMPROMISO ES CONTIGO",
                    size=11,
                    weight=ft.FontWeight.BOLD,
                    color=COLOR_ELECTRIC_LIGHT,
                    text_align=ft.TextAlign.CENTER
                )
            ]
        ),
        bgcolor=COLOR_SURFACE_WHITE,
        padding=24,
        border_radius=20,
        border=ft.Border.all(1, COLOR_BORDER),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=20,
            color="#15000000",
            offset=ft.Offset(0, 6)
        ),
        width=440
    )

    return ft.Container(
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[login_card]
        ),
        alignment=ft.Alignment(0, 0),
        expand=True,
        bgcolor=COLOR_BG_LIGHT
    )
