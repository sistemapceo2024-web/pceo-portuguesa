"""
Módulo Detallado: Plan de Canalización y Construcción de Bermas
Puesto de Comando Estratégico Operacional del Estado Portuguesa (PCEO)
Gobernación del Estado Portuguesa • Secretaría de Infraestructura y Operaciones
Corte Oficial 2026: 380.73 Km Canalizados • 243 Obras Ejecutadas (244 Totales) • 57 Bermas Construidas (>700.000 M³ Removidos)
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
    COLOR_STATUS_AMBER,
    COLOR_STATUS_RED
)
from components.header import create_institutional_header
from modules.excel_import_panel import ExcelImportPanel
from components.print_municipal_report import open_print_preview_dialog
from data.canalizacion_parser import CanalizacionParser, normalize_mun_name, format_number_es
from data.water_data import MUNICIPALITIES_LIST
from data.state import AppState

def get_status_colors(estatus: str) -> tuple:
    """Retorna colores (fondo, texto, borde) según el estatus de la obra."""
    st = (estatus or "").upper()
    if "EJECUTAD" in st or "CULMINAD" in st or "100" in st:
        return ("#DCFCE7", "#16A34A", "#86EFAC")
    elif "PARALIZAD" in st:
        return ("#FEE2E2", "#DC2626", "#FCA5A5")
    return ("#FEF3C7", "#D97706", "#FDE68A")

def get_component_colors(componente: str) -> tuple:
    """Retorna colores según si es Canalización o Berma."""
    cp = (componente or "").upper()
    if "BERMA" in cp:
        return ("#F0FDF4", "#16A34A", "#BBF7D0")
    return ("#EFF6FF", COLOR_ELECTRIC_BLUE, "#BFDBFE")

def build_canalizacion_view(
    page: ft.Page,
    on_back_to_summary,
    on_switch_role,
    on_logout,
    selected_municipio: str = None
) -> ft.Control:
    """Construye la vista interactiva completa del Plan de Canalización y Bermas con estándar PCEO."""
    state = AppState()
    parser = CanalizacionParser()

    active_tab = 0  # 0: Resumen General, 1: Inventario Obras 2026, 2: Frentes Activos y Fluviales
    selected_mun = selected_municipio or state.canalizacion_municipality
    selected_estatus = state.canalizacion_estatus
    selected_componente = state.canalizacion_componente
    search_query = ""

    kpis_container = ft.Row(spacing=8)
    tab_content_area = ft.Container(expand=True)
    tab_chips_row = ft.Row(scroll=ft.ScrollMode.ADAPTIVE, spacing=6)

    def show_feedback_snack(message: str, is_error: bool = False):
        snack = ft.SnackBar(
            content=ft.Text(message, color="#FFFFFF", weight=ft.FontWeight.W_500),
            bgcolor=COLOR_STATUS_RED if is_error else COLOR_NAVY_DARK
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

    # Modal: Ficha Técnica Fluvial de la Obra
    def open_ficha_obra_dialog(obra: dict):
        nombre = obra.get("nombre", "Obra Fluvial")
        comp = obra.get("componente", "CANALIZACIÓN")
        mun = obra.get("municipio", "Portuguesa")
        sec = obra.get("sector", "Sector General")
        est = obra.get("estatus", "EJECUTADA")
        long_val = obra.get("longitud", 0.0)
        exc = obra.get("excavacion_m3", 0.0)
        mat = obra.get("material_removido_m3", 0.0)

        bg_st, col_st, bdr_st = get_status_colors(est)
        bg_cp, col_cp, bdr_cp = get_component_colors(comp)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.WATER_ROUNDED, color=COLOR_ELECTRIC_BLUE, size=24),
                ft.Text("Ficha de Obra Fluvial — Canalización y Bermas", size=15, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
            ], spacing=8),
            content=ft.Container(
                width=520,
                content=ft.Column(
                    tight=True,
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Row([
                            ft.Container(
                                content=ft.Text(f"Municipio {mun}", size=11, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_BLUE),
                                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                bgcolor="#EFF6FF",
                                border_radius=6,
                                border=ft.Border.all(1, "#BFDBFE")
                            ),
                            ft.Row([
                                ft.Container(
                                    content=ft.Text(comp, size=10, weight=ft.FontWeight.BOLD, color=col_cp),
                                    padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                    bgcolor=bg_cp,
                                    border_radius=6,
                                    border=ft.Border.all(1, bdr_cp)
                                ),
                                ft.Container(
                                    content=ft.Text(est, size=10, weight=ft.FontWeight.BOLD, color=col_st),
                                    padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                    bgcolor=bg_st,
                                    border_radius=6,
                                    border=ft.Border.all(1, bdr_st)
                                )
                            ], spacing=6)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(nombre, size=15, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Row([
                            ft.Icon(ft.Icons.PLACE_ROUNDED, size=14, color=COLOR_TEXT_MUTED),
                            ft.Text(f"Sector / Tramo: {sec}", size=12, color=COLOR_TEXT_SECONDARY)
                        ], spacing=4),
                        ft.Divider(height=1, color=COLOR_BORDER),
                        ft.Row([
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("LONGITUD", size=9, color=COLOR_TEXT_MUTED, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{format_number_es(long_val, 2)} Km", size=15, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_BLUE)
                                ], spacing=2),
                                expand=True,
                                padding=8,
                                bgcolor="#F8FAFC",
                                border_radius=6
                            ),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("EXCAVACIÓN Y ARRIME", size=9, color=COLOR_TEXT_MUTED, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{format_number_es(exc, 2)} M³", size=15, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN)
                                ], spacing=2),
                                expand=True,
                                padding=8,
                                bgcolor="#F8FAFC",
                                border_radius=6
                            ),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("MATERIAL REMOVIDO", size=9, color=COLOR_TEXT_MUTED, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{format_number_es(mat, 2)} M³", size=15, weight=ft.FontWeight.BOLD, color="#D97706")
                                ], spacing=2),
                                expand=True,
                                padding=8,
                                bgcolor="#F8FAFC",
                                border_radius=6
                            ),
                        ], spacing=8),
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.ENGINEERING_ROUNDED, size=16, color=COLOR_ELECTRIC_BLUE),
                                ft.Text("Intervención con maquinaria pesada (Jumbo, Retroexcavadoras y Cuadrillas)", size=11, color=COLOR_TEXT_SECONDARY)
                            ], spacing=6),
                            padding=8,
                            bgcolor="#EFF6FF",
                            border_radius=6,
                            border=ft.Border.all(1, "#BFDBFE")
                        )
                    ]
                ),
                padding=ft.Padding.symmetric(vertical=4)
            ),
            actions=[
                ft.TextButton(content=ft.Text("Cerrar"), on_click=lambda e: close_current_dialog())
            ],
            shape=ft.RoundedRectangleBorder(radius=12)
        )
        if hasattr(page, "open"):
            page.open(dlg)
        else:
            page.show_dialog(dlg)
        page.update()

    # Modal: Registrar o Actualizar Obra de Canalización / Berma (Exclusivo Master/Analista)
    def open_add_edit_obra_dialog(obra_existente: dict = None):
        if not state.is_editor():
            show_feedback_snack("Acceso denegado: Función reservada para roles Master y Analista.", is_error=True)
            return

        is_edit = obra_existente is not None
        title_txt = "Actualizar Obra Fluvial" if is_edit else "Registrar Nueva Obra de Canalización / Berma"

        dd_comp = ft.Dropdown(
            label="Componente",
            options=[ft.dropdown.Option("CANALIZACIÓN"), ft.dropdown.Option("BERMAS")],
            value=obra_existente.get("componente", "CANALIZACIÓN") if is_edit else "CANALIZACIÓN",
            border_radius=8,
            text_size=12
        )

        dd_mun = ft.Dropdown(
            label="Municipio",
            options=[ft.dropdown.Option(m) for m in MUNICIPALITIES_LIST if m != "Todos los Municipios"],
            value=obra_existente.get("municipio", "Guanare") if is_edit else "Guanare",
            border_radius=8,
            text_size=12
        )

        txt_nombre = ft.TextField(
            label="Nombre de la Obra / Tramo / Cauce",
            value=obra_existente.get("nombre", "") if is_edit else "",
            border_radius=8,
            text_size=12,
            prefix_icon=ft.Icons.WATER_ROUNDED
        )

        txt_sector = ft.TextField(
            label="Parroquia / Sector / Comunidad",
            value=obra_existente.get("sector", "") if is_edit else "",
            border_radius=8,
            text_size=12,
            prefix_icon=ft.Icons.PLACE_ROUNDED
        )

        dd_estatus = ft.Dropdown(
            label="Estatus",
            options=[
                ft.dropdown.Option("EJECUTADA"),
                ft.dropdown.Option("EN DESARROLLO"),
                ft.dropdown.Option("PARALIZADA")
            ],
            value=obra_existente.get("estatus", "EJECUTADA") if is_edit else "EJECUTADA",
            border_radius=8,
            text_size=12
        )

        txt_long = ft.TextField(
            label="Longitud (Km / ML)",
            value=str(obra_existente.get("longitud", 0.50)) if is_edit else "0.50",
            border_radius=8,
            text_size=12,
            prefix_icon=ft.Icons.STRAIGHTEN_ROUNDED
        )

        txt_exc = ft.TextField(
            label="Excavación / Arrime (M³)",
            value=str(obra_existente.get("excavacion_m3", 0.0)) if is_edit else "0.0",
            border_radius=8,
            text_size=12
        )

        txt_mat = ft.TextField(
            label="Material Removido (M³)",
            value=str(obra_existente.get("material_removido_m3", 0.0)) if is_edit else "0.0",
            border_radius=8,
            text_size=12
        )

        lbl_error = ft.Text("", size=11, color=COLOR_STATUS_RED, visible=False)

        def save_obra(e):
            if not txt_nombre.value.strip():
                lbl_error.value = "Debe ingresar el nombre del tramo o cauce fluvial."
                lbl_error.visible = True
                page.update()
                return

            try:
                long_val = float(txt_long.value.replace(",", "."))
                exc_val = float(txt_exc.value.replace(",", "."))
                mat_val = float(txt_mat.value.replace(",", "."))
            except ValueError:
                lbl_error.value = "Los valores numéricos de metraje y volumen deben ser válidos."
                lbl_error.visible = True
                page.update()
                return

            obra_dict = {
                "id": obra_existente.get("id") if is_edit else f"obra_manual_{int(page.window.width or 1000)}",
                "componente": dd_comp.value,
                "nombre": txt_nombre.value.strip().upper(),
                "municipio": dd_mun.value,
                "sector": txt_sector.value.strip(),
                "estatus": dd_estatus.value,
                "longitud": long_val,
                "unidad_longitud": "KM",
                "excavacion_m3": exc_val,
                "material_removido_m3": mat_val
            }

            state.add_canalizacion_obra(obra_dict, audit_user=state.get_user_display_name())
            close_current_dialog()
            full_refresh()
            show_feedback_snack(f"Obra registrada con éxito: {obra_dict['nombre']} en {obra_dict['municipio']}.")

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.WATER_ROUNDED, color=COLOR_ELECTRIC_BLUE),
                ft.Text(title_txt, size=15, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
            ], spacing=8),
            content=ft.Container(
                width=500,
                content=ft.Column(
                    tight=True,
                    spacing=10,
                    controls=[
                        ft.Text("Complete los datos técnicos para el registro auditado de la obra fluvial:", size=11, color=COLOR_TEXT_SECONDARY),
                        ft.Row([dd_comp, dd_estatus], spacing=8),
                        ft.Row([dd_mun, txt_long], spacing=8),
                        txt_nombre,
                        txt_sector,
                        ft.Row([txt_exc, txt_mat], spacing=8),
                        lbl_error
                    ]
                ),
                padding=ft.Padding.symmetric(vertical=4)
            ),
            actions=[
                ft.TextButton(content=ft.Text("Cancelar"), on_click=lambda e: close_current_dialog()),
                ft.FilledButton(
                    content=ft.Row([ft.Icon(ft.Icons.CHECK_ROUNDED, size=16), ft.Text("Guardar Obra")], tight=True),
                    style=ft.ButtonStyle(bgcolor=COLOR_ELECTRIC_BLUE, color="#FFFFFF"),
                    on_click=save_obra
                )
            ],
            shape=ft.RoundedRectangleBorder(radius=12)
        )
        if hasattr(page, "open"):
            page.open(dlg)
        else:
            page.show_dialog(dlg)
        page.update()

    # Panel de Importación de Excel sin congelamiento
    import_panel_obj = ExcelImportPanel(
        page=page,
        title="Importar Excel Plan de Canalización y Bermas (.xlsx)",
        default_file="PLAN_CANALIZACION_PORTUGUESA_2026.xlsx",
        on_load_callback=state.reload_canalizacion_excel,
        on_success_callback=lambda: full_refresh(),
        accent_color=COLOR_ELECTRIC_BLUE
    )

    def import_excel_dialog(e=None):
        import_panel_obj.toggle(e)

    # -------------------------------------------------------------
    # 4 TARJETAS KPI DINÁMICAS SUPERIORES
    # -------------------------------------------------------------
    def refresh_upper_kpis():
        kpis_container.controls.clear()
        k = state.get_canalizacion_kpis(selected_mun, selected_estatus, selected_componente)

        is_statewide = (selected_mun in ["Todos los Municipios", "TODOS"]) and (selected_estatus in ["Todos", "TODOS"]) and (selected_componente in ["Todos", "TODOS"])

        # Metas oficiales PCEO
        tot_obras = 244 if is_statewide else k.get("total_obras", 0)
        long_km = 380.73 if is_statewide else k.get("longitud_canalizada_km", 0.0)
        bermas_cnt = 57 if is_statewide else k.get("bermas_construidas", 0)
        vol_total = 838440.85 if is_statewide else k.get("volumen_total_m3", 0.0)

        kpis_data = [
            {
                "title": "TOTAL CANALIZACIONES",
                "value": format_number_es(tot_obras),
                "sub": "243 Ejecutadas • 1 En Desarrollo",
                "icon": ft.Icons.WATER_ROUNDED,
                "color": COLOR_ELECTRIC_BLUE,
                "bg": "#EFF6FF"
            },
            {
                "title": "LONGITUD REHABILITADA",
                "value": f"{format_number_es(long_km, 2)} Km",
                "sub": "380.73 Km Cauces Canalizados",
                "icon": ft.Icons.STRAIGHTEN_ROUNDED,
                "color": COLOR_STATUS_GREEN,
                "bg": "#F0FDF4"
            },
            {
                "title": "BERMAS CONSTRUIDAS",
                "value": format_number_es(bermas_cnt),
                "sub": "57 Bermas • Muros de Contención",
                "icon": ft.Icons.SECURITY_ROUNDED,
                "color": "#D97706",
                "bg": "#FEF3C7"
            },
            {
                "title": "VOLUMEN REMOVIDO TOTAL",
                "value": f"{format_number_es(vol_total)} M³",
                "sub": ">700.000 M³ Arrime y Acarreo",
                "icon": ft.Icons.CONSTRUCTION_ROUNDED,
                "color": "#7C3AED",
                "bg": "#F3E8FF"
            }
        ]

        for item in kpis_data:
            card = ft.Container(
                content=ft.Column(
                    spacing=4,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(item["title"], size=10, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY),
                                ft.Container(
                                    content=ft.Icon(item["icon"], size=16, color=item["color"]),
                                    padding=4,
                                    bgcolor=item["bg"],
                                    border_radius=6
                                )
                            ]
                        ),
                        ft.Text(item["value"], size=18, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Text(item["sub"], size=9.5, color=COLOR_TEXT_MUTED, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)
                    ]
                ),
                padding=10,
                bgcolor=COLOR_SURFACE_WHITE,
                border_radius=10,
                border=ft.Border.all(1, COLOR_BORDER),
                shadow=ft.BoxShadow(spread_radius=0, blur_radius=3, color="#0A000000", offset=ft.Offset(0, 1)),
                expand=True
            )
            kpis_container.controls.append(card)

    # -------------------------------------------------------------
    # 1. PESTAÑA: RESUMEN GENERAL ESTADAL (MACRO)
    # -------------------------------------------------------------
    def build_tab_resumen_general() -> ft.Control:
        rows_data = state.get_canalizacion_resumen_general()

        cards = []
        for r in rows_data:
            comp = r.get("componente", "")
            ejec = r.get("ejecutadas", 0)
            des = r.get("en_desarrollo", 0)
            long_val = r.get("longitud", 0.0)
            unidad = r.get("unidad", "KM")
            exc = r.get("excavacion_m3", 0.0)
            mat = r.get("material_removido_m3", 0.0)
            tot = r.get("total", ejec + des)

            is_berma = "BERMA" in comp.upper()
            icon_c = ft.Icons.SECURITY_ROUNDED if is_berma else ft.Icons.WATER_ROUNDED
            color_c = "#16A34A" if is_berma else COLOR_ELECTRIC_BLUE
            bg_c = "#F0FDF4" if is_berma else "#EFF6FF"

            pct_ejec = round((ejec / tot * 100), 1) if tot > 0 else 100.0

            card = ft.Container(
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row([
                                    ft.Container(
                                        content=ft.Icon(icon_c, size=18, color=color_c),
                                        padding=6,
                                        bgcolor=bg_c,
                                        border_radius=8
                                    ),
                                    ft.Column([
                                        ft.Text(comp, size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                        ft.Text(f"Metas Oficiales • {tot} Obras Programadas", size=10, color=COLOR_TEXT_MUTED)
                                    ], spacing=2)
                                ], spacing=8),
                                ft.Container(
                                    content=ft.Text(f"{pct_ejec}% Ejecutado", size=10, weight=ft.FontWeight.BOLD, color=color_c),
                                    padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                                    bgcolor=bg_c,
                                    border_radius=6,
                                    border=ft.Border.all(1, color_c)
                                )
                            ]
                        ),
                        ft.ProgressBar(value=pct_ejec / 100.0, color=color_c, bgcolor="#E2E8F0"),
                        ft.Divider(height=1, color="#F1F5F9"),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Column([
                                    ft.Text("OBRAS EJECUTADAS", size=9, color=COLOR_TEXT_MUTED, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{format_number_es(ejec)} obras", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                                ], spacing=2),
                                ft.Column([
                                    ft.Text("LONGITUD ATENDIDA", size=9, color=COLOR_TEXT_MUTED, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{format_number_es(long_val, 2)} {unidad}", size=13, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_BLUE)
                                ], spacing=2),
                                ft.Column([
                                    ft.Text("EXCAVACIÓN Y ARRIME", size=9, color=COLOR_TEXT_MUTED, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{format_number_es(exc, 2)} M³", size=13, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN)
                                ], spacing=2),
                                ft.Column([
                                    ft.Text("MATERIAL REMOVIDO", size=9, color=COLOR_TEXT_MUTED, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{format_number_es(mat, 2)} M³", size=13, weight=ft.FontWeight.BOLD, color="#D97706")
                                ], spacing=2),
                                ft.Column([
                                    ft.Text("EN DESARROLLO", size=9, color=COLOR_TEXT_MUTED, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{format_number_es(des)}", size=13, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_AMBER if des > 0 else COLOR_TEXT_MUTED)
                                ], spacing=2),
                            ]
                        )
                    ]
                ),
                padding=12,
                bgcolor=COLOR_SURFACE_WHITE,
                border_radius=10,
                border=ft.Border.all(1, COLOR_BORDER),
                shadow=ft.BoxShadow(spread_radius=0, blur_radius=3, color="#0A000000", offset=ft.Offset(0, 1))
            )
            cards.append(card)

        # Fila Consolidada Totalizadora
        tot_card = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, size=22, color=COLOR_STATUS_GREEN),
                ft.Column([
                    ft.Text("TOTAL GENERAL ESTADAL (CANALIZACIONES + BERMAS)", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                    ft.Text("302 Obras Globales • 300 Ejecutadas • 2 En Desarrollo • 380.73 Km Canalizados • 39.58 Km Bermas • 838.441 M³ Volumen", size=11, color=COLOR_TEXT_SECONDARY)
                ], spacing=2, expand=True)
            ], spacing=10),
            padding=12,
            bgcolor="#F0FDF4",
            border_radius=10,
            border=ft.Border.all(1, "#BBF7D0")
        )

        return ft.ListView(
            controls=[tot_card, *cards],
            spacing=8,
            expand=True
        )

    # -------------------------------------------------------------
    # 2. PESTAÑA: INVENTARIO DETALLADO DE OBRAS 2026
    # -------------------------------------------------------------
    def build_tab_inventario_obras() -> ft.Control:
        obras = state.get_canalizacion_obras(selected_mun, selected_estatus, selected_componente, search_query)

        items = []
        for o in obras:
            comp = o.get("componente", "CANALIZACIÓN")
            est = o.get("estatus", "EJECUTADA")
            bg_st, col_st, bdr_st = get_status_colors(est)
            bg_cp, col_cp, bdr_cp = get_component_colors(comp)

            card = ft.Container(
                content=ft.Column(
                    spacing=6,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row([
                                    ft.Container(
                                        content=ft.Text(f"#{o.get('n')}", size=10, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                        bgcolor=COLOR_NAVY_DARK,
                                        width=28,
                                        height=22,
                                        border_radius=4,
                                        alignment=ft.Alignment(0, 0)
                                    ),
                                    ft.Text(o.get("nombre", ""), size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                ], spacing=6, expand=True),
                                ft.Row([
                                    ft.Container(
                                        content=ft.Text(comp, size=9.5, weight=ft.FontWeight.BOLD, color=col_cp),
                                        bgcolor=bg_cp,
                                        padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                        border_radius=4,
                                        border=ft.Border.all(1, bdr_cp)
                                    ),
                                    ft.Container(
                                        content=ft.Text(est, size=9.5, weight=ft.FontWeight.BOLD, color=col_st),
                                        bgcolor=bg_st,
                                        padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                        border_radius=4,
                                        border=ft.Border.all(1, bdr_st)
                                    )
                                ], spacing=4)
                            ]
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row([
                                    ft.Icon(ft.Icons.LOCATION_ON_ROUNDED, size=13, color=COLOR_ELECTRIC_BLUE),
                                    ft.Text(f"{o.get('municipio')} • Sector: {o.get('sector')}", size=11, color=COLOR_TEXT_SECONDARY)
                                ], spacing=4),
                                ft.Row([
                                    ft.Icon(ft.Icons.STRAIGHTEN_ROUNDED, size=13, color=COLOR_ELECTRIC_BLUE),
                                    ft.Text(f"{format_number_es(o.get('longitud', 0), 2)} Km", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                    ft.Text("•", size=10, color=COLOR_TEXT_MUTED),
                                    ft.Text(f"Exc: {format_number_es(o.get('excavacion_m3', 0), 1)} M³", size=10, color=COLOR_STATUS_GREEN, weight=ft.FontWeight.W_600),
                                    ft.Text("•", size=10, color=COLOR_TEXT_MUTED),
                                    ft.Text(f"Rem: {format_number_es(o.get('material_removido_m3', 0), 1)} M³", size=10, color="#D97706", weight=ft.FontWeight.W_600)
                                ], spacing=4)
                            ]
                        )
                    ]
                ),
                padding=10,
                bgcolor=COLOR_SURFACE_WHITE,
                border_radius=8,
                border=ft.Border.all(1, COLOR_BORDER),
                ink=True,
                on_click=lambda e, ob=o: open_ficha_obra_dialog(ob)
            )
            items.append(card)

        if not items:
            items.append(
                ft.Container(
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.SEARCH_OFF_ROUNDED, size=36, color=COLOR_TEXT_MUTED),
                            ft.Text("No se encontraron obras fluviales con los filtros seleccionados.", size=12, color=COLOR_TEXT_MUTED)
                        ]
                    ),
                    padding=30,
                    alignment=ft.Alignment(0, 0)
                )
            )

        return ft.ListView(controls=items, spacing=6, expand=True)

    # -------------------------------------------------------------
    # 3. PESTAÑA: FRENTES ACTIVOS Y FLUVIALES
    # -------------------------------------------------------------
    def build_tab_frentes_fluviales() -> ft.Control:
        frentes = state.get_canalizacion_frentes_fluviales(selected_mun)

        # Destacar primero frentes en desarrollo o prioritarios
        frentes_desarrollo = [f for f in frentes if "DESARROLL" in f.get("estatus", "").upper()]
        frentes_ejecutados = [f for f in frentes if "DESARROLL" not in f.get("estatus", "").upper()]

        frentes_ordenados = frentes_desarrollo + frentes_ejecutados

        items = []
        # Banner de alerta si hay frentes en desarrollo
        if frentes_desarrollo:
            for fd in frentes_desarrollo:
                items.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color="#D97706", size=24),
                            ft.Column([
                                ft.Text(f"FRENTE ACTIVO EN DESARROLLO: {fd.get('cauce')}", size=12, weight=ft.FontWeight.BOLD, color="#B45309"),
                                ft.Text(f"Municipio: {fd.get('municipio')} • Sector: {fd.get('sector')} • {format_number_es(fd.get('longitud', 0), 2)} Km en ejecución técnica prioritaria", size=11, color="#78350F")
                            ], spacing=2, expand=True),
                            ft.FilledButton(
                                content=ft.Text("Ver Ficha"),
                                style=ft.ButtonStyle(bgcolor="#D97706", color="#FFFFFF"),
                                on_click=lambda e, ob=fd: open_ficha_obra_dialog(ob)
                            )
                        ], spacing=10),
                        padding=12,
                        bgcolor="#FEF3C7",
                        border_radius=10,
                        border=ft.Border.all(1, "#FDE68A")
                    )
                )

        for f in frentes_ordenados:
            tipo_c = f.get("tipo_cauce", "RÍO")
            is_berma = "BERMA" in f.get("componente", "").upper()
            est = f.get("estatus", "EJECUTADA")
            bg_st, col_st, bdr_st = get_status_colors(est)

            icon_c = ft.Icons.SECURITY_ROUNDED if is_berma else ft.Icons.WATER_ROUNDED
            color_c = "#16A34A" if is_berma else COLOR_ELECTRIC_BLUE

            card = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(icon_c, size=20, color=color_c),
                        padding=8,
                        bgcolor="#EFF6FF" if not is_berma else "#F0FDF4",
                        border_radius=8
                    ),
                    ft.Column([
                        ft.Row([
                            ft.Text(f.get("cauce", ""), size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                            ft.Container(
                                content=ft.Text(tipo_c, size=9, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_BLUE),
                                bgcolor="#EFF6FF",
                                padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                border_radius=4
                            ),
                            ft.Container(
                                content=ft.Text(est, size=9, weight=ft.FontWeight.BOLD, color=col_st),
                                bgcolor=bg_st,
                                padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                border_radius=4,
                                border=ft.Border.all(1, bdr_st)
                            )
                        ], spacing=6),
                        ft.Text(f"Municipio: {f.get('municipio')} • Sector: {f.get('sector')} • Longitud: {format_number_es(f.get('longitud', 0), 2)} Km", size=11, color=COLOR_TEXT_SECONDARY),
                        ft.Text(f"Excavación: {format_number_es(f.get('excavacion_m3', 0), 1)} M³ | Material Removido: {format_number_es(f.get('material_removido_m3', 0), 1)} M³", size=10, color=COLOR_TEXT_MUTED)
                    ], spacing=3, expand=True),
                    ft.IconButton(
                        icon=ft.Icons.INFO_OUTLINE_ROUNDED,
                        icon_size=18,
                        icon_color=COLOR_ELECTRIC_BLUE,
                        tooltip="Ver Ficha Técnica",
                        on_click=lambda e, ob=f: open_ficha_obra_dialog(ob)
                    )
                ], spacing=10),
                padding=10,
                bgcolor=COLOR_SURFACE_WHITE,
                border_radius=8,
                border=ft.Border.all(1, COLOR_BORDER)
            )
            items.append(card)

        return ft.ListView(controls=items, spacing=6, expand=True)

    # -------------------------------------------------------------
    # RENDERIZADO DE PESTAÑAS (PATRÓN PÍLDORAS)
    # -------------------------------------------------------------
    def render_active_tab():
        if active_tab == 0:
            tab_content_area.content = build_tab_resumen_general()
        elif active_tab == 1:
            tab_content_area.content = build_tab_inventario_obras()
        else:
            tab_content_area.content = build_tab_frentes_fluviales()

    def set_tab(idx: int):
        nonlocal active_tab
        active_tab = idx
        render_tab_chips()
        render_active_tab()
        page.update()

    def render_tab_chips():
        tab_chips_row.controls.clear()
        labels = [
            ("Resumen General Estadal", ft.Icons.TABLE_CHART_ROUNDED),
            ("Inventario de Obras 2026 (43+)", ft.Icons.FORMAT_LIST_BULLETED_ROUNDED),
            ("Frentes Activos y Fluviales", ft.Icons.WATER_ROUNDED),
        ]
        for i, (name, icon) in enumerate(labels):
            is_act = (i == active_tab)
            tab_chips_row.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(icon, size=13, color="#FFFFFF" if is_act else COLOR_NAVY_DARK),
                        ft.Text(name, size=11, weight=ft.FontWeight.BOLD if is_act else ft.FontWeight.W_600, color="#FFFFFF" if is_act else COLOR_NAVY_DARK)
                    ], spacing=4, tight=True),
                    bgcolor=COLOR_NAVY_DARK if is_act else "#E2E8F0",
                    padding=ft.Padding.symmetric(horizontal=10, vertical=6),
                    border_radius=8,
                    ink=True,
                    on_click=lambda e, ti=i: set_tab(ti)
                )
            )

    # -------------------------------------------------------------
    # EVENTOS DE FILTROS SUPERIORES
    # -------------------------------------------------------------
    def on_mun_change(e):
        nonlocal selected_mun
        selected_mun = e.control.value
        state.set_canalizacion_filters(municipality=selected_mun)
        full_refresh()

    def on_estatus_change(e):
        nonlocal selected_estatus
        selected_estatus = e.control.value
        state.set_canalizacion_filters(estatus=selected_estatus)
        full_refresh()

    def on_componente_change(e):
        nonlocal selected_componente
        selected_componente = e.control.value
        state.set_canalizacion_filters(componente=selected_componente)
        full_refresh()

    def on_search_change(e):
        nonlocal search_query
        search_query = e.control.value
        render_active_tab()
        page.update()

    def full_refresh():
        refresh_upper_kpis()
        render_tab_chips()
        render_active_tab()
        page.update()

    # Dropdowns y Buscador Superiores
    mun_options = ["Todos los Municipios"] + [m for m in MUNICIPALITIES_LIST if m != "Todos los Municipios"]
    dd_mun_top = ft.Dropdown(
        label="Municipio",
        options=[ft.dropdown.Option(m) for m in mun_options],
        value=selected_mun,
        content_padding=ft.Padding.symmetric(horizontal=10, vertical=6),
        border_radius=8,
        text_size=11,
        expand=True,
        on_select=on_mun_change
    )

    dd_estatus_top = ft.Dropdown(
        label="Estatus",
        options=[
            ft.dropdown.Option("Todos", "Todos los Estatus"),
            ft.dropdown.Option("EJECUTADA", "Ejecutadas"),
            ft.dropdown.Option("EN DESARROLLO", "En Desarrollo"),
            ft.dropdown.Option("PARALIZADA", "Paralizadas")
        ],
        value=selected_estatus,
        content_padding=ft.Padding.symmetric(horizontal=10, vertical=6),
        border_radius=8,
        text_size=11,
        width=150,
        on_select=on_estatus_change
    )

    dd_comp_top = ft.Dropdown(
        label="Componente",
        options=[
            ft.dropdown.Option("Todos", "Todos los Componentes"),
            ft.dropdown.Option("CANALIZACIÓN", "Canalización"),
            ft.dropdown.Option("BERMAS", "Bermas")
        ],
        value=selected_componente,
        content_padding=ft.Padding.symmetric(horizontal=10, vertical=6),
        border_radius=8,
        text_size=11,
        width=160,
        on_select=on_componente_change
    )

    txt_search = ft.TextField(
        hint_text="Buscar tramo, cauce, río o sector...",
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        border_radius=8,
        text_size=11,
        content_padding=ft.Padding.symmetric(horizontal=10, vertical=8),
        expand=True,
        on_change=on_search_change
    )

    # Botón de Impresión de Reporte Ejecutivo Municipal (Carta Horizontal - Landscape)
    def on_print_click(e=None):
        mun_target = selected_mun if selected_mun not in ["Todos los Municipios", "TODOS"] else "Portuguesa"
        k_kpis = state.get_canalizacion_kpis(selected_mun, selected_estatus, selected_componente)
        demo = state.get_municipio_demografia(mun_target)

        report_data = {
            "municipio": mun_target,
            "fecha": "18/11/2026",
            "demografia": demo,
            "kpis": {
                "pozos": "N/A",
                "asfalto": "N/A",
                "km_vias": f"{format_number_es(k_kpis.get('longitud_canalizada_km', 380.73), 2)} km",
                "fallas": f"{k_kpis.get('bermas_construidas', 57)} bermas",
                "casas_culm": "N/A",
                "casas_proc": "N/A"
            },
            "obras": {
                "total": k_kpis.get("total_obras", 244),
                "culm": k_kpis.get("canalizaciones_ejecutadas", 243),
                "pct_culm": 99.6,
                "proc": k_kpis.get("canalizaciones_en_desarrollo", 1),
                "pct_proc": 0.4,
                "para": 0,
                "pct_para": 0.0
            },
            "planes": [
                {
                    "name": "Plan de Canalización de Ríos y Quebradas",
                    "metric": f"{format_number_es(k_kpis.get('longitud_canalizada_km', 380.73), 2)} Km Canalizados",
                    "detail": f"{k_kpis.get('canalizaciones_ejecutadas', 243)} obras ejecutadas • Maquinaria pesada Jumbo y Retro",
                    "status": "Operativo",
                    "status_color": "#16A34A"
                },
                {
                    "name": "Construcción de Muros de Berma Fluviales",
                    "metric": f"{k_kpis.get('bermas_construidas', 57)} Bermas Fluviales",
                    "detail": "Protección de márgenes y contención de desbordamientos en cauces críticos",
                    "status": "Operativo",
                    "status_color": "#0284C7"
                }
            ]
        }
        open_print_preview_dialog(page, report_data)

    btn_imprimir = ft.OutlinedButton(
        content=ft.Row([
            ft.Icon(ft.Icons.PRINT_ROUNDED, size=14, color=COLOR_ELECTRIC_BLUE),
            ft.Text("Imprimir Reporte", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
        ], tight=True),
        style=ft.ButtonStyle(
            padding=ft.Padding.symmetric(horizontal=10, vertical=6),
            shape=ft.RoundedRectangleBorder(radius=8)
        ),
        tooltip="Imprimir reporte municipal de canalización y bermas en Carta Horizontal",
        on_click=on_print_click
    )

    # Barra inferior de edición (Exclusivo Editor: Master / Analista)
    editor_bar = None
    if state.is_editor():
        editor_bar = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.FilledButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.WATER_ROUNDED, size=16),
                            ft.Text("Registrar o Actualizar Obra Fluvial", size=12, weight=ft.FontWeight.BOLD)
                        ], tight=True),
                        style=ft.ButtonStyle(bgcolor=COLOR_ELECTRIC_BLUE, color="#FFFFFF", padding=ft.Padding.symmetric(horizontal=14, vertical=8)),
                        on_click=lambda e: open_add_edit_obra_dialog()
                    ),
                    ft.OutlinedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.UPLOAD_FILE_ROUNDED, size=15),
                            ft.Text("Importar Excel", size=11, weight=ft.FontWeight.BOLD)
                        ], spacing=4),
                        on_click=import_excel_dialog
                    )
                ], spacing=10),
                ft.Text("Perfil con Privilegios de Escritura • Auditoría Automática PCEO", size=11, color=COLOR_TEXT_MUTED)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            bgcolor=COLOR_SURFACE_WHITE,
            border=ft.Border.only(top=ft.BorderSide(1, COLOR_BORDER))
        )
    else:
        editor_bar = ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=6,
                controls=[
                    ft.Icon(ft.Icons.LOCK_ROUNDED, size=13, color=COLOR_TEXT_MUTED),
                    ft.Text("Despacho del Gobernador • Solo Lectura", size=11, color=COLOR_TEXT_MUTED, weight=ft.FontWeight.W_600)
                ]
            ),
            padding=ft.Padding.symmetric(vertical=6),
            bgcolor="#F8FAFC",
            border=ft.Border.only(top=ft.BorderSide(1, COLOR_BORDER))
        )

    # Inicializar componentes al montar
    refresh_upper_kpis()
    render_tab_chips()
    render_active_tab()

    # Logotipo oficial
    has_logo = os.path.exists("assets/logo_canalizacion.png")
    leading_logo = ft.Image(
        src="logo_canalizacion.png",
        width=36,
        height=36,
        fit=ft.BoxFit.CONTAIN
    ) if has_logo else ft.Icon(ft.Icons.WATER_ROUNDED, color=COLOR_ELECTRIC_BLUE, size=28)

    header = create_institutional_header(
        title="Plan de Canalización y Bermas",
        subtitle="Canalización de Ríos, Quebradas y Mitigación de Riesgos Fluviales",
        current_role=state.current_role,
        show_back_button=True,
        on_back_click=lambda e: on_back_to_summary(),
        on_switch_role_click=on_switch_role,
        on_logout_click=on_logout,
        leading_logo=leading_logo
    )

    return ft.Container(
        content=ft.Column(
            spacing=8,
            controls=[
                header,
                import_panel_obj.panel_container,
                # Barra de Filtros Superiores
                ft.Container(
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Row([dd_mun_top, dd_estatus_top, dd_comp_top, btn_imprimir], spacing=8),
                            ft.Row([txt_search], spacing=8),
                            kpis_container,
                            ft.Container(
                                content=tab_chips_row,
                                padding=ft.Padding.only(bottom=8)
                            )
                        ]
                    ),
                    padding=ft.Padding.symmetric(horizontal=12, vertical=6)
                ),
                # Contenido de la pestaña activa
                ft.Container(
                    content=tab_content_area,
                    padding=ft.Padding.symmetric(horizontal=12, vertical=2),
                    expand=True
                ),
                # Barra de gestión inferior
                editor_bar
            ],
            expand=True
        ),
        expand=True,
        bgcolor=COLOR_BG_LIGHT
    )
