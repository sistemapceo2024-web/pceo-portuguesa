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
    COLOR_STATUS_GREEN,
    create_theme_toggle_switch,
    is_dark_mode
)
from data.auth_manager import AuthManager
from data.state import AppState

def build_login_view(page: ft.Page, on_login_success) -> ft.Control:
    """Construye la vista de autenticación oficial con validación SHA-256."""
    state = AppState()
    auth_mgr = AuthManager()

    # Campos de Entrada Limpios con adaptación dinámica bimodal
    username_field = ft.TextField(
        label="Usuario Institucional",
        hint_text="ej: master1, analista1, gobernador",
        prefix_icon=ft.Icons.ACCOUNT_CIRCLE_ROUNDED,
        border_radius=10,
        text_size=13,
        autofocus=True,
        border_color=COLOR_BORDER,
        color="#FFFFFF" if is_dark_mode() else COLOR_TEXT_PRIMARY,
        label_style=ft.TextStyle(color="#94A3B8" if is_dark_mode() else COLOR_TEXT_MUTED),
        bgcolor="#0B1528" if is_dark_mode() else "#F8FAFC"
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
        color="#FFFFFF" if is_dark_mode() else COLOR_TEXT_PRIMARY,
        label_style=ft.TextStyle(color="#94A3B8" if is_dark_mode() else COLOR_TEXT_MUTED),
        bgcolor="#0B1528" if is_dark_mode() else "#F8FAFC"
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
        uname = username_field.value
        pwd = password_field.value

        success, user, msg = auth_mgr.authenticate(uname, pwd)

        if success and user:
            error_container.visible = False
            state.login_user(user)
            on_login_success()
        else:
            error_text.value = msg
            error_container.visible = True
            page.update()

    # Permitir inicio de sesión al presionar Enter en cualquiera de los campos
    username_field.on_submit = do_login
    password_field.on_submit = do_login

    # Helper para autocompletar credenciales de prueba con un clic
    def quick_fill(uname: str, pwd: str):
        username_field.value = uname
        password_field.value = pwd
        error_container.visible = False
        page.update()

    quick_access_chips = ft.Container(
        content=ft.Column(
            spacing=6,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "Accesos Rápidos de Prueba:",
                    size=11,
                    weight=ft.FontWeight.W_500,
                    color=COLOR_TEXT_MUTED
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=6,
                    controls=[
                        ft.OutlinedButton(
                            content=ft.Text("Master 1", size=10, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_LIGHT),
                            style=ft.ButtonStyle(
                                padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                                shape=ft.RoundedRectangleBorder(radius=8),
                                side=ft.BorderSide(1, "#1E3A8A" if is_dark_mode() else "#BFDBFE")
                            ),
                            on_click=lambda e: quick_fill("master1", "Pceo2026*")
                        ),
                        ft.OutlinedButton(
                            content=ft.Text("Analista 1", size=10, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_LIGHT),
                            style=ft.ButtonStyle(
                                padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                                shape=ft.RoundedRectangleBorder(radius=8),
                                side=ft.BorderSide(1, "#1E3A8A" if is_dark_mode() else "#BFDBFE")
                            ),
                            on_click=lambda e: quick_fill("analista1", "Sala2026*")
                        ),
                        ft.OutlinedButton(
                            content=ft.Text("Gobernador", size=10, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_LIGHT),
                            style=ft.ButtonStyle(
                                padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                                shape=ft.RoundedRectangleBorder(radius=8),
                                side=ft.BorderSide(1, "#1E3A8A" if is_dark_mode() else "#BFDBFE")
                            ),
                            on_click=lambda e: quick_fill("gobernador", "Portuguesa2026")
                        ),
                    ]
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

                # Atajos rápidos de prueba
                quick_access_chips,

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
            color="#30000000" if is_dark_mode() else "#10000000",
            offset=ft.Offset(0, 6)
        ),
        width=440
    )

    # Barra superior permanente con interruptor de tema institucional (Sol / Luna)
    header_bar = ft.Container(
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=6,
                    controls=[
                        ft.Icon(ft.Icons.SHIELD_ROUNDED, size=18, color=COLOR_ELECTRIC_BLUE),
                        ft.Text("PCEO PORTUGUESA", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED)
                    ]
                ),
                create_theme_toggle_switch(
                    lambda is_dark: state.set_theme(is_dark),
                    is_dark=is_dark_mode()
                )
            ]
        ),
        padding=ft.Padding.symmetric(horizontal=24, vertical=14)
    )

    return ft.Container(
        content=ft.Column(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                header_bar,
                login_card,
                ft.Container(height=20)
            ],
            expand=True
        ),
        alignment=ft.Alignment(0, 0),
        expand=True,
        bgcolor=COLOR_BG_LIGHT
    )
