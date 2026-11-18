"""
Módulo Detallado: Plan Construye Tu Casa
Puesto de Comando Estratégico Operacional del Estado Portuguesa (PCEO)
Gobernación del Estado Portuguesa • Ente Ejecutor: FONDEREVI
Corte Oficial 2026: 662 Viviendas Gestionadas (252 Ejecutadas, 410 Proyección y Ejecución, 0 Por Iniciar)
"""
import os
import flet as ft
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
from modules.excel_import_panel import ExcelImportPanel
from components.print_municipal_report import open_print_preview_dialog
from data.casas_parser import CasasParser, normalize_mun_name, format_number_es
from data.water_data import MUNICIPALITIES_LIST
from data.state import AppState

def get_status_colors(estatus: str) -> tuple:
    """Retorna colores (fondo, texto, borde) según el estatus de la vivienda."""
    st = (estatus or "").upper()
    if "CULMINAD" in st or "EJECUTAD" in st or "100" in st:
        return ("#DCFCE7", "#16A34A", "#86EFAC")
    elif "PARALIZAD" in st:
        return ("#FEE2E2", "#DC2626", "#FCA5A5")
    return ("#FEF3C7", "#D97706", "#FDE68A")

def build_construye_tu_casa_view(
    page: ft.Page,
    on_back_to_summary,
    on_switch_role,
    on_logout,
    selected_municipio: str = None
) -> ft.Control:
    """Construye la vista completa del Plan Construye Tu Casa con estándar PCEO."""
    state = AppState()
    casas_parser = CasasParser()

    active_tab = 0  # 0: Consolidado Municipios, 1: Frentes y Urbanismos, 2: Obras Activas
    selected_mun = selected_municipio or state.casas_municipality
    selected_estatus = state.casas_estatus
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

    # Modal: Ficha Técnica del Urbanismo o Frente
    def open_ficha_urbanismo_dialog(frente: dict):
        urb = frente.get("urbanismo", "Frente Habitacional")
        mun = frente.get("municipio", "Portuguesa")
        sec = frente.get("sector", "Sector General")
        ejec = frente.get("ejecutadas", 0)
        en_ejec = frente.get("en_ejecucion", 0)
        tot = frente.get("total", ejec + en_ejec)
        pct = frente.get("pct_avance", 0.0)
        est = frente.get("estatus", "En Ejecución")
        obs = frente.get("observaciones", "Construcción comunitaria asistida.")
        ente = frente.get("ente", "FONDEREVI")

        bg_st, col_st, bdr_st = get_status_colors(est)

        def close_dialog(e=None):
            if hasattr(page, "close"):
                page.close()
            elif hasattr(page, "pop_dialog"):
                page.pop_dialog()
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.HOME_ROUNDED, color=COLOR_ELECTRIC_BLUE, size=24),
                ft.Text("Ficha de Urbanismo — Construye Tu Casa", size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
            ], spacing=8),
            content=ft.Container(
                width=500,
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
                            ft.Container(
                                content=ft.Text(est, size=11, weight=ft.FontWeight.BOLD, color=col_st),
                                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                bgcolor=bg_st,
                                border_radius=6,
                                border=ft.Border.all(1, bdr_st)
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(urb, size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Row([
                            ft.Icon(ft.Icons.LOCATION_ON_ROUNDED, size=14, color=COLOR_TEXT_MUTED),
                            ft.Text(f"Ubicación: {sec}", size=12, color=COLOR_TEXT_SECONDARY)
                        ], spacing=4),
                        ft.Divider(height=1, color="#E2E8F0"),
                        ft.Row([
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Viviendas Culminadas", size=9.5, color=COLOR_TEXT_MUTED),
                                    ft.Text(str(ejec), size=16, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN),
                                ], spacing=2),
                                padding=8, bgcolor="#F8FAFC", border_radius=8, border=ft.Border.all(1, COLOR_BORDER), expand=True
                            ),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("En Ejecución", size=9.5, color=COLOR_TEXT_MUTED),
                                    ft.Text(str(en_ejec), size=16, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_AMBER),
                                ], spacing=2),
                                padding=8, bgcolor="#F8FAFC", border_radius=8, border=ft.Border.all(1, COLOR_BORDER), expand=True
                            ),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Total Gestionadas", size=9.5, color=COLOR_TEXT_MUTED),
                                    ft.Text(str(tot), size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                ], spacing=2),
                                padding=8, bgcolor="#F8FAFC", border_radius=8, border=ft.Border.all(1, COLOR_BORDER), expand=True
                            ),
                        ], spacing=8),
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text("Avance Físico del Frente:", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                    ft.Text(f"{pct}%", size=11, weight=ft.FontWeight.BOLD, color=col_st)
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.ProgressBar(value=pct / 100.0, color=col_st, bgcolor="#E2E8F0", height=8)
                            ], spacing=4),
                            padding=8, bgcolor="#F8FAFC", border_radius=8, border=ft.Border.all(1, COLOR_BORDER)
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=13, color=COLOR_ELECTRIC_BLUE),
                                    ft.Text("Observaciones Técnicas y Alcance:", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                                ], spacing=4),
                                ft.Text(obs, size=11.5, color=COLOR_TEXT_PRIMARY),
                                ft.Text(f"Ente responsable: {ente} • Gobernación del Estado Portuguesa", size=10, color=COLOR_TEXT_MUTED)
                            ], spacing=4),
                            padding=10, bgcolor="#F1F5F9", border_radius=8
                        )
                    ]
                )
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cerrar"),
                    on_click=close_dialog
                )
            ],
            shape=ft.RoundedRectangleBorder(radius=12)
        )
        if hasattr(page, "open"):
            page.open(dlg)
        else:
            page.show_dialog(dlg)
        page.update()

    # Modal para Registrar / Actualizar Frente Habitacional (Exclusivo Editor)
    def open_add_edit_casas_dialog(frente: dict = None):
        is_edit = frente is not None
        title_text = "Modificar Frente Habitacional" if is_edit else "Registrar Nueva Solución Habitacional"

        txt_mun = ft.Dropdown(
            label="Municipio",
            value=frente.get("municipio", "Guanare") if is_edit else (selected_mun if selected_mun != "Todos los Municipios" else "Guanare"),
            options=[ft.dropdown.Option(m, m) for m in MUNICIPALITIES_LIST if m != "Todos los Municipios"],
            dense=True
        )
        txt_urb = ft.TextField(
            label="Nombre del Urbanismo / Comunidad",
            value=frente.get("urbanismo", "") if is_edit else "",
            hint_text="ej: Urbanismo Manuelita Sáenz",
            prefix_icon=ft.Icons.HOME_ROUNDED,
            dense=True
        )
        txt_sector = ft.TextField(
            label="Sector / Parroquia",
            value=frente.get("sector", "") if is_edit else "",
            hint_text="ej: Casco Central, Corredor Comunal",
            prefix_icon=ft.Icons.LOCATION_ON_ROUNDED,
            dense=True
        )
        txt_ejec = ft.TextField(
            label="Viviendas Culminadas",
            value=str(frente.get("ejecutadas", 0)) if is_edit else "0",
            keyboard_type=ft.KeyboardType.NUMBER,
            dense=True,
            width=150
        )
        txt_proy = ft.TextField(
            label="En Ejecución / Proyección",
            value=str(frente.get("en_ejecucion", 0)) if is_edit else "0",
            keyboard_type=ft.KeyboardType.NUMBER,
            dense=True,
            width=150
        )
        txt_obs = ft.TextField(
            label="Observaciones Técnicas / Ente Ejecutor",
            value=frente.get("observaciones", "Construcción comunitaria FONDEREVI.") if is_edit else "Autoconstrucción y kits habitacionales entregados.",
            multiline=True,
            min_lines=2,
            dense=True
        )

        def save_vivienda_action(e):
            try:
                ej = int(txt_ejec.value or 0)
                pr = int(txt_proy.value or 0)
            except ValueError:
                show_feedback_snack("Ingrese cantidades numéricas válidas.", is_error=True)
                return

            tot = ej + pr
            st_text = "Culminada" if pr == 0 else "En Ejecución"

            # Registrar en auditoría
            state.log_audit(
                modulo="Plan Construye Tu Casa",
                accion="Actualización de Frente Habitacional" if is_edit else "Registro de Nuevo Frente",
                detalle=f"Municipio: {txt_mun.value} • Urbanismo: {txt_urb.value} • {ej} Culminadas • {pr} En Ejecución (Total: {tot})"
            )

            if hasattr(page, "close"):
                page.close()
            elif hasattr(page, "pop_dialog"):
                page.pop_dialog()

            full_refresh()
            show_feedback_snack(f"Frente '{txt_urb.value}' registrado exitosamente.")

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.ADD_HOME_WORK_ROUNDED, color=COLOR_ELECTRIC_BLUE),
                ft.Text(title_text, size=15, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
            ], spacing=8),
            content=ft.Container(
                width=460,
                content=ft.Column(
                    tight=True,
                    spacing=10,
                    controls=[txt_mun, txt_urb, txt_sector, ft.Row([txt_ejec, txt_proy], spacing=8), txt_obs]
                )
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cancelar"),
                    on_click=lambda e: page.close() if hasattr(page, "close") else page.pop_dialog()
                ),
                ft.FilledButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CHECK_ROUNDED, size=16),
                        ft.Text("Guardar Registro")
                    ], tight=True),
                    style=ft.ButtonStyle(bgcolor=COLOR_ELECTRIC_BLUE, color="#FFFFFF"),
                    on_click=save_vivienda_action
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
        title="Importar Excel Construye Tu Casa (.xlsx)",
        default_file="CONSTRUYE_TU_CASA_PORTUGUESA_2026.xlsx",
        on_load_callback=state.reload_casas_excel,
        on_success_callback=lambda: full_refresh(),
        accent_color="#D97706"
    )

    def import_excel_dialog(e=None):
        import_panel_obj.toggle(e)

    # -------------------------------------------------------------
    # 4 TARJETAS KPI SUPERIORES (DINÁMICAS SEGÚN FILTROS)
    # -------------------------------------------------------------
    def refresh_upper_kpis():
        kpis_container.controls.clear()
        kpis = casas_parser.get_kpis(selected_mun, selected_estatus)

        def make_kpi(label: str, val: str, sub: str, icon_name, bg_col: str, txt_col: str, bdr_col: str):
            return ft.Container(
                content=ft.Column(
                    spacing=2,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(label, size=9.5, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED),
                                ft.Container(
                                    content=ft.Icon(icon_name, size=15, color=txt_col),
                                    width=26, height=26, bgcolor=bg_col, border_radius=6,
                                    border=ft.Border.all(1, bdr_col),
                                    alignment=ft.Alignment(0, 0)
                                )
                            ]
                        ),
                        ft.Text(val, size=18, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Text(sub, size=9, weight=ft.FontWeight.W_600, color=txt_col)
                    ]
                ),
                bgcolor=COLOR_SURFACE_WHITE,
                padding=ft.Padding.symmetric(horizontal=10, vertical=8),
                border_radius=10,
                border=ft.Border.all(1, COLOR_BORDER),
                shadow=ft.BoxShadow(spread_radius=0, blur_radius=4, color="#0A000000", offset=ft.Offset(0, 1)),
                expand=True
            )

        kpis_container.controls = [
            make_kpi("VIVIENDAS GESTIONADAS", format_number_es(kpis["total_general"]), "Metas Físicas Totales", ft.Icons.HOME_ROUNDED, "#EFF6FF", COLOR_ELECTRIC_BLUE, "#BFDBFE"),
            make_kpi("CULMINADAS / ENTREGADAS", format_number_es(kpis["ejecutadas"]), f"{kpis['pct_ejecutadas']}% del Total", ft.Icons.CHECK_CIRCLE_ROUNDED, "#DCFCE7", COLOR_STATUS_GREEN, "#86EFAC"),
            make_kpi("PROYECCIÓN Y EJECUCIÓN", format_number_es(kpis["proyeccion_ejecucion"]), f"{kpis['pct_en_ejecucion']}% Frentes Activos", ft.Icons.BUILD_ROUNDED, "#FEF3C7", COLOR_STATUS_AMBER, "#FDE68A"),
            make_kpi("ENTE EJECUTOR", "FONDEREVI", "Gobernación de Portuguesa", ft.Icons.LOCATION_CITY_ROUNDED, "#F3E8FF", "#7C3AED", "#DDD6FE")
        ]

    # -------------------------------------------------------------
    # PESTAÑA 1: CONSOLIDADO POR MUNICIPIO (8 MUNICIPIOS OFICIALES)
    # -------------------------------------------------------------
    def build_tab_consolidado_municipios() -> ft.Control:
        muns_data = casas_parser.get_resumen_municipios(selected_mun)
        kpis_total = casas_parser.get_kpis(selected_mun, selected_estatus)

        rows = []
        for m in muns_data:
            pct = m["pct_ejecutado"]
            pct_color = COLOR_STATUS_GREEN if pct >= 80 else (COLOR_STATUS_AMBER if pct >= 40 else COLOR_ELECTRIC_BLUE)
            urbs_list = m.get("urbanismos", [])
            urbs_sample = ", ".join(u["urbanismo"] for u in urbs_list[:2])
            if len(urbs_list) > 2:
                urbs_sample += f" y {len(urbs_list) - 2} más"
            obs_label = f"{len(urbs_list)} Urbanismos: {urbs_sample}" if urbs_list else m.get("observaciones", "")

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Container(content=ft.Text(str(m["numero"]), size=11, color=COLOR_TEXT_MUTED), alignment=ft.Alignment(0, 0))),
                        ft.DataCell(
                            ft.Row([
                                ft.Icon(ft.Icons.LOCATION_ON_ROUNDED, size=13, color=COLOR_ELECTRIC_BLUE),
                                ft.Text(m["municipio"], size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                            ], spacing=6)
                        ),
                        ft.DataCell(ft.Container(content=ft.Text(str(m["ejecutadas"]), size=12, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN), alignment=ft.Alignment(0, 0))),
                        ft.DataCell(ft.Container(content=ft.Text(str(m["proyeccion_ejecucion"]), size=12, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_AMBER), alignment=ft.Alignment(0, 0))),
                        ft.DataCell(ft.Container(content=ft.Text(str(m["por_iniciar"]), size=11, color=COLOR_TEXT_MUTED), alignment=ft.Alignment(0, 0))),
                        ft.DataCell(ft.Container(content=ft.Text(str(m["total"]), size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK), alignment=ft.Alignment(0, 0))),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Row([
                                    ft.ProgressBar(value=pct / 100.0, color=pct_color, bgcolor="#E2E8F0", width=50),
                                    ft.Text(f"{pct}%", size=10.5, weight=ft.FontWeight.BOLD, color=pct_color)
                                ], spacing=6),
                                alignment=ft.Alignment(0, 0)
                            )
                        ),
                        ft.DataCell(
                            ft.Row([
                                ft.Text(obs_label, size=11, color=COLOR_TEXT_SECONDARY),
                                ft.IconButton(
                                    icon=ft.Icons.VISIBILITY_ROUNDED,
                                    icon_size=15,
                                    icon_color=COLOR_ELECTRIC_BLUE,
                                    tooltip=f"Ver frentes de {m['municipio']}",
                                    on_click=lambda e, m_name=m["municipio"]: set_filter_municipio(m_name)
                                )
                            ], spacing=4)
                        )
                    ]
                )
            )

        # Fila de totales
        tot_ej = kpis_total["ejecutadas"]
        tot_pr = kpis_total["proyeccion_ejecucion"]
        tot_gen = kpis_total["total_general"]
        pct_t = kpis_total["pct_ejecutadas"]

        rows.append(
            ft.DataRow(
                color="#EFF6FF",
                cells=[
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("TOTAL GENERAL PORTUGUESA", size=12, weight=ft.FontWeight.BOLD, color="#1E40AF")),
                    ft.DataCell(ft.Container(content=ft.Text(str(tot_ej), size=12, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN), alignment=ft.Alignment(0, 0))),
                    ft.DataCell(ft.Container(content=ft.Text(str(tot_pr), size=12, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_AMBER), alignment=ft.Alignment(0, 0))),
                    ft.DataCell(ft.Container(content=ft.Text("0", size=11, color=COLOR_TEXT_MUTED), alignment=ft.Alignment(0, 0))),
                    ft.DataCell(ft.Container(content=ft.Text(str(tot_gen), size=13, weight=ft.FontWeight.BOLD, color="#1E40AF"), alignment=ft.Alignment(0, 0))),
                    ft.DataCell(ft.Container(content=ft.Text(f"{pct_t}%", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN), alignment=ft.Alignment(0, 0))),
                    ft.DataCell(ft.Text(f"{len(muns_data)} Municipios en Plan Habitacional", size=11, weight=ft.FontWeight.BOLD, color="#1E40AF"))
                ]
            )
        )

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nº", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)),
                ft.DataColumn(ft.Text("Municipio", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)),
                ft.DataColumn(ft.Text("Ejecutadas", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN)),
                ft.DataColumn(ft.Text("Proyección / Ejec.", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_AMBER)),
                ft.DataColumn(ft.Text("Por Iniciar", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED)),
                ft.DataColumn(ft.Text("Total", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)),
                ft.DataColumn(ft.Text("% Avance", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)),
                ft.DataColumn(ft.Text("Observaciones / Frentes", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)),
            ],
            rows=rows,
            border=ft.Border.all(1, COLOR_BORDER),
            border_radius=8,
            heading_row_color="#F8FAFC",
            heading_row_height=38,
            data_row_min_height=42,
            column_spacing=18
        )

        return ft.ListView(
            controls=[
                ft.Container(
                    content=ft.Row([
                        ft.Row([
                            ft.Icon(ft.Icons.TABLE_CHART_ROUNDED, size=16, color=COLOR_ELECTRIC_BLUE),
                            ft.Text("Consolidado Oficial de Soluciones Habitacionales (FONDEREVI)", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                        ], spacing=6),
                        ft.Text(f"{len(muns_data)} Municipios Activos • {tot_gen} Viviendas", size=11, color=COLOR_TEXT_MUTED)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.Padding.only(bottom=8)
                ),
                ft.Row([table], scroll=ft.ScrollMode.ADAPTIVE)
            ],
            spacing=10,
            expand=True
        )

    # -------------------------------------------------------------
    # PESTAÑA 2: FRENTES DE VIVIENDA Y URBANISMOS
    # -------------------------------------------------------------
    def build_tab_frentes_urbanismos() -> ft.Control:
        all_frentes = casas_parser.parse_all()["frentes"]

        # Filtros
        filtered = all_frentes
        if selected_mun != "Todos los Municipios":
            m_norm = normalize_mun_name(selected_mun)
            filtered = [f for f in filtered if normalize_mun_name(f["municipio"]) == m_norm or m_norm in normalize_mun_name(f["municipio"])]

        if selected_estatus != "Todos":
            if selected_estatus == "Culminada":
                filtered = [f for f in filtered if f["estatus"] == "Culminada"]
            elif selected_estatus in ("En Ejecución", "Proyección y Ejecución"):
                filtered = [f for f in filtered if f["estatus"] == "En Ejecución"]

        if search_query:
            q = search_query.lower()
            filtered = [f for f in filtered if q in f["urbanismo"].lower() or q in f["sector"].lower() or q in f["municipio"].lower() or q in f.get("observaciones", "").lower()]

        cards = []
        for f in filtered:
            bg_st, col_st, bdr_st = get_status_colors(f["estatus"])
            pct = f["pct_avance"]

            card = ft.Container(
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.Row([
                            ft.Row([
                                ft.Container(
                                    content=ft.Icon(ft.Icons.HOME_ROUNDED, size=18, color=COLOR_ELECTRIC_BLUE),
                                    width=34, height=34, bgcolor="#EFF6FF", border_radius=8,
                                    alignment=ft.Alignment(0, 0)
                                ),
                                ft.Column([
                                    ft.Text(f["urbanismo"], size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                    ft.Text(f"Municipio {f['municipio']} • Sector: {f['sector']}", size=11, color=COLOR_TEXT_SECONDARY)
                                ], spacing=1)
                            ], spacing=8),
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED if f["estatus"] == "Culminada" else ft.Icons.CONSTRUCTION_ROUNDED, size=12, color=col_st),
                                    ft.Text(f["estatus"].upper(), size=10, weight=ft.FontWeight.BOLD, color=col_st)
                                ], spacing=4, tight=True),
                                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                bgcolor=bg_st,
                                border_radius=6,
                                border=ft.Border.all(1, bdr_st)
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Divider(height=1, color="#F1F5F9"),
                        ft.Row([
                            ft.Container(
                                content=ft.Row([
                                    ft.Text(f"Solución Habitacional:", size=11, color=COLOR_TEXT_MUTED),
                                    ft.Text(f"{f['total']} Viviendas", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                                ], spacing=4, tight=True),
                                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                                bgcolor="#F8FAFC",
                                border_radius=6
                            ),
                            ft.Text(f"✅ Culminadas: {f['ejecutadas']}", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN),
                            ft.Text(f"🔨 En Ejecución: {f['en_ejecucion']}", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_AMBER),
                            ft.Text(f"Ente: {f['ente']}", size=10.5, color=COLOR_TEXT_MUTED)
                        ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.DESCRIPTION_ROUNDED, size=13, color=COLOR_TEXT_SECONDARY),
                                ft.Text(f"Observación Oficial: {f['observaciones']}", size=11, weight=ft.FontWeight.W_500, color=COLOR_TEXT_SECONDARY, expand=True)
                            ], spacing=6),
                            padding=ft.Padding.symmetric(horizontal=8, vertical=5),
                            bgcolor="#F8FAFC",
                            border_radius=6,
                            border=ft.Border.all(1, "#E2E8F0")
                        ),
                        ft.Row([
                            ft.ProgressBar(value=pct / 100.0, color=col_st, bgcolor="#E2E8F0", expand=True, height=6),
                            ft.Text(f"{pct}% Avance", size=10, weight=ft.FontWeight.BOLD, color=col_st),
                            ft.TextButton(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=13),
                                    ft.Text("Ficha Detallada", size=11)
                                ], tight=True),
                                on_click=lambda e, fr=f: open_ficha_urbanismo_dialog(fr)
                            )
                        ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                    ]
                ),
                padding=12,
                bgcolor=COLOR_SURFACE_WHITE,
                border_radius=10,
                border=ft.Border.all(1, COLOR_BORDER),
                shadow=ft.BoxShadow(spread_radius=0, blur_radius=4, color="#0A000000", offset=ft.Offset(0, 1))
            )
            cards.append(card)

        if not cards:
            cards.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SEARCH_OFF_ROUNDED, size=40, color=COLOR_TEXT_MUTED),
                        ft.Text("No se encontraron urbanismos que coincidan con los filtros aplicados.", size=12, color=COLOR_TEXT_MUTED)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
                    padding=40,
                    alignment=ft.Alignment(0, 0)
                )
            )

        tot_ej = sum(f["ejecutadas"] for f in filtered)
        tot_pr = sum(f["en_ejecucion"] for f in filtered)
        tot_all = tot_ej + tot_pr

        return ft.ListView(
            controls=[
                ft.Container(
                    content=ft.Row([
                        ft.Row([
                            ft.Icon(ft.Icons.HOLIDAY_VILLAGE_ROUNDED, size=16, color=COLOR_ELECTRIC_BLUE),
                            ft.Text(f"Desglose Oficial de Urbanismos y Proyectos ({len(filtered)} de 24)", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                        ], spacing=6),
                        ft.Row([
                            ft.Text(f"✅ {tot_ej} Culminadas", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN),
                            ft.Text("•", size=11, color=COLOR_TEXT_MUTED),
                            ft.Text(f"🔨 {tot_pr} En Ejecución", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_AMBER),
                            ft.Text("•", size=11, color=COLOR_TEXT_MUTED),
                            ft.Text(f"🏠 {tot_all} Total", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                        ], spacing=6)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.Padding.only(bottom=4)
                ),
                *cards
            ],
            spacing=10,
            expand=True
        )

    # -------------------------------------------------------------
    # PESTAÑA 3: SEGUIMIENTO DE OBRAS ACTIVAS (EN EJECUCIÓN)
    # -------------------------------------------------------------
    def build_tab_obras_activas() -> ft.Control:
        frentes_activas = casas_parser.get_frentes_prioritarios(selected_mun)

        if search_query:
            q = search_query.lower()
            frentes_activas = [f for f in frentes_activas if q in f["urbanismo"].lower() or q in f["sector"].lower() or q in f["municipio"].lower()]

        tot_activas = sum(f["en_ejecucion"] for f in frentes_activas)

        cards = []
        for f in frentes_activas:
            pct = f["pct_avance"]
            card = ft.Container(
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.Row([
                            ft.Row([
                                ft.Container(
                                    content=ft.Icon(ft.Icons.CONSTRUCTION_ROUNDED, size=18, color=COLOR_STATUS_AMBER),
                                    width=34, height=34, bgcolor="#FEF3C7", border_radius=8,
                                    alignment=ft.Alignment(0, 0)
                                ),
                                ft.Column([
                                    ft.Text(f["urbanismo"], size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                    ft.Text(f"Municipio {f['municipio']} • {f['sector']}", size=11, color=COLOR_TEXT_SECONDARY)
                                ], spacing=1)
                            ], spacing=8),
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.BUILD_ROUNDED, size=11, color="#D97706"),
                                    ft.Text(f"{f['en_ejecucion']} Viviendas Activas", size=10.5, weight=ft.FontWeight.BOLD, color="#D97706")
                                ], spacing=4, tight=True),
                                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                bgcolor="#FEF3C7",
                                border_radius=6,
                                border=ft.Border.all(1, "#FDE68A")
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.DESCRIPTION_ROUNDED, size=13, color="#D97706"),
                                ft.Text(f"Observación Oficial: {f['observaciones']}", size=11, weight=ft.FontWeight.W_500, color=COLOR_NAVY_DARK, expand=True)
                            ], spacing=6),
                            padding=ft.Padding.symmetric(horizontal=8, vertical=5),
                            bgcolor="#FFFBEB",
                            border_radius=6,
                            border=ft.Border.all(1, "#FDE68A")
                        ),
                        ft.Row([
                            ft.ProgressBar(value=pct / 100.0 if pct > 0 else 0.25, color=COLOR_STATUS_AMBER, bgcolor="#E2E8F0", expand=True, height=6),
                            ft.Text(f"{f['en_ejecucion']} Viviendas en Ejecución", size=10, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_AMBER)
                        ], spacing=8),
                        ft.Row([
                            ft.Text(f"Ente Ejecutor: {f['ente']} • Plan Construye Tu Casa", size=10, color=COLOR_TEXT_MUTED),
                            ft.FilledButton(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.EDIT_NOTE_ROUNDED, size=14),
                                    ft.Text("Actualizar Avance", size=11)
                                ], tight=True),
                                style=ft.ButtonStyle(bgcolor=COLOR_NAVY_DARK, color="#FFFFFF", padding=ft.Padding.symmetric(horizontal=10, vertical=4)),
                                on_click=lambda e, fr=f: open_add_edit_casas_dialog(fr)
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ]
                ),
                padding=12,
                bgcolor=COLOR_SURFACE_WHITE,
                border_radius=10,
                border=ft.Border.all(1, "#FDE68A"),
                shadow=ft.BoxShadow(spread_radius=0, blur_radius=4, color="#0A000000", offset=ft.Offset(0, 1))
            )
            cards.append(card)

        if not cards:
            cards.append(
                ft.Container(
                    content=ft.Text("No hay frentes de vivienda activos en ejecución para este filtro.", color=COLOR_TEXT_MUTED, size=12),
                    padding=30,
                    alignment=ft.Alignment(0, 0)
                )
            )

        return ft.ListView(
            controls=[
                ft.Container(
                    content=ft.Row([
                        ft.Row([
                            ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, size=16, color=COLOR_STATUS_AMBER),
                            ft.Text("Seguimiento de Obras Activas en Ejecución", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                        ], spacing=6),
                        ft.Text(f"{tot_activas} Soluciones Habitacionales en Desarrollo", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_AMBER)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.Padding.only(bottom=8)
                ),
                *cards
            ],
            spacing=10,
            expand=True
        )

    # -------------------------------------------------------------
    # GESTIÓN DE PESTAÑAS
    # -------------------------------------------------------------
    def render_active_tab():
        if active_tab == 0:
            tab_content_area.content = build_tab_consolidado_municipios()
        elif active_tab == 1:
            tab_content_area.content = build_tab_frentes_urbanismos()
        else:
            tab_content_area.content = build_tab_obras_activas()

    def set_tab(idx: int):
        nonlocal active_tab
        active_tab = idx
        render_tab_chips()
        render_active_tab()
        page.update()

    def render_tab_chips():
        tab_chips_row.controls.clear()
        kpis = casas_parser.get_kpis(selected_mun, selected_estatus)
        tot_activas = kpis["proyeccion_ejecucion"]
        tot_muns = kpis["municipios_activos"]

        tabs_info = [
            (f"Consolidado por Municipio ({tot_muns})", ft.Icons.TABLE_CHART_ROUNDED),
            ("Frentes y Urbanismos", ft.Icons.HOLIDAY_VILLAGE_ROUNDED),
            (f"Obras Activas en Ejecución ({tot_activas})", ft.Icons.CONSTRUCTION_ROUNDED)
        ]

        for i, (name, icon) in enumerate(tabs_info):
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

    def full_refresh():
        refresh_upper_kpis()
        render_tab_chips()
        render_active_tab()
        page.update()

    def set_filter_municipio(mun_name: str):
        nonlocal selected_mun
        selected_mun = mun_name
        mun_filter.value = mun_name
        full_refresh()

    # -------------------------------------------------------------
    # BARRA DE FILTROS SUPERIORES
    # -------------------------------------------------------------
    mun_filter = ft.Dropdown(
        value=selected_mun,
        options=[ft.dropdown.Option(m, m if m != "Todos los Municipios" else "🏛️ Todos los Municipios") for m in MUNICIPALITIES_LIST],
        label="Municipio",
        dense=True,
        width=220
    )
    def on_mun_change(e):
        nonlocal selected_mun
        selected_mun = e.control.value
        state.set_casas_filters(municipality=selected_mun)
        full_refresh()
    mun_filter.on_select = on_mun_change

    estatus_filter = ft.Dropdown(
        value=selected_estatus,
        options=[
            ft.dropdown.Option("Todos", "Todos los Estatus"),
            ft.dropdown.Option("Culminada", "✅ Culminadas (252)"),
            ft.dropdown.Option("En Ejecución", "🔨 En Ejecución (410)")
        ],
        label="Estatus",
        dense=True,
        width=190
    )
    def on_estatus_change(e):
        nonlocal selected_estatus
        selected_estatus = e.control.value
        state.set_casas_filters(estatus=selected_estatus)
        full_refresh()
    estatus_filter.on_select = on_estatus_change

    search_field = ft.TextField(
        hint_text="Buscar urbanismo, sector u observación...",
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        content_padding=ft.Padding.symmetric(horizontal=10, vertical=6),
        border_radius=10,
        text_size=11,
        expand=True
    )
    def on_search_change(e):
        nonlocal search_query
        search_query = e.control.value
        render_active_tab()
        page.update()
    search_field.on_change = on_search_change

    # Botón Imprimir Reporte Municipal
    def on_print_click(e):
        mun_target = selected_mun if selected_mun != "Todos los Municipios" else "Guanare"
        k_mun = casas_parser.get_kpis(mun_target)
        report_data = {
            "municipio": mun_target,
            "demografia": state.get_municipio_demografia(mun_target),
            "kpis": {
                "pozos_op": "N/A", "pozos_tot": "N/A", "pozos_pct": "N/A",
                "asf_ton": "N/A", "asf_fallas": "N/A",
                "luz_lum": "N/A", "luz_tx": "N/A",
                "aguas_m": "N/A", "hidro_m": "N/A",
                "pue_culm": "N/A", "pue_tot": "N/A",
                "sal_culm": "N/A", "sal_tot": "N/A", "sal_pct": "N/A",
                "esc_culm": "N/A", "esc_tot": "N/A", "esc_pct": "N/A",
                "can_culm": str(k_mun["ejecutadas"]),
                "can_tot": str(k_mun["total_general"]),
                "casas_culm": str(k_mun["ejecutadas"]),
                "casas_tot": str(k_mun["total_general"]),
                "casas_proc": str(k_mun["proyeccion_ejecucion"]),
            },
            "obras": {
                "total": k_mun["total_general"],
                "culm": k_mun["ejecutadas"],
                "pct_culm": k_mun["pct_ejecutadas"],
                "proc": k_mun["proyeccion_ejecucion"],
                "pct_proc": k_mun["pct_en_ejecucion"],
                "para": 0,
                "pct_para": 0.0
            },
            "planes": [
                {
                    "name": "Plan Construye Tu Casa",
                    "metric": f"{k_mun['total_general']} Viviendas Gestionadas",
                    "detail": f"{k_mun['ejecutadas']} Culminadas • {k_mun['proyeccion_ejecucion']} En Ejecución (FONDEREVI)",
                    "status": "Operativo",
                    "status_color": "#16A34A"
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
        tooltip="Imprimir reporte municipal de viviendas en Carta Horizontal",
        on_click=on_print_click
    )

    filter_bar = ft.Container(
        content=ft.Row([mun_filter, estatus_filter, search_field, btn_imprimir], spacing=8),
        padding=ft.Padding.symmetric(horizontal=10, vertical=6),
        bgcolor=COLOR_SURFACE_WHITE,
        border_radius=8,
        border=ft.Border.all(1, COLOR_BORDER)
    )

    # Barra inferior de edición (Exclusivo Editor: Master / Analista)
    editor_bar = None
    if state.is_editor():
        editor_bar = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.FilledButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.ADD_HOME_WORK_ROUNDED, size=16),
                            ft.Text("Registrar o Actualizar Solución Habitacional / Frente", size=12, weight=ft.FontWeight.BOLD)
                        ], tight=True),
                        style=ft.ButtonStyle(bgcolor=COLOR_ELECTRIC_BLUE, color="#FFFFFF", padding=ft.Padding.symmetric(horizontal=14, vertical=8)),
                        on_click=lambda e: open_add_edit_casas_dialog()
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

    # Inicializar componentes
    refresh_upper_kpis()
    render_tab_chips()
    render_active_tab()

    # Logotipo oficial
    has_logo = os.path.exists("assets/logo_casas.png")
    leading_logo = ft.Image(
        src="logo_casas.png",
        width=36,
        height=36,
        fit=ft.BoxFit.CONTAIN
    ) if has_logo else ft.Icon(ft.Icons.HOME_ROUNDED, color=COLOR_ELECTRIC_BLUE, size=28)

    header = create_institutional_header(
        title="Plan Construye Tu Casa",
        subtitle="Autoconstrucción Comunitaria y Soluciones Habitacionales Dignas (FONDEREVI)",
        current_role=state.current_role,
        show_back_button=True,
        on_back_click=lambda e: on_back_to_summary(),
        on_switch_role_click=on_switch_role,
        on_logout_click=on_logout,
        leading_logo=leading_logo
    )

    return ft.Column(
        spacing=0,
        expand=True,
        controls=[
            header,
            import_panel_obj.panel_container,
            ft.Container(
                content=ft.Column(
                    spacing=10,
                    controls=[
                        filter_bar,
                        kpis_container,
                        ft.Container(
                            content=tab_chips_row,
                            padding=ft.Padding.only(bottom=15)
                        ),
                        tab_content_area
                    ],
                    expand=True
                ),
                padding=12,
                expand=True
            ),
            editor_bar
        ]
    )
