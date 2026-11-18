"""
Módulo Detallado: Plan Tramos Caídos
Secretaría Superior de Operaciones Generales - Gobernación del Estado Portuguesa
Carga Oficial: TRAMOS PORTUGUESA ACT2026-8.xlsx
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
from components.semaphore import create_semaphore_badge, create_status_dot
from data.water_data import MUNICIPALITIES_LIST
from data.state import AppState, normalize_name
from modules.excel_import_panel import ExcelImportPanel

def format_num_es(val: int | float, decimals: int = 0) -> str:
    if val is None:
        return "0"
    if decimals > 0:
        formatted = f"{float(val):,.{decimals}f}"
        return formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        return f"{int(round(float(val))):,}".replace(",", ".")

def build_tramos_caidos_view(
    page: ft.Page,
    on_back_to_summary,
    on_switch_role,
    on_logout
) -> ft.Control:
    """Construye la vista interactiva completa del Plan Tramos Caídos."""
    state = AppState()

    active_tab_index = 0
    kpis_row = ft.Row(spacing=8)
    tab_content_area = ft.Container(expand=True)
    tab_chips_row = ft.Row(scroll=ft.ScrollMode.ADAPTIVE, spacing=6)

    # Filtros de Inventario (Pestaña 1)
    inv_filter_estatus = "Todos"
    inv_filter_diametro = "Todos"
    inv_filter_tipo = "Todos"
    inv_search_query = ""

    import_panel_obj = ExcelImportPanel(
        page=page,
        title="Importar Excel Tramos Caídos (.xlsx)",
        default_file="TRAMOS PORTUGUESA ACT2026-8.xlsx",
        on_load_callback=state.reload_tramos_excel,
        on_success_callback=lambda: full_refresh(),
        accent_color=COLOR_ELECTRIC_BLUE
    )

    # Diálogo de Ficha Técnica Detallada
    def open_tramo_detail_dialog(tramo: dict):
        is_ejec = tramo.get("estatus") == "Ejecutado"
        status_bg = "#DCFCE7" if is_ejec else "#FEE2E2"
        status_color = COLOR_STATUS_GREEN if is_ejec else COLOR_STATUS_RED
        status_text = "EJECUTADO" if is_ejec else "POR EJECUTAR"

        details_rows = [
            ft.Row([
                ft.Text("Municipio:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=110),
                ft.Text(tramo.get("municipio", "-"), size=12, weight=ft.FontWeight.W_600, color=COLOR_NAVY_DARK, expand=True)
            ]),
            ft.Row([
                ft.Text("Parroquia:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=110),
                ft.Text(tramo.get("parroquia", "-"), size=12, color=COLOR_TEXT_PRIMARY, expand=True)
            ]),
            ft.Row([
                ft.Text("Sector:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=110),
                ft.Text(tramo.get("sector", "-"), size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK, expand=True)
            ]),
            ft.Row([
                ft.Text("Dirección / Tramo:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=110),
                ft.Text(tramo.get("direccion", "Sin dirección especificada"), size=11, color=COLOR_TEXT_PRIMARY, expand=True)
            ]),
            ft.Divider(height=1, color=COLOR_BORDER),
            ft.Row([
                ft.Text("Diámetro:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=110),
                ft.Container(
                    content=ft.Text(tramo.get("diametro", '-'), size=11, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                    bgcolor=COLOR_NAVY_DARK,
                    padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                    border_radius=6
                )
            ]),
            ft.Row([
                ft.Text("Longitud:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=110),
                ft.Text(f"{format_num_es(tramo.get('longitud_m', 0), 2)} metros", size=12, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_BLUE)
            ]),
            ft.Row([
                ft.Text("Tipo Colector:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=110),
                ft.Text(tramo.get("tipo_colector", "SECUNDARIO"), size=12, color=COLOR_TEXT_PRIMARY)
            ]),
            ft.Row([
                ft.Text("Beneficiarios:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=110),
                ft.Text(f"{format_num_es(tramo.get('beneficiarios', 0))} hab.", size=12, color=COLOR_TEXT_PRIMARY)
            ]),
            ft.Divider(height=1, color=COLOR_BORDER),
            ft.Row([
                ft.Text("Fecha Ejecución:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=110),
                ft.Text(tramo.get("fecha_ejecucion") or "Pendiente por programar", size=12, color=COLOR_STATUS_GREEN if is_ejec else COLOR_STATUS_AMBER)
            ]),
            ft.Row([
                ft.Text("Ente Ejecutor:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=110),
                ft.Text(tramo.get("ente_ejecutor") or "Por Definir", size=12, weight=ft.FontWeight.W_600, color=COLOR_NAVY_DARK)
            ])
        ]

        actions_list = [
            ft.TextButton(content=ft.Text("Cerrar"), on_click=lambda e: page.pop_dialog() or page.update())
        ]

        if state.is_editor():
            actions_list.append(
                ft.FilledButton(
                    content=ft.Text("Cambiar Estatus / Marcar Ejecución"),
                    icon=ft.Icons.EDIT_NOTE_ROUNDED,
                    style=ft.ButtonStyle(bgcolor=COLOR_ELECTRIC_BLUE, color="#FFFFFF"),
                    on_click=lambda e: (page.pop_dialog(), page.update(), open_status_change_dialog(tramo))
                )
            )

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.ENGINEERING_ROUNDED, color=COLOR_ELECTRIC_BLUE),
                            ft.Text(f"Ficha Técnica #{tramo.get('item', tramo.get('id', '-'))}", size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                        ]
                    ),
                    ft.Container(
                        content=ft.Text(status_text, size=11, weight=ft.FontWeight.BOLD, color=status_color),
                        bgcolor=status_bg,
                        padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                        border_radius=6
                    )
                ]
            ),
            content=ft.Container(
                content=ft.Column(
                    tight=True,
                    spacing=8,
                    controls=details_rows
                ),
                width=420
            ),
            actions=actions_list,
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=12)
        )
        page.show_dialog(dialog)
        page.update()

    # Modal para cambiar estatus (Editor)
    def open_status_change_dialog(tramo: dict):
        current_status = tramo.get("estatus", "Por Ejecutar")
        radio_status = ft.RadioGroup(
            content=ft.Row([
                ft.Radio(value="Ejecutado", label="Ejecutado (Verde)"),
                ft.Radio(value="Por Ejecutar", label="Por Ejecutar (Rojo)"),
            ]),
            value=current_status
        )

        date_field = ft.TextField(
            label="Fecha de Ejecución",
            value=tramo.get("fecha_ejecucion") or datetime.now().strftime("%Y-%m-%d"),
            dense=True,
            text_size=12
        )

        ente_opts = [
            ft.DropdownOption("Alcaldía", "Alcaldía"),
            ft.DropdownOption("Hidrosportuguesa", "Hidrosportuguesa"),
            ft.DropdownOption("MinAguas", "MinAguas"),
            ft.DropdownOption("Gobernación", "Gobernación"),
            ft.DropdownOption("Hidroven", "Hidroven"),
        ]
        ente_dd = ft.Dropdown(
            label="Ente Ejecutor",
            value=tramo.get("ente_categoria") or "Hidrosportuguesa",
            options=ente_opts,
            dense=True
        )

        def save_status(e):
            new_st = radio_status.value
            dt_val = (date_field.value or "").strip()
            ent_val = ente_dd.value or "Hidrosportuguesa"
            state.update_tramo_status(
                tramo_id=tramo["id"],
                nuevo_estatus=new_st,
                fecha_ejecucion=dt_val,
                ente_ejecutor=ent_val
            )
            page.pop_dialog()
            full_refresh()
            page.show_dialog(
                ft.SnackBar(
                    content=ft.Text(f"Tramo #{tramo.get('item', tramo['id'])} actualizado a '{new_st}'.", color="#FFFFFF"),
                    bgcolor=COLOR_NAVY_DARK
                )
            )
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.UPDATE_ROUNDED, color=COLOR_ELECTRIC_BLUE),
                ft.Text("Actualizar Estatus de Tramo", size=15, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
            ]),
            content=ft.Container(
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    controls=[
                        ft.Text(f"Sector: {tramo.get('sector', '-')}", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Text(f"Diámetro: {tramo.get('diametro', '-')} | Longitud: {tramo.get('longitud_m', 0)} m", size=11, color=COLOR_TEXT_SECONDARY),
                        ft.Divider(height=1, color=COLOR_BORDER),
                        ft.Text("Seleccione el nuevo estatus:", size=12, weight=ft.FontWeight.BOLD),
                        radio_status,
                        date_field,
                        ente_dd
                    ]
                ),
                width=380
            ),
            actions=[
                ft.TextButton(content=ft.Text("Cancelar"), on_click=lambda e: page.pop_dialog() or page.update()),
                ft.FilledButton(
                    content=ft.Text("Guardar Cambio"),
                    style=ft.ButtonStyle(bgcolor=COLOR_ELECTRIC_BLUE, color="#FFFFFF"),
                    on_click=save_status
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=12)
        )
        page.show_dialog(dialog)
        page.update()

    # Modal para registrar nuevo tramo (Editor)
    def open_add_tramo_dialog():
        mun_opts = [ft.DropdownOption(m, m) for m in MUNICIPALITIES_LIST if m != "Todos los Municipios"]
        mun_dd = ft.Dropdown(value="GUANARE", options=mun_opts, label="Municipio", dense=True)

        parr_field = ft.TextField(label="Parroquia", hint_text="Ej: Guanare", dense=True)
        sector_field = ft.TextField(label="Sector / Comunidad", hint_text="Ej: Barrio San José", dense=True)
        dir_field = ft.TextField(label="Dirección / Tramo", hint_text="Ej: Calle 3 entre carreras 5 y 6", dense=True)

        diam_opts = [
            ft.DropdownOption('6"', '6"'),
            ft.DropdownOption('8"', '8"'),
            ft.DropdownOption('10"', '10"'),
            ft.DropdownOption('12"', '12"'),
            ft.DropdownOption('15"', '15"'),
            ft.DropdownOption('16"', '16"'),
            ft.DropdownOption('18"', '18"'),
            ft.DropdownOption('20"', '20"'),
            ft.DropdownOption('24"', '24"'),
            ft.DropdownOption('30"', '30"'),
            ft.DropdownOption('36"', '36"'),
            ft.DropdownOption('42"', '42"')
        ]
        diam_dd = ft.Dropdown(value='10"', options=diam_opts, label="Diámetro de Tubería", dense=True)

        long_field = ft.TextField(label="Longitud (Metros)", value="60", dense=True, keyboard_type=ft.KeyboardType.NUMBER)
        tipo_dd = ft.Dropdown(
            label="Tipo de Colector",
            value="SECUNDARIO",
            options=[ft.DropdownOption("SECUNDARIO", "Secundario"), ft.DropdownOption("PRINCIPAL", "Principal")],
            dense=True
        )
        ben_field = ft.TextField(label="Beneficiarios Estimados", value="450", dense=True, keyboard_type=ft.KeyboardType.NUMBER)

        st_dd = ft.Dropdown(
            label="Estatus Inicial",
            value="Por Ejecutar",
            options=[ft.DropdownOption("Por Ejecutar", "Por Ejecutar (Rojo)"), ft.DropdownOption("Ejecutado", "Ejecutado (Verde)")],
            dense=True
        )

        ente_dd = ft.Dropdown(
            label="Ente Ejecutor / Asignado",
            value="Hidrosportuguesa",
            options=[
                ft.DropdownOption("Alcaldía", "Alcaldía"),
                ft.DropdownOption("Hidrosportuguesa", "Hidrosportuguesa"),
                ft.DropdownOption("MinAguas", "MinAguas"),
                ft.DropdownOption("Gobernación", "Gobernación"),
                ft.DropdownOption("Hidroven", "Hidroven"),
            ],
            dense=True
        )

        def save_new(e):
            try:
                l_val = float(long_field.value or 0)
                b_val = int(ben_field.value or 0)
            except ValueError:
                return

            sec_val = (sector_field.value or "").strip()
            if not sec_val:
                return

            state.add_nuevo_tramo(
                municipio=mun_dd.value,
                parroquia=parr_field.value or mun_dd.value,
                sector=sec_val,
                direccion=dir_field.value or sec_val,
                diametro=diam_dd.value,
                longitud_m=l_val,
                tipo_colector=tipo_dd.value,
                beneficiarios=b_val,
                estatus=st_dd.value,
                fecha_ejecucion=datetime.now().strftime("%Y-%m-%d") if st_dd.value == "Ejecutado" else "",
                ente_ejecutor=ente_dd.value
            )
            page.pop_dialog()
            full_refresh()
            page.show_dialog(
                ft.SnackBar(content=ft.Text("Nuevo tramo registrado con éxito.", color="#FFFFFF"), bgcolor=COLOR_STATUS_GREEN)
            )
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.ADD_TASK_ROUNDED, color=COLOR_ELECTRIC_BLUE),
                ft.Text("Registrar Nuevo Tramo Caído", size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
            ]),
            content=ft.Container(
                content=ft.Column(
                    tight=True,
                    scroll=ft.ScrollMode.ADAPTIVE,
                    spacing=8,
                    controls=[
                        mun_dd,
                        parr_field,
                        sector_field,
                        dir_field,
                        ft.Row([diam_dd, long_field], spacing=8),
                        ft.Row([tipo_dd, ben_field], spacing=8),
                        ft.Row([st_dd, ente_dd], spacing=8)
                    ]
                ),
                width=420,
                height=450
            ),
            actions=[
                ft.TextButton(content=ft.Text("Cancelar"), on_click=lambda e: page.pop_dialog() or page.update()),
                ft.FilledButton(
                    content=ft.Text("Guardar Tramo"),
                    style=ft.ButtonStyle(bgcolor=COLOR_ELECTRIC_BLUE, color="#FFFFFF"),
                    on_click=save_new
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=12)
        )
        page.show_dialog(dialog)
        page.update()

    # Dropdowns en cascada
    dropdown_parroquia = ft.Dropdown(
        value=state.tramos_parroquia,
        label="Parroquia",
        dense=True,
        expand=True
    )

    def on_municipio_changed(e):
        selected_mun = e.control.value
        state.tramos_municipality = selected_mun
        state.tramos_parroquia = "Todas las Parroquias"

        update_parroquia_dropdown_options(selected_mun)
        full_refresh()

    def on_parroquia_changed(e):
        state.tramos_parroquia = e.control.value
        full_refresh()

    def update_parroquia_dropdown_options(municipio: str):
        parroquias = state.get_tramos_parroquias(municipio)
        options = [ft.DropdownOption("Todas las Parroquias", "Todas las Parroquias")]
        for p in parroquias:
            if p and p != "Todas las Parroquias":
                options.append(ft.DropdownOption(p, p))
        dropdown_parroquia.options = options
        dropdown_parroquia.value = "Todas las Parroquias"
        try:
            if hasattr(dropdown_parroquia, "page") and dropdown_parroquia.page:
                dropdown_parroquia.update()
        except Exception:
            pass

    dropdown_municipio = ft.Dropdown(
        value=state.tramos_municipality,
        options=[ft.DropdownOption(m, m if m != "Todos los Municipios" else "🏛️ Todos los Municipios") for m in MUNICIPALITIES_LIST],
        label="Municipio",
        dense=True,
        expand=True,
        on_select=on_municipio_changed
    )
    dropdown_parroquia.on_select = on_parroquia_changed

    # Refresco de Tarjetas KPI Superiores
    def refresh_upper_kpis():
        kpis = state.get_tramos_caidos_kpis(state.tramos_municipality, state.tramos_parroquia)
        kpis_row.controls.clear()

        # 1. Total Tramos
        kpis_row.controls.append(
            ft.Container(
                content=ft.Column(
                    spacing=2,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text("Tramos Caídos", size=10, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED),
                                ft.Icon(ft.Icons.ENGINEERING_ROUNDED, size=14, color=COLOR_NAVY_DARK)
                            ]
                        ),
                        ft.Text(format_num_es(kpis["tramos_totales"]), size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Text(f"{format_num_es(kpis.get('sectores', 0))} Sectores", size=9, weight=ft.FontWeight.W_600, color=COLOR_ELECTRIC_BLUE)
                    ]
                ),
                bgcolor="#F8FAFC",
                padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                border_radius=8,
                border=ft.Border.all(1, COLOR_BORDER),
                expand=True
            )
        )

        # 2. Tramos Ejecutados
        kpis_row.controls.append(
            ft.Container(
                content=ft.Column(
                    spacing=2,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text("Ejecutados", size=10, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED),
                                ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, size=14, color=COLOR_STATUS_GREEN)
                            ]
                        ),
                        ft.Text(format_num_es(kpis["ejecutados"]), size=16, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN),
                        ft.Text(f"{kpis['pct_ejecutado']}% Culminado", size=9, weight=ft.FontWeight.W_600, color=COLOR_STATUS_GREEN)
                    ]
                ),
                bgcolor="#F0FDF4",
                padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                border_radius=8,
                border=ft.Border.all(1, "#BBF7D0"),
                expand=True
            )
        )

        # 3. Tramos Por Ejecutar
        kpis_row.controls.append(
            ft.Container(
                content=ft.Column(
                    spacing=2,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text("Por Ejecutar", size=10, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED),
                                ft.Icon(ft.Icons.PENDING_ACTIONS_ROUNDED, size=14, color=COLOR_STATUS_RED)
                            ]
                        ),
                        ft.Text(format_num_es(kpis["por_ejecutar"]), size=16, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_RED),
                        ft.Text(f"{kpis['pct_por_ejecutar']}% Pendiente", size=9, weight=ft.FontWeight.W_600, color=COLOR_STATUS_RED)
                    ]
                ),
                bgcolor="#FEF2F2",
                padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                border_radius=8,
                border=ft.Border.all(1, "#FECACA"),
                expand=True
            )
        )

        # 4. Metros Sustituidos vs Pendientes
        kpis_row.controls.append(
            ft.Container(
                content=ft.Column(
                    spacing=2,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text("Metros Sustituidos", size=10, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED),
                                ft.Icon(ft.Icons.STRAIGHTEN_ROUNDED, size=14, color=COLOR_ELECTRIC_BLUE)
                            ]
                        ),
                        ft.Text(f"{format_num_es(kpis['metros_sustituidos'], 0)} m", size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Text(f"{format_num_es(kpis['metros_por_ejecutar'], 0)} m pend.", size=9, weight=ft.FontWeight.W_600, color=COLOR_TEXT_MUTED)
                    ]
                ),
                bgcolor="#EFF6FF",
                padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                border_radius=8,
                border=ft.Border.all(1, "#BFDBFE"),
                expand=True
            )
        )

    # 4 PESTAÑAS INTERNAS
    # PESTAÑA 0: Resumen por Municipio
    def build_tab_resumen_municipios():
        muns = state.get_tramos_municipios_resumen()
        items = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Avance Consolidado por Municipio", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                    ft.Text(f"{len(muns)} Municipios", size=11, color=COLOR_TEXT_MUTED, weight=ft.FontWeight.W_600)
                ]
            )
        ]

        for m in muns:
            pct = m.get("pct_ejecucion", 0.0)
            items.append(
                ft.Container(
                    content=ft.Column(
                        spacing=6,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(m.get("municipio", ""), size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                    ft.Text(f"{m.get('ejecutados', 0)} / {m.get('tramos_totales', 0)} Tramos ({pct}%)", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN)
                                ]
                            ),
                            ft.ProgressBar(
                                value=pct / 100.0 if pct > 0 else 0.0,
                                color=COLOR_STATUS_GREEN,
                                bgcolor="#E2E8F0",
                                height=6
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(f"📏 {format_num_es(m.get('metros_sustituidos', 0), 2)} m sustituidos", size=10, weight=ft.FontWeight.W_600, color=COLOR_NAVY_DARK),
                                    ft.Text(f"🔴 {m.get('por_ejecutar', 0)} por ejecutar", size=10, weight=ft.FontWeight.W_600, color=COLOR_STATUS_RED),
                                    ft.Text(f"📍 {m.get('sectores', 0)} sectores", size=10, color=COLOR_TEXT_MUTED)
                                ]
                            )
                        ]
                    ),
                    bgcolor=COLOR_SURFACE_WHITE,
                    padding=10,
                    border_radius=8,
                    border=ft.Border.all(1, COLOR_BORDER)
                )
            )

        return ft.ListView(controls=items, spacing=8, expand=True)

    # PESTAÑA 1: Inventario de Tramos (885)
    def build_tab_inventario():
        nonlocal inv_filter_estatus, inv_filter_diametro, inv_filter_tipo, inv_search_query

        # Filtrar datos
        tramos = state.get_filtered_tramos(
            municipio=state.tramos_municipality,
            parroquia=state.tramos_parroquia,
            estatus=inv_filter_estatus,
            diametro=inv_filter_diametro,
            tipo_colector=inv_filter_tipo,
            search=inv_search_query
        )

        filter_estatus_dd = ft.Dropdown(
            label="Estatus",
            value=inv_filter_estatus,
            options=[
                ft.DropdownOption("Todos", "Todos"),
                ft.DropdownOption("Ejecutado", "Ejecutado"),
                ft.DropdownOption("Por Ejecutar", "Por Ejecutar")
            ],
            dense=True,
            width=115,
            on_select=lambda e: update_inv_filters(estatus=e.control.value)
        )

        diam_opts = [ft.DropdownOption("Todos", "Todos")]
        for d in [6, 8, 10, 12, 15, 16, 18, 20, 21, 24, 27, 30, 36, 42]:
            diam_opts.append(ft.DropdownOption(str(d), f'{d}"'))
        filter_diam_dd = ft.Dropdown(
            label="Diámetro",
            value=inv_filter_diametro,
            options=diam_opts,
            dense=True,
            width=95,
            on_select=lambda e: update_inv_filters(diametro=e.control.value)
        )

        filter_tipo_dd = ft.Dropdown(
            label="Tipo",
            value=inv_filter_tipo,
            options=[
                ft.DropdownOption("Todos", "Todos"),
                ft.DropdownOption("SECUNDARIO", "Secundario"),
                ft.DropdownOption("PRINCIPAL", "Principal")
            ],
            dense=True,
            width=105,
            on_select=lambda e: update_inv_filters(tipo_colector=e.control.value)
        )

        search_tf = ft.TextField(
            label="Buscar sector o dirección...",
            value=inv_search_query,
            dense=True,
            text_size=11,
            expand=True,
            on_change=lambda e: update_inv_filters(search=e.control.value)
        )

        def update_inv_filters(estatus=None, diametro=None, tipo_colector=None, search=None):
            nonlocal inv_filter_estatus, inv_filter_diametro, inv_filter_tipo, inv_search_query
            if estatus is not None:
                inv_filter_estatus = estatus
            if diametro is not None:
                inv_filter_diametro = diametro
            if tipo_colector is not None:
                inv_filter_tipo = tipo_colector
            if search is not None:
                inv_search_query = search
            render_tab_content()
            page.update()

        header_filters = ft.Container(
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Row([filter_estatus_dd, filter_diam_dd, filter_tipo_dd], spacing=6),
                    ft.Row([search_tf], spacing=6),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(f"Mostrando {len(tramos)} tramos caídos", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                            ft.Text(f"{state.tramos_municipality}", size=10, color=COLOR_TEXT_MUTED)
                        ]
                    )
                ]
            ),
            padding=8,
            bgcolor="#F8FAFC",
            border_radius=8,
            border=ft.Border.all(1, COLOR_BORDER)
        )

        cards = [header_filters]
        for t in tramos[:120]:  # Vista ágil
            is_ejec = t.get("estatus") == "Ejecutado"
            st_color = COLOR_STATUS_GREEN if is_ejec else COLOR_STATUS_RED
            st_bg = "#DCFCE7" if is_ejec else "#FEE2E2"
            st_txt = "EJECUTADO" if is_ejec else "POR EJECUTAR"

            card_actions = [
                ft.TextButton(
                    content=ft.Text("Ver Ficha", size=11),
                    icon=ft.Icons.VISIBILITY_ROUNDED,
                    on_click=lambda e, tr=t: open_tramo_detail_dialog(tr)
                )
            ]
            if state.is_editor():
                card_actions.append(
                    ft.FilledButton(
                        content=ft.Text("Estatus", size=11),
                        icon=ft.Icons.UPDATE_ROUNDED,
                        style=ft.ButtonStyle(bgcolor=COLOR_ELECTRIC_BLUE, color="#FFFFFF"),
                        on_click=lambda e, tr=t: open_status_change_dialog(tr)
                    )
                )

            card = ft.Container(
                content=ft.Column(
                    spacing=4,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(
                                    spacing=6,
                                    controls=[
                                        ft.Container(
                                            content=ft.Text(f"#{t.get('item', t.get('id', '-'))}", size=11, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                            bgcolor=COLOR_NAVY_DARK,
                                            padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                            border_radius=4
                                        ),
                                        ft.Text(t.get("municipio", ""), size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                    ]
                                ),
                                ft.Container(
                                    content=ft.Text(st_txt, size=10, weight=ft.FontWeight.BOLD, color=st_color),
                                    bgcolor=st_bg,
                                    padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                    border_radius=4
                                )
                            ]
                        ),
                        ft.Text(t.get("sector", "-"), size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Text(t.get("direccion", "Sin dirección"), size=10, color=COLOR_TEXT_SECONDARY, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(f"Ø {t.get('diametro', '-')} | 📏 {format_num_es(t.get('longitud_m', 0), 2)} m", size=10, weight=ft.FontWeight.W_600, color=COLOR_ELECTRIC_BLUE),
                                ft.Text(f"Ente: {t.get('ente_ejecutor', '-')}", size=10, color=COLOR_TEXT_MUTED)
                            ]
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.END,
                            spacing=6,
                            controls=card_actions
                        )
                    ]
                ),
                bgcolor=COLOR_SURFACE_WHITE,
                padding=8,
                border_radius=8,
                border=ft.Border.all(1, COLOR_BORDER),
                ink=True,
                on_click=lambda e, tr=t: open_tramo_detail_dialog(tr)
            )
            cards.append(card)

        if len(tramos) > 120:
            cards.append(
                ft.Container(
                    content=ft.Text(f"Mostrando los primeros 120 de {len(tramos)} tramos. Utilice los filtros para afinar su búsqueda.", size=11, color=COLOR_TEXT_MUTED, text_align=ft.TextAlign.CENTER),
                    padding=10,
                    alignment=ft.Alignment(0, 0)
                )
            )

        return ft.ListView(controls=cards, spacing=8, expand=True)

    # PESTAÑA 2: Tramos Críticos Por Ejecutar (253) y Requerimiento de Tubería
    def build_tab_tramos_criticos():
        criticos = state.get_tramos_criticos_por_ejecutar(state.tramos_municipality, state.tramos_parroquia)
        diams = state.get_tramos_diametros_resumen(state.tramos_municipality)

        items = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Requerimiento de Tubería por Diámetro", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                    ft.Text(f"{len(criticos)} Tramos Pendientes", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_RED)
                ]
            )
        ]

        # Fila deslizable con las tarjetas de diámetro requeridas
        diam_cards = []
        for d in diams:
            diam_cards.append(
                ft.Container(
                    content=ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(d.get("diametro", ""), size=12, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                            ft.Text(f"{d.get('tramos_pendientes', 0)} tramos", size=10, color="#FFFFFF"),
                            ft.Text(f"{format_num_es(d.get('metros_pendientes', 0), 1)} m", size=11, weight=ft.FontWeight.BOLD, color="#FEF08A")
                        ]
                    ),
                    bgcolor=COLOR_NAVY_DARK,
                    padding=8,
                    border_radius=8,
                    width=100
                )
            )
        items.append(ft.Row(controls=diam_cards, scroll=ft.ScrollMode.ADAPTIVE, spacing=8))

        items.append(ft.Divider(height=1, color=COLOR_BORDER))
        items.append(
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Listado de Tramos Priorizados Por Ejecutar", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                    ft.Text("Atención Crítica", size=10, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_RED)
                ]
            )
        )

        for t in criticos[:100]:
            btn_mark = None
            if state.is_editor():
                btn_mark = ft.FilledButton(
                    content=ft.Text("Marcar Ejecutado", size=11),
                    icon=ft.Icons.CHECK_CIRCLE_ROUNDED,
                    style=ft.ButtonStyle(bgcolor=COLOR_STATUS_GREEN, color="#FFFFFF"),
                    on_click=lambda e, tr=t: open_status_change_dialog(tr)
                )

            card = ft.Container(
                content=ft.Column(
                    spacing=4,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(
                                    spacing=6,
                                    controls=[
                                        ft.Container(
                                            content=ft.Text(f"#{t.get('item', t.get('id', '-'))}", size=11, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                            bgcolor=COLOR_STATUS_RED,
                                            padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                            border_radius=4
                                        ),
                                        ft.Text(t.get("municipio", ""), size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                        ft.Text(f"• {t.get('parroquia', '')}", size=11, color=COLOR_TEXT_MUTED)
                                    ]
                                ),
                                ft.Container(
                                    content=ft.Text(f"Ø {t.get('diametro', '-')}", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                    bgcolor="#E2E8F0",
                                    padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                    border_radius=4
                                )
                            ]
                        ),
                        ft.Text(t.get("sector", "-"), size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Text(t.get("direccion", "Sin dirección"), size=10, color=COLOR_TEXT_SECONDARY),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(f"Requerimiento: {format_num_es(t.get('longitud_m', 0), 2)} m de tubería", size=10, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_RED),
                                ft.Text(f"👥 {format_num_es(t.get('beneficiarios', 0))} hab.", size=10, color=COLOR_TEXT_MUTED)
                            ]
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.END,
                            spacing=6,
                            controls=[
                                ft.TextButton(
                                    content=ft.Text("Ver Ficha", size=11),
                                    icon=ft.Icons.VISIBILITY_ROUNDED,
                                    on_click=lambda e, tr=t: open_tramo_detail_dialog(tr)
                                ),
                                btn_mark if btn_mark else ft.Container()
                            ]
                        )
                    ]
                ),
                bgcolor="#FEF2F2",
                padding=10,
                border_radius=8,
                border=ft.Border.all(1, "#FECACA"),
                ink=True,
                on_click=lambda e, tr=t: open_tramo_detail_dialog(tr)
            )
            items.append(card)

        return ft.ListView(controls=items, spacing=8, expand=True)

    # PESTAÑA 3: Histórico por Año y Ente Ejecutor (2022–2026)
    def build_tab_historico():
        hist = state.get_tramos_historico_anual(state.tramos_municipality)
        anual = hist.get("anual", {})
        entes = hist.get("entes", {})

        items = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Histórico de Ejecución Anual (2022–2026)", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                    ft.Text(state.tramos_municipality, size=11, color=COLOR_TEXT_MUTED, weight=ft.FontWeight.W_600)
                ]
            )
        ]

        # Tarjetas de los 5 años
        year_cards = []
        for y in ["2022", "2023", "2024", "2025", "2026"]:
            val = anual.get(y, 0)
            year_cards.append(
                ft.Container(
                    content=ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(y, size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED),
                            ft.Text(format_num_es(val), size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                            ft.Text("Tramos Ejec", size=9, color=COLOR_STATUS_GREEN, weight=ft.FontWeight.W_600)
                        ]
                    ),
                    bgcolor=COLOR_SURFACE_WHITE,
                    padding=8,
                    border_radius=8,
                    border=ft.Border.all(1, COLOR_BORDER),
                    expand=True
                )
            )
        items.append(ft.Row(controls=year_cards, spacing=6))

        items.append(ft.Divider(height=1, color=COLOR_BORDER))
        items.append(
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Desglose por Ente Ejecutor", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                    ft.Text("Tramos Culminados", size=11, color=COLOR_STATUS_GREEN, weight=ft.FontWeight.W_600)
                ]
            )
        )

        # Tarjetas de Entes
        total_entes = sum(entes.values()) or 1
        for ente_name, count in entes.items():
            pct = round(count / total_entes * 100.0, 1)
            items.append(
                ft.Container(
                    content=ft.Column(
                        spacing=4,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(ente_name, size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                    ft.Text(f"{format_num_es(count)} Tramos ({pct}%)", size=11, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_BLUE)
                                ]
                            ),
                            ft.ProgressBar(
                                value=pct / 100.0 if pct > 0 else 0.0,
                                color=COLOR_ELECTRIC_BLUE,
                                bgcolor="#E2E8F0",
                                height=6
                            )
                        ]
                    ),
                    bgcolor=COLOR_SURFACE_WHITE,
                    padding=10,
                    border_radius=8,
                    border=ft.Border.all(1, COLOR_BORDER)
                )
            )

        return ft.ListView(controls=items, spacing=8, expand=True)

    def render_tab_chips():
        tab_chips_row.controls.clear()
        tab_names = [
            ("Resumen por Municipio", 0),
            (f"Inventario Tramos ({state.get_tramos_caidos_kpis()['tramos_totales']})", 1),
            (f"Tramos Críticos ({state.get_tramos_caidos_kpis()['por_ejecutar']})", 2),
            ("Histórico (2022–2026)", 3)
        ]

        for label, idx in tab_names:
            is_active = (active_tab_index == idx)
            tab_chips_row.controls.append(
                ft.Container(
                    content=ft.Text(
                        label,
                        size=11,
                        weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
                        color="#FFFFFF" if is_active else COLOR_NAVY_DARK
                    ),
                    bgcolor=COLOR_NAVY_DARK if is_active else "#E2E8F0",
                    padding=ft.Padding.symmetric(horizontal=10, vertical=6),
                    border_radius=8,
                    ink=True,
                    on_click=lambda e, i=idx: set_tab_index(i)
                )
            )

    def set_tab_index(idx: int):
        nonlocal active_tab_index
        active_tab_index = idx
        render_tab_chips()
        render_tab_content()
        page.update()

    def render_tab_content():
        if active_tab_index == 0:
            tab_content_area.content = build_tab_resumen_municipios()
        elif active_tab_index == 1:
            tab_content_area.content = build_tab_inventario()
        elif active_tab_index == 2:
            tab_content_area.content = build_tab_tramos_criticos()
        else:
            tab_content_area.content = build_tab_historico()

    def full_refresh():
        refresh_upper_kpis()
        render_tab_chips()
        render_tab_content()
        page.update()

    # Barra inferior de acciones (Solo Editor)
    bottom_bar = None
    if state.is_editor():
        bottom_bar = ft.Container(
            content=ft.Row(
                spacing=8,
                controls=[
                    ft.FilledButton(
                        content=ft.Text("+ Nuevo Tramo Caído", size=12),
                        icon=ft.Icons.ADD_TASK_ROUNDED,
                        style=ft.ButtonStyle(bgcolor=COLOR_ELECTRIC_BLUE, color="#FFFFFF"),
                        on_click=lambda e: open_add_tramo_dialog(),
                        expand=True
                    ),
                    ft.OutlinedButton(
                        content=ft.Text("Importar Excel (.xlsx)", size=12),
                        icon=ft.Icons.UPLOAD_FILE_ROUNDED,
                        on_click=lambda e: import_panel_obj.toggle(),
                        expand=True
                    )
                ]
            ),
            padding=ft.Padding.all(8),
            bgcolor=COLOR_SURFACE_WHITE,
            border=ft.Border.only(top=ft.BorderSide(1, COLOR_BORDER))
        )
    else:
        bottom_bar = ft.Container(
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

    # Inicializar opciones de parroquia
    update_parroquia_dropdown_options(state.tramos_municipality)
    refresh_upper_kpis()
    render_tab_chips()
    render_tab_content()

    logo_path = "assets/logo_tramos_caidos.png"
    leading_logo = ft.Image(
        src="logo_tramos_caidos.png",
        width=36,
        height=36,
        fit="contain"
    ) if os.path.exists(logo_path) else ft.Icon(
        ft.Icons.ENGINEERING_ROUNDED,
        color="#FFFFFF",
        size=24
    )

    header = create_institutional_header(
        title="Plan Tramos Caídos",
        subtitle="Reconstrucción y Sustitución de Colectores",
        current_role=state.current_role,
        show_back_button=True,
        on_back_click=lambda e: on_back_to_summary(),
        on_switch_role_click=on_switch_role,
        on_logout_click=on_logout,
        leading_logo=leading_logo
    )

    filter_bar = ft.Container(
        content=ft.Row(
            spacing=8,
            controls=[dropdown_municipio, dropdown_parroquia]
        ),
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        bgcolor=COLOR_SURFACE_WHITE,
        border_radius=8,
        border=ft.Border.all(1, COLOR_BORDER)
    )

    return ft.Column(
        spacing=0,
        expand=True,
        controls=[
            header,
            import_panel_obj.panel_container,
            ft.Container(
                content=ft.Column(
                    spacing=8,
                    controls=[
                        filter_bar,
                        kpis_row,
                        ft.Container(
                            content=tab_chips_row,
                            padding=ft.Padding.only(bottom=15)
                        ),
                        tab_content_area
                    ],
                    expand=True
                ),
                padding=10,
                expand=True
            ),
            bottom_bar
        ]
    )
