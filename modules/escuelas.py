"""
Módulo Detallado: Plan de Recuperación de Centros Educativos
Puesto de Comando Estratégico Operacional del Estado Portuguesa (PCEO)
Secretaría Superior de Operaciones Generales - Gobernación del Estado Portuguesa
Corte Oficial: Noviembre 2026 - 259 Centros Intervenidos (241 Culminadas, 16 En Ejecución, 2 Paralizadas)
"""
import os
from typing import Any
import flet as ft
from datetime import datetime
from components.theme import (
    COLOR_NAVY_DARK,
    COLOR_NAVY_MEDIUM,
    COLOR_ELECTRIC_BLUE,
    COLOR_SURFACE_WHITE,
    COLOR_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    COLOR_STATUS_GREEN,
    COLOR_STATUS_AMBER,
    COLOR_STATUS_RED
)
from components.header import create_institutional_header
from data.water_data import MUNICIPALITIES_LIST
from data.state import AppState
from modules.excel_import_panel import ExcelImportPanel

def fmt_es(val: int | float, dec: int = 0) -> str:
    """Formatea números con separador de miles en punto y decimal en coma."""
    if val is None:
        return "0"
    if dec > 0:
        return f"{float(val):,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{int(round(float(val))):,}".replace(",", ".")

def get_programa_badge_color(prog: str) -> tuple[str, str]:
    """Retorna (color_fondo, color_texto) según el programa educativo."""
    p = (prog or "").upper()
    if "BRICOMIL" in p:
        return ("#EFF6FF", "#1D4ED8")   # Azul institucional
    elif "CORAZ" in p:
        return ("#FEF2F2", "#DC2626")   # Rojo / Corazón
    elif "GOTA" in p:
        return ("#F0FDF4", "#15803D")   # Verde esperanza
    return ("#F1F5F9", "#475569")       # Gris neutro

def get_status_badge_color(estatus: str) -> tuple[str, str, str]:
    """Retorna (color_fondo, color_texto, color_borde) según el estatus de la obra."""
    st = (estatus or "").upper()
    if "CULMINAD" in st or "100" in st or "EJECUTAD" in st:
        return ("#DCFCE7", "#16A34A", "#86EFAC")
    elif "PARALIZAD" in st:
        return ("#FEE2E2", "#DC2626", "#FCA5A5")
    return ("#FEF3C7", "#D97706", "#FDE68A")  # En Ejecución

def get_work_type_icon(tipo: str) -> tuple[Any, str, str]:
    """Retorna (icono, color_fondo, color_texto) según el tipo de intervención."""
    t = (tipo or "").upper()
    if "IMPERMEAB" in t or "TECHO" in t:
        return (ft.Icons.ROOFING_ROUNDED, "#EFF6FF", "#1D4ED8")
    elif "PINTURA" in t or "EMBELLEC" in t:
        return (ft.Icons.FORMAT_PAINT_ROUNDED, "#FDF4FF", "#A21CAF")
    elif "BAÑO" in t or "SANITARI" in t or "AGUA" in t:
        return (ft.Icons.WATER_DROP_ROUNDED, "#ECFDF5", "#047857")
    elif "ELECTRI" in t or "ILUMIN" in t:
        return (ft.Icons.LIGHTBULB_ROUNDED, "#FEF3C7", "#B45309")
    elif "CONSTRUCCI" in t or "AULA" in t:
        return (ft.Icons.ARCHITECTURE_ROUNDED, "#FFF1F2", "#BE123C")
    return (ft.Icons.BUILD_CIRCLE_ROUNDED, "#F1F5F9", "#334155")

def build_escuelas_view(
    page: ft.Page,
    on_back_to_summary,
    on_switch_role,
    on_logout
) -> ft.Control:
    """Construye la vista interactiva oficial del Plan de Centros Educativos."""
    state = AppState()

    # Estado local de navegación y filtros
    active_tab = 0  # 0 a 3
    selected_mun = state.escuelas_municipality
    selected_prog = state.escuelas_programa
    selected_estatus = state.escuelas_estatus
    search_query = ""
    search_mun_query = ""

    # Contenedores dinámicos
    kpis_container = ft.Row(spacing=8)
    tab_content_area = ft.Container(expand=True)
    tab_chips_row = ft.Row(scroll=ft.ScrollMode.ADAPTIVE, spacing=6)

    # -------------------------------------------------------------
    # DIÁLOGOS Y NOTIFICACIONES
    # -------------------------------------------------------------
    def show_feedback_snack(message: str, is_error: bool = False):
        snack = ft.SnackBar(
            content=ft.Text(message, color="#FFFFFF", weight=ft.FontWeight.W_500),
            bgcolor=COLOR_STATUS_RED if is_error else COLOR_NAVY_DARK
        )
        if hasattr(page, "open"):
            page.open(snack)
        elif hasattr(page, "show_dialog"):
            page.show_dialog(snack)
        else:
            page.overlay.append(snack)
            snack.open = True
            page.update()

    # Modal: Ficha Técnica Completa de la Institución Educativa
    def open_ficha_tecnica_dialog(centro: dict):
        c_id = centro.get("id")
        inst = centro.get("institucion", "Centro Educativo")
        mun = centro.get("municipio", "Portuguesa")
        sector = centro.get("sector", "Sector General")
        prog = centro.get("programa", "Plan Escolar")
        desc = centro.get("descripcion", "Rehabilitación Integral")
        tipo_trabajo = centro.get("tipo_trabajo", "Rehabilitación Integral")
        estatus = centro.get("estatus", "CULMINADA")
        pct = centro.get("porcentaje", 100)
        año = centro.get("año", "2024-2025")
        notas = centro.get("notas", "Intervención ejecutada en el marco del Plan de Recuperación de Centros Educativos.")

        bg_st, col_st, bdr_st = get_status_badge_color(estatus)
        bg_pr, col_pr = get_programa_badge_color(prog)

        def close_dialog(e=None):
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.SCHOOL_ROUNDED, color=COLOR_ELECTRIC_BLUE, size=24),
                ft.Text("Ficha Técnica de Infraestructura Escolar", size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
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
                                content=ft.Text(f"#{c_id} • {prog}", size=11, weight=ft.FontWeight.BOLD, color=col_pr),
                                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                bgcolor=bg_pr,
                                border_radius=6
                            ),
                            ft.Container(
                                content=ft.Text(f"{estatus} ({pct}%)", size=11, weight=ft.FontWeight.BOLD, color=col_st),
                                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                bgcolor=bg_st,
                                border=ft.Border.all(1, bdr_st),
                                border_radius=6
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(inst, size=15, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Divider(height=1, color=COLOR_BORDER),
                        ft.Row([
                            ft.Icon(ft.Icons.LOCATION_ON_ROUNDED, size=14, color=COLOR_ELECTRIC_BLUE),
                            ft.Text(f"Municipio: {mun}", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                            ft.Text("•", size=11, color=COLOR_TEXT_MUTED),
                            ft.Icon(ft.Icons.NEAR_ME_ROUNDED, size=14, color=COLOR_TEXT_MUTED),
                            ft.Text(f"Sector / Parroquia: {sector}", size=11, color=COLOR_TEXT_SECONDARY, expand=True)
                        ], spacing=4),
                        ft.Row([
                            ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED, size=14, color=COLOR_STATUS_AMBER),
                            ft.Text(f"Año / Período: {año}", size=11, color=COLOR_TEXT_SECONDARY),
                            ft.Text("•", size=11, color=COLOR_TEXT_MUTED),
                            ft.Icon(ft.Icons.CATEGORY_ROUNDED, size=14, color=COLOR_ELECTRIC_BLUE),
                            ft.Text(f"Tipología: {tipo_trabajo}", size=11, color=COLOR_TEXT_SECONDARY)
                        ], spacing=4),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Descripción de los Trabajos e Intervenciones:", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                ft.Text(desc, size=11, color=COLOR_TEXT_SECONDARY)
                            ], spacing=3),
                            padding=8,
                            bgcolor="#F8FAFC",
                            border_radius=6,
                            border=ft.Border.all(1, "#E2E8F0")
                        ),
                        ft.Row([
                            ft.Text("Avance de Obra:", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                            ft.Text(f"{pct}%", size=11, weight=ft.FontWeight.BOLD, color=col_st)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.ProgressBar(value=pct / 100.0, color=col_st, bgcolor="#E2E8F0", height=8),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Observaciones y Seguimiento de Operaciones:", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                ft.Text(notas, size=11, color=COLOR_TEXT_MUTED)
                            ], spacing=2),
                            padding=8,
                            bgcolor="#F1F5F9",
                            border_radius=6
                        )
                    ]
                )
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cerrar"),
                    on_click=close_dialog
                )
            ]
        )

        if hasattr(page, "open"):
            page.open(dlg)
        elif hasattr(page, "show_dialog"):
            page.show_dialog(dlg)
        else:
            page.dialog = dlg
            dlg.open = True
            page.update()

    # Modal: Registrar / Actualizar Centro Educativo (MASTER y ANALISTA)
    def open_centro_educativo_modal(centro: dict = None):
        is_edit = centro is not None
        c_id = centro.get("id") if is_edit else None

        inst_field = ft.TextField(
            label="Nombre de la Institución Educativa *",
            value=centro.get("institucion", "") if is_edit else "",
            dense=True,
            text_size=11,
            border_radius=8
        )
        mun_dropdown = ft.Dropdown(
            label="Municipio *",
            value=centro.get("municipio", "AGUA BLANCA") if is_edit else "AGUA BLANCA",
            options=[ft.DropdownOption(m.upper()) for m in MUNICIPALITIES_LIST if m != "Todos los Municipios"],
            dense=True,
            text_size=11,
            border_radius=8,
            expand=True
        )
        sector_field = ft.TextField(
            label="Sector / Comunidad",
            value=centro.get("sector", "") if is_edit else "",
            dense=True,
            text_size=11,
            border_radius=8,
            expand=True
        )
        prog_dropdown = ft.Dropdown(
            label="Programa *",
            value=centro.get("programa", "BRICOMILES") if is_edit else "BRICOMILES",
            options=[
                ft.DropdownOption("BRICOMILES"),
                ft.DropdownOption("UN CORAZÓN PARA TU ESCUELA"),
                ft.DropdownOption("CENTROS EDUCATIVOS GOTA DE AMOR"),
            ],
            dense=True,
            text_size=11,
            border_radius=8,
            expand=True
        )
        año_field = ft.TextField(
            label="Año / Período",
            value=centro.get("año", "2026") if is_edit else "2026",
            dense=True,
            text_size=11,
            border_radius=8,
            width=130
        )
        desc_field = ft.TextField(
            label="Descripción de Trabajos *",
            value=centro.get("descripcion", "") if is_edit else "REHABILITACION INTEGRAL",
            dense=True,
            text_size=11,
            border_radius=8,
            multiline=True,
            min_lines=2,
            max_lines=3
        )
        estatus_dropdown = ft.Dropdown(
            label="Estatus *",
            value=centro.get("estatus", "CULMINADA") if is_edit else "CULMINADA",
            options=[
                ft.DropdownOption("CULMINADA"),
                ft.DropdownOption("EN EJECUCIÓN"),
                ft.DropdownOption("PARALIZADA"),
            ],
            dense=True,
            text_size=11,
            border_radius=8,
            expand=True
        )
        pct_field = ft.TextField(
            label="Porcentaje (%) *",
            value=str(centro.get("porcentaje", 100)) if is_edit else "100",
            dense=True,
            text_size=11,
            border_radius=8,
            width=130
        )
        notas_field = ft.TextField(
            label="Observaciones y Seguimiento PCEO",
            value=centro.get("notas", "") if is_edit else "",
            dense=True,
            text_size=11,
            border_radius=8,
            multiline=True,
            min_lines=2
        )

        def close_modal(e=None):
            modal_dlg.open = False
            page.update()

        def save_centro(e=None):
            inst_val = inst_field.value.strip()
            if not inst_val:
                show_feedback_snack("Debe ingresar el nombre de la institución.", is_error=True)
                return

            mun = mun_dropdown.value
            prog = prog_dropdown.value
            sector = sector_field.value.strip()
            desc = desc_field.value.strip() or "REHABILITACION INTEGRAL"
            año = año_field.value.strip() or "2026"
            est = estatus_dropdown.value
            try:
                pct = float(pct_field.value.replace("%", "").strip())
            except Exception:
                pct = 100.0 if est == "CULMINADA" else 50.0
            notas = notas_field.value.strip()

            if is_edit:
                success = state.update_centro_educativo(
                    centro_id=c_id,
                    estatus=est,
                    porcentaje=pct,
                    descripcion=desc,
                    notas=notas
                )
                if success:
                    show_feedback_snack(f"Institución #{c_id} actualizada correctamente.")
            else:
                nuevo = state.add_centro_educativo(
                    programa=prog,
                    municipio=mun,
                    institucion=inst_val,
                    descripcion=desc,
                    sector=sector,
                    año=año,
                    estatus=est,
                    porcentaje=pct,
                    notas=notas
                )
                if nuevo:
                    show_feedback_snack(f"Nueva institución #{nuevo.get('id')} registrada exitosamente.")

            close_modal()
            full_refresh()

        modal_dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.EDIT_ROUNDED if is_edit else ft.Icons.ADD_CIRCLE_ROUNDED, color=COLOR_ELECTRIC_BLUE, size=24),
                ft.Text("Actualizar Avance de la Escuela" if is_edit else "Registrar Nueva Institución Educativa", size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
            ], spacing=8),
            content=ft.Container(
                width=520,
                content=ft.Column(
                    tight=True,
                    spacing=8,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        inst_field,
                        ft.Row([mun_dropdown, sector_field], spacing=8),
                        ft.Row([prog_dropdown, año_field], spacing=8),
                        desc_field,
                        ft.Row([estatus_dropdown, pct_field], spacing=8),
                        notas_field
                    ]
                )
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cancelar"),
                    on_click=close_modal
                ),
                ft.FilledButton(
                    content=ft.Text("Guardar Cambios" if is_edit else "Registrar Institución"),
                    bgcolor=COLOR_ELECTRIC_BLUE,
                    color="#FFFFFF",
                    on_click=save_centro
                )
            ]
        )

        if hasattr(page, "open"):
            page.open(modal_dlg)
        elif hasattr(page, "show_dialog"):
            page.show_dialog(modal_dlg)
        else:
            page.dialog = modal_dlg
            modal_dlg.open = True
            page.update()

    # Panel de Importación de Excel sin congelamiento
    import_panel_obj = ExcelImportPanel(
        page=page,
        title="Importar Excel Centros Educativos (.xlsx)",
        default_file="CENTROS_EDUCATIVOS_PORTUGUESA_2026.xlsx",
        on_load_callback=state.reload_escuelas_excel,
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
        kpis = state.get_escuelas_kpis(selected_mun, selected_prog, selected_estatus)

        def make_kpi(titulo: str, valor: str, subtitulo: str, icono, color_fondo: str, color_texto: str, color_borde: str):
            return ft.Container(
                content=ft.Column(
                    spacing=2,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row([
                            ft.Icon(icono, size=14, color=color_texto),
                            ft.Text(titulo, size=10, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=4),
                        ft.Text(valor, size=16, weight=ft.FontWeight.BOLD, color=color_texto),
                        ft.Text(subtitulo, size=9, color=COLOR_TEXT_MUTED, text_align=ft.TextAlign.CENTER)
                    ]
                ),
                padding=ft.Padding.symmetric(horizontal=8, vertical=10),
                bgcolor=color_fondo,
                border_radius=10,
                border=ft.Border.all(1, color_borde),
                expand=True
            )

        kpis_container.controls = [
            make_kpi("TOTAL INTERVENIDOS", str(kpis["total_centros"]), "Instituciones Educativas", ft.Icons.SCHOOL_ROUNDED, "#EFF6FF", COLOR_ELECTRIC_BLUE, "#BFDBFE"),
            make_kpi("CULMINADAS", str(kpis["culminadas"]), f"{kpis['pct_culminadas']}% del Total", ft.Icons.CHECK_CIRCLE_ROUNDED, "#DCFCE7", COLOR_STATUS_GREEN, "#86EFAC"),
            make_kpi("EN EJECUCIÓN", str(kpis["en_ejecucion"]), "Frentes Activos", ft.Icons.ENGINEERING_ROUNDED, "#FEF3C7", COLOR_STATUS_AMBER, "#FDE68A"),
            make_kpi("PARALIZADAS", str(kpis["paralizadas"]), "Atención Prioritaria", ft.Icons.WARNING_AMBER_ROUNDED, "#FEE2E2", COLOR_STATUS_RED, "#FCA5A5")
        ]

    # -------------------------------------------------------------
    # PESTAÑA 0: RESUMEN POR PROGRAMA Y MUNICIPIO
    # -------------------------------------------------------------
    def build_tab_resumen_programa_municipio() -> ft.Control:
        prog_list = state.get_escuelas_programas_resumen()
        mun_list = state.get_escuelas_municipios_resumen()

        if search_mun_query:
            sq = search_mun_query.lower()
            mun_list = [m for m in mun_list if sq in m["municipio"].lower()]

        # 1. Tabla de Programas
        prog_rows = []
        for p in prog_list:
            p_name = p.get("programa", "Programa")
            ejec = p.get("ejecutadas", 0)
            proc = p.get("en_ejecucion", 0)
            para = p.get("paralizadas", 0)
            tot = p.get("total_centros", 0)
            pct = p.get("pct_ejecucion", 0.0)

            bg_pr, col_pr = get_programa_badge_color(p_name)
            prog_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(p_name, size=11, weight=ft.FontWeight.BOLD, color=col_pr),
                                padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                bgcolor=bg_pr,
                                border_radius=4
                            )
                        ),
                        ft.DataCell(ft.Container(content=ft.Text(str(ejec), size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN), alignment=ft.Alignment(0, 0))),
                        ft.DataCell(ft.Container(content=ft.Text(str(proc), size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_AMBER if proc > 0 else COLOR_TEXT_MUTED), alignment=ft.Alignment(0, 0))),
                        ft.DataCell(ft.Container(content=ft.Text(str(para), size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_RED if para > 0 else COLOR_TEXT_MUTED), alignment=ft.Alignment(0, 0))),
                        ft.DataCell(ft.Container(content=ft.Text(str(tot), size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK), alignment=ft.Alignment(0, 0))),
                        ft.DataCell(
                            ft.Row([
                                ft.Container(
                                    content=ft.ProgressBar(value=pct / 100.0, color=COLOR_STATUS_GREEN, bgcolor="#E2E8F0", width=45),
                                    alignment=ft.Alignment(0, 0)
                                ),
                                ft.Text(f"{pct}%", size=10, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN)
                            ], spacing=4)
                        )
                    ]
                )
            )

        prog_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Programa", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)),
                ft.DataColumn(ft.Text("Ejec.", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN)),
                ft.DataColumn(ft.Text("En Ejec.", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_AMBER)),
                ft.DataColumn(ft.Text("Para.", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_RED)),
                ft.DataColumn(ft.Text("Total", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)),
                ft.DataColumn(ft.Text("Avance", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)),
            ],
            rows=prog_rows,
            column_spacing=12,
            heading_row_height=34,
            data_row_min_height=36,
            data_row_max_height=40,
            border=ft.Border.all(1, "#E2E8F0"),
            border_radius=8
        )

        # 2. Tabla de Municipios (14 Municipios)
        mun_rows = []
        for m in mun_list:
            m_name = m.get("municipio", "Municipio")
            culm = m.get("culminadas", 0)
            proc = m.get("en_ejecucion", 0)
            para = m.get("paralizadas", 0)
            tot = m.get("total_centros", 0)
            pct = m.get("pct_ejecucion", 0.0)

            pct_color = COLOR_STATUS_GREEN if pct >= 80 else (COLOR_STATUS_AMBER if pct >= 50 else COLOR_STATUS_RED)

            mun_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Row([
                                ft.Icon(ft.Icons.LOCATION_ON_ROUNDED, size=14, color=COLOR_ELECTRIC_BLUE),
                                ft.Text(m_name, size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                            ], spacing=4)
                        ),
                        ft.DataCell(ft.Container(content=ft.Text(str(culm), size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN), alignment=ft.Alignment(0, 0))),
                        ft.DataCell(ft.Container(content=ft.Text(str(proc), size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_AMBER if proc > 0 else COLOR_TEXT_MUTED), alignment=ft.Alignment(0, 0))),
                        ft.DataCell(ft.Container(content=ft.Text(str(para), size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_RED if para > 0 else COLOR_TEXT_MUTED), alignment=ft.Alignment(0, 0))),
                        ft.DataCell(ft.Container(content=ft.Text(str(tot), size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK), alignment=ft.Alignment(0, 0))),
                        ft.DataCell(
                            ft.Row([
                                ft.Container(
                                    content=ft.ProgressBar(value=pct / 100.0, color=pct_color, bgcolor="#E2E8F0", width=45),
                                    alignment=ft.Alignment(0, 0)
                                ),
                                ft.Text(f"{pct}%", size=10, weight=ft.FontWeight.BOLD, color=pct_color)
                            ], spacing=4)
                        )
                    ]
                )
            )

        mun_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Municipio", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)),
                ft.DataColumn(ft.Text("Culm.", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN)),
                ft.DataColumn(ft.Text("En Ejec.", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_AMBER)),
                ft.DataColumn(ft.Text("Para.", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_RED)),
                ft.DataColumn(ft.Text("Total", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)),
                ft.DataColumn(ft.Text("Avance", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)),
            ],
            rows=mun_rows,
            column_spacing=12,
            heading_row_height=34,
            data_row_min_height=36,
            data_row_max_height=40,
            border=ft.Border.all(1, "#E2E8F0"),
            border_radius=8
        )

        search_mun_field = ft.TextField(
            hint_text="Buscar municipio...",
            prefix_icon=ft.Icons.SEARCH_ROUNDED,
            dense=True,
            text_size=11,
            border_radius=8,
            border_color=COLOR_BORDER,
            expand=True,
            on_change=lambda e: on_mun_search_change(e.control.value)
        )

        def on_mun_search_change(val: str):
            nonlocal search_mun_query
            search_mun_query = val.strip()
            render_tab_content()
            page.update()

        return ft.Column(
            spacing=8,
            controls=[
                ft.Container(
                    content=ft.Text("Consolidado Oficial por Programa de Recuperación", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                    padding=ft.Padding.only(left=4, top=2)
                ),
                prog_table,
                ft.Container(
                    content=ft.Row([
                        ft.Text("Distribución Territorial en los 14 Municipios", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Container(
                            content=ft.Text(f"Total: {len(mun_list)} Municipios", size=11, color=COLOR_TEXT_MUTED, weight=ft.FontWeight.W_500),
                            padding=ft.Padding.symmetric(horizontal=8, vertical=2)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.Padding.only(left=4, top=6)
                ),
                search_mun_field,
                ft.Container(
                    content=ft.Column(
                        scroll=ft.ScrollMode.ADAPTIVE,
                        controls=[mun_table]
                    ),
                    expand=True
                )
            ],
            expand=True
        )

    # -------------------------------------------------------------
    # PESTAÑA 1: INVENTARIO GENERAL DE INSTITUCIONES (259 ESCUELAS)
    # -------------------------------------------------------------
    def build_tab_inventario_instituciones() -> ft.Control:
        centros = state.get_filtered_centros_educativos(selected_mun, selected_prog, selected_estatus, search_query)

        cards = []
        is_editor_role = state.is_editor()

        for c in centros:
            c_id = c.get("id")
            inst = c.get("institucion", "Centro Educativo")
            mun = c.get("municipio", "Portuguesa")
            sector = c.get("sector", "")
            prog = c.get("programa", "BRICOMILES")
            desc = c.get("descripcion", "Rehabilitación Integral")
            tipo_trabajo = c.get("tipo_trabajo", "Rehabilitación")
            est = c.get("estatus", "CULMINADA")
            pct = c.get("porcentaje", 100)
            año = c.get("año", "2024-2025")

            bg_st, col_st, bdr_st = get_status_badge_color(est)
            bg_pr, col_pr = get_programa_badge_color(prog)
            icon_trab, bg_tr, col_tr = get_work_type_icon(tipo_trabajo)

            actions = [
                ft.IconButton(
                    icon=ft.Icons.VISIBILITY_ROUNDED,
                    icon_color=COLOR_ELECTRIC_BLUE,
                    icon_size=18,
                    tooltip="Ver Ficha Técnica",
                    on_click=lambda e, item=c: open_ficha_tecnica_dialog(item)
                )
            ]

            if is_editor_role:
                actions.append(
                    ft.IconButton(
                        icon=ft.Icons.EDIT_ROUNDED,
                        icon_color=COLOR_STATUS_AMBER,
                        icon_size=18,
                        tooltip="Actualizar Avance",
                        on_click=lambda e, item=c: open_centro_educativo_modal(item)
                    )
                )

            card = ft.Container(
                content=ft.Column(
                    spacing=5,
                    controls=[
                        ft.Row([
                            ft.Row([
                                ft.Container(
                                    content=ft.Text(f"#{c_id} • {prog}", size=10, weight=ft.FontWeight.BOLD, color=col_pr),
                                    padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                    bgcolor=bg_pr,
                                    border_radius=4
                                ),
                                ft.Container(
                                    content=ft.Row([
                                        ft.Icon(icon_trab, size=11, color=col_tr),
                                        ft.Text(tipo_trabajo, size=9, weight=ft.FontWeight.BOLD, color=col_tr)
                                    ], spacing=3),
                                    padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                    bgcolor=bg_tr,
                                    border_radius=4
                                ),
                                ft.Text(f"Municipio {mun}", size=11, color=COLOR_TEXT_MUTED, weight=ft.FontWeight.W_500),
                            ], spacing=6),
                            ft.Container(
                                content=ft.Text(f"{est} ({pct}%)", size=10, weight=ft.FontWeight.BOLD, color=col_st),
                                padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                bgcolor=bg_st,
                                border=ft.Border.all(1, bdr_st),
                                border_radius=4
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(inst, size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Row([
                            ft.Icon(ft.Icons.BUILD_ROUNDED, size=12, color=COLOR_ELECTRIC_BLUE),
                            ft.Text(desc, size=10, color=COLOR_TEXT_SECONDARY, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                            ft.Text("•", size=10, color=COLOR_TEXT_MUTED),
                            ft.Icon(ft.Icons.PIN_DROP_ROUNDED, size=12, color=COLOR_TEXT_MUTED),
                            ft.Text(sector or mun, size=10, color=COLOR_TEXT_MUTED, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)
                        ], spacing=4),
                        ft.Row([
                            ft.Row([
                                ft.Icon(ft.Icons.CALENDAR_TODAY_ROUNDED, size=12, color=COLOR_TEXT_MUTED),
                                ft.Text(f"Período: {año}", size=10, color=COLOR_TEXT_MUTED)
                            ], spacing=4),
                            ft.Row(actions, spacing=0)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ]
                ),
                padding=10,
                bgcolor="#FFFFFF",
                border_radius=8,
                border=ft.Border.all(1, "#E2E8F0"),
                margin=ft.Padding.only(bottom=6)
            )
            cards.append(card)

        if not cards:
            cards.append(
                ft.Container(
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.SEARCH_OFF_ROUNDED, size=36, color=COLOR_TEXT_MUTED),
                            ft.Text("No se encontraron instituciones educativas con los filtros actuales.", size=12, color=COLOR_TEXT_MUTED)
                        ]
                    ),
                    padding=20,
                    alignment=ft.Alignment(0, 0)
                )
            )

        return ft.Column(
            spacing=4,
            controls=[
                ft.Container(
                    content=ft.Text(f"Mostrando {len(centros)} instituciones educativas registradas", size=11, color=COLOR_TEXT_MUTED, weight=ft.FontWeight.W_500),
                    padding=ft.Padding.symmetric(horizontal=4, vertical=2)
                ),
                ft.Container(
                    content=ft.ListView(
                        controls=cards,
                        expand=True,
                        spacing=6
                    ),
                    expand=True
                )
            ],
            expand=True
        )

    # -------------------------------------------------------------
    # PESTAÑA 2: INFRAESTRUCTURA POR TIPO DE TRABAJO
    # -------------------------------------------------------------
    def build_tab_infraestructura_tipos() -> ft.Control:
        tipos_list = state.get_escuelas_tipos_trabajo()
        centros = state.escuelas_data.get("centros", []) if state.escuelas_data else []

        tipos_cards = []
        for item in tipos_list:
            t_name = item.get("tipo", "Tipo")
            cant = item.get("cantidad", 0)
            pct = item.get("pct", 0.0)

            icon_trab, bg_tr, col_tr = get_work_type_icon(t_name)

            # Sub-centros correspondientes
            centros_sub = [c for c in centros if c.get("tipo_trabajo") == t_name]
            culm_sub = sum(1 for c in centros_sub if c.get("estatus") == "CULMINADA")
            proc_sub = sum(1 for c in centros_sub if c.get("estatus") == "EN EJECUCIÓN")
            para_sub = sum(1 for c in centros_sub if c.get("estatus") == "PARALIZADA")

            sample_instituciones = [c.get("institucion", "") for c in centros_sub[:3]]
            sample_txt = " • ".join(sample_instituciones) if sample_instituciones else "Obras en ejecución territorial"

            card = ft.Container(
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.Row([
                            ft.Row([
                                ft.Container(
                                    content=ft.Icon(icon_trab, size=20, color=col_tr),
                                    padding=8,
                                    bgcolor=bg_tr,
                                    border_radius=8
                                ),
                                ft.Column([
                                    ft.Text(t_name, size=14, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                    ft.Text(f"{cant} Centros Educativos • {pct}% del Total Intervenido", size=11, color=COLOR_TEXT_MUTED)
                                ], spacing=1)
                            ], spacing=8),
                            ft.Container(
                                content=ft.Text(f"{cant} Obras", size=13, weight=ft.FontWeight.BOLD, color=col_tr),
                                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                                bgcolor=bg_tr,
                                border_radius=6
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([
                            ft.Row([
                                ft.Container(width=8, height=8, border_radius=4, bgcolor=COLOR_STATUS_GREEN),
                                ft.Text(f"Culminadas: {culm_sub}", size=11, color=COLOR_STATUS_GREEN, weight=ft.FontWeight.BOLD),
                            ], spacing=4),
                            ft.Row([
                                ft.Container(width=8, height=8, border_radius=4, bgcolor=COLOR_STATUS_AMBER),
                                ft.Text(f"En Ejecución: {proc_sub}", size=11, color=COLOR_STATUS_AMBER, weight=ft.FontWeight.BOLD),
                            ], spacing=4),
                            ft.Row([
                                ft.Container(width=8, height=8, border_radius=4, bgcolor=COLOR_STATUS_RED),
                                ft.Text(f"Paralizadas: {para_sub}", size=11, color=COLOR_STATUS_RED, weight=ft.FontWeight.BOLD),
                            ], spacing=4),
                        ], spacing=16),
                        ft.ProgressBar(value=cant / 259.0 if cant <= 259 else 1.0, color=col_tr, bgcolor="#E2E8F0", height=6),
                        ft.Row([
                            ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=12, color=COLOR_TEXT_MUTED),
                            ft.Text(f"Ejemplos: {sample_txt}", size=10, color=COLOR_TEXT_SECONDARY, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, expand=True)
                        ], spacing=4)
                    ]
                ),
                padding=12,
                bgcolor="#FFFFFF",
                border_radius=10,
                border=ft.Border.all(1, "#E2E8F0"),
                margin=ft.Padding.only(bottom=8)
            )
            tipos_cards.append(card)

        return ft.Column(
            spacing=6,
            controls=[
                ft.Container(
                    content=ft.Text("Desglose de Intervenciones por Tipología de Trabajo Técnico", size=11, color=COLOR_TEXT_MUTED, weight=ft.FontWeight.W_500),
                    padding=ft.Padding.symmetric(horizontal=4, vertical=2)
                ),
                ft.Container(
                    content=ft.ListView(
                        controls=tipos_cards,
                        expand=True,
                        spacing=6
                    ),
                    expand=True
                )
            ],
            expand=True
        )

    # -------------------------------------------------------------
    # PESTAÑA 3: FRENTES EN EJECUCIÓN Y PARALIZADOS (18 FRENTES)
    # -------------------------------------------------------------
    def build_tab_frentes_prioritarios() -> ft.Control:
        frentes = state.get_escuelas_frentes_prioritarios(selected_mun)
        is_editor_role = state.is_editor()

        frentes_cards = []
        for c in frentes:
            c_id = c.get("id")
            inst = c.get("institucion", "Centro Educativo")
            mun = c.get("municipio", "Portuguesa")
            sector = c.get("sector", "")
            prog = c.get("programa", "BRICOMILES")
            desc = c.get("descripcion", "Rehabilitación")
            tipo_trabajo = c.get("tipo_trabajo", "Rehabilitación")
            est = c.get("estatus", "EN EJECUCIÓN")
            pct = c.get("porcentaje", 0)
            año = c.get("año", "2026")

            is_para = est == "PARALIZADA"
            border_c = COLOR_STATUS_RED if is_para else COLOR_STATUS_AMBER
            bg_card = "#FFF5F5" if is_para else "#FFFBEB"
            icon_trab, bg_tr, col_tr = get_work_type_icon(tipo_trabajo)

            edit_btn = ft.IconButton(
                icon=ft.Icons.EDIT_ROUNDED,
                icon_color=COLOR_STATUS_RED if is_para else COLOR_STATUS_AMBER,
                icon_size=18,
                tooltip="Actualizar Estado del Frente",
                on_click=lambda e, item=c: open_centro_educativo_modal(item)
            ) if is_editor_role else ft.Container()

            card = ft.Container(
                content=ft.Column(
                    spacing=6,
                    controls=[
                        ft.Row([
                            ft.Row([
                                ft.Icon(ft.Icons.WARNING_ROUNDED if is_para else ft.Icons.CONSTRUCTION_ROUNDED, color=border_c, size=16),
                                ft.Text(f"Frente #{c_id} • {prog}", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                ft.Text(f"({mun})", size=11, color=COLOR_TEXT_MUTED)
                            ], spacing=6),
                            ft.Row([
                                ft.Container(
                                    content=ft.Text(f"{est} • {pct}%", size=11, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                    padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                    bgcolor=border_c,
                                    border_radius=4
                                ),
                                edit_btn
                            ], spacing=4)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(inst, size=14, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.ProgressBar(value=pct / 100.0, color=border_c, bgcolor="#E2E8F0", height=6),
                        ft.Row([
                            ft.Row([
                                ft.Icon(icon_trab, size=12, color=col_tr),
                                ft.Text(f"Tipo: {tipo_trabajo}", size=11, weight=ft.FontWeight.W_500, color=COLOR_NAVY_DARK)
                            ], spacing=4),
                            ft.Row([
                                ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED, size=12, color=COLOR_TEXT_MUTED),
                                ft.Text(f"Período: {año}", size=10, color=COLOR_TEXT_MUTED)
                            ], spacing=4)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([
                            ft.Icon(ft.Icons.BUILD_CIRCLE_ROUNDED, size=12, color=COLOR_TEXT_MUTED),
                            ft.Text(desc, size=10, color=COLOR_TEXT_SECONDARY, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, expand=True)
                        ], spacing=4),
                        ft.Row([
                            ft.Icon(ft.Icons.PIN_DROP_ROUNDED, size=12, color=COLOR_TEXT_MUTED),
                            ft.Text(f"Ubicación: {sector or mun}", size=10, color=COLOR_TEXT_MUTED)
                        ], spacing=4)
                    ]
                ),
                padding=10,
                bgcolor=bg_card,
                border_radius=8,
                border=ft.Border.all(1.5, border_c),
                margin=ft.Padding.only(bottom=6)
            )
            frentes_cards.append(card)

        if not frentes_cards:
            frentes_cards.append(
                ft.Container(
                    content=ft.Text("No hay frentes en ejecución o paralizados para la selección actual.", size=12, color=COLOR_TEXT_MUTED),
                    padding=20,
                    alignment=ft.Alignment(0, 0)
                )
            )

        return ft.Column(
            spacing=4,
            controls=[
                ft.Container(
                    content=ft.Row([
                        ft.Text(f"Prioridad Gubernamental: {len(frentes)} frentes escolares en seguimiento", size=11, color=COLOR_NAVY_DARK, weight=ft.FontWeight.BOLD),
                        ft.Text("Gestión Directa Gobernador y Secretaría Superior de Operaciones", size=10, color=COLOR_STATUS_AMBER, weight=ft.FontWeight.BOLD)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.Padding.symmetric(horizontal=4, vertical=2)
                ),
                ft.Container(
                    content=ft.ListView(
                        controls=frentes_cards,
                        expand=True,
                        spacing=6
                    ),
                    expand=True
                )
            ],
            expand=True
        )

    # -------------------------------------------------------------
    # RENDERIZADO DE PESTAÑAS (TABS PERSONALIZADOS)
    # -------------------------------------------------------------
    tabs_def = [
        ("Resumen por Programa y Municipio", ft.Icons.MAP_ROUNDED),
        ("Inventario Instituciones (259)", ft.Icons.SCHOOL_ROUNDED),
        ("Infraestructura por Tipo de Trabajo", ft.Icons.PIE_CHART_ROUNDED),
        ("Frentes en Ejecución y Paralizados (18)", ft.Icons.WARNING_ROUNDED),
    ]

    def select_tab(index: int):
        nonlocal active_tab
        active_tab = index
        render_tab_chips()
        render_tab_content()
        page.update()

    def render_tab_chips():
        tab_chips_row.controls.clear()
        for idx, (label, icon) in enumerate(tabs_def):
            is_sel = idx == active_tab
            tab_chips_row.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(icon, size=14, color="#FFFFFF" if is_sel else COLOR_NAVY_DARK),
                        ft.Text(label, size=11, weight=ft.FontWeight.BOLD if is_sel else ft.FontWeight.W_500, color="#FFFFFF" if is_sel else COLOR_NAVY_DARK)
                    ], spacing=4),
                    padding=ft.Padding.symmetric(horizontal=10, vertical=6),
                    bgcolor=COLOR_ELECTRIC_BLUE if is_sel else "#F1F5F9",
                    border_radius=8,
                    border=ft.Border.all(1, COLOR_ELECTRIC_BLUE if is_sel else "#CBD5E1"),
                    on_click=lambda e, i=idx: select_tab(i)
                )
            )

    def render_tab_content():
        if active_tab == 0:
            tab_content_area.content = build_tab_resumen_programa_municipio()
        elif active_tab == 1:
            tab_content_area.content = build_tab_inventario_instituciones()
        elif active_tab == 2:
            tab_content_area.content = build_tab_infraestructura_tipos()
        elif active_tab == 3:
            tab_content_area.content = build_tab_frentes_prioritarios()

    def full_refresh():
        refresh_upper_kpis()
        render_tab_chips()
        render_tab_content()
        page.update()

    # -------------------------------------------------------------
    # BARRA SUPERIOR DE FILTROS Y ACCIONES
    # -------------------------------------------------------------
    mun_filter_dropdown = ft.Dropdown(
        label="Municipio",
        value=selected_mun,
        options=[ft.DropdownOption("Todos los Municipios")] + [ft.DropdownOption(m) for m in MUNICIPALITIES_LIST if m != "Todos los Municipios"],
        dense=True,
        text_size=11,
        border_radius=8,
        border_color=COLOR_BORDER,
        expand=True,
        on_select=lambda e: on_mun_filter_changed(e.control.value)
    )

    prog_filter_dropdown = ft.Dropdown(
        label="Programa",
        value=selected_prog,
        options=[
            ft.DropdownOption("Todos"),
            ft.DropdownOption("Bricomiles (115)"),
            ft.DropdownOption("Un Corazón para tu Escuela (93)"),
            ft.DropdownOption("Gota de Amor (51)"),
        ],
        dense=True,
        text_size=11,
        border_radius=8,
        border_color=COLOR_BORDER,
        expand=True,
        on_select=lambda e: on_prog_filter_changed(e.control.value)
    )

    estatus_filter_dropdown = ft.Dropdown(
        label="Estatus",
        value=selected_estatus,
        options=[
            ft.DropdownOption("Todos"),
            ft.DropdownOption("Culminada (241)"),
            ft.DropdownOption("En Ejecución (16)"),
            ft.DropdownOption("Paralizada (2)"),
        ],
        dense=True,
        text_size=11,
        border_radius=8,
        border_color=COLOR_BORDER,
        expand=True,
        on_select=lambda e: on_estatus_filter_changed(e.control.value)
    )

    def on_mun_filter_changed(val: str):
        nonlocal selected_mun
        selected_mun = val
        state.set_escuelas_filters(municipality=val)
        full_refresh()

    def on_prog_filter_changed(val: str):
        nonlocal selected_prog
        selected_prog = val
        state.set_escuelas_filters(programa=val)
        full_refresh()

    def on_estatus_filter_changed(val: str):
        nonlocal selected_estatus
        selected_estatus = val
        state.set_escuelas_filters(estatus=val)
        full_refresh()

    filter_bar = ft.Container(
        content=ft.Row([
            mun_filter_dropdown,
            prog_filter_dropdown,
            estatus_filter_dropdown
        ], spacing=8),
        padding=ft.Padding.symmetric(horizontal=12, vertical=4)
    )

    # Buscador de escuelas por texto
    search_bar_field = ft.TextField(
        hint_text="Buscar escuela por nombre, municipio, sector, tipo de trabajo o programa...",
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        dense=True,
        text_size=11,
        border_radius=8,
        border_color=COLOR_BORDER,
        expand=True,
        on_change=lambda e: on_search_text_changed(e.control.value)
    )

    def on_search_text_changed(val: str):
        nonlocal search_query
        search_query = val.strip()
        render_tab_content()
        page.update()

    # Botones exclusivos de gestión (Solo MASTER y ANALISTA)
    admin_buttons = []
    if state.is_editor():
        admin_buttons.append(
            ft.FilledButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.ADD_CIRCLE_ROUNDED, size=14, color="#FFFFFF"),
                    ft.Text("+ Registrar / Actualizar Centro Educativo", size=11, weight=ft.FontWeight.BOLD)
                ], spacing=4),
                bgcolor=COLOR_STATUS_GREEN,
                color="#FFFFFF",
                on_click=lambda e: open_centro_educativo_modal(None)
            )
        )
        admin_buttons.append(
            ft.OutlinedButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.FILE_UPLOAD_ROUNDED, size=14, color=COLOR_ELECTRIC_BLUE),
                    ft.Text("Importar Excel", size=11, weight=ft.FontWeight.BOLD)
                ], spacing=4),
                on_click=import_excel_dialog
            )
        )

    search_bar = ft.Container(
        content=ft.Row([
            search_bar_field,
            ft.Row(admin_buttons, spacing=6)
        ], spacing=8),
        padding=ft.Padding.symmetric(horizontal=12, vertical=4)
    )

    # -------------------------------------------------------------
    # LOGO INSTITUCIONAL Y ENCABEZADO
    # -------------------------------------------------------------
    logo_path = "logo_escuelas.png" if os.path.exists("assets/logo_escuelas.png") else None
    leading_logo = (
        ft.Image(src=logo_path, width=42, height=42, fit="contain")
        if logo_path else ft.Icon(ft.Icons.SCHOOL_ROUNDED, size=28, color=COLOR_ELECTRIC_BLUE)
    )
    header_box = create_institutional_header(
        title="Plan de Recuperación de Centros Educativos",
        subtitle="Puesto de Comando Estratégico Operacional del Estado Portuguesa • PCEO",
        show_back_button=True,
        on_back_click=lambda e: on_back_to_summary(),
        on_logout_click=lambda e: on_logout(),
        on_switch_role_click=on_switch_role,
        show_user_chip=True,
        leading_logo=leading_logo
    )

    # Inicializar componentes
    refresh_upper_kpis()
    render_tab_chips()
    render_tab_content()

    # Contenedor raíz
    return ft.Container(
        content=ft.Column(
            spacing=10,
            expand=True,
            controls=[
                header_box,
                import_panel_obj.panel_container,
                filter_bar,
                search_bar,
                kpis_container,
                ft.Container(
                    content=tab_chips_row,
                    padding=ft.Padding.only(bottom=15)
                ),
                tab_content_area
            ]
        ),
        padding=10,
        expand=True
    )
