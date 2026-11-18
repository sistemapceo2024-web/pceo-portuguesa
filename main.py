"""
Aplicación Móvil Flet (Material Design 3)
Secretaría Superior de Operaciones Generales de Portuguesa
Gobernación del Estado Portuguesa

Fase 1:
- Pantalla de Login con selector de rol de prueba ('Equipo Técnico (Editor)' / 'Despacho Gobernador (Solo Lectura)').
- Pantalla principal 'Resumen Ejecutivo' con las 8 tarjetas KPI de los planes de gobierno.
- Módulo detallado 'Fiesta del Agua' con KPIs dinámicos, selector de los 14 municipios, 3 pestañas y control de permisos por rol.
"""
import os
import sys

# Fijar directorio base para rutas relativas consistentes en entorno web y CLI
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if os.getcwd() != BASE_DIR:
    os.chdir(BASE_DIR)

import flet as ft

# Wrapper universal de compatibilidad Flet v0.80+ y Flet 1.x
def _compat_run_app(*args, **kwargs):
    target = kwargs.pop("target", None)
    if target is None and len(args) > 0:
        target = args[0]
        args = args[1:]
    if hasattr(ft, "run") and callable(getattr(ft, "run", None)):
        return ft.run(target, *args, **kwargs)
    elif hasattr(ft, "app") and callable(getattr(ft, "app", None)):
        return ft.app(target=target, *args, **kwargs)

if not hasattr(ft, "app"):
    ft.app = _compat_run_app

from components.theme import (
    COLOR_BG_LIGHT,
    COLOR_NAVY_DARK,
    COLOR_ELECTRIC_BLUE,
    COLOR_SURFACE_WHITE,
    COLOR_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    is_dark_mode,
    set_theme_mode
)
from data.models import ROLE_EDITOR, ROLE_VIEWER
from data.state import AppState
from modules.login import build_login_view
from modules.executive_summary import build_executive_summary_view
from modules.fiesta_agua import build_fiesta_agua_view
from modules.cero_botes import build_cero_botes_view
from modules.tramos_caidos import build_tramos_caidos_view
from modules.ruta_hidrojet import build_ruta_hidrojet_view
from modules.fiesta_luz import build_fiesta_luz_view
from modules.puentes import build_puentes_view
from modules.cero_huecos import build_cero_huecos_view
from modules.vialidad import build_vialidad_view
from modules.salud import build_salud_view
from modules.cancha_para_todos import build_cancha_para_todos_view
from modules.canchas import build_canchas_view
from modules.escuelas import build_escuelas_view
from modules.construye_casa import build_construye_casa_view
from modules.construye_tu_casa import build_construye_tu_casa_view
from modules.canalizacion import build_canalizacion_view
from modules.usuarios import build_usuarios_view

PLAN_VIEW_MAP = {
    "fiesta_agua": build_fiesta_agua_view,
    "cero_botes": build_cero_botes_view,
    "tramos_caidos": build_tramos_caidos_view,
    "ruta_hidrojet": build_ruta_hidrojet_view,
    "cero_huecos": build_cero_huecos_view,
    "cero_hueco": build_cero_huecos_view,
    "usuarios": build_usuarios_view,
    "fiesta_luz": build_fiesta_luz_view,
    "puentes": build_puentes_view,
    "vialidad": build_vialidad_view,
    "salud": build_salud_view,
    "canchas": build_cancha_para_todos_view,
    "cancha_para_todos": build_cancha_para_todos_view,
    "una_cancha_para_todos": build_cancha_para_todos_view,
    "educacion": build_escuelas_view,
    "escuelas": build_escuelas_view,
    "construye_casa": build_construye_casa_view,
    "construye_tu_casa": build_construye_tu_casa_view,
    "canalizacion": build_canalizacion_view,
    "canalizaciones": build_canalizacion_view,
    "bermas": build_canalizacion_view,
}

def main(page: ft.Page):
    # Compatibilidad de padding y diálogos para Flet
    if hasattr(ft, "Padding") and not hasattr(ft.padding, "only"):
        ft.padding.only = ft.Padding.only
    if hasattr(ft, "Margin") and not hasattr(ft.margin, "only"):
        ft.margin.only = ft.Margin.only
    if not hasattr(ft, "colors") and hasattr(ft, "Colors"):
        ft.colors = ft.Colors
    if not hasattr(ft, "border") and hasattr(ft, "Border"):
        ft.border = ft.Border

    if not hasattr(page, "open"):
        page.open = lambda d: page.show_dialog(d)
    if not hasattr(page, "close"):
        page.close = lambda d=None: page.pop_dialog()

    # Configuración de Ventana y Estética Centro de Comando Ejecutivo (Dark Executive Theme)
    page.title = "Puesto de Comando Estratégico Operacional - Gobernación de Portuguesa"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = COLOR_BG_LIGHT
    page.padding = 0

    # Dimensiones sugeridas para Tablero Ejecutivo y Panel de Control
    page.window.width = 1200
    page.window.height = 850
    page.window.resizable = True
    page.window.min_width = 400
    page.window.min_height = 650

    state = AppState()
    current_view_name = "login"

    # Diálogo rápido para alternar roles de prueba desde la barra superior (Exclusivo Master)
    def open_quick_role_switcher():
        role_radio = ft.RadioGroup(
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Radio(value="MASTER", label="Coordinador Master (Control Total)"),
                    ft.Radio(value="ANALISTA", label="Analista de Sala (Editor Completo)"),
                    ft.Radio(value="EJECUTIVO", label="Ejecutivo / Despacho (Solo Lectura)"),
                ]
            ),
            value=state.current_role
        )

        def switch_and_close(e):
            new_role = role_radio.value
            state.set_role(new_role)
            if hasattr(page, "close"):
                page.close()
            elif hasattr(page, "pop_dialog"):
                page.pop_dialog()
            render_current_view()
            
            # Notificación visual
            snack = ft.SnackBar(
                content=ft.Text(f"Rol alternado a: {new_role}", color="#FFFFFF"),
                bgcolor=COLOR_NAVY_DARK
            )
            if hasattr(page, "open"):
                page.open(snack)
            elif hasattr(page, "show_dialog"):
                page.show_dialog(snack)
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            bgcolor=COLOR_SURFACE_WHITE,
            title=ft.Row(
                spacing=8,
                controls=[
                    ft.Icon(ft.Icons.SWAP_HORIZ_ROUNDED, color=COLOR_ELECTRIC_BLUE),
                    ft.Text("Alternar Rol de Prueba", size=15, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY)
                ]
            ),
            content=ft.Container(
                content=ft.Column(
                    tight=True,
                    spacing=8,
                    controls=[
                        ft.Text(
                            "Seleccione el perfil para verificar los permisos de edición o solo lectura en tiempo real:",
                            size=12,
                            color=COLOR_TEXT_SECONDARY
                        ),
                        role_radio
                    ]
                ),
                width=360,
                padding=ft.Padding.symmetric(vertical=4)
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cancelar"),
                    on_click=lambda e: (page.close() if hasattr(page, "close") else page.pop_dialog()) or page.update()
                ),
                ft.FilledButton(
                    content=ft.Text("Aplicar Rol"),
                    style=ft.ButtonStyle(bgcolor=COLOR_ELECTRIC_BLUE, color="#FFFFFF"),
                    on_click=switch_and_close
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=12)
        )
        if hasattr(page, "open"):
            page.open(dialog)
        else:
            page.show_dialog(dialog)
        page.update()

    def handle_theme_toggle(is_dark: bool = None):
        """Manejador central para alternar al instante entre Modo Oscuro Ejecutivo y Modo Claro Institucional."""
        if is_dark is None:
            is_dark = not state.is_dark_mode
        if state.is_dark_mode != is_dark:
            state.is_dark_mode = is_dark
            set_theme_mode(is_dark)
        page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
        page.bgcolor = COLOR_BG_LIGHT
        app_canvas.bgcolor = COLOR_BG_LIGHT
        render_current_view()
        page.update()

    # Suscribir manejador a cambios de tema en AppState
    state.theme_change_listeners.clear()
    state.theme_change_listeners.append(handle_theme_toggle)

    def navigate_to(view_name: str):
        nonlocal current_view_name
        current_view_name = view_name
        render_current_view()

    # Contenedor con AnimatedSwitcher para transiciones y animaciones fluidas instantáneas
    animated_switcher = ft.AnimatedSwitcher(
        content=ft.Container(expand=True),
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=150,
        reverse_duration=100,
        switch_in_curve=ft.AnimationCurve.EASE_OUT,
        switch_out_curve=ft.AnimationCurve.EASE_IN,
        expand=True
    )

    app_canvas = ft.Container(
        expand=True,
        bgcolor=COLOR_BG_LIGHT,
        content=animated_switcher,
        animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
    )

    def handle_logout():
        state.logout_user()
        navigate_to("login")

    def render_current_view():
        view_key = f"{current_view_name}_{'dark' if state.is_dark_mode else 'light'}"

        if current_view_name == "login":
            view = build_login_view(
                page=page,
                on_login_success=lambda: navigate_to("executive_summary")
            )
        elif current_view_name == "executive_summary":
            view = build_executive_summary_view(
                page=page,
                on_open_plan=lambda pid: navigate_to(pid),
                on_switch_role=open_quick_role_switcher,
                on_logout=handle_logout,
                on_open_users=lambda e=None: navigate_to("usuarios"),
                on_theme_toggle=handle_theme_toggle
            )
        elif current_view_name in PLAN_VIEW_MAP:
            view = PLAN_VIEW_MAP[current_view_name](
                page=page,
                on_back_to_summary=lambda: navigate_to("executive_summary"),
                on_switch_role=open_quick_role_switcher,
                on_logout=handle_logout
            )
        else:
            view = ft.Text("Vista no encontrada")

        # Envoltorio adaptativo con animación de opacidad y clave única para AnimatedSwitcher
        view_wrapper = ft.Container(
            key=view_key,
            content=view,
            expand=True,
            bgcolor=COLOR_BG_LIGHT,
            animate_opacity=150
        )

        animated_switcher.content = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[view_wrapper],
            expand=True
        )
        page.update()

    # Iniciar aplicación en vista Login
    page.add(app_canvas)
    render_current_view()

if __name__ == "__main__":
    # Si el usuario especifica --desktop ejecuta ventana nativa de escritorio
    if "--desktop" in sys.argv:
        ft.app(target=main, assets_dir="assets")
    else:
        # Modo servidor web interactivo accesible por navegador en http://localhost:8550
        print("Iniciando servidor web PCEO en http://localhost:8550 ...")
        ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550, assets_dir="assets")
