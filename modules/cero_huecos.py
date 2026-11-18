"""
Módulo Oficial: Plan Cero Huecos (Asfalto, Bacheo y Pavimentación)
Puesto de Comando Estratégico Operacional del Estado Portuguesa (PCEO)
"""
import os
import flet as ft
from datetime import datetime
from typing import Optional, List, Dict
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
from components.print_municipal_report import open_print_preview_dialog
from data.state import AppState
from modules.excel_import_panel import ExcelImportPanel

def fmt_es(val: int | float, dec: int = 0) -> str:
    """Formatea números con separador de miles en punto y decimal en coma."""
    if val is None:
        return "0"
    if dec > 0:
        return f"{float(val):,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{int(round(float(val))):,}".replace(",", ".")

def build_cero_huecos_view(
    page: ft.Page,
    on_back_to_summary,
    on_switch_role,
    on_logout
) -> ft.Control:
    """Construye la vista interactiva oficial del Plan Cero Huecos."""
    state = AppState()

    # Estado local de navegación y filtros
    active_tab = 0  # 0 a 3
    selected_ub = state.cero_huecos_ubicacion
    selected_per = state.cero_huecos_periodo

    # Buscadores locales
    search_ub_query = ""
    search_fallas_query = ""
    search_desglose_query = ""
    filtro_tipo_ub = "Todos"
    filtro_prog_desglose = "Todos"

    # Áreas dinámicas
    kpis_container = ft.Row(spacing=8)
    tab_content_area = ft.Container(expand=True)
    tab_chips_row = ft.Row(scroll=ft.ScrollMode.ADAPTIVE, spacing=6)

    # -------------------------------------------------------------
    # DIÁLOGOS DE EDICIÓN E IMPORTACIÓN (SOLO MASTER Y ANALISTA)
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
        page.update()

    def close_current_dialog():
        if hasattr(page, "close"):
            page.close()
        elif hasattr(page, "pop_dialog"):
            page.pop_dialog()
        page.update()

    # Modal: Registrar Jornada de Asfalto / Bacheo
    def open_add_jornada_dialog(e=None):
        if not state.is_editor():
            show_feedback_snack("Acceso denegado: Función reservada para roles Master y Analista.", is_error=True)
            return

        today_str = datetime.now().strftime("%Y-%m-%d")
        txt_fecha = ft.TextField(
            label="Fecha del Evento",
            value=today_str,
            prefix_icon=ft.Icons.CALENDAR_TODAY_ROUNDED,
            border_radius=8,
            text_size=12
        )

        ubicaciones_opciones = state.get_cero_huecos_ubicaciones_list()
        dd_ubicacion = ft.Dropdown(
            label="Ubicación / Eje Vial / Municipio",
            options=[ft.dropdown.Option(u) for u in ubicaciones_opciones if u != "Todas las Ubicaciones"],
            value="MUNICIPIO GUANARE",
            border_radius=8,
            text_size=12
        )

        dd_programa = ft.Dropdown(
            label="Programa de Asfalto",
            options=[
                ft.dropdown.Option("Plan Cero Huecos", "Plan Cero Huecos (Gobernación / Ejes Estadales)"),
                ft.dropdown.Option("Plan Nacional de Asfalto", "Plan Nacional de Asfalto (Autopista JAP)")
            ],
            value="Plan Cero Huecos",
            border_radius=8,
            text_size=12
        )

        txt_toneladas = ft.TextField(
            label="Toneladas Colocadas (Ton)",
            value="25.0",
            prefix_icon=ft.Icons.SCALE_ROUNDED,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=8,
            text_size=12
        )

        txt_kilometros = ft.TextField(
            label="Kilómetros Atendidos (km)",
            value="1.5",
            prefix_icon=ft.Icons.ADD_ROAD_ROUNDED,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=8,
            text_size=12
        )

        # Campos por tipo de falla corregida
        txt_huecos = ft.TextField(label="Huecos", value="15", keyboard_type=ft.KeyboardType.NUMBER, text_size=11, expand=True)
        txt_taponeo = ft.TextField(label="Taponeo", value="4", keyboard_type=ft.KeyboardType.NUMBER, text_size=11, expand=True)
        txt_bacheo = ft.TextField(label="Bacheo", value="6", keyboard_type=ft.KeyboardType.NUMBER, text_size=11, expand=True)
        txt_carpetas = ft.TextField(label="Carpetas", value="2", keyboard_type=ft.KeyboardType.NUMBER, text_size=11, expand=True)
        txt_grietas_l = ft.TextField(label="Grietas Long.", value="0", keyboard_type=ft.KeyboardType.NUMBER, text_size=11, expand=True)
        txt_grietas_t = ft.TextField(label="Grietas Transv.", value="0", keyboard_type=ft.KeyboardType.NUMBER, text_size=11, expand=True)

        txt_notas = ft.TextField(
            label="Observaciones Técnicas",
            hint_text="ej: Colocación de mezcla caliente en tramo crítico",
            prefix_icon=ft.Icons.NOTES_ROUNDED,
            border_radius=8,
            text_size=12
        )

        lbl_error = ft.Text("", color=COLOR_STATUS_RED, size=11, visible=False)

        def save_jornada(ev):
            try:
                ton = float(txt_toneladas.value.strip().replace(",", "."))
                km = float(txt_kilometros.value.strip().replace(",", "."))
                h = int(txt_huecos.value.strip() or 0)
                t = int(txt_taponeo.value.strip() or 0)
                b = int(txt_bacheo.value.strip() or 0)
                c = int(txt_carpetas.value.strip() or 0)
                gl = int(txt_grietas_l.value.strip() or 0)
                gt = int(txt_grietas_t.value.strip() or 0)
            except Exception:
                lbl_error.value = "Por favor ingrese valores numéricos válidos en toneladas, km y fallas."
                lbl_error.visible = True
                page.update()
                return

            state.add_cero_huecos_jornada(
                fecha=txt_fecha.value.strip(),
                ubicacion=dd_ubicacion.value,
                programa=dd_programa.value,
                toneladas=ton,
                kilometros=km,
                taponeo=t,
                bacheo=b,
                carpetas=c,
                huecos=h,
                grietas_long=gl,
                grietas_transv=gt,
                responsable=state.get_user_display_name(),
                notas=txt_notas.value.strip()
            )

            close_current_dialog()
            full_refresh()
            show_feedback_snack(f"Jornada registrada con éxito: {ton:.2f} Ton en {dd_ubicacion.value}.")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.ADD_ROAD_ROUNDED, color=COLOR_ELECTRIC_BLUE),
                ft.Text("Registrar Jornada de Asfalto / Bacheo", size=15, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
            ], spacing=8),
            content=ft.Container(
                content=ft.Column(
                    tight=True,
                    spacing=10,
                    controls=[
                        ft.Text("Ingrese el reporte técnico de la cuadrilla de pavimentación:", size=11, color=COLOR_TEXT_SECONDARY),
                        ft.Row([txt_fecha, dd_programa], spacing=8),
                        dd_ubicacion,
                        ft.Row([txt_toneladas, txt_kilometros], spacing=8),
                        ft.Text("Fallas Corregidas en la Jornada:", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Row([txt_huecos, txt_taponeo, txt_bacheo], spacing=6),
                        ft.Row([txt_carpetas, txt_grietas_l, txt_grietas_t], spacing=6),
                        txt_notas,
                        lbl_error
                    ]
                ),
                width=420,
                padding=ft.Padding.symmetric(vertical=4)
            ),
            actions=[
                ft.TextButton(content=ft.Text("Cancelar"), on_click=lambda ev: close_current_dialog()),
                ft.FilledButton(
                    content=ft.Row([ft.Icon(ft.Icons.CHECK_ROUNDED, size=16), ft.Text("Guardar Jornada")], tight=True),
                    style=ft.ButtonStyle(bgcolor=COLOR_ELECTRIC_BLUE, color="#FFFFFF"),
                    on_click=save_jornada
                )
            ],
            shape=ft.RoundedRectangleBorder(radius=12)
        )

        if hasattr(page, "open"):
            page.open(dialog)
        elif hasattr(page, "show_dialog"):
            page.show_dialog(dialog)
        page.update()

    # Panel de Importación de Excel sin congelamiento
    import_panel_obj = ExcelImportPanel(
        page=page,
        title="Importar Excel Plan Cero Huecos (.xlsx)",
        default_file="RESUMEN_ASFALTO_17_11_2026.xlsx",
        on_load_callback=state.reload_cero_huecos_excel,
        on_success_callback=lambda: full_refresh(),
        accent_color=COLOR_ELECTRIC_BLUE
    )

    def import_excel_dialog(e=None):
        import_panel_obj.toggle(e)

    # -------------------------------------------------------------
    # 3 TARJETAS KPI DINÁMICAS SUPERIORES
    # -------------------------------------------------------------
    def refresh_upper_kpis():
        kpis_container.controls.clear()
        kpis = state.get_cero_huecos_kpis(selected_ub, selected_per)

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
            make_kpi(
                "Asfalto Colocado",
                f"{fmt_es(kpis['toneladas'], 2)} Ton",
                f"{selected_per}",
                ft.Icons.SCALE_ROUNDED,
                "#EFF6FF",
                COLOR_ELECTRIC_BLUE,
                "#BFDBFE"
            ),
            make_kpi(
                "Kilómetros",
                f"{fmt_es(kpis['kilometros'], 2)} km",
                "Rehabilitados",
                ft.Icons.ADD_ROAD_ROUNDED,
                "#F0FDF4",
                COLOR_STATUS_GREEN,
                "#BBF7D0"
            ),
            make_kpi(
                "Fallas Corregidas",
                f"{fmt_es(kpis['fallas'])}",
                "Bacheo y Huecos",
                ft.Icons.HANDYMAN_ROUNDED,
                "#FEF3C7",
                COLOR_STATUS_AMBER,
                "#FDE68A"
            ),
        ]

    # -------------------------------------------------------------
    # 1. PESTAÑA: CONSOLIDADO POR MUNICIPIO Y VÍA (26)
    # -------------------------------------------------------------
    def build_tab_consolidado_ubicaciones() -> ft.Control:
        data = state.cero_huecos_data
        if not data:
            return ft.Text("No se han cargado datos de Cero Huecos.", size=12)

        ubicaciones = data.get("ubicaciones", [])
        periodo_clave = "2026" if selected_per == "2026" else ("2022-2025" if "2022-2025" in selected_per or selected_per in ["2022", "2023", "2024", "2025"] else "Total Acumulado")

        # Filtro de búsqueda y tipo
        filtered = ubicaciones
        if search_ub_query:
            q = search_ub_query.lower()
            filtered = [u for u in filtered if q in u.get("nombre", "").lower() or q in u.get("tipo", "").lower()]

        if filtro_tipo_ub == "Municipios":
            filtered = [u for u in filtered if u.get("es_municipio")]
        elif filtro_tipo_ub == "Ejes Viales":
            filtered = [u for u in filtered if not u.get("es_municipio")]

        items = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(f"26 Ubicaciones Oficiales ({len(filtered)} mostradas)", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                    ft.Text(f"Periodo: {periodo_clave}", size=10, color=COLOR_ELECTRIC_BLUE, weight=ft.FontWeight.BOLD)
                ]
            )
        ]

        for u in filtered:
            metrics = u.get(periodo_clave, {})
            tipo_label = u.get("tipo", "VÍA")
            badge_color = "#16A34A" if u.get("es_municipio") else "#2563EB"

            card = ft.Container(
                content=ft.Column(
                    spacing=6,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row([
                                    ft.Container(
                                        content=ft.Text(str(u["n"]), size=10, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                        bgcolor=COLOR_NAVY_DARK,
                                        width=22,
                                        height=22,
                                        border_radius=11,
                                        alignment=ft.Alignment(0, 0)
                                    ),
                                    ft.Text(u["nombre"], size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                                ], spacing=6),
                                ft.Container(
                                    content=ft.Text(tipo_label, size=9, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                    bgcolor=badge_color,
                                    padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                    border_radius=6
                                )
                            ]
                        ),
                        ft.Divider(height=1, color="#F1F5F9"),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row([
                                    ft.Icon(ft.Icons.SCALE_ROUNDED, size=12, color=COLOR_ELECTRIC_BLUE),
                                    ft.Text(f"{fmt_es(metrics.get('toneladas', 0), 2)} Ton", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                                ], spacing=3),
                                ft.Row([
                                    ft.Icon(ft.Icons.ADD_ROAD_ROUNDED, size=12, color=COLOR_STATUS_GREEN),
                                    ft.Text(f"{fmt_es(metrics.get('kilometros', 0), 2)} km", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                                ], spacing=3),
                                ft.Row([
                                    ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, size=12, color=COLOR_STATUS_AMBER),
                                    ft.Text(f"{fmt_es(metrics.get('fallas', 0))} fallas", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                                ], spacing=3)
                            ]
                        )
                    ]
                ),
                padding=10,
                bgcolor=COLOR_SURFACE_WHITE,
                border_radius=10,
                border=ft.Border.all(1, COLOR_BORDER),
                shadow=ft.BoxShadow(spread_radius=0, blur_radius=3, color="#0A000000", offset=ft.Offset(0, 1))
            )
            items.append(card)

        if not filtered:
            items.append(
                ft.Container(
                    content=ft.Text("No se encontraron ubicaciones con el criterio especificado.", size=11, color=COLOR_TEXT_MUTED),
                    padding=20,
                    alignment=ft.Alignment(0, 0)
                )
            )

        return ft.Column(
            spacing=8,
            controls=[
                ft.Row([
                    ft.TextField(
                        hint_text="Buscar ubicación, municipio o troncal...",
                        prefix_icon=ft.Icons.SEARCH_ROUNDED,
                        border_radius=8,
                        text_size=11,
                        content_padding=ft.Padding.symmetric(horizontal=10, vertical=8),
                        expand=True,
                        on_change=on_search_ub
                    ),
                    ft.Dropdown(
                        options=[
                            ft.dropdown.Option("Todos", "Todos"),
                            ft.dropdown.Option("Municipios", "Municipios (14)"),
                            ft.dropdown.Option("Ejes Viales", "Ejes Viales (12)")
                        ],
                        value=filtro_tipo_ub,
                        border_radius=8,
                        text_size=11,
                        content_padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                        width=140,
                        on_select=on_change_tipo_ub
                    )
                ], spacing=6),
                ft.ListView(controls=items, spacing=6, expand=True)
            ],
            expand=True
        )

    def on_search_ub(e):
        nonlocal search_ub_query
        search_ub_query = e.control.value
        render_active_tab()
        page.update()

    def on_change_tipo_ub(e):
        nonlocal filtro_tipo_ub
        filtro_tipo_ub = e.control.value
        render_active_tab()
        page.update()

    # -------------------------------------------------------------
    # 2. PESTAÑA: TIPOLOGÍA DE FALLAS CORREGIDAS (341.057)
    # -------------------------------------------------------------
    def build_tab_tipologia_fallas() -> ft.Control:
        data = state.cero_huecos_data
        if not data:
            return ft.Text("No hay datos disponibles.", size=12)

        totales = data.get("totales_estatales", {})
        tip = totales.get("tipologia", {})
        tot_fallas = totales.get("fallas", 342563)

        # 6 Tarjetas superiores por tipo de falla
        tipos_data = [
            ("Huecos", tip.get("huecos", 266586), "#DC2626", ft.Icons.ERROR_ROUNDED),
            ("Taponeo", tip.get("taponeo", 31963), "#2563EB", ft.Icons.CHANGE_CIRCLE_ROUNDED),
            ("Bacheo", tip.get("bacheo", 30594), "#059669", ft.Icons.CONSTRUCTION_ROUNDED),
            ("Carpetas", tip.get("carpetas", 10078), "#7C3AED", ft.Icons.LAYERS_ROUNDED),
            ("Grietas Long.", tip.get("grietas_long", 2302), "#D97706", ft.Icons.TIMELAPSE_ROUNDED),
            ("Grietas Transv.", tip.get("grietas_transv", 1040), "#475569", ft.Icons.LINEAR_SCALE_ROUNDED),
        ]

        tarjetas_tipos = []
        for name, val, col, icon_d in tipos_data:
            pct = (val / tot_fallas) * 100.0 if tot_fallas > 0 else 0
            tarjetas_tipos.append(
                ft.Container(
                    content=ft.Column(
                        spacing=2,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(icon_d, size=15, color=col),
                            ft.Text(fmt_es(val), size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                            ft.Text(name, size=10, weight=ft.FontWeight.W_600, color=COLOR_TEXT_PRIMARY),
                            ft.Text(f"{pct:.1f}%", size=9, color=col, weight=ft.FontWeight.BOLD)
                        ]
                    ),
                    padding=6,
                    bgcolor=COLOR_SURFACE_WHITE,
                    border_radius=8,
                    border=ft.Border.all(1, COLOR_BORDER),
                    expand=True
                )
            )

        # Desglose 2026 detallado
        fallas_26 = data.get("fallas_2026", [])
        if search_fallas_query:
            q = search_fallas_query.lower()
            fallas_26 = [f for f in fallas_26 if q in f.get("nombre", "").lower()]

        items_fallas = [
            ft.Row(tarjetas_tipos[:3], spacing=6),
            ft.Row(tarjetas_tipos[3:], spacing=6),
            ft.Divider(height=1, color=COLOR_BORDER),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(f"Detalle Operativo 2026 por Municipio y Tramo ({len(fallas_26)} sectores)", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                    ft.Text("Total: 99.865 fallas", size=10, color=COLOR_STATUS_RED, weight=ft.FontWeight.BOLD)
                ]
            )
        ]

        for f in fallas_26:
            row_card = ft.Container(
                content=ft.Column(
                    spacing=4,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(f"{f['n']}. {f['nombre']}", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                ft.Container(
                                    content=ft.Text(f"{fmt_es(f['total_fallas'])} fallas", size=10, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                    bgcolor=COLOR_STATUS_RED,
                                    padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                    border_radius=6
                                )
                            ]
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(f"Huecos: {fmt_es(f['huecos'])}", size=9, color=COLOR_TEXT_SECONDARY),
                                ft.Text(f"Taponeo: {fmt_es(f['taponeo'])}", size=9, color=COLOR_TEXT_SECONDARY),
                                ft.Text(f"Bacheo: {fmt_es(f['bacheo'])}", size=9, color=COLOR_TEXT_SECONDARY),
                                ft.Text(f"Carpetas: {fmt_es(f['carpetas'])}", size=9, color=COLOR_TEXT_SECONDARY),
                                ft.Text(f"Grietas: {fmt_es(f['grietas_long'] + f['grietas_transv'])}", size=9, color=COLOR_TEXT_SECONDARY),
                            ]
                        )
                    ]
                ),
                padding=8,
                bgcolor=COLOR_SURFACE_WHITE,
                border_radius=8,
                border=ft.Border.all(1, COLOR_BORDER)
            )
            items_fallas.append(row_card)

        return ft.Column(
            spacing=8,
            controls=[
                ft.TextField(
                    hint_text="Buscar en fallas 2026 por municipio o vía...",
                    prefix_icon=ft.Icons.SEARCH_ROUNDED,
                    border_radius=8,
                    text_size=11,
                    content_padding=ft.Padding.symmetric(horizontal=10, vertical=8),
                    on_change=on_search_fallas
                ),
                ft.ListView(controls=items_fallas, spacing=6, expand=True)
            ],
            expand=True
        )

    def on_search_fallas(e):
        nonlocal search_fallas_query
        search_fallas_query = e.control.value
        render_active_tab()
        page.update()

    # -------------------------------------------------------------
    # 3. PESTAÑA: EVOLUCIÓN ANUAL (2022–2026)
    # -------------------------------------------------------------
    def build_tab_evolucion_anual() -> ft.Control:
        data = state.cero_huecos_data
        if not data:
            return ft.Text("No hay datos disponibles.", size=12)

        evolucion = data.get("resumen", {}).get("evolucion_anual", [])
        max_ton = max((y["toneladas"] for y in evolucion), default=73396.39)
        max_fal = max((y["total_fallas"] for y in evolucion), default=98359)

        cards = []
        for y in evolucion:
            pct_ton = (y["toneladas"] / max_ton) if max_ton > 0 else 0
            pct_fal = (y["total_fallas"] / max_fal) if max_fal > 0 else 0

            card = ft.Container(
                content=ft.Column(
                    spacing=6,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row([
                                    ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED, size=15, color=COLOR_ELECTRIC_BLUE),
                                    ft.Text(f"AÑO {y['year']}", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                                ], spacing=4),
                                ft.Row([
                                    ft.Text(f"{fmt_es(y['toneladas'], 2)} Ton", size=12, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_BLUE),
                                    ft.Text("•", size=10, color=COLOR_TEXT_MUTED),
                                    ft.Text(f"{fmt_es(y['total_fallas'])} Fallas", size=12, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_AMBER)
                                ], spacing=6)
                            ]
                        ),
                        # Barra de progreso de Asfalto
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Row([
                                    ft.Text("Toneladas de Asfalto:", size=10, color=COLOR_TEXT_MUTED),
                                    ft.Text(f"{fmt_es(y['toneladas'], 2)} Ton", size=10, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_BLUE)
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.ProgressBar(value=pct_ton, color=COLOR_ELECTRIC_BLUE, bgcolor="#E2E8F0")
                            ]
                        ),
                        # Barra de progreso de Fallas Corregidas
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Row([
                                    ft.Text("Fallas Corregidas:", size=10, color=COLOR_TEXT_MUTED),
                                    ft.Text(f"{fmt_es(y['total_fallas'])}", size=10, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_AMBER)
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.ProgressBar(value=pct_fal, color=COLOR_STATUS_AMBER, bgcolor="#E2E8F0")
                            ]
                        ),
                        # Desglose en línea de fallas
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(f"Huecos: {fmt_es(y['huecos'])}", size=9, color=COLOR_TEXT_SECONDARY),
                                ft.Text(f"Taponeo: {fmt_es(y['taponeo'])}", size=9, color=COLOR_TEXT_SECONDARY),
                                ft.Text(f"Bacheo: {fmt_es(y['bacheo'])}", size=9, color=COLOR_TEXT_SECONDARY),
                                ft.Text(f"Carpetas: {fmt_es(y['carpetas'])}", size=9, color=COLOR_TEXT_SECONDARY),
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

        return ft.ListView(
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Evolución Anual del Plan (2022 - 2026)", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Text("Comparativa Histórica", size=10, color=COLOR_TEXT_MUTED)
                    ]
                ),
                *cards
            ],
            spacing=8,
            expand=True
        )

    # -------------------------------------------------------------
    # 4. PESTAÑA: DESGLOSE OPERATIVO 2026 (PROGRAMAS)
    # -------------------------------------------------------------
    def build_tab_desglose_operativo() -> ft.Control:
        data = state.cero_huecos_data
        if not data:
            return ft.Text("No hay datos disponibles.", size=12)

        desglose = data.get("desglose_asfalto", {})
        programas = desglose.get("resumen_programas", {})
        ch_prog = programas.get("cero_huecos", {})
        pn_prog = programas.get("plan_nacional", {})

        # Tarjetas comparativas de los dos programas en 2026
        card_cero_huecos = ft.Container(
            content=ft.Column(
                spacing=3,
                controls=[
                    ft.Row([
                        ft.Icon(ft.Icons.LOCATION_CITY_ROUNDED, size=15, color=COLOR_ELECTRIC_BLUE),
                        ft.Text("Plan Cero Huecos", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                    ], spacing=4),
                    ft.Text(f"{fmt_es(ch_prog.get('toneladas', 58140.53), 2)} Ton", size=16, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_BLUE),
                    ft.Text(f"{fmt_es(ch_prog.get('kilometros', 532.83), 2)} km • {ch_prog.get('porcentaje', 75.0)}% del 2026", size=10, color=COLOR_TEXT_SECONDARY),
                    ft.Text("Gobernación y Alcaldías", size=9, color=COLOR_TEXT_MUTED)
                ]
            ),
            padding=10,
            bgcolor="#EFF6FF",
            border_radius=10,
            border=ft.Border.all(1, "#BFDBFE"),
            expand=True
        )

        card_plan_nacional = ft.Container(
            content=ft.Column(
                spacing=3,
                controls=[
                    ft.Row([
                        ft.Icon(ft.Icons.ADD_ROAD_ROUNDED, size=15, color="#16A34A"),
                        ft.Text("Plan Nacional de Asfalto", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                    ], spacing=4),
                    ft.Text(f"{fmt_es(pn_prog.get('toneladas', 19432.00), 2)} Ton", size=16, weight=ft.FontWeight.BOLD, color="#16A34A"),
                    ft.Text(f"{fmt_es(pn_prog.get('kilometros', 73.80), 2)} km • {pn_prog.get('porcentaje', 25.0)}% del 2026", size=10, color=COLOR_TEXT_SECONDARY),
                    ft.Text("Autopista José Antonio Páez", size=9, color=COLOR_TEXT_MUTED)
                ]
            ),
            padding=10,
            bgcolor="#F0FDF4",
            border_radius=10,
            border=ft.Border.all(1, "#BBF7D0"),
            expand=True
        )

        # Listado de registros detallados
        registros = desglose.get("registros", [])
        if search_desglose_query:
            q = search_desglose_query.lower()
            registros = [r for r in registros if q in r.get("sector", "").lower() or q in r.get("subsector", "").lower()]

        if filtro_prog_desglose == "Cero Huecos":
            registros = [r for r in registros if not r.get("es_plan_nacional")]
        elif filtro_prog_desglose == "Plan Nacional":
            registros = [r for r in registros if r.get("es_plan_nacional")]

        items = [
            ft.Row([card_cero_huecos, card_plan_nacional], spacing=8),
            ft.Divider(height=1, color=COLOR_BORDER),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(f"Sectores Atendidos en 2026 ({len(registros)} registros)", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                    ft.Text("Corte Oficial: 17/11/2026", size=10, color=COLOR_TEXT_MUTED)
                ]
            )
        ]

        for r in registros:
            badge_col = "#16A34A" if r.get("es_plan_nacional") else COLOR_ELECTRIC_BLUE
            card = ft.Container(
                content=ft.Column(
                    spacing=4,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(f"{r['sector']}", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                ft.Container(
                                    content=ft.Text(r["programa"], size=9, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                    bgcolor=badge_col,
                                    padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                    border_radius=6
                                )
                            ]
                        ),
                        ft.Text(f"Subsector / Tramo: {r['subsector']}", size=10, color=COLOR_TEXT_SECONDARY),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row([
                                    ft.Icon(ft.Icons.SCALE_ROUNDED, size=12, color=COLOR_ELECTRIC_BLUE),
                                    ft.Text(f"{fmt_es(r['toneladas'], 2)} Ton", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                                ], spacing=3),
                                ft.Row([
                                    ft.Icon(ft.Icons.ADD_ROAD_ROUNDED, size=12, color=COLOR_STATUS_GREEN),
                                    ft.Text(f"{fmt_es(r['kilometros'], 2)} km", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                                ], spacing=3)
                            ]
                        )
                    ]
                ),
                padding=8,
                bgcolor=COLOR_SURFACE_WHITE,
                border_radius=8,
                border=ft.Border.all(1, COLOR_BORDER)
            )
            items.append(card)

        return ft.Column(
            spacing=8,
            controls=[
                ft.Row([
                    ft.TextField(
                        hint_text="Buscar sector, municipio o tramo 2026...",
                        prefix_icon=ft.Icons.SEARCH_ROUNDED,
                        border_radius=8,
                        text_size=11,
                        content_padding=ft.Padding.symmetric(horizontal=10, vertical=8),
                        expand=True,
                        on_change=on_search_desglose
                    ),
                    ft.Dropdown(
                        options=[
                            ft.dropdown.Option("Todos", "Todos"),
                            ft.dropdown.Option("Cero Huecos", "Cero Huecos"),
                            ft.dropdown.Option("Plan Nacional", "Plan Nacional")
                        ],
                        value=filtro_prog_desglose,
                        border_radius=8,
                        text_size=11,
                        content_padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                        width=140,
                        on_select=on_change_prog_desglose
                    )
                ], spacing=6),
                ft.ListView(controls=items, spacing=6, expand=True)
            ],
            expand=True
        )

    def on_search_desglose(e):
        nonlocal search_desglose_query
        search_desglose_query = e.control.value
        render_active_tab()
        page.update()

    def on_change_prog_desglose(e):
        nonlocal filtro_prog_desglose
        filtro_prog_desglose = e.control.value
        render_active_tab()
        page.update()

    # -------------------------------------------------------------
    # GESTIÓN Y RENDERIZADO DE PESTAÑAS (PATRÓN PÍLDORAS)
    # -------------------------------------------------------------
    def render_active_tab():
        if active_tab == 0:
            tab_content_area.content = build_tab_consolidado_ubicaciones()
        elif active_tab == 1:
            tab_content_area.content = build_tab_tipologia_fallas()
        elif active_tab == 2:
            tab_content_area.content = build_tab_evolucion_anual()
        else:
            tab_content_area.content = build_tab_desglose_operativo()

    def set_tab(idx: int):
        nonlocal active_tab
        active_tab = idx
        render_tab_chips()
        render_active_tab()
        page.update()

    def render_tab_chips():
        tab_chips_row.controls.clear()
        labels = [
            ("Consolidado Ubicaciones (26)", ft.Icons.LOCATION_CITY_ROUNDED),
            ("Tipología de Fallas (342k)", ft.Icons.HANDYMAN_ROUNDED),
            ("Evolución Anual (22-26)", ft.Icons.SHOW_CHART_ROUNDED),
            ("Desglose 2026 (Programas)", ft.Icons.PIE_CHART_ROUNDED),
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
    def on_ub_change(e):
        nonlocal selected_ub
        selected_ub = e.control.value
        state.set_cero_huecos_filters(ubicacion=selected_ub)
        full_refresh()

    def on_per_change(e):
        nonlocal selected_per
        selected_per = e.control.value
        state.set_cero_huecos_filters(periodo=selected_per)
        full_refresh()

    def full_refresh():
        refresh_upper_kpis()
        render_tab_chips()
        render_active_tab()
        page.update()

    # Dropdowns Superiores
    ubicaciones_list = state.get_cero_huecos_ubicaciones_list()
    dd_ubicacion_top = ft.Dropdown(
        label="Ubicación / Municipio",
        options=[ft.dropdown.Option(u) for u in ubicaciones_list],
        value=selected_ub,
        content_padding=ft.Padding.symmetric(horizontal=10, vertical=6),
        border_radius=8,
        text_size=11,
        expand=True,
        on_select=on_ub_change
    )

    periodos_list = [
        "Acumulado Total",
        "2026",
        "Acumulado 2022-2025",
        "2025",
        "2024",
        "2023",
        "2022"
    ]
    dd_periodo_top = ft.Dropdown(
        label="Periodo / Año",
        options=[ft.dropdown.Option(p) for p in periodos_list],
        value=selected_per,
        content_padding=ft.Padding.symmetric(horizontal=10, vertical=6),
        border_radius=8,
        text_size=11,
        width=160,
        on_select=on_per_change
    )

    # Botón de Impresión de Reporte Ejecutivo en Formato Carta Horizontal (Landscape)
    def on_print_cero_huecos_click(e=None):
        mun_target = selected_ub if selected_ub in state.get_cero_huecos_ubicaciones_list() and selected_ub not in ("Todas las Ubicaciones", "Ejes Viales (12)", "Municipios (14)") else "Portuguesa"
        k_kpis = state.get_cero_huecos_kpis(selected_ub, selected_per)
        report_data = {
            "municipio": mun_target,
            "fecha": "17/11/2026",
            "kpis": {
                "asfalto": f"{fmt_es(k_kpis['toneladas'], 2)} Ton",
                "km_vias": f"{fmt_es(k_kpis['kilometros'], 2)} km",
                "fallas": fmt_es(k_kpis['fallas']),
                "pozos": "N/A",
                "casas_culm": "N/A",
                "casas_proc": "N/A",
            },
            "obras": {
                "total": int(round(k_kpis["fallas"])),
                "culm": int(round(k_kpis["fallas"])),
                "pct_culm": 100.0,
                "proc": 0,
                "pct_proc": 0.0,
                "para": 0,
                "pct_para": 0.0,
            },
            "planes": [
                {
                    "name": "Plan Cero Huecos (Gobernación y Alcaldías)",
                    "metric": f"{fmt_es(k_kpis['toneladas'], 2)} Ton Asfalto",
                    "detail": f"{fmt_es(k_kpis['kilometros'], 2)} km rehabilitados • {fmt_es(k_kpis['fallas'])} fallas atendidas ({selected_ub} - {selected_per})",
                    "status": "Operativo",
                    "status_color": "#16A34A"
                },
                {
                    "name": "Plan Nacional de Asfalto (Autopista JAP)",
                    "metric": "19.432,00 Ton Asfalto",
                    "detail": "73,80 km atendidos en tramos estratégicos de la Autopista José Antonio Páez",
                    "status": "En Ejecución",
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
        tooltip="Imprimir reporte de asfalto y vialidad en Carta Horizontal",
        on_click=on_print_cero_huecos_click
    )

    # Botones exclusivos de gestión (Solo Editor / Master)
    action_buttons = []
    if state.is_editor():
        action_buttons.extend([
            ft.FilledButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.ADD_ROAD_ROUNDED, size=15),
                    ft.Text("Registrar Asfalto", size=11, weight=ft.FontWeight.BOLD)
                ], tight=True),
                style=ft.ButtonStyle(
                    bgcolor=COLOR_ELECTRIC_BLUE,
                    color="#FFFFFF",
                    padding=ft.Padding.symmetric(horizontal=10, vertical=8),
                    shape=ft.RoundedRectangleBorder(radius=8)
                ),
                on_click=open_add_jornada_dialog
            ),
            ft.OutlinedButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.UPLOAD_FILE_ROUNDED, size=15),
                    ft.Text("Importar Excel", size=11, weight=ft.FontWeight.BOLD)
                ], tight=True),
                style=ft.ButtonStyle(
                    padding=ft.Padding.symmetric(horizontal=10, vertical=8),
                    shape=ft.RoundedRectangleBorder(radius=8)
                ),
                on_click=import_excel_dialog
            )
        ])

    # Header Institucional PCEO con logo oficial
    logo_file = "assets/logo_cero_huecos.png"
    has_logo = os.path.exists(logo_file)
    leading_logo_ctrl = ft.Image(src="logo_cero_huecos.png", width=36, height=36, fit="contain") if has_logo else None

    header = create_institutional_header(
        title="Plan Cero Huecos",
        subtitle="Puesto de Comando Estratégico Operacional",
        current_role=state.current_role,
        show_back_button=True,
        on_back_click=lambda e: on_back_to_summary(),
        on_switch_role_click=on_switch_role,
        on_logout_click=on_logout,
        leading_logo=leading_logo_ctrl
    )

    # Inicializar componentes al montar
    refresh_upper_kpis()
    render_tab_chips()
    render_active_tab()

    return ft.Container(
        content=ft.Column(
            spacing=8,
            controls=[
                header,
                import_panel_obj.panel_container,
                # Barra de filtros superiores
                ft.Container(
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Row([dd_ubicacion_top, dd_periodo_top, btn_imprimir], spacing=8),
                            kpis_container,
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Container(
                                        content=tab_chips_row,
                                        padding=ft.Padding.only(bottom=15)
                                    ),
                                    ft.Row(action_buttons, spacing=6) if action_buttons else ft.Container()
                                ]
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
                )
            ],
            expand=True
        ),
        expand=True,
        bgcolor=COLOR_BG_LIGHT
    )
