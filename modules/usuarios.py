"""
Módulo de Gestión de Usuarios y Bitácora de Auditoría (Exclusivo Master)
Puesto de Comando Estratégico Operacional del Estado Portuguesa
"""
import os
import flet as ft
from components.theme import (
    COLOR_NAVY_DARK,
    COLOR_NAVY_MEDIUM,
    COLOR_ELECTRIC_BLUE,
    COLOR_SURFACE_WHITE,
    COLOR_BG_LIGHT,
    COLOR_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    COLOR_STATUS_GREEN,
    COLOR_STATUS_RED,
    COLOR_STATUS_AMBER
)
from components.header import create_institutional_header
from data.auth_manager import AuthManager
from data.state import AppState

def build_usuarios_view(
    page: ft.Page,
    on_back_to_summary,
    on_logout,
    on_switch_role=None
) -> ft.Control:
    """Construye el panel de administración de cuentas y bitácora de auditoría."""
    state = AppState()
    auth_mgr = AuthManager()

    # Si el usuario no es Master, mostrar pantalla de acceso restringido
    if not state.is_master():
        return ft.Container(
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
                controls=[
                    ft.Icon(ft.Icons.SECURITY_ROUNDED, size=64, color=COLOR_STATUS_RED),
                    ft.Text(
                        "Acceso Restringido — Módulo Master",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_NAVY_DARK
                    ),
                    ft.Text(
                        "Este módulo está reservado exclusivamente para la Coordinación Master del PCEO.",
                        size=13,
                        color=COLOR_TEXT_SECONDARY,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.FilledButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.ARROW_BACK_ROUNDED, size=18),
                            ft.Text("Volver al Tablero Principal")
                        ], tight=True),
                        style=ft.ButtonStyle(bgcolor=COLOR_ELECTRIC_BLUE, color="#FFFFFF"),
                        on_click=lambda e: on_back_to_summary()
                    )
                ]
            ),
            alignment=ft.Alignment(0, 0),
            padding=32,
            expand=True
        )

    # Variables de estado local
    search_user_query = ""
    audit_module_filter = "Todos"
    audit_search_query = ""

    # Control de permisos para modificación de contraseñas (exclusivo @master1 / MASTER absoluto)
    current_username = (state.get_username() or "").lower().strip()
    can_change_password = state.is_master() and (current_username in ("master1", "@master1", "master"))

    # Header institucional
    header = create_institutional_header(
        title="Gestión de Usuarios y Auditoría",
        subtitle="Puesto de Comando Estratégico Operacional",
        current_role="MASTER",
        show_back_button=True,
        on_back_click=lambda e: on_back_to_summary(),
        on_logout_click=on_logout
    )

    # Contenedores dinámicos para actualización reactiva
    users_list_container = ft.Column(spacing=10)
    audit_list_container = ft.Column(spacing=10)
    kpis_users_container = ft.Row(spacing=8)
    kpis_audit_container = ft.Row(spacing=8)

    # -------------------------------------------------------------
    # HELPERS Y DIÁLOGOS MODALES (COMPATIBLES FLET v0.80+)
    # -------------------------------------------------------------
    def show_feedback_snack(message: str, is_error: bool = False):
        snack = ft.SnackBar(
            content=ft.Text(message, color="#FFFFFF", weight=ft.FontWeight.W_500),
            bgcolor=COLOR_STATUS_RED if is_error else COLOR_STATUS_GREEN
        )
        if hasattr(page, "open"):
            page.open(snack)
        elif hasattr(page, "show_dialog"):
            page.show_dialog(snack)
        page.update()

    def close_current_dialog():
        if hasattr(page, "close"):
            page.close()
        elif hasattr(page, "pop_dialog"):
            page.pop_dialog()
        page.update()

    # Modal: Crear Nuevo Usuario
    def open_create_user_modal(e):
        txt_username = ft.TextField(
            label="Nombre de Usuario (@usuario)",
            hint_text="ej: analista4, director_sala",
            prefix_icon=ft.Icons.ALTERNATE_EMAIL_ROUNDED,
            autofocus=True
        )
        txt_nombre = ft.TextField(
            label="Nombre Completo / Cargo",
            hint_text="ej: Ing. Pedro Pérez — Sala Situacional",
            prefix_icon=ft.Icons.BADGE_ROUNDED
        )
        dd_rol = ft.Dropdown(
            label="Rol Institucional",
            options=[
                ft.dropdown.Option("ANALISTA", "Analista de Sala (Editor Completo)"),
                ft.dropdown.Option("EJECUTIVO", "Ejecutivo / Despacho (Solo Lectura)"),
                ft.dropdown.Option("MASTER", "Coordinador Master (Control Total)")
            ],
            value="ANALISTA"
        )
        txt_clave = ft.TextField(
            label="Contraseña Inicial",
            hint_text="Mínimo 4 caracteres",
            prefix_icon=ft.Icons.LOCK_ROUNDED,
            password=True,
            can_reveal_password=True,
            value="Pceo2026*"
        )
        lbl_error = ft.Text("", color=COLOR_STATUS_RED, size=12, visible=False)

        def save_new_user(ev):
            uname = txt_username.value
            nombre = txt_nombre.value
            rol = dd_rol.value
            clave = txt_clave.value

            success, msg = auth_mgr.create_user(
                username=uname,
                nombre=nombre,
                password=clave,
                rol=rol,
                creator_username=state.get_username()
            )

            if success:
                close_current_dialog()
                refresh_users_tab()
                refresh_audit_tab()
                show_feedback_snack(msg)
            else:
                lbl_error.value = msg
                lbl_error.visible = True
                page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.PERSON_ADD_ROUNDED, color=COLOR_ELECTRIC_BLUE),
                ft.Text("Registrar Nueva Cuenta", size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
            ], spacing=8),
            content=ft.Container(
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    controls=[
                        ft.Text(
                            "Ingrese los datos del nuevo funcionario para otorgarle acceso al sistema:",
                            size=12,
                            color=COLOR_TEXT_SECONDARY
                        ),
                        txt_username,
                        txt_nombre,
                        dd_rol,
                        txt_clave,
                        lbl_error
                    ]
                ),
                width=380,
                padding=ft.Padding.symmetric(vertical=6)
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cancelar"),
                    on_click=lambda ev: close_current_dialog()
                ),
                ft.FilledButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CHECK_ROUNDED, size=16),
                        ft.Text("Crear Cuenta")
                    ], tight=True),
                    style=ft.ButtonStyle(bgcolor=COLOR_ELECTRIC_BLUE, color="#FFFFFF"),
                    on_click=save_new_user
                )
            ],
            shape=ft.RoundedRectangleBorder(radius=12)
        )

        if hasattr(page, "open"):
            page.open(dialog)
        else:
            page.show_dialog(dialog)
        page.update()

    # Modal: Editar Usuario
    def open_edit_user_modal(user_dict: dict):
        txt_nombre = ft.TextField(
            label="Nombre Completo / Cargo",
            value=user_dict.get("nombre", ""),
            prefix_icon=ft.Icons.BADGE_ROUNDED
        )
        dd_rol = ft.Dropdown(
            label="Rol Institucional",
            options=[
                ft.dropdown.Option("ANALISTA", "Analista de Sala (Editor Completo)"),
                ft.dropdown.Option("EJECUTIVO", "Ejecutivo / Despacho (Solo Lectura)"),
                ft.dropdown.Option("MASTER", "Coordinador Master (Control Total)")
            ],
            value=user_dict.get("rol", "ANALISTA")
        )
        sw_activo = ft.Switch(
            label="Cuenta Activa y Habilitada",
            value=user_dict.get("activo", True),
            active_color=COLOR_STATUS_GREEN
        )
        lbl_error = ft.Text("", color=COLOR_STATUS_RED, size=12, visible=False)

        def save_edited_user(ev):
            success, msg = auth_mgr.update_user(
                username=user_dict["username"],
                nombre=txt_nombre.value,
                rol=dd_rol.value,
                activo=sw_activo.value,
                editor_username=state.get_username()
            )

            if success:
                close_current_dialog()
                refresh_users_tab()
                refresh_audit_tab()
                show_feedback_snack(msg)
            else:
                lbl_error.value = msg
                lbl_error.visible = True
                page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.EDIT_ROUNDED, color=COLOR_ELECTRIC_BLUE),
                ft.Text(f"Editar @{user_dict['username']}", size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
            ], spacing=8),
            content=ft.Container(
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    controls=[
                        txt_nombre,
                        dd_rol,
                        sw_activo,
                        lbl_error
                    ]
                ),
                width=380,
                padding=ft.Padding.symmetric(vertical=6)
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cancelar"),
                    on_click=lambda ev: close_current_dialog()
                ),
                ft.FilledButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.SAVE_ROUNDED, size=16),
                        ft.Text("Guardar Cambios")
                    ], tight=True),
                    style=ft.ButtonStyle(bgcolor=COLOR_ELECTRIC_BLUE, color="#FFFFFF"),
                    on_click=save_edited_user
                )
            ],
            shape=ft.RoundedRectangleBorder(radius=12)
        )

        if hasattr(page, "open"):
            page.open(dialog)
        else:
            page.show_dialog(dialog)
        page.update()

    # Modal: Restablecer Contraseña (Exclusivo @master1)
    def open_reset_password_modal(user_dict: dict):
        if not can_change_password:
            show_feedback_snack(
                "Acceso restringido: Solo el maestro principal (@master1) tiene autorización para modificar contraseñas.",
                is_error=True
            )
            return

        txt_clave = ft.TextField(
            label="Nueva Contraseña",
            hint_text="Mínimo 4 caracteres",
            prefix_icon=ft.Icons.KEY_ROUNDED,
            password=True,
            can_reveal_password=True,
            autofocus=True,
            text_size=12
        )
        txt_confirm_clave = ft.TextField(
            label="Confirmar Nueva Contraseña",
            hint_text="Repita la nueva contraseña",
            prefix_icon=ft.Icons.LOCK_RESET_ROUNDED,
            password=True,
            can_reveal_password=True,
            text_size=12
        )
        lbl_error = ft.Text("", color=COLOR_STATUS_RED, size=12, visible=False)

        def save_new_password(ev):
            c1 = (txt_clave.value or "").strip()
            c2 = (txt_confirm_clave.value or "").strip()

            if not c1:
                lbl_error.value = "Por favor ingrese la nueva contraseña."
                lbl_error.visible = True
                page.update()
                return

            if len(c1) < 4:
                lbl_error.value = "La contraseña debe tener al menos 4 caracteres."
                lbl_error.visible = True
                page.update()
                return

            if c1 != c2:
                lbl_error.value = "Las contraseñas no coinciden. Por favor verifíquelas."
                lbl_error.visible = True
                page.update()
                return

            success, msg = auth_mgr.reset_password(
                username=user_dict["username"],
                new_password=c1,
                master_username=state.get_username()
            )

            if success:
                close_current_dialog()
                refresh_audit_tab()
                show_feedback_snack(f"Contraseña de @{user_dict['username']} actualizada y auditada exitosamente.")
            else:
                lbl_error.value = msg
                lbl_error.visible = True
                page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.KEY_ROUNDED, color=COLOR_ELECTRIC_BLUE, size=20),
                ft.Text(f"Modificar Contraseña: @{user_dict['username']}", size=15, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
            ], spacing=8),
            content=ft.Container(
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    controls=[
                        ft.Text(
                            f"Establezca y confirme la nueva credencial de acceso para {user_dict.get('nombre', '')}:",
                            size=12,
                            color=COLOR_TEXT_SECONDARY
                        ),
                        txt_clave,
                        txt_confirm_clave,
                        lbl_error
                    ]
                ),
                width=380,
                padding=ft.Padding.symmetric(vertical=6)
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cancelar"),
                    on_click=lambda ev: close_current_dialog()
                ),
                ft.FilledButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CHECK_ROUNDED, size=16),
                        ft.Text("Guardar Contraseña")
                    ], tight=True),
                    style=ft.ButtonStyle(bgcolor=COLOR_ELECTRIC_BLUE, color="#FFFFFF"),
                    on_click=save_new_password
                )
            ],
            shape=ft.RoundedRectangleBorder(radius=12)
        )

        if hasattr(page, "open"):
            page.open(dialog)
        else:
            page.show_dialog(dialog)
        page.update()

    # -------------------------------------------------------------
    # PESTAÑA 1: ADMINISTRACIÓN DE CUENTAS
    # -------------------------------------------------------------
    def render_user_card(user: dict) -> ft.Container:
        rol = user.get("rol", "ANALISTA")
        activo = user.get("activo", True)

        if rol == "MASTER":
            badge_color = "#7C3AED"
            icon_name = ft.Icons.ADMIN_PANEL_SETTINGS_ROUNDED
        elif rol == "ANALISTA":
            badge_color = COLOR_ELECTRIC_BLUE
            icon_name = ft.Icons.BUILD_ROUNDED
        else:
            badge_color = "#475569"
            icon_name = ft.Icons.VISIBILITY_ROUNDED

        status_chip = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED if activo else ft.Icons.CANCEL_ROUNDED, size=12, color="#FFFFFF"),
                ft.Text("ACTIVO" if activo else "INACTIVO", size=9, weight=ft.FontWeight.BOLD, color="#FFFFFF")
            ], spacing=3, tight=True),
            padding=ft.Padding.symmetric(horizontal=6, vertical=2),
            bgcolor=COLOR_STATUS_GREEN if activo else COLOR_STATUS_RED,
            border_radius=8
        )

        role_chip = ft.Container(
            content=ft.Row([
                ft.Icon(icon_name, size=12, color="#FFFFFF"),
                ft.Text(rol, size=9, weight=ft.FontWeight.BOLD, color="#FFFFFF")
            ], spacing=3, tight=True),
            padding=ft.Padding.symmetric(horizontal=6, vertical=2),
            bgcolor=badge_color,
            border_radius=8
        )

        return ft.Container(
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row([
                                ft.Container(
                                    content=ft.Icon(icon_name, size=20, color="#FFFFFF"),
                                    width=38,
                                    height=38,
                                    border_radius=19,
                                    bgcolor=badge_color,
                                    alignment=ft.Alignment(0, 0)
                                ),
                                ft.Column([
                                    ft.Text(user.get("nombre", "Sin Nombre"), size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                    ft.Text(f"@{user.get('username', '')}", size=11, color=COLOR_ELECTRIC_BLUE, weight=ft.FontWeight.W_500)
                                ], spacing=1)
                            ], spacing=10),
                            ft.Row([role_chip, status_chip], spacing=4)
                        ]
                    ),
                    ft.Divider(height=1, color="#F1F5F9"),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Row([
                                ft.Icon(ft.Icons.ACCESS_TIME_ROUNDED, size=13, color=COLOR_TEXT_MUTED),
                                ft.Text(f"Último acceso: {user.get('ultimo_acceso', 'Nunca')}", size=11, color=COLOR_TEXT_MUTED)
                            ], spacing=4),
                            ft.Row([
                                ft.OutlinedButton(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.KEY_ROUNDED, size=14),
                                        ft.Text("Clave", size=11)
                                    ], tight=True),
                                    style=ft.ButtonStyle(
                                        padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                                        shape=ft.RoundedRectangleBorder(radius=8)
                                    ),
                                    visible=can_change_password,
                                    tooltip="Modificar contraseña (Exclusivo @master1)" if can_change_password else None,
                                    on_click=lambda ev, u=user: open_reset_password_modal(u)
                                ),
                                ft.OutlinedButton(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.EDIT_ROUNDED, size=14),
                                        ft.Text("Editar", size=11)
                                    ], tight=True),
                                    style=ft.ButtonStyle(
                                        padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                                        shape=ft.RoundedRectangleBorder(radius=8)
                                    ),
                                    on_click=lambda ev, u=user: open_edit_user_modal(u)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.POWER_SETTINGS_NEW_ROUNDED,
                                    icon_color=COLOR_STATUS_GREEN if activo else COLOR_STATUS_RED,
                                    icon_size=18,
                                    tooltip="Desactivar Cuenta" if activo else "Activar Cuenta",
                                    on_click=lambda ev, u=user: toggle_user_status(u)
                                )
                            ], spacing=4)
                        ]
                    )
                ]
            ),
            padding=12,
            bgcolor=COLOR_SURFACE_WHITE,
            border_radius=12,
            border=ft.Border.all(1, COLOR_BORDER),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=4, color="#0A000000", offset=ft.Offset(0, 1))
        )

    def toggle_user_status(user: dict):
        uname = user["username"]
        success, msg = auth_mgr.toggle_user_active(uname, master_username=state.get_username())
        if success:
            refresh_users_tab()
            refresh_audit_tab()
            show_feedback_snack(msg)
        else:
            show_feedback_snack(msg, is_error=True)

    def refresh_users_tab():
        all_users = auth_mgr.get_users()
        filtered = all_users

        if search_user_query:
            q = search_user_query.lower()
            filtered = [
                u for u in all_users
                if q in u.get("username", "").lower() or q in u.get("nombre", "").lower() or q in u.get("rol", "").lower()
            ]

        # Actualizar KPIs
        total = len(all_users)
        masters = sum(1 for u in all_users if u.get("rol") == "MASTER")
        analistas = sum(1 for u in all_users if u.get("rol") == "ANALISTA")
        ejecutivos = sum(1 for u in all_users if u.get("rol") == "EJECUTIVO")

        def make_kpi(label: str, val: int, color: str, icon_name):
            return ft.Container(
                content=ft.Column(
                    spacing=2,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(icon_name, size=16, color=color),
                        ft.Text(str(val), size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Text(label, size=10, color=COLOR_TEXT_MUTED, text_align=ft.TextAlign.CENTER)
                    ]
                ),
                padding=8,
                bgcolor=COLOR_SURFACE_WHITE,
                border_radius=10,
                border=ft.Border.all(1, COLOR_BORDER),
                expand=True
            )

        kpis_users_container.controls = [
            make_kpi("Total Cuentas", total, COLOR_ELECTRIC_BLUE, ft.Icons.PEOPLE_ROUNDED),
            make_kpi("Masters", masters, "#7C3AED", ft.Icons.ADMIN_PANEL_SETTINGS_ROUNDED),
            make_kpi("Analistas", analistas, COLOR_ELECTRIC_BLUE, ft.Icons.BUILD_ROUNDED),
            make_kpi("Ejecutivos", ejecutivos, "#475569", ft.Icons.VISIBILITY_ROUNDED),
        ]

        # Lista de tarjetas
        users_list_container.controls = [render_user_card(u) for u in filtered]
        if not filtered:
            users_list_container.controls = [
                ft.Container(
                    content=ft.Text("No se encontraron usuarios con el criterio de búsqueda.", color=COLOR_TEXT_MUTED, size=12),
                    padding=20,
                    alignment=ft.Alignment(0, 0)
                )
            ]
        page.update()

    # Buscador de usuarios
    def on_search_users(e):
        nonlocal search_user_query
        search_user_query = e.control.value
        refresh_users_tab()

    users_search_field = ft.TextField(
        hint_text="Buscar por usuario, nombre o cargo...",
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        content_padding=ft.Padding.symmetric(horizontal=12, vertical=8),
        border_radius=10,
        text_size=12,
        expand=True,
        on_change=on_search_users
    )

    btn_new_user = ft.FilledButton(
        content=ft.Row([
            ft.Icon(ft.Icons.PERSON_ADD_ROUNDED, size=16),
            ft.Text("Nuevo Usuario", size=12, weight=ft.FontWeight.BOLD)
        ], tight=True),
        style=ft.ButtonStyle(
            bgcolor=COLOR_ELECTRIC_BLUE,
            color="#FFFFFF",
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            shape=ft.RoundedRectangleBorder(radius=10)
        ),
        on_click=open_create_user_modal
    )

    # -------------------------------------------------------------
    # PESTAÑA 2: BITÁCORA DE AUDITORÍA (data/auditoria.json)
    # -------------------------------------------------------------
    def get_module_color(mod: str) -> str:
        if "Fiesta del Agua" in mod:
            return "#0284C7"
        if "Cero Botes" in mod:
            return "#2563EB"
        if "Tramos" in mod:
            return "#EA580C"
        if "Hidrojet" in mod:
            return "#16A34A"
        if "Usuarios" in mod:
            return "#7C3AED"
        return "#475569"

    def render_audit_entry(entry: dict) -> ft.Container:
        mod = entry.get("modulo", "Sistema")
        mod_col = get_module_color(mod)

        return ft.Container(
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.LAYERS_ROUNDED, size=11, color="#FFFFFF"),
                                    ft.Text(mod, size=9, weight=ft.FontWeight.BOLD, color="#FFFFFF")
                                ], spacing=3, tight=True),
                                padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                bgcolor=mod_col,
                                border_radius=6
                            ),
                            ft.Row([
                                ft.Icon(ft.Icons.CALENDAR_TODAY_ROUNDED, size=11, color=COLOR_TEXT_MUTED),
                                ft.Text(entry.get("timestamp", ""), size=10, color=COLOR_TEXT_MUTED)
                            ], spacing=3)
                        ]
                    ),
                    ft.Row([
                        ft.Icon(ft.Icons.BOLT_ROUNDED, size=14, color=mod_col),
                        ft.Text(entry.get("accion", "Acción"), size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                    ], spacing=4),
                    ft.Text(
                        entry.get("detalle", ""),
                        size=11,
                        color="#334155"
                    ),
                    ft.Divider(height=1, color="#F1F5F9"),
                    ft.Row([
                        ft.Icon(ft.Icons.ACCOUNT_CIRCLE_ROUNDED, size=12, color=COLOR_ELECTRIC_BLUE),
                        ft.Text(
                            f"Ejecutado por: {entry.get('nombre', 'Usuario')} (@{entry.get('username', '')})",
                            size=10,
                            color=COLOR_TEXT_SECONDARY,
                            weight=ft.FontWeight.W_500
                        )
                    ], spacing=4)
                ]
            ),
            padding=10,
            bgcolor=COLOR_SURFACE_WHITE,
            border_radius=10,
            border=ft.Border.all(1, COLOR_BORDER),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=3, color="#0A000000", offset=ft.Offset(0, 1))
        )

    def refresh_audit_tab():
        all_audit = auth_mgr.get_auditoria()
        filtered = all_audit

        if audit_module_filter != "Todos":
            filtered = [e for e in filtered if audit_module_filter.lower() in e.get("modulo", "").lower()]

        if audit_search_query:
            q = audit_search_query.lower()
            filtered = [
                e for e in filtered
                if q in e.get("detalle", "").lower() or q in e.get("accion", "").lower() or q in e.get("username", "").lower() or q in e.get("nombre", "").lower()
            ]

        # KPIs de Auditoría
        total_events = len(all_audit)
        modules_count = len(set(e.get("modulo", "") for e in all_audit))
        last_event_time = all_audit[0].get("timestamp", "N/A") if all_audit else "N/A"

        kpis_audit_container.controls = [
            ft.Container(
                content=ft.Column([
                    ft.Text(str(total_events), size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                    ft.Text("Eventos Registrados", size=10, color=COLOR_TEXT_MUTED)
                ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=8,
                bgcolor=COLOR_SURFACE_WHITE,
                border_radius=10,
                border=ft.Border.all(1, COLOR_BORDER),
                expand=True
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text(str(modules_count), size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                    ft.Text("Módulos Auditados", size=10, color=COLOR_TEXT_MUTED)
                ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=8,
                bgcolor=COLOR_SURFACE_WHITE,
                border_radius=10,
                border=ft.Border.all(1, COLOR_BORDER),
                expand=True
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("En Tiempo Real", size=13, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN),
                    ft.Text("Persistencia JSON", size=10, color=COLOR_TEXT_MUTED)
                ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=8,
                bgcolor=COLOR_SURFACE_WHITE,
                border_radius=10,
                border=ft.Border.all(1, COLOR_BORDER),
                expand=True
            )
        ]

        # Limitar renderizado a los 200 más recientes para fluidez total del scroll
        display_entries = filtered[:200]
        entries_controls = [render_audit_entry(e) for e in display_entries]
        if len(filtered) > 200:
            entries_controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=14, color=COLOR_ELECTRIC_BLUE),
                        ft.Text(
                            f"Mostrando los 200 eventos más recientes de {len(filtered)} registrados. Utilice el selector de módulos o el buscador superior para acotar los resultados.",
                            size=11,
                            color=COLOR_TEXT_SECONDARY
                        )
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
                    padding=12,
                    alignment=ft.Alignment(0, 0)
                )
            )

        audit_list_container.controls = entries_controls
        if not filtered:
            audit_list_container.controls = [
                ft.Container(
                    content=ft.Text("No se encontraron registros de auditoría para este filtro.", color=COLOR_TEXT_MUTED, size=12),
                    padding=20,
                    alignment=ft.Alignment(0, 0)
                )
            ]
        page.update()

    def on_audit_mod_change(e):
        nonlocal audit_module_filter
        audit_module_filter = e.control.value
        refresh_audit_tab()

    def on_audit_search(e):
        nonlocal audit_search_query
        audit_search_query = e.control.value
        refresh_audit_tab()

    dd_audit_module = ft.Dropdown(
        label="Módulo",
        options=[
            ft.dropdown.Option("Todos", "Todos los Módulos"),
            ft.dropdown.Option("Fiesta del Agua", "Fiesta del Agua"),
            ft.dropdown.Option("Cero Botes", "Plan Cero Botes"),
            ft.dropdown.Option("Tramos", "Tramos Caídos"),
            ft.dropdown.Option("Hidrojet", "Ruta del Hidrojet"),
            ft.dropdown.Option("Usuarios", "Gestión de Usuarios"),
            ft.dropdown.Option("Autenticación", "Autenticación")
        ],
        value="Todos",
        content_padding=ft.Padding.symmetric(horizontal=10, vertical=6),
        border_radius=10,
        text_size=11,
        width=170,
        on_select=on_audit_mod_change
    )

    audit_search_field = ft.TextField(
        hint_text="Buscar en bitácora...",
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        content_padding=ft.Padding.symmetric(horizontal=10, vertical=8),
        border_radius=10,
        text_size=11,
        expand=True,
        on_change=on_audit_search
    )

    # -------------------------------------------------------------
    # TABS PRINCIPALES CON SCROLL VERTICAL FLUIDO
    # -------------------------------------------------------------
    accounts_tab_content = ft.ListView(
        controls=[
            kpis_users_container,
            ft.Row([users_search_field, btn_new_user], spacing=8),
            users_list_container,
            ft.Container(height=24)
        ],
        spacing=12,
        padding=ft.Padding.only(top=10, bottom=24),
        expand=True
    )

    audit_tab_content = ft.ListView(
        controls=[
            kpis_audit_container,
            ft.Row([dd_audit_module, audit_search_field], spacing=8),
            audit_list_container,
            ft.Container(height=24)
        ],
        spacing=12,
        padding=ft.Padding.only(top=10, bottom=24),
        expand=True
    )

    # -------------------------------------------------------------
    # PESTAÑAS PERSONALIZADAS HORIZONTALES (PATRÓN FIESTA DEL AGUA)
    # -------------------------------------------------------------
    active_tab = 0  # 0: Cuentas, 1: Auditoría
    tab_chips_row = ft.Row(spacing=8, scroll=ft.ScrollMode.ADAPTIVE)
    tab_content_area = ft.Container(expand=True)

    def render_active_tab():
        if active_tab == 0:
            tab_content_area.content = accounts_tab_content
        else:
            tab_content_area.content = audit_tab_content

    def set_tab(idx: int):
        nonlocal active_tab
        active_tab = idx
        if idx == 1:
            refresh_audit_tab()
        elif idx == 0:
            refresh_users_tab()
        render_tab_chips()
        render_active_tab()
        page.update()

    def render_tab_chips():
        tab_chips_row.controls.clear()
        all_users = auth_mgr.get_users()
        all_audit = auth_mgr.get_auditoria()

        tab_labels = [
            (f"Administración de Cuentas ({len(all_users)})", ft.Icons.PEOPLE_ROUNDED),
            (f"Bitácora de Auditoría ({len(all_audit)})", ft.Icons.SECURITY_ROUNDED),
        ]
        for i, (name, icon) in enumerate(tab_labels):
            is_act = (i == active_tab)
            tab_chips_row.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(icon, size=14, color="#FFFFFF" if is_act else COLOR_NAVY_DARK),
                        ft.Text(name, size=11, weight=ft.FontWeight.BOLD if is_act else ft.FontWeight.W_600, color="#FFFFFF" if is_act else COLOR_NAVY_DARK)
                    ], spacing=6, tight=True),
                    bgcolor=COLOR_NAVY_DARK if is_act else "#E2E8F0",
                    padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                    border_radius=10,
                    ink=True,
                    on_click=lambda e, ti=i: set_tab(ti)
                )
            )

    # Inicializar datos al cargar la vista
    refresh_users_tab()
    render_tab_chips()
    render_active_tab()

    return ft.Container(
        content=ft.Column(
            spacing=0,
            controls=[
                header,
                ft.Container(
                    content=tab_chips_row,
                    padding=ft.Padding.only(left=12, right=12, top=10, bottom=15),
                    bgcolor="#F8FAFC",
                    border=ft.Border.only(bottom=ft.BorderSide(1, COLOR_BORDER))
                ),
                ft.Container(
                    content=tab_content_area,
                    padding=ft.Padding.symmetric(horizontal=12, vertical=4),
                    expand=True
                )
            ],
            expand=True
        ),
        expand=True,
        bgcolor=COLOR_BG_LIGHT
    )
