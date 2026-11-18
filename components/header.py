"""
Encabezado Institucional y Barra Superior
Puesto de Comando Estratégico Operacional del Estado Portuguesa
"""
import os
import flet as ft
from components.theme import (
    COLOR_NAVY_DARK,
    COLOR_ELECTRIC_BLUE,
    COLOR_SURFACE_WHITE,
    COLOR_STATUS_GREEN,
    COLOR_STATUS_AMBER
)
from data.models import ROLE_EDITOR, ROLE_VIEWER

def create_institutional_header(
    title: str = "Puesto de Comando Estratégico Operacional del Estado Portuguesa (PCEO)",
    subtitle: str = None,
    current_role: str = None,
    show_back_button: bool = False,
    on_back_click=None,
    on_logout_click=None,
    on_switch_role_click=None,
    on_users_click=None,
    on_theme_toggle=None,
    user_display_name: str = None,
    leading_logo: ft.Control = None,
    show_user_chip: bool = False
) -> ft.Container:
    """Crea la barra de navegación institucional superior con identidad PCEO."""
    from data.state import AppState
    state = AppState()
    
    active_role = current_role if current_role else state.current_role
    active_user_name = user_display_name if user_display_name else state.get_user_display_name()

    # Configuración de apariencia según rol oficial
    if active_role == "MASTER":
        role_label = "MASTER"
        role_icon = ft.Icons.ADMIN_PANEL_SETTINGS_ROUNDED
        role_bg = "#7C3AED"  # Púrpura Imperial Master
    elif active_role == "ANALISTA" or active_role == ROLE_EDITOR or active_role == "Equipo Técnico (Editor)":
        role_label = "ANALISTA"
        role_icon = ft.Icons.BUILD_ROUNDED
        role_bg = COLOR_ELECTRIC_BLUE
    else:
        role_label = "EJECUTIVO"
        role_icon = ft.Icons.VISIBILITY_ROUNDED
        role_bg = "#475569"  # Slate institucional

    # Chip con Rol y Nombre de Usuario
    role_controls = [
        ft.Icon(role_icon, size=13, color="#FFFFFF"),
        ft.Text(role_label, size=10, weight=ft.FontWeight.BOLD, color="#FFFFFF")
    ]
    if active_user_name and active_user_name != "Usuario Conectado":
        # Formato compacto del nombre para no saturar la barra
        short_name = active_user_name.split("—")[0].strip()
        role_controls.extend([
            ft.Text("•", size=10, color="#CBD5E1"),
            ft.Text(short_name, size=10, weight=ft.FontWeight.W_500, color="#F8FAFC", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)
        ])

    role_chip = ft.Container(
        content=ft.Row(
            spacing=5,
            tight=True,
            controls=role_controls
        ),
        padding=ft.Padding.symmetric(horizontal=8, vertical=4),
        bgcolor=role_bg,
        border_radius=12,
        tooltip=f"Usuario Conectado: {active_user_name} ({active_role})"
    )

    left_controls = []
    if show_back_button:
        left_controls.append(
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
                icon_color="#FFFFFF",
                icon_size=18,
                tooltip="Volver al Resumen Ejecutivo",
                on_click=on_back_click
            )
        )

    if leading_logo:
        left_controls.append(
            ft.Container(
                content=leading_logo,
                padding=ft.Padding.only(right=4)
            )
        )
    elif not show_back_button:
        pceo_logo = (
            ft.Image(src="logo_pceo.png", width=36, height=36)
            if os.path.exists("assets/logo_pceo.png")
            else ft.Icon(ft.Icons.SHIELD_ROUNDED, color=COLOR_ELECTRIC_BLUE, size=24)
        )
        left_controls.append(
            ft.Container(
                content=pceo_logo,
                padding=ft.Padding.only(right=6)
            )
        )

    left_controls.append(
        ft.Column(
            spacing=1,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Text(
                            title,
                            size=15,
                            weight=ft.FontWeight.BOLD,
                            color="#FFFFFF",
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS
                        ),
                    ]
                )
            ]
        )
    )

    if subtitle:
        left_controls[-1].controls.append(
            ft.Text(
                subtitle,
                size=11,
                color="#94A3B8",
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS
            )
        )

    right_controls = []

    if show_user_chip or on_logout_click or on_switch_role_click:
        right_controls.append(role_chip)
        if on_users_click and active_role == "MASTER":
            right_controls.append(
                ft.IconButton(
                    icon=ft.Icons.MANAGE_ACCOUNTS_ROUNDED,
                    icon_color="#38BDF8",
                    icon_size=20,
                    tooltip="Gestión de Usuarios y Auditoría (Master)",
                    on_click=on_users_click
                )
            )
        if on_switch_role_click and active_role == "MASTER":
            right_controls.append(
                ft.IconButton(
                    icon=ft.Icons.SWAP_HORIZ_ROUNDED,
                    icon_color="#CBD5E1",
                    icon_size=20,
                    tooltip="Alternar Rol Rápido (Master)",
                    on_click=on_switch_role_click
                )
            )
        if on_logout_click:
            right_controls.append(
                ft.IconButton(
                    icon=ft.Icons.LOGOUT_ROUNDED,
                    icon_color="#EF4444",
                    icon_size=18,
                    tooltip="Cerrar Sesión",
                    on_click=on_logout_click
                )
            )

    return ft.Container(
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=left_controls,
                    expand=True
                ),
                ft.Row(
                    spacing=4,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=right_controls
                )
            ]
        ),
        bgcolor=COLOR_NAVY_DARK,
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        border=ft.Border.only(bottom=ft.BorderSide(2, COLOR_ELECTRIC_BLUE))
    )
