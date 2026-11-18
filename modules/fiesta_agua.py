"""
Módulo Detallado: Fiesta del Agua - Plan Maestro Hídrico de Portuguesa
Basado en datos oficiales de HIDROVEN / Hidrosportuguesa (OPERATIVIDAD PORTUGUESA-8.xlsx)
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
    COLOR_STATUS_RED,
    COLOR_STATUS_RED_BORDER
)
from components.header import create_institutional_header
from components.semaphore import create_semaphore_badge, create_status_dot
from components.kpi_card import create_dynamic_kpi_metric
from data.water_data import MUNICIPALITIES_LIST
from data.state import AppState, normalize_name
from modules.excel_import_panel import ExcelImportPanel

def fmt_es(val: int | float, dec: int = 0) -> str:
    if dec > 0:
        return f"{val:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{int(val):,}".replace(",", ".")

def build_fiesta_agua_view(
    page: ft.Page,
    on_back_to_summary,
    on_switch_role,
    on_logout
) -> ft.Control:
    """Construye la vista interactiva oficial de Fiesta del Agua con 6 pestañas."""
    state = AppState()

    selected_mun = state.selected_municipality
    selected_parr = state.fiesta_agua_parroquia
    active_tab = 0  # 0 a 6
    perf_year = "Todos los Años"
    perf_fuente = "Todas las Fuentes"
    perf_estatus = "Todos los Estatus"
    inops_sort_order = "recent_first"  # "recent_first" o "oldest_first"
    itvs_sort_order = "recent_first"   # "recent_first" o "oldest_first"

    kpis_container = ft.Column(spacing=6)
    tab_content_area = ft.Container(expand=True)
    tab_chips_row = ft.Row(scroll=ft.ScrollMode.ADAPTIVE, spacing=6)

    import_panel_obj = ExcelImportPanel(
        page=page,
        title="Importar Reporte HIDROVEN (.xlsx)",
        default_file="OPERATIVIDAD  PORTUGUESA 17-11-26.xlsx" if os.path.exists("OPERATIVIDAD  PORTUGUESA 17-11-26.xlsx") else "OPERATIVIDAD  PORTUGUESA-8.xlsx",
        on_load_callback=state.reload_hidroven_excel,
        on_success_callback=lambda: full_refresh(),
        accent_color=COLOR_ELECTRIC_BLUE
    )

    def refresh_upper_kpis():
        kpis_container.controls.clear()
        h_data = state.hidroven_data

        if not h_data:
            tot = {"total_pozos": 535, "operativos_total": 464, "inoperativos_total": 71, "pct_operatividad": 86.73, "pct_inoperatividad": 13.27, "caudal_total_lps": 8174.41}
        else:
            tot = h_data["totales_estado"]

        # Si hay un municipio seleccionado, calcular sus números exactos
        if selected_mun != "Todos los Municipios" and h_data:
            m_info = next((m for m in h_data["municipios"] if normalize_name(m["municipio"]) == normalize_name(selected_mun)), None)
            if m_info:
                tot_p = m_info["total_pozos"]
                op_p = m_info["operativos_total"]
                inop_p = m_info["inoperativos_total"]
                pct_op = m_info["pct_operatividad"]
                pct_inop = round(100.0 - pct_op, 2)
                caudal = m_info["caudal_lps"]
            else:
                tot_p, op_p, inop_p, pct_op, pct_inop, caudal = 0, 0, 0, 0, 0, 0
        else:
            tot_p = tot["total_pozos"]
            op_p = tot["operativos_total"]
            inop_p = tot["inoperativos_total"]
            pct_op = tot.get("pct_operatividad", 86.73)
            pct_inop = tot.get("pct_inoperatividad", 13.27)
            caudal = tot.get("caudal_total_lps", 8174.41)

        # Fila 1: Pozos
        kpis_container.controls.append(
            ft.Row(
                spacing=8,
                controls=[
                    create_dynamic_kpi_metric(
                        title=f"Total Pozos ({'Estadal' if selected_mun == 'Todos los Municipios' else selected_mun})",
                        main_value=str(tot_p),
                        subtitle="Fuente: HIDROVEN",
                        icon=ft.Icons.WATER_DROP_ROUNDED,
                        accent_color=COLOR_ELECTRIC_BLUE,
                        bg_tint="#F0F7FF"
                    ),
                    create_dynamic_kpi_metric(
                        title="Pozos Operativos",
                        main_value=str(op_p),
                        subtitle=f"{pct_op:.1f}% Operatividad",
                        icon=ft.Icons.CHECK_CIRCLE_ROUNDED,
                        accent_color=COLOR_STATUS_GREEN,
                        bg_tint="#F0FDF4"
                    ),
                    create_dynamic_kpi_metric(
                        title="Pozos Inoperativos",
                        main_value=str(inop_p),
                        subtitle=f"{pct_inop:.1f}% Afectación",
                        icon=ft.Icons.ERROR_ROUNDED,
                        accent_color=COLOR_STATUS_RED,
                        bg_tint="#FEF2F2"
                    ),
                ]
            )
        )

        # Fila 2: Caudal y Estaciones
        reb_total = 30
        reb_op = 27
        if h_data and "estaciones_rebombeo" in h_data:
            c_sur = h_data["estaciones_rebombeo"].get("cono_sur", [])
            c_nor = h_data["estaciones_rebombeo"].get("cono_norte", [])
            c_cap = h_data["estaciones_rebombeo"].get("captacion_conduccion", [])
            all_st = c_sur + c_nor + c_cap
            reb_total = len(all_st)
            reb_op = sum(1 for s in all_st if s["operatividad"] == "SI")

        kpis_container.controls.append(
            ft.Row(
                spacing=8,
                controls=[
                    create_dynamic_kpi_metric(
                        title="Caudal de Producción",
                        main_value=f"{fmt_es(caudal, 2)} L/s",
                        subtitle="Aforo Oficial Activo",
                        icon=ft.Icons.SPEED_ROUNDED,
                        accent_color="#0284C7",
                        bg_tint="#F0F9FF"
                    ),
                    create_dynamic_kpi_metric(
                        title="Estaciones de Rebombeo",
                        main_value=f"{reb_op} Op / {reb_total - reb_op} Inop",
                        subtitle=f"{reb_total} Sistemas Cono Sur/Norte",
                        icon=ft.Icons.FACTORY_ROUNDED,
                        accent_color="#7C3AED",
                        bg_tint="#F5F3FF"
                    ),
                ]
            )
        )

    # Modal para Cambio de Estatus (Operativo / Inoperativo) - Analistas de Sala (Editor)
    def open_change_status_dialog(pozo: dict):
        if not state.is_editor():
            return

        from datetime import datetime
        today_str = datetime.now().strftime("%Y-%m-%d")

        is_currently_op = pozo.get("operatividad", "SI") == "SI"
        suggested_next = "NO" if is_currently_op else "SI"

        status_dropdown = ft.Dropdown(
            label="Nuevo Estatus",
            value=suggested_next,
            options=[
                ft.dropdown.Option("SI", "Operativo (SI) - Puesta en Servicio"),
                ft.dropdown.Option("NO", "Inoperativo (NO) - Salida de Servicio"),
            ],
            border_color=COLOR_ELECTRIC_BLUE,
            focused_border_color=COLOR_NAVY_DARK,
            text_size=13
        )

        fecha_input = ft.TextField(
            label="Fecha del Evento (AAAA-MM-DD)",
            value=today_str,
            hint_text="YYYY-MM-DD",
            border_color=COLOR_BORDER,
            focused_border_color=COLOR_ELECTRIC_BLUE,
            text_size=13
        )

        obs_input = ft.TextField(
            label="Observación / Requerimiento Técnico",
            hint_text="Motivo de la falla, diagnóstico o equipo electromecánico instalado...",
            multiline=True,
            min_lines=2,
            max_lines=4,
            border_color=COLOR_BORDER,
            focused_border_color=COLOR_ELECTRIC_BLUE,
            text_size=12
        )

        ente_dropdown = ft.Dropdown(
            label="Ente / Fuente de Financiamiento (Opcional)",
            value="Gobernación",
            options=[
                ft.dropdown.Option("Gobernación", "Gobernación de Portuguesa"),
                ft.dropdown.Option("Alcaldía", "Alcaldía Bolivariana"),
                ft.dropdown.Option("Hidrosportuguesa", "Hidrosportuguesa"),
                ft.dropdown.Option("MinAguas", "Ministerio de Aguas (MinAguas)"),
            ],
            border_color=COLOR_BORDER,
            focused_border_color=COLOR_ELECTRIC_BLUE,
            text_size=12
        )

        def save_status(e):
            nuevo_estatus = status_dropdown.value
            fecha = (fecha_input.value or today_str).strip()
            obs = (obs_input.value or "").strip()
            ente = ente_dropdown.value or "Gobernación"

            if not obs:
                obs = "Puesta en servicio operativo con equipo instalado" if nuevo_estatus == "SI" else "Salida de servicio para diagnóstico electromecánico"

            well_n = pozo.get("n", 0)
            success = state.update_pozo_status(
                well_n=well_n,
                nuevo_estatus=nuevo_estatus,
                fecha_evento=fecha,
                observacion=obs,
                ente=ente
            )

            if hasattr(page, "close"):
                page.close(dialog_status)
            elif hasattr(page, "pop_dialog"):
                page.pop_dialog()
            page.update()

            if success:
                page.show_dialog(
                    ft.SnackBar(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, color="#FFFFFF"),
                            ft.Text(f"Pozo #{well_n} actualizado exitosamente a {'OPERATIVO' if nuevo_estatus == 'SI' else 'INOPERATIVO'}.", color="#FFFFFF")
                        ]),
                        bgcolor=COLOR_STATUS_GREEN if nuevo_estatus == "SI" else COLOR_STATUS_RED
                    )
                )
                full_refresh()
            else:
                page.show_dialog(
                    ft.SnackBar(
                        content=ft.Text("Error al actualizar estatus del pozo.", color="#FFFFFF"),
                        bgcolor=COLOR_STATUS_RED
                    )
                )
            page.update()

        def cancel_status(e):
            if hasattr(page, "close"):
                page.close(dialog_status)
            elif hasattr(page, "pop_dialog"):
                page.pop_dialog()
            page.update()

        dialog_status = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.SYNC_ALT_ROUNDED, color=COLOR_ELECTRIC_BLUE),
                ft.Text(f"Cambiar Estatus: Pozo #{pozo.get('n', '')}", size=15, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
            ]),
            content=ft.Container(
                content=ft.Column(
                    tight=True,
                    spacing=10,
                    controls=[
                        ft.Text(f"{pozo.get('cod_minaguas', '')} - {pozo.get('ubicacion', '')}", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Text(f"Municipio: {pozo.get('municipio', '')} • Parroquia: {pozo.get('parroquia', '')}", size=11, color=COLOR_TEXT_SECONDARY),
                        ft.Divider(height=1, color=COLOR_BORDER),
                        status_dropdown,
                        fecha_input,
                        obs_input,
                        ente_dropdown
                    ]
                ),
                width=420,
                padding=ft.Padding.all(4)
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cancel_status),
                ft.FilledButton(
                    "Guardar Cambio",
                    on_click=save_status,
                    style=ft.ButtonStyle(bgcolor=COLOR_ELECTRIC_BLUE, color="#FFFFFF")
                )
            ]
        )
        if hasattr(page, "open"):
            page.open(dialog_status)
        else:
            page.show_dialog(dialog_status)
        page.update()

    # Modal de Ficha Técnica Emergente de Pozo
    def open_well_detail_dialog(pozo: dict):
        is_op = pozo["operatividad"] == "SI"
        inop = pozo.get("inoperativo_info")
        itvs = pozo.get("intervenciones", [])

        # Lista de intervenciones
        itv_controls = []
        if itvs:
            for it in itvs[:5]:  # Mostrar hasta las 5 más recientes
                itv_controls.append(
                    ft.Container(
                        content=ft.Column(
                            spacing=2,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(f"📅 {it['fecha']} • {it['tipo']}", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                        ft.Text(f"Fuente: {it['fuente']}", size=10, weight=ft.FontWeight.W_600, color=COLOR_ELECTRIC_BLUE)
                                    ]
                                ),
                                ft.Text(it["observacion"], size=10, color=COLOR_TEXT_SECONDARY)
                            ]
                        ),
                        padding=6,
                        bgcolor="#F8FAFC",
                        border_radius=6,
                        border=ft.Border.all(1, COLOR_BORDER)
                    )
                )
        else:
            itv_controls.append(
                ft.Text("Sin intervenciones registradas en el histórico reciente.", size=11, color="#64748B")
            )

        inop_section = None
        if not is_op:
            req_text = inop["requerimiento"] if inop else "Amerita evaluación electromecánica y diagnóstico de cuadrilla."
            cap_text = inop["capacidad"] if inop else f"{pozo['motor_hp']} HP"
            salida_text = inop["fecha_salida"] if inop else "Registrado en bitácora de contingencia"

            inop_section = ft.Container(
                content=ft.Column(
                    spacing=4,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Row([
                            ft.Icon(ft.Icons.WARNING_ROUNDED, color=COLOR_STATUS_RED, size=16),
                            ft.Text("REQUERIMIENTO TÉCNICO Y DIAGNÓSTICO", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_RED)
                        ]),
                        ft.Text(req_text, size=11, weight=ft.FontWeight.W_600, color="#991B1B"),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(f"⚡ Capacidad: {cap_text}", size=10, color="#991B1B"),
                                ft.Text(f"🗓️ Fecha de Salida: {salida_text}", size=10, color="#991B1B")
                            ]
                        )
                    ]
                ),
                padding=10,
                bgcolor="#FEF2F2",
                border_radius=8,
                border=ft.Border.all(1, "#FCA5A5")
            )

        content = ft.Container(
            content=ft.Column(
                tight=True,
                spacing=10,
                scroll=ft.ScrollMode.ADAPTIVE,
                controls=[
                    # Estatus
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(f"{pozo['cod_minaguas']} (Ant: {pozo['num_anterior']})", size=14, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                            create_semaphore_badge("Operativo" if is_op else "Inoperativo", compact=True)
                        ]
                    ),
                    ft.Text(f"📍 {pozo['ubicacion']}", size=12, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_BLUE),
                    ft.Text(f"Municipio: {pozo['municipio']} • Parroquia: {pozo['parroquia']} ({pozo['area']})", size=11, color=COLOR_TEXT_SECONDARY),
                    ft.Divider(height=1, color=COLOR_BORDER),

                    # Ficha técnica
                    ft.Container(
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_AROUND,
                            controls=[
                                ft.Column([
                                    ft.Text(f"{pozo['motor_hp']} HP", size=14, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                    ft.Text("Motor", size=10, color=COLOR_TEXT_MUTED)
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                ft.Column([
                                    ft.Text(f"{pozo['caudal_lps']} L/s", size=14, weight=ft.FontWeight.BOLD, color="#0284C7"),
                                    ft.Text("Caudal", size=10, color=COLOR_TEXT_MUTED)
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                ft.Column([
                                    ft.Text(fmt_es(pozo['poblacion']), size=14, weight=ft.FontWeight.BOLD, color="#7C3AED"),
                                    ft.Text("Población", size=10, color=COLOR_TEXT_MUTED)
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            ]
                        ),
                        padding=8,
                        bgcolor="#F8FAFC",
                        border_radius=8
                    ),

                    inop_section if inop_section else ft.Container(),

                    # Historial de intervenciones
                    ft.Text("Historial de Intervenciones Oficiales (HIDROVEN):", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                    *itv_controls
                ]
            ),
            width=460,
            padding=ft.Padding.all(6)
        )

        def close_dialog(e):
            if hasattr(page, "close"):
                page.close(dialog)
            elif hasattr(page, "pop_dialog"):
                page.pop_dialog()
            page.update()

        actions = []
        if state.is_editor():
            def on_change_status_from_detail(e):
                close_dialog(e)
                open_change_status_dialog(pozo)

            actions.append(
                ft.OutlinedButton(
                    content=ft.Text("Cambiar Estatus (Operativo / Inoperativo)"),
                    icon=ft.Icons.SYNC_ALT_ROUNDED,
                    icon_color=COLOR_ELECTRIC_BLUE,
                    on_click=on_change_status_from_detail,
                    style=ft.ButtonStyle(
                        color=COLOR_ELECTRIC_BLUE,
                        side=ft.BorderSide(1, COLOR_ELECTRIC_BLUE)
                    )
                )
            )
        actions.append(ft.TextButton("Cerrar", on_click=close_dialog))

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, color=COLOR_ELECTRIC_BLUE),
                ft.Text("Ficha Técnica del Pozo", size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
            ]),
            content=content,
            actions=actions
        )
        if hasattr(page, "open"):
            page.open(dialog)
        else:
            page.show_dialog(dialog)
        page.update()

    # 1. PESTAÑA: RESUMEN POR MUNICIPIO
    def build_tab_resumen_municipios() -> ft.Control:
        h_data = state.hidroven_data
        if not h_data:
            return ft.Text("Cargue el archivo de datos HIDROVEN.", size=12)

        items = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Operatividad Oficial por Municipio (HIDROVEN)", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                    ft.Text("14 Municipios de Portuguesa", size=11, color="#64748B")
                ]
            )
        ]

        muns = h_data["municipios"]
        if selected_mun != "Todos los Municipios":
            muns = [m for m in muns if m["municipio"].lower() == selected_mun.lower()]

        for m in muns:
            pct = m["pct_operatividad"]
            badge_color = COLOR_STATUS_GREEN if pct >= 85 else (COLOR_STATUS_AMBER if pct >= 70 else COLOR_STATUS_RED)

            card = ft.Container(
                content=ft.Column(
                    spacing=6,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(
                                    spacing=6,
                                    controls=[
                                        ft.Icon(ft.Icons.LOCATION_CITY_ROUNDED, size=16, color=COLOR_ELECTRIC_BLUE),
                                        ft.Text(f"Municipio {m['municipio']}", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                                    ]
                                ),
                                ft.Container(
                                    content=ft.Text(f"{pct}% Operativo", size=10, weight=ft.FontWeight.BOLD, color=badge_color),
                                    padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                    bgcolor="#F8FAFC",
                                    border_radius=8,
                                    border=ft.Border.all(1, badge_color)
                                )
                            ]
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_AROUND,
                            controls=[
                                ft.Text(f"Total: {m['total_pozos']} Pozos", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                ft.Text(f"🟢 {m['operativos_total']} Op ({m['op_urb']} Urb / {m['op_rur']} Rur)", size=11, color=COLOR_STATUS_GREEN),
                                ft.Text(f"🔴 {m['inoperativos_total']} Inop ({m['inop_urb']} Urb / {m['inop_rur']} Rur)", size=11, color=COLOR_STATUS_RED),
                                ft.Text(f"💧 {fmt_es(m['caudal_lps'], 1)} L/s", size=11, weight=ft.FontWeight.BOLD, color="#0284C7"),
                            ]
                        )
                    ]
                ),
                bgcolor=COLOR_SURFACE_WHITE,
                padding=10,
                border_radius=8,
                border=ft.Border.all(1, COLOR_BORDER)
            )
            items.append(card)

        return ft.ListView(controls=items, spacing=8, expand=True)

    # 2. PESTAÑA: INVENTARIO DE POZOS
    def build_tab_inventario_pozos() -> ft.Control:
        pozos = state.get_filtered_pozos_hidroven(selected_mun, selected_parr)
        sub_title = f"{selected_mun}" if selected_mun != "Todos los Municipios" else "Estadal Completo"
        if selected_parr and selected_parr != "Todas las Parroquias":
            sub_title += f" • {selected_parr}"

        items = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(f"Inventario de Pozos: {sub_title} ({len(pozos)} pozos)", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                    ft.Text("Toque cualquier pozo para ver ficha y requerimiento", size=11, color=COLOR_ELECTRIC_BLUE, weight=ft.FontWeight.W_600)
                ]
            )
        ]

        if not pozos:
            items.append(
                ft.Container(
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.SEARCH_OFF_ROUNDED, size=40, color=COLOR_TEXT_MUTED),
                            ft.Text("No se encontraron pozos para el filtro seleccionado.", size=12, color=COLOR_TEXT_SECONDARY),
                        ]
                    ),
                    padding=30,
                    alignment=ft.Alignment(0, 0)
                )
            )
            return ft.ListView(controls=items, spacing=6, expand=True)

        for p in pozos:
            is_op = p["operatividad"] == "SI"
            right_actions = [
                create_semaphore_badge("Operativo" if is_op else "Inoperativo", compact=True)
            ]
            if state.is_editor():
                right_actions.append(
                    ft.IconButton(
                        icon=ft.Icons.SYNC_ALT_ROUNDED,
                        icon_color=COLOR_ELECTRIC_BLUE,
                        icon_size=18,
                        tooltip="Cambiar Estatus (Operativo / Inoperativo)",
                        on_click=lambda e, pz=p: open_change_status_dialog(pz)
                    )
                )

            card = ft.Container(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            spacing=8,
                            controls=[
                                ft.Container(
                                    content=ft.Text(str(p["n"]), size=10, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                    bgcolor=COLOR_NAVY_DARK,
                                    width=24,
                                    height=24,
                                    border_radius=12,
                                    alignment=ft.Alignment(0, 0)
                                ),
                                ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text(f"{p['cod_minaguas']} - {p['ubicacion']}", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                        ft.Text(f"📍 {p['municipio']} • {p['parroquia']} ({p['area']}) | {p['motor_hp']} HP - {p['caudal_lps']} L/s - {fmt_es(p['poblacion'])} hab.", size=10, color=COLOR_TEXT_SECONDARY)
                                    ]
                                )
                            ],
                            expand=True
                        ),
                        ft.Row(
                            spacing=4,
                            tight=True,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=right_actions
                        )
                    ]
                ),
                bgcolor=COLOR_SURFACE_WHITE,
                padding=10,
                border_radius=8,
                border=ft.Border.all(1, COLOR_STATUS_RED_BORDER if not is_op else COLOR_BORDER),
                ink=True,
                on_click=lambda e, pz=p: open_well_detail_dialog(pz)
            )
            items.append(card)

        return ft.ListView(controls=items, spacing=6, expand=True)

    # 3. PESTAÑA: POZOS INOPERATIVOS Y REQUERIMIENTOS
    def build_tab_inoperativos() -> ft.Control:
        inops = state.get_filtered_inoperativos_hidroven(selected_mun, selected_parr)
        sub_title = f"{selected_mun}" if selected_mun != "Todos los Municipios" else "Estadal Completo"
        if selected_parr and selected_parr != "Todas las Parroquias":
            sub_title += f" • {selected_parr}"

        # Normalización y ordenamiento cronológico por fecha de salida
        def get_inop_sort_key(item):
            f_raw = str(item.get("fecha_salida", "")).strip().upper()
            if "MAS" in f_raw or "10 A" in f_raw or "AÑOS" in f_raw:
                return "1900-01-01"  # 'MAS DE 10 AÑOS' tratados como los más antiguos
            parts = f_raw.split("/")
            if len(parts) == 3:
                try:
                    d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
                    return f"{y:04d}-{m:02d}-{d:02d}"
                except Exception:
                    pass
            parts = f_raw.split("-")
            if len(parts) == 3:
                try:
                    y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
                    return f"{y:04d}-{m:02d}-{d:02d}"
                except Exception:
                    pass
            if len(f_raw) == 4 and f_raw.isdigit():
                return f"{f_raw}-01-01"
            return f_raw

        valid_inops = []
        empty_inops = []
        for item in inops:
            f_clean = str(item.get("fecha_salida", "")).strip().upper()
            if not f_clean or f_clean in ("NAN", "NONE", "-", "SIN FECHA", "S/F"):
                empty_inops.append(item)
            else:
                valid_inops.append(item)

        reverse_order = (inops_sort_order == "recent_first")
        valid_inops.sort(key=get_inop_sort_key, reverse=reverse_order)
        sorted_inops = valid_inops + empty_inops

        def set_inops_sort(new_order: str):
            nonlocal inops_sort_order
            inops_sort_order = new_order
            render_active_tab()
            page.update()

        sort_selector_inops = ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=4,
                        controls=[
                            ft.Icon(ft.Icons.SORT_ROUNDED, size=15, color=COLOR_NAVY_DARK),
                            ft.Text("Ordenar por fecha de salida:", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ]
                    ),
                    ft.Row(
                        spacing=6,
                        controls=[
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.ARROW_DOWNWARD_ROUNDED, size=12, color="#FFFFFF" if inops_sort_order == "recent_first" else COLOR_NAVY_DARK),
                                    ft.Text("Más recientes primero", size=10, weight=ft.FontWeight.BOLD if inops_sort_order == "recent_first" else ft.FontWeight.W_500, color="#FFFFFF" if inops_sort_order == "recent_first" else COLOR_NAVY_DARK)
                                ], spacing=3, tight=True),
                                bgcolor=COLOR_STATUS_RED if inops_sort_order == "recent_first" else "#F1F5F9",
                                padding=ft.Padding.symmetric(horizontal=8, vertical=5),
                                border_radius=6,
                                border=ft.Border.all(1, COLOR_STATUS_RED if inops_sort_order == "recent_first" else "#CBD5E1"),
                                ink=True,
                                on_click=lambda e: set_inops_sort("recent_first")
                            ),
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.ARROW_UPWARD_ROUNDED, size=12, color="#FFFFFF" if inops_sort_order == "oldest_first" else COLOR_NAVY_DARK),
                                    ft.Text("Más antiguos primero", size=10, weight=ft.FontWeight.BOLD if inops_sort_order == "oldest_first" else ft.FontWeight.W_500, color="#FFFFFF" if inops_sort_order == "oldest_first" else COLOR_NAVY_DARK)
                                ], spacing=3, tight=True),
                                bgcolor=COLOR_STATUS_RED if inops_sort_order == "oldest_first" else "#F1F5F9",
                                padding=ft.Padding.symmetric(horizontal=8, vertical=5),
                                border_radius=6,
                                border=ft.Border.all(1, COLOR_STATUS_RED if inops_sort_order == "oldest_first" else "#CBD5E1"),
                                ink=True,
                                on_click=lambda e: set_inops_sort("oldest_first")
                            )
                        ]
                    )
                ]
            ),
            bgcolor=COLOR_SURFACE_WHITE,
            padding=ft.Padding.symmetric(horizontal=10, vertical=6),
            border_radius=8,
            border=ft.Border.all(1, COLOR_BORDER)
        )

        items = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(f"Pozos Inoperativos: {sub_title} ({len(inops)} pozos)", size=13, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_RED),
                    ft.Text("Meta de Reactivación Gobernación", size=11, color="#64748B")
                ]
            ),
            sort_selector_inops
        ]

        if not inops:
            items.append(
                ft.Container(
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, size=40, color=COLOR_STATUS_GREEN),
                            ft.Text("¡Excelente! No hay pozos inoperativos registrados bajo este filtro.", size=12, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN),
                        ]
                    ),
                    padding=30,
                    alignment=ft.Alignment(0, 0)
                )
            )
            return ft.ListView(controls=items, spacing=8, expand=True)

        for i in sorted_inops:
            matching_pozo = next(
                (p for p in state.hidroven_data.get("pozos", [])
                 if p.get("n") == i.get("n") or p.get("cod_minaguas") == i.get("cod_minaguas")),
                None
            )
            pozo_target = matching_pozo if matching_pozo else {
                "n": i.get("n", 0),
                "cod_minaguas": i.get("cod_minaguas", i.get("num_pozo", "")),
                "ubicacion": i.get("ubicacion", ""),
                "municipio": i.get("municipio", ""),
                "parroquia": i.get("parroquia", ""),
                "operatividad": "NO",
                "motor_hp": 0,
                "caudal_lps": 0.0,
                "poblacion": i.get("poblacion", 0)
            }

            inop_badge_controls = [
                create_semaphore_badge("Inoperativo", compact=True)
            ]
            if state.is_editor():
                inop_badge_controls.append(
                    ft.IconButton(
                        icon=ft.Icons.SYNC_ALT_ROUNDED,
                        icon_color=COLOR_STATUS_GREEN,
                        icon_size=18,
                        tooltip="Reactivar / Cambiar Estatus del Pozo",
                        on_click=lambda e, pz=pozo_target: open_change_status_dialog(pz)
                    )
                )

            card = ft.Container(
                content=ft.Column(
                    spacing=6,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(
                                    spacing=6,
                                    controls=[
                                        ft.Icon(ft.Icons.REPORT_PROBLEM_ROUNDED, size=16, color=COLOR_STATUS_RED),
                                        ft.Text(f"{i['num_pozo']} - {i['ubicacion']}", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                                    ]
                                ),
                                ft.Row(
                                    spacing=4,
                                    tight=True,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=inop_badge_controls
                                )
                            ]
                        ),
                        ft.Text(f"📍 {i['municipio']} • {i['parroquia']} ({i['area']}) | Población afectada: {fmt_es(i['poblacion'])} hab.", size=10, color=COLOR_TEXT_SECONDARY),
                        # Diagnóstico
                        ft.Container(
                            content=ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text("REQUERIMIENTO:", size=9, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_RED),
                                    ft.Text(i["requerimiento"], size=10, weight=ft.FontWeight.W_600, color="#991B1B"),
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Text(f"⚡ Capacidad requerida: {i['capacidad']}", size=9, color="#991B1B"),
                                            ft.Text(f"🗓️ Fecha de Salida: {i['fecha_salida']}", size=9, color="#991B1B"),
                                        ]
                                    )
                                ]
                            ),
                            bgcolor="#FEF2F2",
                            padding=6,
                            border_radius=6,
                            border=ft.Border.all(1, "#FCA5A5")
                        )
                    ]
                ),
                bgcolor=COLOR_SURFACE_WHITE,
                padding=10,
                border_radius=8,
                border=ft.Border.all(1, "#FCA5A5")
            )
            items.append(card)

        return ft.ListView(controls=items, spacing=8, expand=True)

    # Modal para Registrar Nueva Perforación (Solo Editor)
    def open_add_perforacion_dialog():
        if not state.is_editor():
            return

        mun_options = [m for m in MUNICIPALITIES_LIST if m != "Todos los Municipios"]
        mun_dd = ft.Dropdown(
            label="Municipio",
            value="ARAURE" if selected_mun == "Todos los Municipios" else selected_mun.upper(),
            options=[ft.dropdown.Option(m.upper(), m) for m in mun_options],
            border_color=COLOR_BORDER,
            focused_border_color=COLOR_ELECTRIC_BLUE,
            text_size=12
        )
        ubicacion_tf = ft.TextField(
            label="Sector / Ubicación de la Obra",
            hint_text="Ej: VILLA NUEVA SECTOR 2",
            border_color=COLOR_BORDER,
            focused_border_color=COLOR_ELECTRIC_BLUE,
            text_size=12
        )
        year_dd = ft.Dropdown(
            label="Año de Ejecución",
            value="2026",
            options=[ft.dropdown.Option(y, y) for y in ["2026", "2025", "2024", "2023", "2022", "2021"]],
            border_color=COLOR_BORDER,
            focused_border_color=COLOR_ELECTRIC_BLUE,
            text_size=12
        )
        fuente_dd = ft.Dropdown(
            label="Fuente de Financiamiento",
            value="GOBERNACION",
            options=[
                ft.dropdown.Option("GOBERNACION", "GOBERNACION"),
                ft.dropdown.Option("ALCALDIA", "ALCALDIA"),
                ft.dropdown.Option("MINAGUAS", "MINAGUAS"),
                ft.dropdown.Option("LA COMUNA", "LA COMUNA"),
            ],
            border_color=COLOR_BORDER,
            focused_border_color=COLOR_ELECTRIC_BLUE,
            text_size=12
        )
        equipo_tf = ft.TextField(
            label="Equipo Instalado (HP)",
            value="SIN EQUIPO",
            hint_text="Ej: 50HP, 75HP o SIN EQUIPO",
            border_color=COLOR_BORDER,
            focused_border_color=COLOR_ELECTRIC_BLUE,
            text_size=12
        )
        estatus_dd = ft.Dropdown(
            label="Estatus de la Perforación",
            value="EN EJECUCION",
            options=[
                ft.dropdown.Option("OPERATIVA", "OPERATIVA"),
                ft.dropdown.Option("OPERATIVA POR INAUGURAR", "OPERATIVA POR INAUGURAR"),
                ft.dropdown.Option("INOPERATIVA POR INAUGURAR", "INOPERATIVA POR INAUGURAR"),
                ft.dropdown.Option("POR INAUGURAR", "POR INAUGURAR"),
                ft.dropdown.Option("EN EJECUCION", "EN EJECUCION"),
                ft.dropdown.Option("PARALIZADO", "PARALIZADO"),
            ],
            border_color=COLOR_BORDER,
            focused_border_color=COLOR_ELECTRIC_BLUE,
            text_size=12
        )

        def save_nueva_perf(e):
            if not ubicacion_tf.value.strip():
                page.show_dialog(
                    ft.SnackBar(content=ft.Text("Ingrese la ubicación de la perforación.", color="#FFFFFF"), bgcolor=COLOR_STATUS_RED)
                )
                page.update()
                return

            state.add_nueva_perforacion(
                municipio=mun_dd.value,
                ubicacion=ubicacion_tf.value.strip(),
                year=year_dd.value,
                fuente=fuente_dd.value,
                equipo_hp=equipo_tf.value.strip(),
                estatus=estatus_dd.value
            )

            if hasattr(page, "close"):
                page.close(dialog)
            elif hasattr(page, "pop_dialog"):
                page.pop_dialog()
            page.update()

            page.show_dialog(
                ft.SnackBar(
                    content=ft.Text("Nueva obra de perforación registrada exitosamente.", color="#FFFFFF"),
                    bgcolor=COLOR_STATUS_GREEN
                )
            )
            render_active_tab()
            page.update()

        def cancel_dlg(e):
            if hasattr(page, "close"):
                page.close(dialog)
            elif hasattr(page, "pop_dialog"):
                page.pop_dialog()
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.ADD_CIRCLE_ROUNDED, color=COLOR_ELECTRIC_BLUE),
                ft.Text("Registrar Nueva Perforación", size=15, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
            ]),
            content=ft.Container(
                content=ft.Column(
                    tight=True,
                    spacing=10,
                    controls=[
                        mun_dd,
                        ubicacion_tf,
                        ft.Row([year_dd, fuente_dd], spacing=8),
                        ft.Row([equipo_tf, estatus_dd], spacing=8),
                    ]
                ),
                width=440,
                padding=ft.Padding.all(4)
            ),
            actions=[
                ft.TextButton(content=ft.Text("Cancelar"), on_click=cancel_dlg),
                ft.FilledButton(
                    content=ft.Text("Registrar Perforación"),
                    on_click=save_nueva_perf,
                    style=ft.ButtonStyle(bgcolor=COLOR_ELECTRIC_BLUE, color="#FFFFFF")
                )
            ]
        )
        if hasattr(page, "open"):
            page.open(dialog)
        else:
            page.show_dialog(dialog)
        page.update()

    # Modal para Editar Perforación (Solo Editor)
    def open_edit_perforacion_dialog(perf: dict):
        if not state.is_editor():
            return

        ubicacion_tf = ft.TextField(
            label="Ubicación / Sector",
            value=perf.get("ubicacion", ""),
            border_color=COLOR_BORDER,
            focused_border_color=COLOR_ELECTRIC_BLUE,
            text_size=12
        )
        equipo_tf = ft.TextField(
            label="Equipo Instalado (HP)",
            value=perf.get("equipo_hp", "SIN EQUIPO"),
            hint_text="Ej: 50HP, 75HP o SIN EQUIPO",
            border_color=COLOR_BORDER,
            focused_border_color=COLOR_ELECTRIC_BLUE,
            text_size=12
        )
        estatus_dd = ft.Dropdown(
            label="Estatus",
            value=perf.get("estatus", "OPERATIVA"),
            options=[
                ft.dropdown.Option("OPERATIVA", "OPERATIVA"),
                ft.dropdown.Option("OPERATIVA POR INAUGURAR", "OPERATIVA POR INAUGURAR"),
                ft.dropdown.Option("INOPERATIVA POR INAUGURAR", "INOPERATIVA POR INAUGURAR"),
                ft.dropdown.Option("POR INAUGURAR", "POR INAUGURAR"),
                ft.dropdown.Option("EN EJECUCION", "EN EJECUCION"),
                ft.dropdown.Option("PARALIZADO", "PARALIZADO"),
            ],
            border_color=COLOR_BORDER,
            focused_border_color=COLOR_ELECTRIC_BLUE,
            text_size=12
        )
        fuente_dd = ft.Dropdown(
            label="Fuente de Financiamiento",
            value=perf.get("fuente", "GOBERNACION"),
            options=[
                ft.dropdown.Option("GOBERNACION", "GOBERNACION"),
                ft.dropdown.Option("ALCALDIA", "ALCALDIA"),
                ft.dropdown.Option("MINAGUAS", "MINAGUAS"),
                ft.dropdown.Option("LA COMUNA", "LA COMUNA"),
            ],
            border_color=COLOR_BORDER,
            focused_border_color=COLOR_ELECTRIC_BLUE,
            text_size=12
        )

        def save_edit_perf(e):
            state.update_nueva_perforacion(
                perf_id=perf.get("id"),
                equipo_hp=equipo_tf.value.strip(),
                estatus=estatus_dd.value,
                ubicacion=ubicacion_tf.value.strip(),
                fuente=fuente_dd.value
            )

            if hasattr(page, "close"):
                page.close(dialog)
            elif hasattr(page, "pop_dialog"):
                page.pop_dialog()
            page.update()

            page.show_dialog(
                ft.SnackBar(
                    content=ft.Text(f"Perforación #{perf.get('id')} actualizada exitosamente.", color="#FFFFFF"),
                    bgcolor=COLOR_STATUS_GREEN
                )
            )
            render_active_tab()
            page.update()

        def cancel_dlg(e):
            if hasattr(page, "close"):
                page.close(dialog)
            elif hasattr(page, "pop_dialog"):
                page.pop_dialog()
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.EDIT_NOTE_ROUNDED, color=COLOR_ELECTRIC_BLUE),
                ft.Text(f"Editar Perforación #{perf.get('id')}", size=15, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
            ]),
            content=ft.Container(
                content=ft.Column(
                    tight=True,
                    spacing=10,
                    controls=[
                        ft.Text(f"Municipio: {perf.get('municipio')} • Año: {perf.get('year')}", size=12, color=COLOR_TEXT_SECONDARY),
                        ubicacion_tf,
                        fuente_dd,
                        equipo_tf,
                        estatus_dd
                    ]
                ),
                width=420,
                padding=ft.Padding.all(4)
            ),
            actions=[
                ft.TextButton(content=ft.Text("Cancelar"), on_click=cancel_dlg),
                ft.FilledButton(
                    content=ft.Text("Guardar Cambios"),
                    on_click=save_edit_perf,
                    style=ft.ButtonStyle(bgcolor=COLOR_ELECTRIC_BLUE, color="#FFFFFF")
                )
            ]
        )
        if hasattr(page, "open"):
            page.open(dialog)
        else:
            page.show_dialog(dialog)
        page.update()

    # 4. PESTAÑA: NUEVAS PERFORACIONES (34)
    def build_tab_nuevas_perforaciones() -> ft.Control:
        kpis = state.get_nuevas_perforaciones_kpis(selected_mun)
        perfs = state.get_nuevas_perforaciones(
            municipio=selected_mun,
            year=perf_year,
            fuente=perf_fuente,
            estatus=perf_estatus
        )

        sub_title = selected_mun if selected_mun != "Todos los Municipios" else "Estadal Completo"

        def create_kpi_card_perf(title: str, value: int, color_hex: str, icon, bg_color: str):
            return ft.Container(
                content=ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            content=ft.Icon(icon, size=18, color=color_hex),
                            bgcolor=bg_color,
                            width=36,
                            height=36,
                            border_radius=8,
                            alignment=ft.Alignment(0, 0)
                        ),
                        ft.Column(
                            spacing=1,
                            controls=[
                                ft.Text(str(value), size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                ft.Text(title, size=10, weight=ft.FontWeight.W_600, color=COLOR_TEXT_SECONDARY)
                            ]
                        )
                    ]
                ),
                bgcolor=COLOR_SURFACE_WHITE,
                padding=ft.Padding.symmetric(horizontal=10, vertical=8),
                border_radius=8,
                border=ft.Border.all(1, COLOR_BORDER),
                expand=True
            )

        kpis_row = ft.Row(
            spacing=8,
            controls=[
                create_kpi_card_perf("Operativas", kpis["operativas"], "#16A34A", ft.Icons.CHECK_CIRCLE_ROUNDED, "#DCFCE7"),
                create_kpi_card_perf("Por Inaugurar", kpis["por_inaugurar"], "#0284C7", ft.Icons.FLAG_ROUNDED, "#E0F2FE"),
                create_kpi_card_perf("En Ejecución", kpis["en_ejecucion"], "#D97706", ft.Icons.HANDYMAN_ROUNDED, "#FEF3C7"),
                create_kpi_card_perf("Paralizado", kpis["paralizado"], "#DC2626", ft.Icons.WARNING_ROUNDED, "#FEE2E2"),
            ]
        )

        def on_filter_change(e):
            nonlocal perf_year, perf_fuente, perf_estatus
            perf_year = dd_year.value
            perf_fuente = dd_fuente.value
            perf_estatus = dd_estatus.value
            render_active_tab()
            page.update()

        dd_year = ft.Dropdown(
            label="Año",
            value=perf_year,
            options=[ft.dropdown.Option(y, y) for y in ["Todos los Años", "2026", "2025", "2024", "2023", "2022", "2021"]],
            on_select=on_filter_change,
            text_size=11,
            border_color=COLOR_BORDER,
            focused_border_color=COLOR_ELECTRIC_BLUE,
            content_padding=ft.Padding.symmetric(horizontal=8, vertical=4),
            expand=True
        )

        dd_fuente = ft.Dropdown(
            label="Fuente",
            value=perf_fuente,
            options=[ft.dropdown.Option(f, f) for f in ["Todas las Fuentes", "GOBERNACION", "ALCALDIA", "MINAGUAS", "LA COMUNA"]],
            on_select=on_filter_change,
            text_size=11,
            border_color=COLOR_BORDER,
            focused_border_color=COLOR_ELECTRIC_BLUE,
            content_padding=ft.Padding.symmetric(horizontal=8, vertical=4),
            expand=True
        )

        dd_estatus = ft.Dropdown(
            label="Estatus",
            value=perf_estatus,
            options=[ft.dropdown.Option(s, s) for s in ["Todos los Estatus", "OPERATIVA", "POR INAUGURAR", "EN EJECUCION", "PARALIZADO"]],
            on_select=on_filter_change,
            text_size=11,
            border_color=COLOR_BORDER,
            focused_border_color=COLOR_ELECTRIC_BLUE,
            content_padding=ft.Padding.symmetric(horizontal=8, vertical=4),
            expand=True
        )

        filter_bar_perf_controls = [dd_year, dd_fuente, dd_estatus]
        if state.is_editor():
            filter_bar_perf_controls.append(
                ft.FilledButton(
                    content=ft.Text("+ Nueva Perforación"),
                    icon=ft.Icons.ADD_ROUNDED,
                    style=ft.ButtonStyle(bgcolor=COLOR_ELECTRIC_BLUE, color="#FFFFFF"),
                    on_click=lambda e: open_add_perforacion_dialog()
                )
            )

        filter_bar_perf = ft.Container(
            content=ft.Row(
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=filter_bar_perf_controls
            ),
            bgcolor=COLOR_SURFACE_WHITE,
            padding=8,
            border_radius=8,
            border=ft.Border.all(1, COLOR_BORDER)
        )

        items = [
            kpis_row,
            filter_bar_perf,
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(f"Listado de Perforaciones: {sub_title} ({len(perfs)} obras)", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                    ft.Text(f"Filtros: {perf_year} • {perf_fuente} • {perf_estatus}", size=11, color=COLOR_TEXT_SECONDARY)
                ]
            )
        ]

        if not perfs:
            items.append(
                ft.Container(
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.SEARCH_OFF_ROUNDED, size=40, color=COLOR_TEXT_MUTED),
                            ft.Text("No se encontraron perforaciones con los filtros seleccionados.", size=12, color=COLOR_TEXT_SECONDARY),
                        ]
                    ),
                    padding=30,
                    alignment=ft.Alignment(0, 0)
                )
            )
            return ft.ListView(controls=items, spacing=8, expand=True)

        for p in perfs:
            st_text = p.get("estatus", "OPERATIVA")
            if st_text == "OPERATIVA":
                badge_bg = "#DCFCE7"
                badge_fg = "#16A34A"
                border_c = "#BBF7D0"
                badge_label = "Operativa"
            elif "INAUGURAR" in st_text:
                badge_bg = "#E0F2FE"
                badge_fg = "#0284C7"
                border_c = "#BAE6FD"
                badge_label = "Por Inaugurar" if st_text == "POR INAUGURAR" else ("Op. Por Inaugurar" if "OPERATIVA" in st_text else "Inop. Por Inaugurar")
            elif "EJECUCION" in st_text:
                badge_bg = "#FEF3C7"
                badge_fg = "#D97706"
                border_c = "#FDE68A"
                badge_label = "En Ejecución"
            else:
                badge_bg = "#FEE2E2"
                badge_fg = "#DC2626"
                border_c = "#FECACA"
                badge_label = "Paralizado"

            badge = ft.Container(
                content=ft.Text(badge_label, size=10, weight=ft.FontWeight.BOLD, color=badge_fg),
                bgcolor=badge_bg,
                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                border_radius=10,
                border=ft.Border.all(1, border_c)
            )

            right_controls = [badge]
            if state.is_editor():
                right_controls.append(
                    ft.IconButton(
                        icon=ft.Icons.EDIT_ROUNDED,
                        icon_color=COLOR_ELECTRIC_BLUE,
                        icon_size=18,
                        tooltip=f"Editar Perforación #{p.get('id')}",
                        on_click=lambda e, item=p: open_edit_perforacion_dialog(item)
                    )
                )

            card = ft.Container(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                    content=ft.Text(f"#{p.get('id')}", size=11, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                    bgcolor=COLOR_NAVY_DARK,
                                    width=32,
                                    height=32,
                                    border_radius=16,
                                    alignment=ft.Alignment(0, 0)
                                ),
                                ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text(f"{p.get('ubicacion')}", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                        ft.Text(f"📍 {p.get('municipio')} • Año: {p.get('year')} • Fuente: {p.get('fuente')}", size=11, color=COLOR_TEXT_SECONDARY),
                                        ft.Row([
                                            ft.Icon(ft.Icons.BOLT_ROUNDED, size=13, color=COLOR_ELECTRIC_BLUE),
                                            ft.Text(f"Equipo: {p.get('equipo_hp')}", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                                        ], spacing=2)
                                    ]
                                )
                            ],
                            expand=True
                        ),
                        ft.Row(
                            spacing=4,
                            tight=True,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=right_controls
                        )
                    ]
                ),
                bgcolor=COLOR_SURFACE_WHITE,
                padding=10,
                border_radius=8,
                border=ft.Border.all(1, border_c),
            )
            items.append(card)

        return ft.ListView(controls=items, spacing=8, expand=True)

    # 5. PESTAÑA: ESTACIONES Y CAPTACIÓN
    def build_tab_estaciones() -> ft.Control:
        h_data = state.hidroven_data
        if not h_data or "estaciones_rebombeo" not in h_data:
            return ft.Text("No hay estaciones cargadas.", size=12)

        reb = h_data["estaciones_rebombeo"]
        c_sur = reb.get("cono_sur", [])
        c_nor = reb.get("cono_norte", [])
        c_cap = reb.get("captacion_conduccion", [])

        items = []

        # 1. Cono Sur (17 estaciones)
        items.append(ft.Text(f"Estaciones de Rebombeo Cono Sur ({len(c_sur)} estaciones)", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK))
        for st in c_sur:
            items.append(
                ft.Container(
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(f"{st['item']}. {st['ubicacion']} ({st['municipio']})", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                    ft.Text(f"Motor: {st['motor_marca']} {st['motor_hp']} HP ({st['voltaje']}) | Bomba: {st['bomba_marca']} {st['bomba_modelo']} | Caudal: {st['caudal_lps']} L/s", size=10, color=COLOR_TEXT_SECONDARY)
                                ]
                            ),
                            create_semaphore_badge("Operativo" if st["operatividad"] == "SI" else "Inoperativo", compact=True)
                        ]
                    ),
                    bgcolor=COLOR_SURFACE_WHITE,
                    padding=8,
                    border_radius=8,
                    border=ft.Border.all(1, COLOR_BORDER)
                )
            )

        # 2. Cono Norte (10 estaciones)
        items.append(ft.Container(height=8))
        items.append(ft.Text(f"Estaciones de Rebombeo Cono Norte ({len(c_nor)} estaciones)", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK))
        for st in c_nor:
            items.append(
                ft.Container(
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(f"{st['item']}. {st['ubicacion']} ({st['municipio']})", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                    ft.Text(f"Motor: {st['motor_marca']} {st['motor_hp']} ({st['voltaje']}) | Caudal: {st['caudal_lps']} L/s | {fmt_es(st['habitantes'])} hab.", size=10, color=COLOR_TEXT_SECONDARY)
                                ]
                            ),
                            create_semaphore_badge("Operativo" if st["operatividad"] == "SI" else "Inoperativo", compact=True)
                        ]
                    ),
                    bgcolor=COLOR_SURFACE_WHITE,
                    padding=8,
                    border_radius=8,
                    border=ft.Border.all(1, COLOR_BORDER)
                )
            )

        # 3. Captación y Conducción (3 estaciones)
        items.append(ft.Container(height=8))
        items.append(ft.Text(f"Estaciones de Captación y Conducción Mayores ({len(c_cap)} estaciones)", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK))
        for st in c_cap:
            items.append(
                ft.Container(
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(f"{st['item']}. {st['ubicacion']} ({st['municipio']})", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                    ft.Text(f"Voltaje: {st['voltaje']} | Caudal: {st['caudal_lps']} L/s | Población: {fmt_es(st['habitantes'])} hab.", size=10, color=COLOR_TEXT_SECONDARY)
                                ]
                            ),
                            create_semaphore_badge("Operativo" if st["operatividad"] == "SI" else "Inoperativo", compact=True)
                        ]
                    ),
                    bgcolor=COLOR_SURFACE_WHITE,
                    padding=8,
                    border_radius=8,
                    border=ft.Border.all(1, COLOR_BORDER)
                )
            )

        return ft.ListView(controls=items, spacing=6, expand=True)

    # 5. PESTAÑA: HISTÓRICO E INTERVENCIONES (2021-2026)
    def build_tab_intervenciones() -> ft.Control:
        h_data = state.hidroven_data
        if not h_data:
            return ft.Text("No hay intervenciones cargadas.", size=12)

        # Datos consolidados del municipio seleccionado (u origen estatal)
        rehab_info = state.get_consolidado_rehab_for_municipio(selected_mun)
        itvs = state.get_filtered_intervenciones(selected_mun, selected_parr)
        anual = rehab_info.get("anual", {})

        # Chips de años (2021 a 2026)
        year_chips = []
        for y in ["2021", "2022", "2023", "2024", "2025", "2026"]:
            val = anual.get(y, 0)
            year_chips.append(
                ft.Container(
                    content=ft.Column(
                        spacing=1,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(y, size=10, weight=ft.FontWeight.W_600, color=COLOR_TEXT_SECONDARY),
                            ft.Text(str(val), size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ]
                    ),
                    bgcolor="#F1F5F9",
                    padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                    border_radius=6,
                    border=ft.Border.all(1, "#CBD5E1"),
                    expand=True
                )
            )

        items = [
            # Título de contexto
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(
                        f"Histórico de Rehabilitación: {rehab_info['municipio']}",
                        size=13,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_NAVY_DARK
                    ),
                    ft.Text("Hoja Oficial CONSOLIDADO REHAB.", size=10, color=COLOR_TEXT_MUTED)
                ]
            ),
            # 3 Tarjetas KPI superiores (Rehabilitados, Intervenciones Mayores, Mantenimientos)
            ft.Row(
                spacing=8,
                controls=[
                    ft.Container(
                        content=ft.Column(
                            spacing=2,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Text(fmt_es(rehab_info.get("rehabilitados", 0)), size=18, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN),
                                ft.Text("Rehabilitados", size=10, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                ft.Text("(2021 - 2026)", size=9, color=COLOR_TEXT_MUTED),
                            ]
                        ),
                        bgcolor="#DCFCE7",
                        padding=ft.Padding.symmetric(horizontal=8, vertical=10),
                        border_radius=8,
                        border=ft.Border.all(1, "#86EFAC"),
                        expand=True
                    ),
                    ft.Container(
                        content=ft.Column(
                            spacing=2,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Text(fmt_es(rehab_info.get("intervenciones", 0)), size=18, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_BLUE),
                                ft.Text("Intervenciones", size=10, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                ft.Text("Mayores", size=9, color=COLOR_TEXT_MUTED),
                            ]
                        ),
                        bgcolor="#EFF6FF",
                        padding=ft.Padding.symmetric(horizontal=8, vertical=10),
                        border_radius=8,
                        border=ft.Border.all(1, "#BFDBFE"),
                        expand=True
                    ),
                    ft.Container(
                        content=ft.Column(
                            spacing=2,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Text(fmt_es(rehab_info.get("mantenimientos", 0)), size=18, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_AMBER),
                                ft.Text("Mantenimientos", size=10, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                ft.Text("Electromecánicos", size=9, color=COLOR_TEXT_MUTED),
                            ]
                        ),
                        bgcolor="#FEF3C7",
                        padding=ft.Padding.symmetric(horizontal=8, vertical=10),
                        border_radius=8,
                        border=ft.Border.all(1, "#FDE68A"),
                        expand=True
                    ),
                ]
            ),
            # Desglose anual (2021 - 2026)
            ft.Container(
                content=ft.Column(
                    spacing=6,
                    controls=[
                        ft.Text("Desglose Anual de Pozos Rehabilitados (2021–2026):", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Row(controls=year_chips, spacing=6)
                    ]
                ),
                padding=10,
                bgcolor=COLOR_SURFACE_WHITE,
                border_radius=8,
                border=ft.Border.all(1, COLOR_BORDER)
            ),
        ]

        # Normalización y ordenamiento cronológico por fecha de intervención
        def get_itvs_sort_key(item):
            f_raw = str(item.get("fecha", "")).strip().upper()
            if "NUEVO" in f_raw:
                return "9999-99-99"  # Ubicado junto con los más recientes
            parts = f_raw.split("/")
            if len(parts) == 3:
                try:
                    d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
                    return f"{y:04d}-{m:02d}-{d:02d}"
                except Exception:
                    pass
            parts = f_raw.split("-")
            if len(parts) == 3:
                try:
                    y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
                    return f"{y:04d}-{m:02d}-{d:02d}"
                except Exception:
                    pass
            if len(f_raw) == 4 and f_raw.isdigit():
                return f"{f_raw}-01-01"
            return f_raw

        valid_itvs = []
        empty_itvs = []
        for item in itvs:
            f_clean = str(item.get("fecha", "")).strip().upper()
            if not f_clean or f_clean in ("NAN", "NONE", "-", "SIN FECHA", "S/F"):
                empty_itvs.append(item)
            else:
                valid_itvs.append(item)

        reverse_order = (itvs_sort_order == "recent_first")
        valid_itvs.sort(key=get_itvs_sort_key, reverse=reverse_order)
        sorted_itvs = valid_itvs + empty_itvs

        def set_itvs_sort(new_order: str):
            nonlocal itvs_sort_order
            itvs_sort_order = new_order
            render_active_tab()
            page.update()

        sort_selector_itvs = ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=4,
                        controls=[
                            ft.Icon(ft.Icons.SORT_ROUNDED, size=15, color=COLOR_NAVY_DARK),
                            ft.Text("Ordenar por fecha de intervención:", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ]
                    ),
                    ft.Row(
                        spacing=6,
                        controls=[
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.ARROW_DOWNWARD_ROUNDED, size=12, color="#FFFFFF" if itvs_sort_order == "recent_first" else COLOR_NAVY_DARK),
                                    ft.Text("Más recientes primero", size=10, weight=ft.FontWeight.BOLD if itvs_sort_order == "recent_first" else ft.FontWeight.W_500, color="#FFFFFF" if itvs_sort_order == "recent_first" else COLOR_NAVY_DARK)
                                ], spacing=3, tight=True),
                                bgcolor=COLOR_ELECTRIC_BLUE if itvs_sort_order == "recent_first" else "#F1F5F9",
                                padding=ft.Padding.symmetric(horizontal=8, vertical=5),
                                border_radius=6,
                                border=ft.Border.all(1, COLOR_ELECTRIC_BLUE if itvs_sort_order == "recent_first" else "#CBD5E1"),
                                ink=True,
                                on_click=lambda e: set_itvs_sort("recent_first")
                            ),
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.ARROW_UPWARD_ROUNDED, size=12, color="#FFFFFF" if itvs_sort_order == "oldest_first" else COLOR_NAVY_DARK),
                                    ft.Text("Más antiguos primero", size=10, weight=ft.FontWeight.BOLD if itvs_sort_order == "oldest_first" else ft.FontWeight.W_500, color="#FFFFFF" if itvs_sort_order == "oldest_first" else COLOR_NAVY_DARK)
                                ], spacing=3, tight=True),
                                bgcolor=COLOR_ELECTRIC_BLUE if itvs_sort_order == "oldest_first" else "#F1F5F9",
                                padding=ft.Padding.symmetric(horizontal=8, vertical=5),
                                border_radius=6,
                                border=ft.Border.all(1, COLOR_ELECTRIC_BLUE if itvs_sort_order == "oldest_first" else "#CBD5E1"),
                                ink=True,
                                on_click=lambda e: set_itvs_sort("oldest_first")
                            )
                        ]
                    )
                ]
            ),
            bgcolor=COLOR_SURFACE_WHITE,
            padding=ft.Padding.symmetric(horizontal=10, vertical=6),
            border_radius=8,
            border=ft.Border.all(1, COLOR_BORDER)
        )

        items.extend([
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(f"Bitácora de Intervenciones Individuales ({len(itvs)} registros)", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                    ft.Text(f"Mostrando {min(len(itvs), 100)} de {len(itvs)}", size=10, color=COLOR_TEXT_MUTED)
                ]
            ),
            sort_selector_itvs
        ])

        if not itvs:
            items.append(
                ft.Container(
                    content=ft.Text("No se registraron intervenciones para el filtro seleccionado.", size=11, color=COLOR_TEXT_MUTED),
                    padding=20,
                    alignment=ft.Alignment(0, 0)
                )
            )
        else:
            # Lista de intervenciones ordenadas cronológicamente
            for it in sorted_itvs[:100]:
                fuente_color = COLOR_ELECTRIC_BLUE if it["fuente"] == "GOB" else COLOR_NAVY_DARK
                items.append(
                    ft.Container(
                        content=ft.Column(
                            spacing=3,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(f"{it['pozo']} ({it['municipio']})", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                        ft.Text(f"📅 {it['fecha']}", size=10, color="#64748B")
                                    ]
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(f"Tipo: {it['tipo']}", size=10, weight=ft.FontWeight.W_600, color=COLOR_ELECTRIC_BLUE),
                                        ft.Container(
                                            content=ft.Text(f"Fuente: {it['fuente']}", size=10, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                            bgcolor=fuente_color,
                                            padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                            border_radius=4
                                        )
                                    ]
                                ),
                                ft.Text(it["observacion"], size=10, color=COLOR_TEXT_SECONDARY)
                            ]
                        ),
                        bgcolor=COLOR_SURFACE_WHITE,
                        padding=8,
                        border_radius=8,
                        border=ft.Border.all(1, COLOR_BORDER)
                    )
                )

        return ft.ListView(controls=items, spacing=6, expand=True)

    # 6. PESTAÑA: CUADRILLAS BRIPPA Y MANIOBRAS
    def build_tab_brippas_maniobras() -> ft.Control:
        h_data = state.hidroven_data
        if not h_data:
            return ft.Text("No hay datos de BRIPPA.", size=12)

        bri = h_data.get("brippas", {})
        cuads = bri.get("cuadrillas", [])
        resp = bri.get("responsables", [])
        maniobras = h_data.get("maniobras", [])

        items = [
            ft.Text("Cuadrillas BRIPPA Desplegadas por Municipio", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
        ]

        for c in cuads:
            items.append(
                ft.Container(
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column([
                                ft.Text(f"Municipio {c['municipio']}", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                ft.Text(f"Inicio: {c['fecha_inicio']} | Personal: {c['personal']}", size=10, color=COLOR_TEXT_SECONDARY)
                            ]),
                            ft.Row([
                                ft.Text(f"💧 1x10: {c['potable_1x10']} / Cero Botes: {c['potable_cero_botes']}", size=10, weight=ft.FontWeight.W_600, color=COLOR_ELECTRIC_BLUE),
                            ])
                        ]
                    ),
                    bgcolor=COLOR_SURFACE_WHITE,
                    padding=8,
                    border_radius=8,
                    border=ft.Border.all(1, COLOR_BORDER)
                )
            )

        # Directorio de Responsables
        items.append(ft.Container(height=6))
        items.append(ft.Text("Directorio Oficial de Responsables BRIPPA", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK))
        resp_row = []
        for r in resp:
            resp_row.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(r["nombre"], size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Text(f"📞 {r['telefono']}", size=10, color=COLOR_ELECTRIC_BLUE)
                    ]),
                    bgcolor="#EFF6FF",
                    padding=8,
                    border_radius=8,
                    border=ft.Border.all(1, "#BFDBFE"),
                    expand=True
                )
            )
        items.append(ft.Row(resp_row, spacing=6))

        # Maniobras de válvulas
        items.append(ft.Container(height=6))
        items.append(ft.Text("Cronograma Semanal de Maniobras de Válvulas de Sectorización", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK))
        for m in maniobras:
            items.append(
                ft.Container(
                    content=ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text(f"Válvula: {m['valvula']}", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                            ft.Row([
                                ft.Text(f"L: {m['lunes'] or '-'}", size=9, color=COLOR_TEXT_SECONDARY),
                                ft.Text(f"M: {m['martes'] or '-'}", size=9, color=COLOR_TEXT_SECONDARY),
                                ft.Text(f"X: {m['miercoles'] or '-'}", size=9, color=COLOR_TEXT_SECONDARY),
                                ft.Text(f"J: {m['jueves'] or '-'}", size=9, color=COLOR_TEXT_SECONDARY),
                                ft.Text(f"V: {m['viernes'] or '-'}", size=9, color=COLOR_TEXT_SECONDARY),
                                ft.Text(f"S: {m['sabado'] or '-'}", size=9, color=COLOR_TEXT_SECONDARY),
                                ft.Text(f"D: {m['domingo'] or '-'}", size=9, color=COLOR_TEXT_SECONDARY),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                        ]
                    ),
                    bgcolor=COLOR_SURFACE_WHITE,
                    padding=8,
                    border_radius=8,
                    border=ft.Border.all(1, COLOR_BORDER)
                )
            )

        return ft.ListView(controls=items, spacing=6, expand=True)

    def render_active_tab():
        if active_tab == 0:
            tab_content_area.content = build_tab_resumen_municipios()
        elif active_tab == 1:
            tab_content_area.content = build_tab_inventario_pozos()
        elif active_tab == 2:
            tab_content_area.content = build_tab_inoperativos()
        elif active_tab == 3:
            tab_content_area.content = build_tab_nuevas_perforaciones()
        elif active_tab == 4:
            tab_content_area.content = build_tab_estaciones()
        elif active_tab == 5:
            tab_content_area.content = build_tab_intervenciones()
        else:
            tab_content_area.content = build_tab_brippas_maniobras()

    def set_tab(idx: int):
        nonlocal active_tab
        active_tab = idx
        render_tab_chips()
        render_active_tab()
        page.update()

    def render_tab_chips():
        tab_chips_row.controls.clear()

        pozos_actuales = state.get_filtered_pozos_hidroven(selected_mun, selected_parr)
        inops_actuales = state.get_filtered_inoperativos_hidroven(selected_mun, selected_parr)
        kpis_perf = state.get_nuevas_perforaciones_kpis(selected_mun)

        tab_labels = [
            ("Resumen por Municipio", ft.Icons.LOCATION_CITY_ROUNDED),
            (f"Inventario de Pozos ({len(pozos_actuales)})", ft.Icons.WATER_DROP_ROUNDED),
            (f"Pozos Inoperativos ({len(inops_actuales)})", ft.Icons.REPORT_PROBLEM_ROUNDED),
            (f"Nuevas Perforaciones ({kpis_perf['total']})", ft.Icons.CONSTRUCTION_ROUNDED),
            ("Estaciones y Captación", ft.Icons.FACTORY_ROUNDED),
            ("Histórico e Intervenciones", ft.Icons.HISTORY_ROUNDED),
            ("Cuadrillas y Maniobras", ft.Icons.PEOPLE_ALT_ROUNDED),
        ]
        for i, (name, icon) in enumerate(tab_labels):
            is_act = (i == active_tab)
            tab_chips_row.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(icon, size=13, color="#FFFFFF" if is_act else COLOR_NAVY_DARK),
                        ft.Text(name, size=11, weight=ft.FontWeight.BOLD if is_act else ft.FontWeight.W_600, color="#FFFFFF" if is_act else COLOR_NAVY_DARK)
                    ], spacing=4),
                    bgcolor=COLOR_NAVY_DARK if is_act else "#E2E8F0",
                    padding=ft.Padding.symmetric(horizontal=10, vertical=6),
                    border_radius=8,
                    ink=True,
                    on_click=lambda e, ti=i: set_tab(ti)
                )
            )

    def full_refresh():
        refresh_upper_kpis()
        render_tab_chips()
        render_active_tab()
        page.update()

    # Filtros en Cascada de Municipio y Parroquia
    parroquia_dd = ft.Dropdown(
        value=selected_parr,
        options=[ft.DropdownOption(key=p, text=p) for p in state.get_parroquias_for_municipio(selected_mun)],
        dense=True,
        text_size=11,
        label="Parroquia",
        bgcolor=COLOR_SURFACE_WHITE,
        border_radius=8,
        expand=True
    )

    def on_parroquia_selected(e):
        nonlocal selected_parr
        selected_parr = e.control.value if e.control.value else "Todas las Parroquias"
        state.fiesta_agua_parroquia = selected_parr
        full_refresh()

    parroquia_dd.on_select = on_parroquia_selected
    parroquia_dd.on_text_change = on_parroquia_selected

    municipio_dd = ft.Dropdown(
        value=selected_mun,
        options=[ft.DropdownOption(key=m, text=m if m != "Todos los Municipios" else "🏛️ Todos los 14 Municipios") for m in MUNICIPALITIES_LIST],
        dense=True,
        text_size=11,
        label="Municipio",
        bgcolor=COLOR_SURFACE_WHITE,
        border_radius=8,
        expand=True
    )

    def on_municipio_selected(e):
        nonlocal selected_mun, selected_parr
        selected_mun = e.control.value if e.control.value else "Todos los Municipios"
        state.selected_municipality = selected_mun

        # 1. Actualizar dinámicamente las options del Dropdown de Parroquia:
        # Si elige un municipio específico, muestra 'Todas las Parroquias' + parroquias únicas de ese municipio.
        # Si elige 'Todos los Municipios', carga todas las parroquias únicas del estado.
        new_parrs = state.get_parroquias_for_municipio(selected_mun)
        parroquia_dd.options = [ft.DropdownOption(key=p, text=p) for p in new_parrs]

        # 2. Reiniciar automáticamente el valor a 'Todas las Parroquias'
        selected_parr = "Todas las Parroquias"
        parroquia_dd.value = "Todas las Parroquias"
        state.fiesta_agua_parroquia = "Todas las Parroquias"

        # 3. Llamar a parroquia_dd.update() antes de refrescar los datos
        parroquia_dd.update()

        # 4. Refrescar datos y tableros
        full_refresh()

    municipio_dd.on_select = on_municipio_selected
    municipio_dd.on_text_change = on_municipio_selected

    filter_bar = ft.Container(
        content=ft.Row([municipio_dd, parroquia_dd], spacing=8),
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        bgcolor=COLOR_SURFACE_WHITE,
        border_radius=8,
        border=ft.Border.all(1, COLOR_BORDER)
    )

    # Barra inferior de permisos:
    # Si Editor: muestra botón 'Importar Reporte HIDROVEN (.xlsx)'
    # Si Solo Lectura: Oculto completamente
    editor_bar = None
    if state.is_editor():
        editor_bar = ft.Container(
            content=ft.FilledButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.UPLOAD_FILE_ROUNDED, size=16),
                    ft.Text("Importar Reporte HIDROVEN (.xlsx)", size=12, weight=ft.FontWeight.BOLD)
                ], tight=True),
                style=ft.ButtonStyle(
                    bgcolor=COLOR_ELECTRIC_BLUE,
                    color="#FFFFFF",
                    padding=ft.Padding.symmetric(horizontal=14, vertical=10)
                ),
                on_click=lambda e: import_panel_obj.toggle(),
                expand=True
            ),
            padding=ft.Padding.all(8),
            bgcolor=COLOR_SURFACE_WHITE,
            border=ft.Border.only(top=ft.BorderSide(1, COLOR_BORDER))
        )
    else:
        editor_bar = ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=6,
                controls=[
                    ft.Icon(ft.Icons.LOCK_ROUNDED, size=13, color="#64748B"),
                    ft.Text("Despacho del Gobernador • Solo Lectura", size=11, color="#64748B", weight=ft.FontWeight.W_600)
                ]
            ),
            padding=ft.Padding.symmetric(vertical=8),
            bgcolor="#F8FAFC",
            border=ft.Border.only(top=ft.BorderSide(1, COLOR_BORDER))
        )

    # Inicializar vista
    refresh_upper_kpis()
    render_tab_chips()
    render_active_tab()

    # Logotipo oficial de Fiesta del Agua o respaldo limpio
    has_logo = os.path.exists(os.path.join("assets", "logo_fiesta_agua.png"))
    leading_logo = ft.Image(
        src="logo_fiesta_agua.png",
        width=48,
        height=48,
        fit="contain"
    ) if has_logo else ft.Icon(ft.Icons.WATER_DROP_ROUNDED, color=COLOR_ELECTRIC_BLUE, size=28)

    header = create_institutional_header(
        title="Fiesta del Agua",
        subtitle="Reporte Oficial HIDROVEN / Hidrosportuguesa",
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
