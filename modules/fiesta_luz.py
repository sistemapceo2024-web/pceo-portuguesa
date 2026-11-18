"""
Módulo Detallado: Plan Fiesta de la Luz
Puesto de Comando Estratégico Operacional del Estado Portuguesa (PCEO)
Consolidado General de Alumbrado Público, Transformadores y Puntos Apagados
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
from data.fiesta_luz_parser import normalize_mun_name
from data.state import AppState
from modules.excel_import_panel import ExcelImportPanel

YEARS_FIESTA_LUZ = [
    "Acumulado Total 2022-2026",
    "2026",
    "2025",
    "2024",
    "2023",
    "2022"
]

def fmt_es(val: int | float, dec: int = 0) -> str:
    """Formatea números con separador de miles en punto y decimal en coma."""
    if val is None:
        return "0"
    if dec > 0:
        return f"{float(val):,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{int(round(float(val))):,}".replace(",", ".")

def build_fiesta_luz_view(
    page: ft.Page,
    on_back_to_summary,
    on_switch_role,
    on_logout
) -> ft.Control:
    """Construye la vista interactiva oficial del Plan Fiesta de la Luz."""
    state = AppState()

    # Estado local de navegación y filtros
    active_tab = 0  # 0 a 4
    selected_mun = state.fiesta_luz_municipality if state.fiesta_luz_municipality in MUNICIPALITIES_LIST else "Todos los Municipios"
    selected_yr = state.fiesta_luz_year if state.fiesta_luz_year in YEARS_FIESTA_LUZ else YEARS_FIESTA_LUZ[0]

    # Buscadores locales
    search_mun_query = ""
    search_apagados_query = ""
    filtro_potencia_apagados = "Todos"
    search_tx_inst_query = ""
    filtro_ente_tx_inst = "Todos"
    filtro_status_fallados = "Todos"
    search_fallados_query = ""

    # Áreas dinámicas
    kpis_container = ft.Row(spacing=8)
    tab_content_area = ft.Container(expand=True)
    tab_chips_row = ft.Row(scroll=ft.ScrollMode.ADAPTIVE, spacing=6)

    # -------------------------------------------------------------
    # DIÁLOGOS Y NOTIFICACIONES (SOLO MASTER Y ANALISTA)
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

    # Diálogo de Marcar TX Fallado como Atendido / Instalado
    def open_atender_tx_dialog(tx_item: dict):
        if not state.is_editor():
            show_feedback_snack("Acceso denegado: Función reservada para roles Master y Analista.", is_error=True)
            return

        tx_id = tx_item.get("id")
        codigo = tx_item.get("codigo_1x10") or "S/C"
        mun = tx_item.get("municipio", "Estadal")
        parr = tx_item.get("parroquia", "")
        sector = tx_item.get("direccion_sector", "")
        kva = tx_item.get("capacidad_kva", 25)
        tension = tx_item.get("tension", "")
        qty = tx_item.get("cantidad", 1)

        fecha_field = ft.TextField(
            label="Fecha de Instalación",
            value=datetime.now().strftime("%Y-%m-%d"),
            hint_text="YYYY-MM-DD",
            border_color="#CBD5E1",
            focused_border_color=COLOR_STATUS_GREEN,
            height=45,
            text_size=13
        )

        ente_dropdown = ft.Dropdown(
            label="Ente Ejecutor",
            value="Corpoelec",
            options=[
                ft.dropdown.Option("Corpoelec"),
                ft.dropdown.Option("Gobernación"),
                ft.dropdown.Option("Alcaldía"),
                ft.dropdown.Option("Poder Popular")
            ],
            border_color="#CBD5E1",
            focused_border_color=COLOR_STATUS_GREEN,
            height=45,
            text_size=13
        )

        def close_dialog(e=None):
            dialog.open = False
            page.update()

        def confirm_atencion(e=None):
            fecha = fecha_field.value.strip() or datetime.now().strftime("%Y-%m-%d")
            ente = ente_dropdown.value or "Corpoelec"
            ok = state.marcar_tx_fallado_atendido(tx_id, fecha, ente)
            if ok:
                close_dialog()
                full_refresh()
                show_feedback_snack(f"Transformador {codigo} marcado como ATENDIDO ({ente}).")
            else:
                show_feedback_snack("Error al procesar la atención del transformador.", is_error=True)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, color=COLOR_STATUS_GREEN, size=22),
                ft.Text("Atender Transformador Fallado", size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
            ], spacing=8),
            content=ft.Container(
                width=420,
                content=ft.Column(
                    tight=True,
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(f"Código: {codigo}", weight=ft.FontWeight.BOLD, size=13, color=COLOR_NAVY_DARK),
                                    ft.Container(
                                        content=ft.Text(f"{kva} KVA • {qty} unidad(es)", size=11, color="#FFFFFF", weight=ft.FontWeight.BOLD),
                                        padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                        bgcolor=COLOR_STATUS_RED,
                                        border_radius=4
                                    )
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Text(f"Ubicación: {mun} • {parr}", size=11, color=COLOR_TEXT_SECONDARY),
                                ft.Text(f"Dirección: {sector}", size=10, color=COLOR_TEXT_MUTED, max_lines=2),
                                ft.Text(f"Tensión: {tension}", size=10, color=COLOR_TEXT_MUTED)
                            ], spacing=3),
                            padding=10,
                            bgcolor="#FEF2F2",
                            border_radius=8,
                            border=ft.Border.all(1, "#FECACA")
                        ),
                        fecha_field,
                        ente_dropdown
                    ]
                )
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cancelar", color=COLOR_TEXT_SECONDARY),
                    on_click=close_dialog
                ),
                ft.FilledButton(
                    content=ft.Text("Confirmar Atención", color="#FFFFFF", weight=ft.FontWeight.BOLD),
                    bgcolor=COLOR_STATUS_GREEN,
                    on_click=confirm_atencion
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        if hasattr(page, "open"):
            page.open(dialog)
        elif hasattr(page, "show_dialog"):
            page.show_dialog(dialog)
        else:
            page.dialog = dialog
            dialog.open = True
            page.update()

    # Modal para Registrar Nuevo Evento (Luminarias / TX / Punto Apagado)
    def open_nuevo_registro_modal(e=None):
        if not state.is_editor():
            show_feedback_snack("Acceso denegado: Función reservada para roles Master y Analista.", is_error=True)
            return

        muns_options = [m for m in MUNICIPALITIES_LIST if m != "Todos los Municipios"]

        tipo_dropdown = ft.Dropdown(
            label="Tipo de Registro",
            value="Luminarias",
            options=[
                ft.dropdown.Option("Luminarias"),
                ft.dropdown.Option("Transformador"),
                ft.dropdown.Option("Punto Apagado")
            ],
            border_color="#CBD5E1",
            focused_border_color=COLOR_ELECTRIC_BLUE,
            height=45,
            text_size=13
        )

        mun_dropdown = ft.Dropdown(
            label="Municipio",
            value="Guanare",
            options=[ft.dropdown.Option(m) for m in muns_options],
            border_color="#CBD5E1",
            focused_border_color=COLOR_ELECTRIC_BLUE,
            height=45,
            text_size=13
        )

        sector_field = ft.TextField(
            label="Sector / Comunidad",
            hint_text="Ej. Barrio El Placer, Calle 3",
            border_color="#CBD5E1",
            focused_border_color=COLOR_ELECTRIC_BLUE,
            height=45,
            text_size=13
        )

        cantidad_field = ft.TextField(
            label="Cantidad",
            value="1",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color="#CBD5E1",
            focused_border_color=COLOR_ELECTRIC_BLUE,
            height=45,
            text_size=13
        )

        potencia_field = ft.TextField(
            label="Potencia / Capacidad (KVA o Watts)",
            value="100W",
            hint_text="Ej. 100W, 150W, 25 KVA, 50 KVA",
            border_color="#CBD5E1",
            focused_border_color=COLOR_ELECTRIC_BLUE,
            height=45,
            text_size=13
        )

        ente_dropdown = ft.Dropdown(
            label="Ente Ejecutor",
            value="Gobernación",
            options=[
                ft.dropdown.Option("Gobernación"),
                ft.dropdown.Option("Corpoelec"),
                ft.dropdown.Option("Alcaldía"),
                ft.dropdown.Option("Poder Popular")
            ],
            border_color="#CBD5E1",
            focused_border_color=COLOR_ELECTRIC_BLUE,
            height=45,
            text_size=13
        )

        detalle_field = ft.TextField(
            label="Observaciones / Detalle",
            hint_text="Detalles del reporte o instalación",
            multiline=True,
            min_lines=2,
            border_color="#CBD5E1",
            focused_border_color=COLOR_ELECTRIC_BLUE,
            text_size=12
        )

        def close_modal(ev=None):
            modal_dlg.open = False
            page.update()

        def save_registro(ev=None):
            tipo = tipo_dropdown.value or "Luminarias"
            mun = mun_dropdown.value or "Guanare"
            sector = sector_field.value.strip() or "Sector Central"
            try:
                qty = int(cantidad_field.value.strip() or "1")
            except ValueError:
                qty = 1
            pot = potencia_field.value.strip() or "100W"
            ente = ente_dropdown.value or "Gobernación"
            det = detalle_field.value.strip() or "Registro en sala"

            state.add_fiesta_luz_registro(
                tipo=tipo,
                municipio=mun,
                sector=sector,
                cantidad=qty,
                detalle=det,
                ente=ente,
                potencia=pot
            )
            close_modal()
            full_refresh()
            show_feedback_snack(f"Nuevo registro agregado: {qty} {tipo} en {mun}.")

        modal_dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED, color=COLOR_ELECTRIC_BLUE, size=22),
                ft.Text("Registrar Luminarias / TX / Punto Apagado", size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
            ], spacing=8),
            content=ft.Container(
                width=440,
                content=ft.Column(
                    tight=True,
                    spacing=8,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        tipo_dropdown,
                        ft.Row([mun_dropdown, cantidad_field], spacing=8),
                        ft.Row([potencia_field, ente_dropdown], spacing=8),
                        sector_field,
                        detalle_field
                    ]
                )
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cancelar", color=COLOR_TEXT_SECONDARY),
                    on_click=close_modal
                ),
                ft.FilledButton(
                    content=ft.Text("Guardar Registro", color="#FFFFFF", weight=ft.FontWeight.BOLD),
                    bgcolor=COLOR_ELECTRIC_BLUE,
                    on_click=save_registro
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
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
        title="Importar Excel Fiesta de la Luz (.xlsx)",
        default_file="PLAN_FIESTA_DE_LA_LUZ_PORTUGUESA_2026.xlsx",
        on_load_callback=state.reload_fiesta_luz_excel,
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
        kpis = state.get_fiesta_luz_kpis(selected_mun, selected_yr)

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
                "Luminarias Instaladas",
                f"{fmt_es(kpis['luminarias'])}",
                "Alumbrado Activo",
                ft.Icons.LIGHTBULB_ROUNDED,
                "#F0FDF4",
                COLOR_STATUS_GREEN,
                "#BBF7D0"
            ),
            make_kpi(
                "Puntos Apagados",
                f"{fmt_es(kpis['puntos_apagados'])}",
                "Por Sustituir",
                ft.Icons.WARNING_AMBER_ROUNDED,
                "#FFFBEB",
                COLOR_STATUS_AMBER,
                "#FDE68A"
            ),
            make_kpi(
                "TX Instalados",
                f"{fmt_es(kpis['tx_instalados'])}",
                "Corpoelec + Gob.",
                ft.Icons.ELECTRICAL_SERVICES_ROUNDED,
                "#EFF6FF",
                COLOR_ELECTRIC_BLUE,
                "#BFDBFE"
            ),
            make_kpi(
                "TX Fallados",
                f"{fmt_es(kpis['tx_fallados'])}",
                f"{kpis['tx_fallados_con_codigo']} C/Cód • {kpis['tx_fallados_sin_codigo']} S/Cód",
                ft.Icons.ERROR_ROUNDED,
                "#FEF2F2",
                COLOR_STATUS_RED,
                "#FECACA"
            ),
        ]

    # -------------------------------------------------------------
    # CONSTRUCCIÓN DE LAS 5 PESTAÑAS
    # -------------------------------------------------------------

    # PESTAÑA 0: Resumen por Municipio
    def build_tab_resumen_municipio() -> ft.Control:
        data = state.fiesta_luz_data or {}
        muns_dict = data.get("municipios_resumen", {})
        lum_hist_por_m = data.get("luminarias_historico", {}).get("por_municipio", {})
        tx_hist_por_m = data.get("tx_instalados_historico", {}).get("por_municipio", {})
        is_accum = (not selected_yr or "Acumulado" in selected_yr)
        is_single_mun = bool(selected_mun and selected_mun != "Todos los Municipios")

        search_field = ft.TextField(
            hint_text="Buscar municipio...",
            prefix_icon=ft.Icons.SEARCH_ROUNDED,
            value=search_mun_query,
            height=38,
            text_size=12,
            border_color="#CBD5E1",
            focused_border_color=COLOR_ELECTRIC_BLUE,
            expand=True,
            on_change=lambda e: on_search_mun(e.control.value)
        )

        def on_search_mun(q: str):
            nonlocal search_mun_query
            search_mun_query = q.strip().lower()
            render_tab_content()

        def reset_mun_filter(e=None):
            nonlocal selected_mun
            selected_mun = "Todos los Municipios"
            mun_dropdown.value = "Todos los Municipios"
            state.set_fiesta_luz_filters(municipality="Todos los Municipios")
            full_refresh()

        # Filtrar municipios
        items = []
        for mun_name, m_info in muns_dict.items():
            # Si el usuario seleccionó un municipio específico en el selector superior
            if is_single_mun:
                if normalize_mun_name(mun_name).lower() != normalize_mun_name(selected_mun).lower():
                    continue

            if search_mun_query and search_mun_query not in mun_name.lower():
                continue

            if is_accum:
                item_data = dict(m_info)
            else:
                m_lum = lum_hist_por_m.get(mun_name, {})
                g_lum = m_lum.get("gob_alc", {}).get(selected_yr, 0)
                c_lum = m_lum.get("corpoelec", {}).get(selected_yr, 0)
                m_tx = tx_hist_por_m.get(mun_name, {}).get(selected_yr, {})
                item_data = {
                    "municipio": mun_name,
                    "luminarias": g_lum + c_lum,
                    "puntos_apagados": m_info.get("puntos_apagados", 0) if selected_yr == "2026" else 0,
                    "tx_instalados": m_tx.get("tot", 0),
                    "tx_corpoelec": m_tx.get("corp", 0),
                    "tx_gobernacion": m_tx.get("gob", 0),
                    "tx_fallados": m_info.get("tx_fallados", 0) if selected_yr == "2026" else 0,
                    "tx_fallados_con_codigo": m_info.get("tx_fallados_con_codigo", 0) if selected_yr == "2026" else 0,
                    "tx_fallados_sin_codigo": m_info.get("tx_fallados_sin_codigo", 0) if selected_yr == "2026" else 0,
                    "sectores": m_info.get("sectores", 0),
                    "beneficiarios_luminarias": m_info.get("beneficiarios_luminarias", 0)
                }
            items.append(item_data)

        # Ordenar por luminarias descendente
        items.sort(key=lambda x: x.get("luminarias", 0), reverse=True)

        # Totales calculados con base en los ítems mostrados
        tot_lum_v = sum(it.get("luminarias", 0) for it in items)
        tot_apa_v = sum(it.get("puntos_apagados", 0) for it in items)
        tot_txi_v = sum(it.get("tx_instalados", 0) for it in items)
        tot_txc_v = sum(it.get("tx_corpoelec", 0) for it in items)
        tot_txg_v = sum(it.get("tx_gobernacion", 0) for it in items)
        tot_txf_v = sum(it.get("tx_fallados", 0) for it in items)
        tot_tfc_v = sum(it.get("tx_fallados_con_codigo", 0) for it in items)
        tot_tfs_v = sum(it.get("tx_fallados_sin_codigo", 0) for it in items)
        tot_sec_v = sum(it.get("sectores", 0) for it in items)
        tot_ben_v = sum(it.get("beneficiarios_luminarias", 0) for it in items)

        # Filas de la tabla
        filas = []
        for it in items:
            filas.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.LOCATION_CITY_ROUNDED, size=14, color=COLOR_ELECTRIC_BLUE),
                                ft.Text(it["municipio"], size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                            ], spacing=6),
                            width=160
                        ),
                        ft.Container(
                            content=ft.Text(fmt_es(it.get("luminarias", 0)), size=12, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN),
                            width=110,
                            alignment=ft.Alignment(1, 0)
                        ),
                        ft.Container(
                            content=ft.Text(fmt_es(it.get("puntos_apagados", 0)), size=12, color=COLOR_STATUS_AMBER if it.get("puntos_apagados", 0) > 0 else COLOR_TEXT_MUTED),
                            width=100,
                            alignment=ft.Alignment(1, 0)
                        ),
                        ft.Container(
                            content=ft.Text(f"{fmt_es(it.get('tx_instalados', 0))} ({it.get('tx_corpoelec', 0)} / {it.get('tx_gobernacion', 0)})", size=11, color=COLOR_ELECTRIC_BLUE),
                            width=140,
                            alignment=ft.Alignment(1, 0)
                        ),
                        ft.Container(
                            content=ft.Text(
                                f"{it.get('tx_fallados', 0)} ({it.get('tx_fallados_con_codigo', 0)}/{it.get('tx_fallados_sin_codigo', 0)})",
                                size=11,
                                weight=ft.FontWeight.BOLD if it.get("tx_fallados", 0) > 0 else ft.FontWeight.NORMAL,
                                color=COLOR_STATUS_RED if it.get("tx_fallados", 0) > 0 else COLOR_TEXT_MUTED
                            ),
                            width=100,
                            alignment=ft.Alignment(1, 0)
                        ),
                        ft.Container(
                            content=ft.Text(fmt_es(it.get("sectores", 0)), size=11, color=COLOR_TEXT_PRIMARY),
                            width=80,
                            alignment=ft.Alignment(1, 0)
                        ),
                        ft.Container(
                            content=ft.Text(fmt_es(it.get("beneficiarios_luminarias", 0)), size=11, color=COLOR_TEXT_SECONDARY),
                            width=110,
                            alignment=ft.Alignment(1, 0)
                        ),
                    ], spacing=10),
                    padding=ft.Padding.symmetric(horizontal=10, vertical=8),
                    border=ft.Border(bottom=ft.BorderSide(1, "#F1F5F9")),
                    bgcolor="#FFFFFF"
                )
            )

        # Fila de totales adaptativa
        label_total = f"TOTAL {selected_mun.upper()}" if is_single_mun else "TOTAL PORTUGUESA"
        fila_total = ft.Container(
            content=ft.Row([
                ft.Container(ft.Text(label_total, size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK), width=160),
                ft.Container(ft.Text(fmt_es(tot_lum_v), size=12, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN), width=110, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text(fmt_es(tot_apa_v), size=12, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_AMBER), width=100, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text(f"{fmt_es(tot_txi_v)} ({tot_txc_v} / {tot_txg_v})", size=11, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_BLUE), width=140, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text(f"{tot_txf_v} ({tot_tfc_v}/{tot_tfs_v})", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_RED), width=100, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text(fmt_es(tot_sec_v), size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY), width=80, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text(fmt_es(tot_ben_v), size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY), width=110, alignment=ft.Alignment(1, 0)),
            ], spacing=10),
            padding=ft.Padding.symmetric(horizontal=10, vertical=10),
            bgcolor="#F8FAFC",
            border_radius=8,
            border=ft.Border.all(1, "#E2E8F0")
        )

        header_tabla = ft.Container(
            content=ft.Row([
                ft.Container(ft.Text("Municipio", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=160),
                ft.Container(ft.Text("Luminarias", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=110, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text("Puntos Apagados", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=100, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text("TX Instalados (Corp/Gob)", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=140, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text("TX Fallados (C/S)", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=100, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text("Sectores", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=80, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text("Beneficiarios", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=110, alignment=ft.Alignment(1, 0)),
            ], spacing=10),
            padding=ft.Padding.symmetric(horizontal=10, vertical=8),
            bgcolor="#F1F5F9",
            border_radius=6
        )

        # Banner informativo cuando hay filtro activo
        banner_filtro = None
        if is_single_mun:
            banner_filtro = ft.Container(
                content=ft.Row([
                    ft.Row([
                        ft.Icon(ft.Icons.FILTER_ALT_ROUNDED, size=15, color=COLOR_ELECTRIC_BLUE),
                        ft.Text(f"Filtro activo: Municipio {selected_mun}", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Container(
                            content=ft.Text(f"Corte: {selected_yr}", size=10, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                            padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                            bgcolor="#E2E8F0",
                            border_radius=12
                        )
                    ], spacing=6),
                    ft.TextButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CLEAR_ALL_ROUNDED, size=14, color=COLOR_ELECTRIC_BLUE),
                            ft.Text("Ver todos los 14 municipios", size=11, color=COLOR_ELECTRIC_BLUE, weight=ft.FontWeight.BOLD)
                        ], spacing=4),
                        on_click=reset_mun_filter
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                bgcolor="#EFF6FF",
                border_radius=8,
                border=ft.Border.all(1, "#BFDBFE")
            )

        col_controls = []
        if banner_filtro:
            col_controls.append(banner_filtro)

        col_controls.extend([
            ft.Row([
                search_field,
                ft.Text(
                    f"Municipio {selected_mun} (1 de 14)" if is_single_mun else f"{len(items)} de 14 Municipios",
                    size=11,
                    color=COLOR_TEXT_MUTED
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            header_tabla,
            ft.Container(
                content=ft.ListView(controls=filas, spacing=0),
                expand=True,
                border=ft.Border.all(1, "#E2E8F0"),
                border_radius=8
            ),
            fila_total
        ])

        return ft.Column(
            spacing=10,
            expand=True,
            controls=col_controls
        )

    # PESTAÑA 1: Alumbrado Público
    def build_tab_alumbrado_publico() -> ft.Control:
        data = state.fiesta_luz_data or {}
        lum_data = data.get("luminarias_historico", {})
        is_single_mun = bool(selected_mun and selected_mun != "Todos los Municipios")

        if is_single_mun:
            mun_lum = lum_data.get("por_municipio", {}).get(selected_mun, {})
            gob_a = mun_lum.get("gob_alc", {})
            corp_a = mun_lum.get("corpoelec", {})
            gob_sub = gob_a.get("subtotal", 0)
            corp_sub = corp_a.get("subtotal", 0)
            tot_lum = mun_lum.get("total", gob_sub + corp_sub)
            pct_gob = round((gob_sub / tot_lum) * 100, 1) if tot_lum else 0
            pct_corp = round((corp_sub / tot_lum) * 100, 1) if tot_lum else 0
            entidad_titulo = f"Municipio {selected_mun}"
        else:
            estatal = lum_data.get("estatal", {})
            gob_a = estatal.get("gob_alc", {})
            corp_a = estatal.get("corpoelec", {})
            gob_sub = gob_a.get("subtotal", 126338)
            corp_sub = corp_a.get("subtotal", 23895)
            tot_lum = estatal.get("total", 150233)
            pct_gob = estatal.get("pct_gob_alc", 84.1)
            pct_corp = estatal.get("pct_corpoelec", 15.9)
            entidad_titulo = "Total Estado Portuguesa"

        # 2 Tarjetas superiores comparativas
        card_gob = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.LOCATION_CITY_ROUNDED, size=15, color=COLOR_NAVY_DARK),
                    ft.Text(f"Gobernación y Alcaldías ({entidad_titulo})", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                ], spacing=4),
                ft.Text(f"{fmt_es(gob_sub)}", size=20, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                ft.Text(f"{pct_gob}% del Total ({entidad_titulo}) • 2022–2026", size=10, color=COLOR_TEXT_SECONDARY)
            ], spacing=3),
            padding=12,
            bgcolor="#EFF6FF",
            border_radius=10,
            border=ft.Border.all(1, "#BFDBFE"),
            expand=True
        )

        card_corp = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.BOLT_ROUNDED, size=15, color=COLOR_STATUS_GREEN),
                    ft.Text(f"Corpoelec ({entidad_titulo})", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                ], spacing=4),
                ft.Text(f"{fmt_es(corp_sub)}", size=20, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN),
                ft.Text(f"{pct_corp}% del Total ({entidad_titulo}) • 2023–2024", size=10, color=COLOR_TEXT_SECONDARY)
            ], spacing=3),
            padding=12,
            bgcolor="#F0FDF4",
            border_radius=10,
            border=ft.Border.all(1, "#BBF7D0"),
            expand=True
        )

        # Barra de distribución visual
        expand_gob = max(1, int(pct_gob * 10)) if pct_gob > 0 else 0
        expand_corp = max(1, int(pct_corp * 10)) if pct_corp > 0 else 0
        barra_controls = []
        if expand_gob > 0:
            barra_controls.append(ft.Container(bgcolor=COLOR_NAVY_DARK, height=10, expand=expand_gob, border_radius=ft.BorderRadius(4, 0, 0, 4) if expand_corp > 0 else 4))
        if expand_corp > 0:
            barra_controls.append(ft.Container(bgcolor=COLOR_STATUS_GREEN, height=10, expand=expand_corp, border_radius=ft.BorderRadius(0, 4, 4, 0) if expand_gob > 0 else 4))

        barra_dist = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(f"Distribución Institucional de Luminarias - {entidad_titulo}", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                    ft.Text(f"{fmt_es(tot_lum)} Luminarias Totales", size=11, color=COLOR_TEXT_MUTED)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row(barra_controls, spacing=2)
            ], spacing=4),
            padding=ft.Padding.symmetric(horizontal=10, vertical=8),
            bgcolor="#F8FAFC",
            border_radius=8,
            border=ft.Border.all(1, "#E2E8F0")
        )

        # Tabla de evolución anual
        años_data = [
            ("2022", gob_a.get("2022", 0), 0),
            ("2023", gob_a.get("2023", 0), corp_a.get("2023", 0)),
            ("2024", gob_a.get("2024", 0), corp_a.get("2024", 0)),
            ("2025", gob_a.get("2025", 0), 0),
            ("2026", gob_a.get("2026", 0), 0),
        ]

        filas_años = []
        for yr, g_val, c_val in años_data:
            t_val = g_val + c_val
            pct_yr = round((t_val / tot_lum) * 100, 1) if tot_lum else 0
            filas_años.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(ft.Text(f"Año {yr}", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK), width=90),
                        ft.Container(ft.Text(fmt_es(g_val), size=12, color=COLOR_TEXT_PRIMARY), width=130, alignment=ft.Alignment(1, 0)),
                        ft.Container(ft.Text(fmt_es(c_val) if c_val > 0 else "-", size=12, color=COLOR_TEXT_PRIMARY), width=130, alignment=ft.Alignment(1, 0)),
                        ft.Container(ft.Text(fmt_es(t_val), size=12, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN), width=130, alignment=ft.Alignment(1, 0)),
                        ft.Container(
                            content=ft.Row([
                                ft.ProgressBar(value=pct_yr / 100.0, color=COLOR_STATUS_GREEN, bgcolor="#E2E8F0", height=6, width=120),
                                ft.Text(f"{pct_yr}%", size=11, color=COLOR_TEXT_MUTED)
                            ], spacing=6),
                            expand=True
                        )
                    ], spacing=10),
                    padding=ft.Padding.symmetric(horizontal=10, vertical=8),
                    border=ft.Border(bottom=ft.BorderSide(1, "#F1F5F9")),
                    bgcolor="#FFFFFF"
                )
            )

        header_años = ft.Container(
            content=ft.Row([
                ft.Container(ft.Text("Periodo", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=90),
                ft.Container(ft.Text("Gob-Alcaldías", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=130, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text("Corpoelec", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=130, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text("Total Luminarias", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=130, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text("Proporción", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), expand=True),
            ], spacing=10),
            padding=ft.Padding.symmetric(horizontal=10, vertical=8),
            bgcolor="#F1F5F9",
            border_radius=6
        )

        return ft.Column(
            spacing=10,
            expand=True,
            scroll=ft.ScrollMode.ADAPTIVE,
            controls=[
                ft.Row([card_gob, card_corp], spacing=8),
                barra_dist,
                ft.Text(f"Evolución Cronológica del Alumbrado - {entidad_titulo} (2022–2026)", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                header_años,
                ft.Container(
                    content=ft.Column(controls=filas_años, spacing=0),
                    border=ft.Border.all(1, "#E2E8F0"),
                    border_radius=8
                )
            ]
        )

    # PESTAÑA 2: Puntos Apagados
    def build_tab_puntos_apagados() -> ft.Control:
        data = state.fiesta_luz_data or {}
        detalle = data.get("puntos_apagados_detalle", [])
        resumen = data.get("puntos_apagados_resumen", [])
        is_single_mun = bool(selected_mun and selected_mun != "Todos los Municipios")

        if is_single_mun:
            mun_resumen = [r for r in resumen if normalize_mun_name(r.get("municipio", "")).lower() == normalize_mun_name(selected_mun).lower()]
            tot_lum_ap = sum(r.get("luminarias", 0) for r in mun_resumen)
            tot_bom_ap = sum(r.get("bombillos", 0) for r in mun_resumen)
            tot_ref_ap = sum(r.get("reflectores", 0) for r in mun_resumen)
            tot_gen_ap = tot_lum_ap + tot_bom_ap + tot_ref_ap
        else:
            tot_lum_ap = sum(r.get("luminarias", 0) for r in resumen)
            tot_bom_ap = sum(r.get("bombillos", 0) for r in resumen)
            tot_ref_ap = sum(r.get("reflectores", 0) for r in resumen)
            tot_gen_ap = tot_lum_ap + tot_bom_ap + tot_ref_ap

        # Mini KPI cards de puntos apagados
        def mini_kpi(label: str, val: int, col: str):
            return ft.Container(
                content=ft.Column([
                    ft.Text(label, size=10, color=COLOR_TEXT_MUTED, weight=ft.FontWeight.BOLD),
                    ft.Text(fmt_es(val), size=16, weight=ft.FontWeight.BOLD, color=col)
                ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                bgcolor="#FFFFFF",
                border_radius=8,
                border=ft.Border.all(1, "#E2E8F0"),
                expand=True
            )

        label_tot_diag = f"Total {selected_mun}" if is_single_mun else "Total Diagnosticados"
        kpi_row = ft.Row([
            mini_kpi("Luminarias Apagadas", tot_lum_ap, COLOR_STATUS_AMBER),
            mini_kpi("Bombillos Apagados", tot_bom_ap, COLOR_STATUS_RED),
            mini_kpi("Reflectores Apagados", tot_ref_ap, COLOR_TEXT_MUTED),
            mini_kpi(label_tot_diag, tot_gen_ap, COLOR_NAVY_DARK)
        ], spacing=8)

        # Filtros locales
        search_field = ft.TextField(
            hint_text="Buscar por sector o comunidad...",
            prefix_icon=ft.Icons.SEARCH_ROUNDED,
            value=search_apagados_query,
            height=38,
            text_size=12,
            border_color="#CBD5E1",
            focused_border_color=COLOR_ELECTRIC_BLUE,
            expand=True,
            on_change=lambda e: on_search_apagados(e.control.value)
        )

        def on_search_apagados(q: str):
            nonlocal search_apagados_query
            search_apagados_query = q.strip().lower()
            render_tab_content()

        potencias_opts = ["Todos", "100W", "150W", "200W", "50W"]
        pot_dropdown = ft.Dropdown(
            value=filtro_potencia_apagados,
            options=[ft.dropdown.Option(p) for p in potencias_opts],
            height=38,
            text_size=12,
            border_color="#CBD5E1",
            focused_border_color=COLOR_ELECTRIC_BLUE,
            width=130,
            on_select=lambda e: on_filter_pot(e.control.value)
        )

        def on_filter_pot(p: str):
            nonlocal filtro_potencia_apagados
            filtro_potencia_apagados = p
            render_tab_content()

        # Filtrar registros
        filtrados = []
        for d in detalle:
            if is_single_mun:
                if normalize_mun_name(d.get("municipio", "")).lower() != normalize_mun_name(selected_mun).lower():
                    continue
            if filtro_potencia_apagados != "Todos":
                if filtro_potencia_apagados not in d.get("potencia", ""):
                    continue
            if search_apagados_query:
                txt = f"{d.get('sector', '')} {d.get('municipio', '')} {d.get('observacion', '')}".lower()
                if search_apagados_query not in txt:
                    continue
            filtrados.append(d)

        # Nota informativa de campo (ej. sectores de Páez pendientes de conteo)
        nota_campo = None
        has_pendientes = any("PENDIENTE" in str(x.get("observacion", "")).upper() for x in filtrados)
        if is_single_mun and tot_gen_ap == 0 and has_pendientes:
            nota_campo = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=16, color=COLOR_STATUS_AMBER),
                    ft.Column([
                        ft.Text(f"Diagnóstico de Campo en Proceso ({selected_mun})", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Text(
                            f"Los sectores de {selected_mun} se encuentran en levantamiento de campo con estatus 'PENDIENTE CONTEO' en la base oficial. Total cuantitativo preliminar: 0.",
                            size=10,
                            color=COLOR_TEXT_SECONDARY
                        )
                    ], spacing=1, expand=True)
                ], spacing=8),
                padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                bgcolor="#FFFBEB",
                border_radius=8,
                border=ft.Border.all(1, "#FDE68A")
            )

        filas = []
        for it in filtrados[:200]:  # Máximo 200 para rendimiento fluido
            filas.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(ft.Text(str(it.get("item", "")), size=11, color=COLOR_TEXT_MUTED), width=45),
                        ft.Container(ft.Text(it.get("municipio", ""), size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK), width=120),
                        ft.Container(ft.Text(it.get("sector", ""), size=11, color=COLOR_TEXT_PRIMARY), expand=True),
                        ft.Container(
                            ft.Text(f"{it.get('cantidad', 0)}", size=12, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_AMBER if it.get("cantidad", 0) > 0 else COLOR_TEXT_MUTED),
                            width=70,
                            alignment=ft.Alignment(1, 0)
                        ),
                        ft.Container(
                            content=ft.Container(
                                content=ft.Text(it.get("potencia", "-"), size=10, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                bgcolor="#F1F5F9",
                                border_radius=4
                            ),
                            width=90,
                            alignment=ft.Alignment(0, 0)
                        ),
                        ft.Container(ft.Text(it.get("observacion", "-"), size=10, color=COLOR_TEXT_MUTED), width=130)
                    ], spacing=8),
                    padding=ft.Padding.symmetric(horizontal=10, vertical=7),
                    border=ft.Border(bottom=ft.BorderSide(1, "#F1F5F9")),
                    bgcolor="#FFFFFF"
                )
            )

        header_tabla = ft.Container(
            content=ft.Row([
                ft.Container(ft.Text("N°", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=45),
                ft.Container(ft.Text("Municipio", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=120),
                ft.Container(ft.Text("Sector / Comunidad", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), expand=True),
                ft.Container(ft.Text("Apagados", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=70, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text("Potencia", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=90, alignment=ft.Alignment(0, 0)),
                ft.Container(ft.Text("Observación", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=130),
            ], spacing=8),
            padding=ft.Padding.symmetric(horizontal=10, vertical=8),
            bgcolor="#F1F5F9",
            border_radius=6
        )

        puntos_controls = [kpi_row]
        if nota_campo:
            puntos_controls.append(nota_campo)
        puntos_controls.extend([
            ft.Row([
                search_field,
                pot_dropdown,
                ft.Text(f"{len(filtrados)} sectores", size=11, color=COLOR_TEXT_MUTED)
            ], spacing=8),
            header_tabla,
            ft.Container(
                content=ft.ListView(controls=filas, spacing=0),
                expand=True,
                border=ft.Border.all(1, "#E2E8F0"),
                border_radius=8
            )
        ])

        return ft.Column(
            spacing=10,
            expand=True,
            controls=puntos_controls
        )

    # PESTAÑA 3: Transformadores Instalados
    def build_tab_tx_instalados() -> ft.Control:
        data = state.fiesta_luz_data or {}
        tx_hist = data.get("tx_instalados_historico", {})
        capacidades = data.get("tx_capacidades_estatal", {})
        detalle_2026 = data.get("tx_instalados_2026_detalle", [])
        is_single_mun = bool(selected_mun and selected_mun != "Todos los Municipios")

        # Filtrar bitácora 2026 primero
        filtrados_2026 = []
        for it in detalle_2026:
            if is_single_mun:
                if normalize_mun_name(it.get("municipio", "")).lower() != normalize_mun_name(selected_mun).lower():
                    continue
            if filtro_ente_tx_inst != "Todos":
                if filtro_ente_tx_inst.lower() not in it.get("ente_categoria", "").lower() and filtro_ente_tx_inst.lower() not in it.get("ente_ejecutor", "").lower():
                    continue
            if search_tx_inst_query:
                txt = f"{it.get('direccion_sector', '')} {it.get('municipio', '')} {it.get('codigo_serial', '')} {it.get('ente_ejecutor', '')}".lower()
                if search_tx_inst_query not in txt:
                    continue
            filtrados_2026.append(it)

        # Tarjetas de KVA o Resumen Institucional
        cap_cards = []
        if is_single_mun:
            mun_tx_h = tx_hist.get("por_municipio", {}).get(selected_mun, {})
            tot_mun = mun_tx_h.get("total", len(filtrados_2026))
            corp_mun = mun_tx_h.get("total_corpoelec", 0)
            gob_mun = mun_tx_h.get("total_gobernacion", 0)
            ben_mun = mun_tx_h.get("beneficiarios", 0)
            tx_2026_count = mun_tx_h.get("2026", {}).get("tot", len(filtrados_2026))

            def tx_mini_card(title: str, val: str, sub: str, col: str):
                return ft.Container(
                    content=ft.Column([
                        ft.Text(title, size=10, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Text(val, size=15, weight=ft.FontWeight.BOLD, color=col),
                        ft.Text(sub, size=9, color=COLOR_TEXT_MUTED)
                    ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                    bgcolor="#F8FAFC",
                    border_radius=8,
                    border=ft.Border.all(1, "#E2E8F0"),
                    expand=True
                )

            cap_cards = [
                tx_mini_card(f"Total {selected_mun}", fmt_es(tot_mun), "Acumulado 2022-2026", COLOR_ELECTRIC_BLUE),
                tx_mini_card("Corpoelec", fmt_es(corp_mun), f"{round(corp_mun/tot_mun*100, 1) if tot_mun else 0}% del total", COLOR_STATUS_GREEN),
                tx_mini_card("Gobernación", fmt_es(gob_mun), f"{round(gob_mun/tot_mun*100, 1) if tot_mun else 0}% del total", COLOR_NAVY_DARK),
                tx_mini_card("Instalados 2026", fmt_es(tx_2026_count), f"{len(filtrados_2026)} en bitácora", COLOR_STATUS_AMBER),
                tx_mini_card("Beneficiarios", fmt_es(ben_mun), "Población atendida", COLOR_TEXT_PRIMARY),
            ]
        else:
            tot_tx_cap = sum(capacidades.values()) or 3444
            for kva_lbl, kva_val in capacidades.items():
                pct = round((kva_val / tot_tx_cap) * 100, 1)
                cap_cards.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(kva_lbl, size=10, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                            ft.Text(fmt_es(kva_val), size=14, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_BLUE),
                            ft.Text(f"{pct}%", size=9, color=COLOR_TEXT_MUTED)
                        ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                        bgcolor="#F8FAFC",
                        border_radius=6,
                        border=ft.Border.all(1, "#E2E8F0"),
                        expand=True
                    )
                )

        # Buscador y filtro para bitácora 2026
        search_field = ft.TextField(
            hint_text="Buscar en bitácora 2026 (sector, dirección, código)...",
            prefix_icon=ft.Icons.SEARCH_ROUNDED,
            value=search_tx_inst_query,
            height=38,
            text_size=12,
            border_color="#CBD5E1",
            focused_border_color=COLOR_ELECTRIC_BLUE,
            expand=True,
            on_change=lambda e: on_search_tx(e.control.value)
        )

        def on_search_tx(q: str):
            nonlocal search_tx_inst_query
            search_tx_inst_query = q.strip().lower()
            render_tab_content()

        ente_dropdown = ft.Dropdown(
            value=filtro_ente_tx_inst,
            options=[ft.dropdown.Option("Todos"), ft.dropdown.Option("Corpoelec"), ft.dropdown.Option("Gobernación"), ft.dropdown.Option("Alcaldía")],
            height=38,
            text_size=12,
            border_color="#CBD5E1",
            focused_border_color=COLOR_ELECTRIC_BLUE,
            width=130,
            on_select=lambda e: on_filter_ente_tx(e.control.value)
        )

        def on_filter_ente_tx(val: str):
            nonlocal filtro_ente_tx_inst
            filtro_ente_tx_inst = val
            render_tab_content()

        filas_2026 = []
        for it in filtrados_2026[:200]:
            filas_2026.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(ft.Text(it.get("fecha", "-"), size=11, color=COLOR_TEXT_MUTED), width=85),
                        ft.Container(ft.Text(it.get("municipio", "-"), size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK), width=110),
                        ft.Container(ft.Text(it.get("direccion_sector", "-"), size=11, color=COLOR_TEXT_PRIMARY), expand=True),
                        ft.Container(
                            ft.Text(f"{it.get('capacidad_kva', '-')} KVA", size=11, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_BLUE),
                            width=75,
                            alignment=ft.Alignment(0, 0)
                        ),
                        ft.Container(
                            content=ft.Container(
                                content=ft.Text(it.get("ente_categoria", "Corpoelec"), size=10, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                bgcolor=COLOR_ELECTRIC_BLUE if "Corp" in it.get("ente_categoria", "") else COLOR_NAVY_DARK,
                                border_radius=4
                            ),
                            width=95,
                            alignment=ft.Alignment(0, 0)
                        ),
                        ft.Container(ft.Text(it.get("codigo_serial", "-"), size=10, color=COLOR_TEXT_MUTED), width=100)
                    ], spacing=8),
                    padding=ft.Padding.symmetric(horizontal=10, vertical=7),
                    border=ft.Border(bottom=ft.BorderSide(1, "#F1F5F9")),
                    bgcolor="#FFFFFF"
                )
            )

        header_2026 = ft.Container(
            content=ft.Row([
                ft.Container(ft.Text("Fecha", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=85),
                ft.Container(ft.Text("Municipio", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=110),
                ft.Container(ft.Text("Dirección / Sector", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), expand=True),
                ft.Container(ft.Text("Capacidad", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=75, alignment=ft.Alignment(0, 0)),
                ft.Container(ft.Text("Ente", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=95, alignment=ft.Alignment(0, 0)),
                ft.Container(ft.Text("1x10 / Serial", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=100),
            ], spacing=8),
            padding=ft.Padding.symmetric(horizontal=10, vertical=8),
            bgcolor="#F1F5F9",
            border_radius=6
        )

        title_tx_top = f"Consolidado Operativo de Transformadores - {selected_mun}" if is_single_mun else "Distribución Acumulada por Capacidad KVA (2022–2026)"

        return ft.Column(
            spacing=10,
            expand=True,
            controls=[
                ft.Text(title_tx_top, size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                ft.Row(controls=cap_cards, spacing=6),
                ft.Row([
                    search_field,
                    ente_dropdown,
                    ft.Text(f"{len(filtrados_2026)} registros en bitácora 2026", size=11, color=COLOR_TEXT_MUTED)
                ], spacing=8),
                header_2026,
                ft.Container(
                    content=ft.ListView(controls=filas_2026, spacing=0),
                    expand=True,
                    border=ft.Border.all(1, "#E2E8F0"),
                    border_radius=8
                )
            ]
        )

    # PESTAÑA 4: Transformadores Fallados Críticos (75)
    def build_tab_tx_fallados() -> ft.Control:
        data = state.fiesta_luz_data or {}
        fallados = data.get("tx_fallados_detalle", [])

        # Subfiltros
        opts_status = ["Todos", "CON CODIGO", "SIN CODIGO", "Pendientes", "Atendidos"]
        status_chips = []
        for st_name in opts_status:
            is_active = (filtro_status_fallados == st_name)
            status_chips.append(
                ft.Container(
                    content=ft.Text(
                        st_name,
                        size=11,
                        weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
                        color="#FFFFFF" if is_active else COLOR_NAVY_DARK
                    ),
                    padding=ft.Padding.symmetric(horizontal=10, vertical=5),
                    bgcolor=COLOR_STATUS_RED if (is_active and st_name != "Atendidos") else (COLOR_STATUS_GREEN if is_active else "#F1F5F9"),
                    border_radius=20,
                    ink=True,
                    on_click=lambda e, s=st_name: on_filter_status_fallados(s)
                )
            )

        def on_filter_status_fallados(s: str):
            nonlocal filtro_status_fallados
            filtro_status_fallados = s
            render_tab_content()

        search_field = ft.TextField(
            hint_text="Buscar por sector, dirección, código o reportante...",
            prefix_icon=ft.Icons.SEARCH_ROUNDED,
            value=search_fallados_query,
            height=38,
            text_size=12,
            border_color="#CBD5E1",
            focused_border_color=COLOR_STATUS_RED,
            expand=True,
            on_change=lambda e: on_search_fallados(e.control.value)
        )

        def on_search_fallados(q: str):
            nonlocal search_fallados_query
            search_fallados_query = q.strip().lower()
            render_tab_content()

        is_single_mun = bool(selected_mun and selected_mun != "Todos los Municipios")

        # Filtrar tarjetas
        filtrados = []
        for it in fallados:
            if is_single_mun:
                if normalize_mun_name(it.get("municipio", "")).lower() != normalize_mun_name(selected_mun).lower():
                    continue
            if filtro_status_fallados == "CON CODIGO" and it.get("estatus_codigo") != "CON CODIGO":
                continue
            if filtro_status_fallados == "SIN CODIGO" and it.get("estatus_codigo") != "SIN CODIGO":
                continue
            if filtro_status_fallados == "Pendientes" and it.get("atendido"):
                continue
            if filtro_status_fallados == "Atendidos" and not it.get("atendido"):
                continue
            if search_fallados_query:
                txt = f"{it.get('codigo_1x10', '')} {it.get('direccion_sector', '')} {it.get('municipio', '')} {it.get('usuario_reportante', '')} {it.get('telefono', '')}".lower()
                if search_fallados_query not in txt:
                    continue
            filtrados.append(it)

        # Construcción de tarjetas o estado positivo sin fallas
        cards = []
        if len(filtrados) == 0:
            msg_mun = f"en el Municipio {selected_mun}" if is_single_mun else "con los criterios actuales"
            sub_mun = f"El Municipio {selected_mun} no registra transformadores fallados críticos pendientes en el corte oficial 2026." if is_single_mun else "No se encontraron casos de transformadores fallados pendientes para este filtro."
            cards.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, size=46, color=COLOR_STATUS_GREEN),
                        ft.Text(f"Sin Reportes Críticos {msg_mun}", size=14, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Text(sub_mun, size=11, color=COLOR_TEXT_SECONDARY, text_align=ft.TextAlign.CENTER)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
                    padding=30,
                    alignment=ft.Alignment(0, 0),
                    bgcolor="#F0FDF4",
                    border_radius=10,
                    border=ft.Border.all(1, "#BBF7D0")
                )
            )
        else:
            for it in filtrados:
                is_atendido = it.get("atendido", False)
                cod = it.get("codigo_1x10") or "S/C"
                has_cod = (it.get("estatus_codigo") == "CON CODIGO")

                # Botón de acción para Master y Analista
                accion_btn = None
                if state.is_editor():
                    if not is_atendido:
                        accion_btn = ft.FilledButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, size=14, color="#FFFFFF"),
                                ft.Text("Marcar Atendido", size=11, color="#FFFFFF", weight=ft.FontWeight.BOLD)
                            ], spacing=4),
                            bgcolor=COLOR_STATUS_GREEN,
                            height=30,
                            on_click=lambda e, item=it: open_atender_tx_dialog(item)
                        )
                    else:
                        accion_btn = ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, size=14, color=COLOR_STATUS_GREEN),
                                ft.Text(f"Atendido ({it.get('ente_atendio', 'Corpoelec')})", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN)
                            ], spacing=4),
                            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                            bgcolor="#F0FDF4",
                            border_radius=6,
                            border=ft.Border.all(1, "#BBF7D0")
                        )

                card = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Row([
                                ft.Icon(ft.Icons.ERROR_ROUNDED if not is_atendido else ft.Icons.CHECK_CIRCLE_ROUNDED, size=16, color=COLOR_STATUS_RED if not is_atendido else COLOR_STATUS_GREEN),
                                ft.Text(f"Caso 1x10: {cod}", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                ft.Container(
                                    content=ft.Text("CON CÓDIGO" if has_cod else "SIN CÓDIGO", size=9, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                    padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                    bgcolor=COLOR_NAVY_DARK if has_cod else "#64748B",
                                    border_radius=4
                                )
                            ], spacing=6),
                            ft.Container(
                                content=ft.Text("RESUELTO" if is_atendido else "CRÍTICO", size=10, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                bgcolor=COLOR_STATUS_GREEN if is_atendido else COLOR_STATUS_RED,
                                border_radius=4
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Divider(height=1, color="#FEE2E2" if not is_atendido else "#DCFCE7"),
                        ft.Row([
                            ft.Column([
                                ft.Text(f"Ubicación: {it.get('municipio')} • Parroquia {it.get('parroquia')}", size=11, weight=ft.FontWeight.W_500, color=COLOR_NAVY_DARK),
                                ft.Text(f"Dirección: {it.get('direccion_sector')}", size=10, color=COLOR_TEXT_SECONDARY, max_lines=2),
                                ft.Text(f"Reportado: {it.get('fecha_reporte')}", size=9, color=COLOR_TEXT_MUTED)
                            ], spacing=2, expand=True),
                            ft.Column([
                                ft.Container(
                                    content=ft.Text(f"{it.get('capacidad_kva')} KVA • {it.get('cantidad')} Unidad(es)", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_RED if not is_atendido else COLOR_STATUS_GREEN),
                                    padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                    bgcolor="#FFFFFF",
                                    border_radius=4,
                                    border=ft.Border.all(1, "#FECACA" if not is_atendido else "#BBF7D0")
                                ),
                                ft.Text(f"Tensión: {it.get('tension', '-')}", size=9, color=COLOR_TEXT_MUTED)
                            ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.END)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([
                            ft.Row([
                                ft.Icon(ft.Icons.PERSON_ROUNDED, size=13, color=COLOR_TEXT_MUTED),
                                ft.Text(f"{it.get('usuario_reportante') or 'Comunidad'}", size=10, color=COLOR_TEXT_MUTED),
                                ft.Icon(ft.Icons.PHONE_ROUNDED, size=12, color=COLOR_TEXT_MUTED),
                                ft.Text(f"{it.get('telefono') or 'No registrado'}", size=10, color=COLOR_TEXT_MUTED)
                            ], spacing=4),
                            accion_btn if accion_btn else ft.Container()
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ], spacing=6),
                    padding=12,
                    bgcolor="#FEF2F2" if not is_atendido else "#F0FDF4",
                    border_radius=10,
                    border=ft.Border.all(1, "#FECACA" if not is_atendido else "#BBF7D0")
                )
                cards.append(card)

        return ft.Column(
            spacing=10,
            expand=True,
            controls=[
                ft.Row([
                    ft.Row(controls=status_chips, spacing=6),
                    ft.Text(f"{len(filtrados)} transformadores", size=11, color=COLOR_TEXT_MUTED)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                search_field,
                ft.Container(
                    content=ft.ListView(controls=cards, spacing=8),
                    expand=True
                )
            ]
        )

    # -------------------------------------------------------------
    # CONTROLADOR DE PESTAÑAS Y NAVEGACIÓN
    # -------------------------------------------------------------
    def get_tab_labels():
        kpis = state.get_fiesta_luz_kpis(selected_mun, selected_yr)
        is_single_mun = bool(selected_mun and selected_mun != "Todos los Municipios")
        mun_tag = selected_mun if is_single_mun else "14"
        return [
            (f"Resumen ({mun_tag})", ft.Icons.LOCATION_CITY_ROUNDED),
            (f"Alumbrado ({fmt_es(kpis['luminarias'])})", ft.Icons.LIGHTBULB_ROUNDED),
            (f"Puntos Apagados ({fmt_es(kpis['puntos_apagados'])})", ft.Icons.WARNING_AMBER_ROUNDED),
            (f"TX Instalados ({fmt_es(kpis['tx_instalados'])})", ft.Icons.ELECTRICAL_SERVICES_ROUNDED),
            (f"TX Fallados ({fmt_es(kpis['tx_fallados'])})", ft.Icons.ERROR_ROUNDED),
        ]

    def render_tab_chips():
        tab_chips_row.controls.clear()
        for idx, (label, icon_d) in enumerate(get_tab_labels()):
            is_active = (active_tab == idx)
            tab_chips_row.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(icon_d, size=14, color="#FFFFFF" if is_active else COLOR_NAVY_DARK),
                        ft.Text(
                            label,
                            size=12,
                            weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
                            color="#FFFFFF" if is_active else COLOR_NAVY_DARK
                        )
                    ], spacing=6),
                    padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                    bgcolor=COLOR_NAVY_DARK if is_active else "#F1F5F9",
                    border_radius=20,
                    ink=True,
                    on_click=lambda e, ti=idx: set_tab(ti)
                )
            )

    def set_tab(ti: int):
        nonlocal active_tab
        active_tab = ti
        render_tab_chips()
        render_tab_content()
        page.update()

    def render_tab_content():
        if active_tab == 0:
            tab_content_area.content = build_tab_resumen_municipio()
        elif active_tab == 1:
            tab_content_area.content = build_tab_alumbrado_publico()
        elif active_tab == 2:
            tab_content_area.content = build_tab_puntos_apagados()
        elif active_tab == 3:
            tab_content_area.content = build_tab_tx_instalados()
        elif active_tab == 4:
            tab_content_area.content = build_tab_tx_fallados()
        page.update()

    def full_refresh():
        refresh_upper_kpis()
        render_tab_chips()
        render_tab_content()
        page.update()

    # -------------------------------------------------------------
    # BARRA SUPERIOR DE FILTROS Y ACCIONES
    # -------------------------------------------------------------
    mun_dropdown = ft.Dropdown(
        value=selected_mun,
        options=[ft.dropdown.Option(m) for m in MUNICIPALITIES_LIST],
        height=38,
        text_size=12,
        border_color="#CBD5E1",
        focused_border_color=COLOR_ELECTRIC_BLUE,
        width=190,
        on_select=lambda e: on_select_mun(e.control.value)
    )

    def on_select_mun(m: str):
        nonlocal selected_mun
        selected_mun = m
        state.set_fiesta_luz_filters(municipality=m)
        full_refresh()

    if selected_yr not in YEARS_FIESTA_LUZ:
        selected_yr = YEARS_FIESTA_LUZ[0]

    year_dropdown = ft.Dropdown(
        value=selected_yr,
        options=[ft.dropdown.Option(y) for y in YEARS_FIESTA_LUZ],
        height=38,
        text_size=12,
        border_color="#CBD5E1",
        focused_border_color=COLOR_ELECTRIC_BLUE,
        width=210,
        on_select=lambda e: on_select_year(e.control.value)
    )

    def on_select_year(y: str):
        nonlocal selected_yr
        selected_yr = y
        state.set_fiesta_luz_filters(year=y)
        full_refresh()

    # Botones protegidos por rol (Master y Analista)
    editor_actions = []
    if state.is_editor():
        btn_nuevo = ft.FilledButton(
            content=ft.Row([
                ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED, size=15, color="#FFFFFF"),
                ft.Text("+ Registrar Luminarias / TX", size=11, color="#FFFFFF", weight=ft.FontWeight.BOLD)
            ], spacing=4),
            bgcolor=COLOR_STATUS_GREEN,
            height=36,
            on_click=open_nuevo_registro_modal
        )

        btn_import = ft.OutlinedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.UPLOAD_FILE_ROUNDED, size=15, color=COLOR_ELECTRIC_BLUE),
                ft.Text("Importar Excel (.xlsx)", size=11, color=COLOR_ELECTRIC_BLUE, weight=ft.FontWeight.BOLD)
            ], spacing=4),
            height=36,
            on_click=import_excel_dialog
        )
        editor_actions.extend([btn_nuevo, btn_import])

    filter_bar = ft.Container(
        content=ft.Row([
            ft.Row([
                ft.Text("Municipio:", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                mun_dropdown,
                ft.Text("Año / Corte:", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                year_dropdown,
            ], spacing=8),
            ft.Row(editor_actions, spacing=6)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.Padding.symmetric(horizontal=12, vertical=8),
        bgcolor="#FFFFFF",
        border_radius=10,
        border=ft.Border.all(1, "#E2E8F0")
    )

    # -------------------------------------------------------------
    # LOGO INSTITUCIONAL Y ENCABEZADO
    # -------------------------------------------------------------
    logo_path = "logo_fiesta_luz.png" if os.path.exists("assets/logo_fiesta_luz.png") else None
    leading_logo = (
        ft.Image(src=logo_path, width=42, height=42, fit="contain")
        if logo_path else ft.Icon(ft.Icons.LIGHTBULB_ROUNDED, size=28, color=COLOR_ELECTRIC_BLUE)
    )
    header_box = create_institutional_header(
        title="Plan Fiesta de la Luz",
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
