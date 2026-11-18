"""
Módulo Detallado: Plan de Recuperación y Rehabilitación de Espacios de Salud
Puesto de Comando Estratégico Operacional del Estado Portuguesa (PCEO)
Secretaría Superior de Operaciones Generales - Gobernación del Estado Portuguesa
Corte Oficial: Noviembre 2026 - 134 Obras (113 Culminadas, 17 En Proceso, 4 Paralizadas)
"""
import os
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

def get_tipo_badge_color(tipo: str) -> tuple[str, str]:
    """Retorna (color_fondo, color_texto) según el tipo de centro de salud."""
    t = (tipo or "").upper()
    if "HOSPITAL" in t:
        return ("#EFF6FF", "#1D4ED8")   # Azul
    elif "CDI" in t:
        return ("#F0FDF4", "#15803D")   # Verde
    elif "SRI" in t:
        return ("#FDF4FF", "#A21CAF")   # Púrpura
    elif "CPT" in t:
        return ("#FEF3C7", "#B45309")   # Ámbar
    elif "FARMACIA" in t:
        return ("#ECFDF5", "#047857")   # Esmeralda
    elif "ESPECIAL" in t or "CAT" in t:
        return ("#FFF1F2", "#BE123C")   # Rosa fuerte
    return ("#F1F5F9", "#475569")       # Gris

def get_status_badge_color(estatus: str) -> tuple[str, str, str]:
    """Retorna (color_fondo, color_texto, color_borde) según el estatus del centro."""
    st = (estatus or "").upper()
    if "CULMINAD" in st or "100" in st:
        return ("#DCFCE7", "#16A34A", "#86EFAC")
    elif "PARALIZAD" in st:
        return ("#FEE2E2", "#DC2626", "#FCA5A5")
    return ("#FEF3C7", "#D97706", "#FDE68A")  # En proceso / Por equipar

def build_salud_view(
    page: ft.Page,
    on_back_to_summary,
    on_switch_role,
    on_logout
) -> ft.Control:
    """Construye la vista interactiva oficial del Plan Espacios de Salud."""
    state = AppState()

    # Estado local de navegación y filtros
    active_tab = 0  # 0 a 3
    selected_mun = state.salud_municipality
    selected_tipo = state.salud_tipo
    selected_estatus = state.salud_estatus
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

    # Modal: Ficha Técnica Completa del Centro de Salud
    def open_ficha_tecnica_dialog(centro: dict):
        c_id = centro.get("id")
        nombre = centro.get("nombre", "Centro de Salud")
        mun = centro.get("municipio", "Portuguesa")
        asic = centro.get("asic", "ASIC General")
        direccion = centro.get("direccion", "Dirección en campo")
        tipo = centro.get("tipo_centro", "CPT")
        fase = centro.get("fase_nivel", "")
        estatus = centro.get("estatus", "CULMINADA")
        pct = centro.get("porcentaje", 100)
        ente = centro.get("ente_ejecutor", "Gobernación")
        notas = centro.get("notas", "Intervención ejecutada en el marco del Plan de Recuperación de Espacios de Salud.")

        bg_st, col_st, bdr_st = get_status_badge_color(estatus)
        bg_tp, col_tp = get_tipo_badge_color(tipo)

        def close_dialog(e=None):
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.LOCAL_HOSPITAL_ROUNDED, color=COLOR_ELECTRIC_BLUE, size=24),
                ft.Text("Ficha del Centro de Salud", size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
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
                                content=ft.Text(f"Centro #{c_id} • {tipo} {fase}".strip(), size=11, weight=ft.FontWeight.BOLD, color=col_tp),
                                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                bgcolor=bg_tp,
                                border_radius=6
                            ),
                            ft.Container(
                                content=ft.Text(f"{estatus} ({pct}%)", size=11, weight=ft.FontWeight.BOLD, color=col_st),
                                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                bgcolor=bg_st,
                                border=ft.Border.all(1, bdr_st),
                                border_radius=6
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(nombre, size=15, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Container(
                            content=ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Row([
                                        ft.Icon(ft.Icons.LOCATION_CITY_ROUNDED, size=14, color=COLOR_ELECTRIC_BLUE),
                                        ft.Text(f"Municipio: {mun}", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                        ft.Text("•", size=12, color=COLOR_TEXT_MUTED),
                                        ft.Icon(ft.Icons.BUSINESS_ROUNDED, size=14, color="#64748B"),
                                        ft.Text(f"ASIC: {asic}", size=12, color=COLOR_TEXT_SECONDARY)
                                    ], spacing=4),
                                    ft.Row([
                                        ft.Icon(ft.Icons.PIN_DROP_ROUNDED, size=14, color=COLOR_TEXT_MUTED),
                                        ft.Text(f"Dirección: {direccion}", size=11, color=COLOR_TEXT_SECONDARY, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS)
                                    ], spacing=4),
                                    ft.Row([
                                        ft.Icon(ft.Icons.ENGINEERING_ROUNDED, size=14, color=COLOR_STATUS_AMBER),
                                        ft.Text(f"Ente Ejecutor: {ente}", size=11, weight=ft.FontWeight.W_500, color=COLOR_NAVY_DARK)
                                    ], spacing=4)
                                ]
                            ),
                            padding=10,
                            bgcolor="#F8FAFC",
                            border_radius=8,
                            border=ft.Border.all(1, "#E2E8F0")
                        ),
                        ft.Text("Porcentaje de Ejecución Física:", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.ProgressBar(value=pct / 100.0, color=col_st, bgcolor="#E2E8F0", height=8),
                        ft.Text("Observaciones y Notas de Gestión:", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Container(
                            content=ft.Text(notas, size=11, color=COLOR_NAVY_DARK),
                            padding=8,
                            bgcolor="#FFFFFF",
                            border_radius=6,
                            border=ft.Border.all(1, "#CBD5E1")
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

    # Modal: Registrar Centro de Salud / Actualizar Avance (Solo MASTER y ANALISTA)
    def open_centro_salud_modal(centro_existente: dict = None):
        is_edit = centro_existente is not None

        nombre_field = ft.TextField(
            label="Nombre del Centro de Salud *",
            value=centro_existente.get("nombre", "") if is_edit else "",
            dense=True,
            text_size=12,
            border_radius=8,
            border_color=COLOR_BORDER
        )

        muns_options = [m for m in MUNICIPALITIES_LIST if m != "Todos los Municipios"]
        mun_dropdown = ft.Dropdown(
            label="Municipio *",
            value=centro_existente.get("municipio", "Guanare") if is_edit else "Guanare",
            options=[ft.DropdownOption(m) for m in muns_options],
            dense=True,
            text_size=12,
            border_radius=8,
            border_color=COLOR_BORDER
        )

        asic_field = ft.TextField(
            label="ASIC (Área de Salud Integral) *",
            value=centro_existente.get("asic", "") if is_edit else "",
            dense=True,
            text_size=12,
            border_radius=8,
            border_color=COLOR_BORDER
        )

        dir_field = ft.TextField(
            label="Dirección / Ubicación Exacta *",
            value=centro_existente.get("direccion", "") if is_edit else "",
            dense=True,
            text_size=12,
            border_radius=8,
            border_color=COLOR_BORDER
        )

        tipos_opts = ["CPT", "CDI", "SRI", "HOSPITAL", "FARMACIA", "ESPECIAL", "CAT"]
        tipo_dropdown = ft.Dropdown(
            label="Tipo de Centro *",
            value=centro_existente.get("tipo_centro", "CPT") if is_edit else "CPT",
            options=[ft.DropdownOption(t) for t in tipos_opts],
            dense=True,
            text_size=12,
            border_radius=8,
            border_color=COLOR_BORDER
        )

        fase_field = ft.TextField(
            label="Fase / Nivel (ej. CPT II, Hospital II, SRI I)",
            value=centro_existente.get("fase_nivel", "") if is_edit else "CPT II",
            dense=True,
            text_size=12,
            border_radius=8,
            border_color=COLOR_BORDER
        )

        estatus_dropdown = ft.Dropdown(
            label="Estatus de la Obra *",
            value=centro_existente.get("estatus", "CULMINADA") if is_edit else "CULMINADA",
            options=[
                ft.DropdownOption("CULMINADA"),
                ft.DropdownOption("EN PROCESO"),
                ft.DropdownOption("PARALIZADA")
            ],
            dense=True,
            text_size=12,
            border_radius=8,
            border_color=COLOR_BORDER
        )

        pct_field = ft.TextField(
            label="% de Avance Físico (0 - 100) *",
            value=str(centro_existente.get("porcentaje", 100)) if is_edit else "100",
            dense=True,
            text_size=12,
            border_radius=8,
            border_color=COLOR_BORDER
        )

        ente_field = ft.TextField(
            label="Ente Ejecutor *",
            value=centro_existente.get("ente_ejecutor", "GOBERNACIÓN Y ALCALDÍA") if is_edit else "GOBERNACIÓN Y ALCALDÍA",
            dense=True,
            text_size=12,
            border_radius=8,
            border_color=COLOR_BORDER
        )

        notas_field = ft.TextField(
            label="Notas de Inspección / Observaciones",
            value=centro_existente.get("notas", "") if is_edit else "",
            dense=True,
            text_size=12,
            multiline=True,
            min_lines=2,
            max_lines=3,
            border_radius=8,
            border_color=COLOR_BORDER
        )

        def close_modal(e=None):
            modal_dlg.open = False
            page.update()

        def save_centro(e):
            nom = nombre_field.value.strip()
            mun = mun_dropdown.value
            asic = asic_field.value.strip()
            direc = dir_field.value.strip()
            tipo = tipo_dropdown.value
            fase = fase_field.value.strip()
            est = estatus_dropdown.value
            ente = ente_field.value.strip() or "GOBERNACIÓN"
            notas = notas_field.value.strip()

            if not nom or not mun or not asic:
                show_feedback_snack("Debe completar los campos obligatorios: Nombre, Municipio y ASIC.", is_error=True)
                return

            try:
                pct = float(pct_field.value.strip().replace("%", "").replace(",", "."))
                pct = max(0.0, min(100.0, pct))
            except Exception:
                pct = 100.0 if est == "CULMINADA" else 50.0

            if is_edit:
                c_id = centro_existente.get("id")
                ok = state.update_centro_salud(
                    centro_id=c_id,
                    estatus=est,
                    porcentaje=pct,
                    ente_ejecutor=ente,
                    notas=notas
                )
                if ok:
                    show_feedback_snack(f"Centro #{c_id} '{nom}' actualizado correctamente.")
                else:
                    show_feedback_snack("Error al actualizar el centro.", is_error=True)
            else:
                nuevo = state.add_centro_salud(
                    municipio=mun,
                    nombre=nom,
                    asic=asic,
                    direccion=direc,
                    tipo_centro=tipo,
                    fase_nivel=fase,
                    estatus=est,
                    porcentaje=pct,
                    ente_ejecutor=ente,
                    notas=notas
                )
                if nuevo:
                    show_feedback_snack(f"Nuevo centro de salud #{nuevo.get('id')} registrado exitosamente.")

            close_modal()
            full_refresh()

        modal_dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.EDIT_ROUNDED if is_edit else ft.Icons.ADD_CIRCLE_ROUNDED, color=COLOR_ELECTRIC_BLUE, size=24),
                ft.Text("Actualizar Avance del Centro" if is_edit else "Registrar Nuevo Centro de Salud", size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
            ], spacing=8),
            content=ft.Container(
                width=500,
                content=ft.Column(
                    tight=True,
                    spacing=8,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        nombre_field,
                        ft.Row([mun_dropdown, asic_field], spacing=8),
                        dir_field,
                        ft.Row([tipo_dropdown, fase_field], spacing=8),
                        ft.Row([estatus_dropdown, pct_field], spacing=8),
                        ente_field,
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
                    content=ft.Text("Guardar Cambios" if is_edit else "Registrar Centro"),
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
        title="Importar Excel Espacios de Salud (.xlsx)",
        default_file="ESPACIOS_DE_SALUD_PORTUGUESA_2026.xlsx",
        on_load_callback=state.reload_salud_excel,
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
        kpis = state.get_salud_kpis(selected_mun, selected_tipo, selected_estatus)

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
            make_kpi("TOTAL OBRAS", str(kpis["total_obras"]), f"{kpis['total_centros']} Centros Salud", ft.Icons.LOCAL_HOSPITAL_ROUNDED, "#EFF6FF", COLOR_ELECTRIC_BLUE, "#BFDBFE"),
            make_kpi("CULMINADAS", str(kpis["culminadas"]), f"{kpis['pct_culminadas']}% del Total", ft.Icons.CHECK_CIRCLE_ROUNDED, "#DCFCE7", COLOR_STATUS_GREEN, "#86EFAC"),
            make_kpi("EN PROCESO", str(kpis["en_proceso"]), "Frentes Activos", ft.Icons.ENGINEERING_ROUNDED, "#FEF3C7", COLOR_STATUS_AMBER, "#FDE68A"),
            make_kpi("PARALIZADAS", str(kpis["paralizadas"]), "Atención Crítica", ft.Icons.WARNING_AMBER_ROUNDED, "#FEE2E2", COLOR_STATUS_RED, "#FCA5A5")
        ]

    # -------------------------------------------------------------
    # PESTAÑA 0: RESUMEN POR MUNICIPIO (14 MUNICIPIOS)
    # -------------------------------------------------------------
    def build_tab_resumen_municipio() -> ft.Control:
        resumen_list = state.get_salud_municipios_resumen()

        if search_mun_query:
            sq = search_mun_query.lower()
            resumen_list = [m for m in resumen_list if sq in m["municipio"].lower()]

        rows = []
        for item in resumen_list:
            m_name = item["municipio"]
            culm = item["culminadas"]
            proc = item["en_proceso"]
            para = item["paralizadas"]
            tot = item["total_obras"]
            pct = item["pct_culminacion"]

            pct_color = COLOR_STATUS_GREEN if pct >= 80 else (COLOR_STATUS_AMBER if pct >= 50 else COLOR_STATUS_RED)

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Row([
                                ft.Icon(ft.Icons.LOCATION_ON_ROUNDED, size=14, color=COLOR_ELECTRIC_BLUE),
                                ft.Text(m_name, size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                            ], spacing=4)
                        ),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(str(culm), size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN),
                                alignment=ft.Alignment(0, 0)
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(str(proc), size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_AMBER if proc > 0 else COLOR_TEXT_MUTED),
                                alignment=ft.Alignment(0, 0)
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(str(para), size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_RED if para > 0 else COLOR_TEXT_MUTED),
                                alignment=ft.Alignment(0, 0)
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(str(tot), size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                alignment=ft.Alignment(0, 0)
                            )
                        ),
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

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Municipio", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)),
                ft.DataColumn(ft.Text("Culm.", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN)),
                ft.DataColumn(ft.Text("Proc.", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_AMBER)),
                ft.DataColumn(ft.Text("Para.", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_RED)),
                ft.DataColumn(ft.Text("Total", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)),
                ft.DataColumn(ft.Text("Avance", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)),
            ],
            rows=rows,
            column_spacing=12,
            heading_row_height=36,
            data_row_min_height=36,
            data_row_max_height=42,
            border=ft.Border.all(1, "#E2E8F0"),
            border_radius=8
        )

        return ft.Column(
            spacing=8,
            controls=[
                ft.Row([
                    search_mun_field,
                    ft.Container(
                        content=ft.Text(f"Total: {len(resumen_list)} Municipios", size=11, color=COLOR_TEXT_MUTED, weight=ft.FontWeight.W_500),
                        padding=ft.Padding.symmetric(horizontal=8, vertical=4)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(
                    content=ft.Column(
                        scroll=ft.ScrollMode.ADAPTIVE,
                        controls=[table]
                    ),
                    expand=True
                )
            ],
            expand=True
        )

    # -------------------------------------------------------------
    # PESTAÑA 1: INVENTARIO GENERAL DE CENTROS (133 CENTROS)
    # -------------------------------------------------------------
    def build_tab_inventario_centros() -> ft.Control:
        centros = state.get_filtered_centros_salud(selected_mun, selected_tipo, selected_estatus, search_query)

        cards = []
        is_editor_role = state.is_editor()

        for c in centros:
            c_id = c.get("id")
            nom = c.get("nombre")
            mun = c.get("municipio")
            asic = c.get("asic")
            direc = c.get("direccion")
            tipo = c.get("tipo_centro")
            fase = c.get("fase_nivel")
            est = c.get("estatus")
            pct = c.get("porcentaje")
            ente = c.get("ente_ejecutor")

            bg_st, col_st, bdr_st = get_status_badge_color(est)
            bg_tp, col_tp = get_tipo_badge_color(tipo)

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
                        on_click=lambda e, item=c: open_centro_salud_modal(item)
                    )
                )

            card = ft.Container(
                content=ft.Column(
                    spacing=6,
                    controls=[
                        ft.Row([
                            ft.Row([
                                ft.Container(
                                    content=ft.Text(f"#{c_id} • {tipo} {fase}".strip(), size=10, weight=ft.FontWeight.BOLD, color=col_tp),
                                    padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                    bgcolor=bg_tp,
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
                        ft.Text(nom, size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Row([
                            ft.Icon(ft.Icons.BUSINESS_ROUNDED, size=12, color=COLOR_ELECTRIC_BLUE),
                            ft.Text(f"ASIC: {asic}", size=11, color=COLOR_NAVY_DARK, weight=ft.FontWeight.W_500),
                            ft.Text("•", size=11, color=COLOR_TEXT_MUTED),
                            ft.Icon(ft.Icons.PIN_DROP_ROUNDED, size=12, color=COLOR_TEXT_MUTED),
                            ft.Text(direc, size=10, color=COLOR_TEXT_MUTED, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, expand=True)
                        ], spacing=4),
                        ft.Row([
                            ft.Row([
                                ft.Icon(ft.Icons.HANDSHAKE_ROUNDED, size=12, color=COLOR_STATUS_AMBER),
                                ft.Text(f"Ente: {ente}", size=10, color=COLOR_TEXT_SECONDARY)
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
                            ft.Text("No se encontraron centros de salud con los filtros actuales.", size=12, color=COLOR_TEXT_MUTED)
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
                    content=ft.Text(f"Mostrando {len(centros)} centros de salud registrados", size=11, color=COLOR_TEXT_MUTED, weight=ft.FontWeight.W_500),
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
    # PESTAÑA 2: INFRAESTRUCTURA POR TIPOLOGÍA
    # -------------------------------------------------------------
    def build_tab_infraestructura_tipologia() -> ft.Control:
        tipos_list = state.get_salud_tipologias_resumen()
        centros = state.salud_data.get("centros", []) if state.salud_data else []

        tipos_cards = []
        icons_map = {
            "HOSPITAL": ft.Icons.LOCAL_HOSPITAL_ROUNDED,
            "CDI": ft.Icons.MEDICAL_SERVICES_ROUNDED,
            "SRI": ft.Icons.HEALING_ROUNDED,
            "CPT": ft.Icons.HEALTH_AND_SAFETY_ROUNDED,
            "ESPECIAL": ft.Icons.VACCINES_ROUNDED,
            "FARMACIA": ft.Icons.MEDICATION_ROUNDED,
        }

        for item in tipos_list:
            t_name = item["tipo"]
            cant = item["cantidad"]

            # Contar en detalle cuántos corresponden a este tipo
            matching_key = "HOSPITAL" if "HOSPITAL" in t_name.upper() else (
                "CDI" if "CDI" in t_name.upper() else (
                    "SRI" if "SRI" in t_name.upper() else (
                        "CPT" if "CPT" in t_name.upper() else (
                            "FARMACIA" if "FARMACIA" in t_name.upper() else "ESPECIAL"
                        )
                    )
                )
            )

            icon_item = icons_map.get(matching_key, ft.Icons.LOCAL_HOSPITAL_ROUNDED)
            bg_tp, col_tp = get_tipo_badge_color(matching_key)

            # Centros del detalle de esta tipología
            centros_sub = [c for c in centros if matching_key in c.get("tipo_centro", "") or (matching_key == "ESPECIAL" and "CAT" in c.get("tipo_centro", ""))]
            culm_sub = sum(1 for c in centros_sub if c.get("estatus") == "CULMINADA")
            proc_sub = sum(1 for c in centros_sub if c.get("estatus") == "EN PROCESO")
            para_sub = sum(1 for c in centros_sub if c.get("estatus") == "PARALIZADA")

            card = ft.Container(
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.Row([
                            ft.Row([
                                ft.Container(
                                    content=ft.Icon(icon_item, size=20, color=col_tp),
                                    padding=6,
                                    bgcolor=bg_tp,
                                    border_radius=8
                                ),
                                ft.Column([
                                    ft.Text(t_name, size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                    ft.Text(f"Tipología de Red Asistencial Pública", size=10, color=COLOR_TEXT_MUTED)
                                ], spacing=1)
                            ], spacing=8),
                            ft.Container(
                                content=ft.Text(f"{cant} Centros", size=13, weight=ft.FontWeight.BOLD, color=col_tp),
                                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                                bgcolor=bg_tp,
                                border_radius=6
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, size=12, color=COLOR_STATUS_GREEN),
                                    ft.Text(f"{culm_sub} Culminadas", size=11, color=COLOR_STATUS_GREEN, weight=ft.FontWeight.BOLD)
                                ], spacing=4),
                                expand=True
                            ),
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.ENGINEERING_ROUNDED, size=12, color=COLOR_STATUS_AMBER),
                                    ft.Text(f"{proc_sub} En Proceso", size=11, color=COLOR_STATUS_AMBER, weight=ft.FontWeight.BOLD)
                                ], spacing=4),
                                expand=True
                            ),
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, size=12, color=COLOR_STATUS_RED),
                                    ft.Text(f"{para_sub} Paralizadas", size=11, color=COLOR_STATUS_RED, weight=ft.FontWeight.BOLD)
                                ], spacing=4),
                                expand=True
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
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
                    content=ft.Text("Desglose Oficial de la Red Hospitalaria y Ambulatoria de Portuguesa", size=11, color=COLOR_TEXT_MUTED, weight=ft.FontWeight.W_500),
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
    # PESTAÑA 3: FRENTES EN PROCESO Y PARALIZADOS (21 FRENTES)
    # -------------------------------------------------------------
    def build_tab_frentes_prioritarios() -> ft.Control:
        frentes = state.get_salud_frentes_prioritarios(selected_mun)
        is_editor_role = state.is_editor()

        frentes_cards = []
        for c in frentes:
            c_id = c.get("id")
            nom = c.get("nombre")
            mun = c.get("municipio")
            asic = c.get("asic")
            direc = c.get("direccion")
            tipo = c.get("tipo_centro")
            fase = c.get("fase_nivel")
            est = c.get("estatus")
            pct = c.get("porcentaje")
            ente = c.get("ente_ejecutor")

            is_para = est == "PARALIZADA"
            border_c = COLOR_STATUS_RED if is_para else COLOR_STATUS_AMBER
            bg_card = "#FFF5F5" if is_para else "#FFFBEB"

            edit_btn = ft.IconButton(
                icon=ft.Icons.EDIT_ROUNDED,
                icon_color=COLOR_STATUS_RED if is_para else COLOR_STATUS_AMBER,
                icon_size=18,
                tooltip="Actualizar Estado del Frente",
                on_click=lambda e, item=c: open_centro_salud_modal(item)
            ) if is_editor_role else ft.Container()

            card = ft.Container(
                content=ft.Column(
                    spacing=6,
                    controls=[
                        ft.Row([
                            ft.Row([
                                ft.Icon(ft.Icons.WARNING_ROUNDED if is_para else ft.Icons.CONSTRUCTION_ROUNDED, color=border_c, size=16),
                                ft.Text(f"Frente #{c_id} • {tipo} {fase}".strip(), size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
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
                        ft.Text(nom, size=14, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.ProgressBar(value=pct / 100.0, color=border_c, bgcolor="#E2E8F0", height=6),
                        ft.Row([
                            ft.Row([
                                ft.Icon(ft.Icons.BUSINESS_ROUNDED, size=12, color=COLOR_ELECTRIC_BLUE),
                                ft.Text(f"ASIC: {asic}", size=11, weight=ft.FontWeight.W_500, color=COLOR_NAVY_DARK)
                            ], spacing=4),
                            ft.Row([
                                ft.Icon(ft.Icons.HANDSHAKE_ROUNDED, size=12, color=COLOR_TEXT_MUTED),
                                ft.Text(f"Ente: {ente}", size=10, color=COLOR_TEXT_MUTED)
                            ], spacing=4)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([
                            ft.Icon(ft.Icons.PIN_DROP_ROUNDED, size=12, color=COLOR_TEXT_MUTED),
                            ft.Text(direc, size=10, color=COLOR_TEXT_SECONDARY, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)
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
                    content=ft.Text("No hay frentes en proceso o paralizados para la selección actual.", size=12, color=COLOR_TEXT_MUTED),
                    padding=20,
                    alignment=ft.Alignment(0, 0)
                )
            )

        return ft.Column(
            spacing=4,
            controls=[
                ft.Container(
                    content=ft.Row([
                        ft.Text(f"Prioridad Gubernamental: {len(frentes)} frentes en seguimiento directo", size=11, color=COLOR_NAVY_DARK, weight=ft.FontWeight.BOLD),
                        ft.Text("Gestión Directa Gobernador y ESINSEP", size=10, color=COLOR_STATUS_AMBER, weight=ft.FontWeight.BOLD)
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
        ("Resumen por Municipio", ft.Icons.MAP_ROUNDED),
        ("Inventario Centros (133)", ft.Icons.LOCAL_HOSPITAL_ROUNDED),
        ("Infraestructura por Tipo", ft.Icons.PIE_CHART_ROUNDED),
        ("Frentes en Proceso (21)", ft.Icons.WARNING_ROUNDED),
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
            tab_content_area.content = build_tab_resumen_municipio()
        elif active_tab == 1:
            tab_content_area.content = build_tab_inventario_centros()
        elif active_tab == 2:
            tab_content_area.content = build_tab_infraestructura_tipologia()
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

    tipo_filter_dropdown = ft.Dropdown(
        label="Tipo de Centro",
        value=selected_tipo,
        options=[
            ft.DropdownOption("Todos los Tipos"),
            ft.DropdownOption("Hospitales (8)"),
            ft.DropdownOption("CDI (11)"),
            ft.DropdownOption("SRI (7)"),
            ft.DropdownOption("CPT (50)"),
            ft.DropdownOption("Especiales (6)"),
            ft.DropdownOption("Farmacias (6)"),
        ],
        dense=True,
        text_size=11,
        border_radius=8,
        border_color=COLOR_BORDER,
        expand=True,
        on_select=lambda e: on_tipo_filter_changed(e.control.value)
    )

    estatus_filter_dropdown = ft.Dropdown(
        label="Estatus",
        value=selected_estatus,
        options=[
            ft.DropdownOption("Todos los Estatus"),
            ft.DropdownOption("Culminada (113)"),
            ft.DropdownOption("En Proceso (17)"),
            ft.DropdownOption("Paralizada (4)"),
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
        state.set_salud_filters(municipality=val)
        full_refresh()

    def on_tipo_filter_changed(val: str):
        nonlocal selected_tipo
        selected_tipo = val
        state.set_salud_filters(tipo=val)
        full_refresh()

    def on_estatus_filter_changed(val: str):
        nonlocal selected_estatus
        selected_estatus = val
        state.set_salud_filters(estatus=val)
        full_refresh()

    filter_bar = ft.Container(
        content=ft.Row([
            mun_filter_dropdown,
            tipo_filter_dropdown,
            estatus_filter_dropdown
        ], spacing=8),
        padding=ft.Padding.symmetric(horizontal=12, vertical=4)
    )

    # Buscador de centros por texto
    search_bar_field = ft.TextField(
        hint_text="Buscar centro por nombre, ASIC, dirección o ente ejecutor...",
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
                    ft.Text("+ Registrar Centro / Avance", size=11, weight=ft.FontWeight.BOLD)
                ], spacing=4),
                bgcolor=COLOR_STATUS_GREEN,
                color="#FFFFFF",
                on_click=lambda e: open_centro_salud_modal(None)
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
    logo_path = "logo_espacios_salud.png" if os.path.exists("assets/logo_espacios_salud.png") else None
    leading_logo = (
        ft.Image(src=logo_path, width=42, height=42, fit="contain")
        if logo_path else ft.Icon(ft.Icons.LOCAL_HOSPITAL_ROUNDED, size=28, color=COLOR_ELECTRIC_BLUE)
    )
    header_box = create_institutional_header(
        title="Plan Espacios de Salud",
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
