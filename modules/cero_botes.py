"""
Módulo Detallado: Plan Cero Botes de Agua
Secretaría Superior de Operaciones Generales - Gobernación de Portuguesa
Carga Oficial: PLAN CERO BOTES PORTUGUESA 2026-6.xlsx
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

YEARS_CERO_BOTES = [
    ("Acumulado Total", "Acumulado Total 2022–2026"),
    ("2026", "Año 2026"),
    ("2025", "Año 2025"),
    ("2024", "Año 2024"),
    ("2023", "Año 2023"),
    ("2022", "Año 2022")
]

def format_number_es(val: int | float, decimals: int = 0) -> str:
    """Formatea un número con separadores de miles (.) y decimales (,)."""
    if val is None:
        return "0"
    if decimals > 0:
        formatted = f"{float(val):,.{decimals}f}"
        return formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        return f"{int(round(float(val))):,}".replace(",", ".")

def build_cero_botes_view(
    page: ft.Page,
    on_back_to_summary,
    on_switch_role,
    on_logout
) -> ft.Control:
    """Construye la vista interactiva completa del Plan Cero Botes de Agua."""
    state = AppState()

    active_tab_index = 0
    kpis_row = ft.Row(spacing=8)
    tab_content_area = ft.Container(expand=True)
    tab_chips_row = ft.Row(scroll=ft.ScrollMode.ADAPTIVE, spacing=6)

    # Filtros de Bitácora (Pestaña 1)
    bitacora_search_query = ""
    bitacora_solo_1x10 = False

    import_panel_obj = ExcelImportPanel(
        page=page,
        title="Importar Excel Cero Botes de Agua (.xlsx)",
        default_file="PLAN CERO BOTES PORTUGUESA 2026-6.xlsx",
        on_load_callback=state.reload_cero_botes_excel,
        on_success_callback=lambda: full_refresh(),
        accent_color=COLOR_ELECTRIC_BLUE
    )

    # Modal de Ficha Técnica Detallada de Filtración
    def open_filtracion_detail_dialog(f: dict):
        is_1x10 = f.get("es_1x10", False)
        badge_bg = "#DCFCE7" if is_1x10 else "#EFF6FF"
        badge_color = COLOR_STATUS_GREEN if is_1x10 else COLOR_ELECTRIC_BLUE
        badge_text = "CASO 1X10" if is_1x10 else "REPORTE COMUNAL"

        details_rows = [
            ft.Row([
                ft.Text("Municipio:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=120),
                ft.Text(f.get("municipio", "-"), size=12, weight=ft.FontWeight.W_600, color=COLOR_NAVY_DARK, expand=True)
            ]),
            ft.Row([
                ft.Text("Comunidad:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=120),
                ft.Text(f.get("comunidad", "-"), size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK, expand=True)
            ]),
            ft.Row([
                ft.Text("Dirección / Ubicación:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=120),
                ft.Text(f.get("direccion", "Sin dirección especificada"), size=11, color=COLOR_TEXT_PRIMARY, expand=True)
            ]),
            ft.Divider(height=1, color=COLOR_BORDER),
            ft.Row([
                ft.Text("Fecha de Reparación:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=120),
                ft.Text(f.get("fecha", "-"), size=12, color=COLOR_TEXT_PRIMARY)
            ]),
            ft.Row([
                ft.Text("Diámetro de Tubería:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=120),
                ft.Container(
                    content=ft.Text(f.get("diametro", '-'), size=11, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                    bgcolor=COLOR_NAVY_DARK,
                    padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                    border_radius=6
                )
            ]),
            ft.Row([
                ft.Text("Caudal Recuperado:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=120),
                ft.Text(f"{format_number_es(f.get('caudal_lps', 0), 2)} L/s ({format_number_es(f.get('caudal_lpd', 0))} L/día)", size=12, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_BLUE)
            ]),
            ft.Row([
                ft.Text("Personas Beneficiadas:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=120),
                ft.Text(f"{format_number_es(f.get('beneficiarios', 0))} hab.", size=12, color=COLOR_TEXT_PRIMARY)
            ]),
            ft.Divider(height=1, color=COLOR_BORDER),
            ft.Row([
                ft.Text("Piezas Colocadas:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=120),
                ft.Text(f.get("piezas_colocadas") or "Materiales estándar de reparación", size=11, color=COLOR_NAVY_DARK, expand=True)
            ]),
            ft.Row([
                ft.Text("Observaciones:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=120),
                ft.Text(f.get("observaciones") or "Sin observaciones registradas", size=11, color=COLOR_TEXT_MUTED, expand=True)
            ]),
            ft.Row([
                ft.Text("Ente Ejecutor:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=120),
                ft.Text(f.get("ente_ejecutor") or "HIDROSPORTUGUESA", size=12, weight=ft.FontWeight.W_600, color=COLOR_NAVY_DARK)
            ])
        ]

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.PLUMBING_ROUNDED, color=COLOR_ELECTRIC_BLUE),
                            ft.Text(f"Ficha Reparación #{f.get('item', f.get('id', '-'))}", size=15, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                        ]
                    ),
                    ft.Container(
                        content=ft.Text(badge_text, size=10, weight=ft.FontWeight.BOLD, color=badge_color),
                        bgcolor=badge_bg,
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
            actions=[
                ft.TextButton(content=ft.Text("Cerrar"), on_click=lambda e: page.pop_dialog() or page.update())
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=12)
        )
        page.show_dialog(dialog)
        page.update()

    # Modal para registrar nueva reparación de bote (Editor)
    def open_add_repair_dialog():
        mun_opts = [ft.DropdownOption(m, m) for m in MUNICIPALITIES_LIST if m != "Todos los Municipios"]
        mun_dd = ft.Dropdown(value="GUANARE", options=mun_opts, label="Municipio", dense=True)

        fecha_field = ft.TextField(
            label="Fecha de Reparación",
            value=datetime.now().strftime("%Y-%m-%d"),
            dense=True,
            text_size=12
        )

        com_field = ft.TextField(label="Comunidad / Sector", hint_text="Ej: Barrio San José", dense=True)
        dir_field = ft.TextField(label="Dirección / Punto de Referencia", hint_text="Ej: Carrera 5 entre calles 10 y 11", dense=True)

        diam_opts = [
            ft.DropdownOption('1/2"', '1/2"'),
            ft.DropdownOption('3/4"', '3/4"'),
            ft.DropdownOption('1"', '1"'),
            ft.DropdownOption('1 1/2"', '1 1/2"'),
            ft.DropdownOption('2"', '2"'),
            ft.DropdownOption('3"', '3"'),
            ft.DropdownOption('4"', '4"'),
            ft.DropdownOption('6"', '6"'),
            ft.DropdownOption('8"', '8"'),
            ft.DropdownOption('10"', '10"'),
            ft.DropdownOption('12"', '12"'),
            ft.DropdownOption('16"', '16"')
        ]
        diam_dd = ft.Dropdown(value='1/2"', options=diam_opts, label="Diámetro de Tubería", dense=True)

        caudal_field = ft.TextField(label="Caudal Recuperado (Lts/Seg)", value="0.10", dense=True, keyboard_type=ft.KeyboardType.NUMBER)
        lpd_display = ft.Text("Caudal estimado: 8.640 Lts/Día", size=11, color=COLOR_ELECTRIC_BLUE, weight=ft.FontWeight.W_600)

        def on_caudal_change(e):
            try:
                c_val = float(caudal_field.value or 0)
                lpd_val = round(c_val * 86400, 0)
                lpd_display.value = f"Caudal estimado: {format_number_es(lpd_val)} Lts/Día"
            except ValueError:
                lpd_display.value = "Caudal inválido"
            lpd_display.update()

        caudal_field.on_change = on_caudal_change

        ben_field = ft.TextField(label="Personas Beneficiadas", value="6", dense=True, keyboard_type=ft.KeyboardType.NUMBER)
        piezas_field = ft.TextField(label="Piezas Colocadas", hint_text="Ej: 1 Abrazadera 1/2, 1 niple galvanizado", dense=True)
        obs_field = ft.TextField(label="Observaciones", hint_text="Ej: Fuga reparada por cuadrilla de guardia", dense=True)

        check_1x10 = ft.Checkbox(label="Caso 1x10 del Buen Gobierno", value=True)

        ente_opts = [
            ft.DropdownOption("HIDROSPORTUGUESA", "Hidrosportuguesa"),
            ft.DropdownOption("HIDROVEN", "Hidroven"),
            ft.DropdownOption("SECRETARIA", "Secretaría"),
            ft.DropdownOption("ALCALDIA", "Alcaldía")
        ]
        ente_dd = ft.Dropdown(value="HIDROSPORTUGUESA", options=ente_opts, label="Ente Ejecutor", dense=True)

        def save_repair(e):
            try:
                c_val = float(caudal_field.value or 0)
                b_val = int(ben_field.value or 0)
            except ValueError:
                return

            com_val = (com_field.value or "").strip()
            if not com_val:
                return

            state.add_cero_botes_repair(
                fecha=fecha_field.value,
                municipio=mun_dd.value,
                comunidad=com_val,
                direccion=dir_field.value or com_val,
                diametro=diam_dd.value,
                caudal_lps=c_val,
                beneficiarios=b_val,
                piezas_colocadas=piezas_field.value or "",
                observaciones=obs_field.value or "",
                es_1x10=check_1x10.value,
                ente_ejecutor=ente_dd.value
            )
            page.pop_dialog()
            full_refresh()
            page.show_dialog(
                ft.SnackBar(content=ft.Text("Bote reparado registrado y sumado exitosamente.", color="#FFFFFF"), bgcolor=COLOR_STATUS_GREEN)
            )
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.ADD_TASK_ROUNDED, color=COLOR_ELECTRIC_BLUE),
                ft.Text("Registrar Bote de Agua Reparado", size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
            ]),
            content=ft.Container(
                content=ft.Column(
                    tight=True,
                    scroll=ft.ScrollMode.ADAPTIVE,
                    spacing=8,
                    controls=[
                        ft.Row([mun_dd, fecha_field], spacing=8),
                        com_field,
                        dir_field,
                        ft.Row([diam_dd, caudal_field], spacing=8),
                        lpd_display,
                        ben_field,
                        piezas_field,
                        obs_field,
                        check_1x10,
                        ente_dd
                    ]
                ),
                width=420,
                height=480
            ),
            actions=[
                ft.TextButton(content=ft.Text("Cancelar"), on_click=lambda e: page.pop_dialog() or page.update()),
                ft.FilledButton(
                    content=ft.Text("Guardar Reparación"),
                    style=ft.ButtonStyle(bgcolor=COLOR_ELECTRIC_BLUE, color="#FFFFFF"),
                    on_click=save_repair
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=12)
        )
        page.show_dialog(dialog)
        page.update()

    # Dropdowns de filtros superiores
    def on_municipio_select(e):
        state.cero_botes_municipality = e.control.value
        full_refresh()

    def on_year_select(e):
        state.cero_botes_year = e.control.value
        full_refresh()

    dropdown_municipio = ft.Dropdown(
        value=state.cero_botes_municipality,
        options=[ft.DropdownOption(m, m if m != "Todos los Municipios" else "🏛️ Todos los Municipios") for m in MUNICIPALITIES_LIST],
        label="Municipio",
        dense=True,
        expand=True,
        on_select=on_municipio_select
    )

    dropdown_year = ft.Dropdown(
        value=state.cero_botes_year,
        options=[ft.DropdownOption(k, v) for k, v in YEARS_CERO_BOTES],
        label="Período",
        dense=True,
        expand=True,
        on_select=on_year_select
    )

    # 4 Tarjetas KPI Superiores Dinámicas
    def refresh_upper_kpis():
        kpis = state.get_cero_botes_kpis(state.cero_botes_municipality, state.cero_botes_year)
        kpis_row.controls.clear()

        # 1. Botes Reparados
        kpis_row.controls.append(
            ft.Container(
                content=ft.Column(
                    spacing=2,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text("Botes Reparados", size=10, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED),
                                ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, size=14, color=COLOR_STATUS_GREEN)
                            ]
                        ),
                        ft.Text(format_number_es(kpis["botes"]), size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Text(f"{kpis['year']}", size=9, weight=ft.FontWeight.W_600, color=COLOR_STATUS_GREEN)
                    ]
                ),
                bgcolor="#F0FDF4",
                padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                border_radius=8,
                border=ft.Border.all(1, "#BBF7D0"),
                expand=True
            )
        )

        # 2. Caudal Lts/Seg
        kpis_row.controls.append(
            ft.Container(
                content=ft.Column(
                    spacing=2,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text("Caudal Lts/Seg", size=10, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED),
                                ft.Icon(ft.Icons.SPEED_ROUNDED, size=14, color=COLOR_ELECTRIC_BLUE)
                            ]
                        ),
                        ft.Text(format_number_es(kpis["caudal_lps"], 2), size=16, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_BLUE),
                        ft.Text("Recuperado", size=9, weight=ft.FontWeight.W_600, color=COLOR_ELECTRIC_BLUE)
                    ]
                ),
                bgcolor="#EFF6FF",
                padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                border_radius=8,
                border=ft.Border.all(1, "#BFDBFE"),
                expand=True
            )
        )

        # 3. Caudal Lts/Día
        kpis_row.controls.append(
            ft.Container(
                content=ft.Column(
                    spacing=2,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text("Caudal Lts/Día", size=10, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED),
                                ft.Icon(ft.Icons.WATER_ROUNDED, size=14, color=COLOR_NAVY_DARK)
                            ]
                        ),
                        ft.Text(f"{format_number_es(kpis['caudal_lts_dia'] / 1_000_000, 1)}M L/d", size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Text(f"{format_number_es(kpis['caudal_lts_dia'])} L", size=9, color=COLOR_TEXT_MUTED)
                    ]
                ),
                bgcolor="#F8FAFC",
                padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                border_radius=8,
                border=ft.Border.all(1, COLOR_BORDER),
                expand=True
            )
        )

        # 4. Personas Beneficiadas
        kpis_row.controls.append(
            ft.Container(
                content=ft.Column(
                    spacing=2,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text("Beneficiarios", size=10, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED),
                                ft.Icon(ft.Icons.PEOPLE_ALT_ROUNDED, size=14, color=COLOR_NAVY_DARK)
                            ]
                        ),
                        ft.Text(format_number_es(kpis["beneficiarios"]), size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Text("Habitantes", size=9, weight=ft.FontWeight.W_600, color=COLOR_TEXT_MUTED)
                    ]
                ),
                bgcolor="#FAF5FF",
                padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                border_radius=8,
                border=ft.Border.all(1, "#E9D5FF"),
                expand=True
            )
        )

    # PESTAÑA 0: Resumen por Municipio
    def build_tab_resumen_municipio():
        muns = state.get_cero_botes_municipios_resumen(state.cero_botes_year)
        items = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(f"Comparativa Municipal ({state.cero_botes_year})", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                    ft.Text(f"{len(muns)} Municipios", size=11, color=COLOR_TEXT_MUTED, weight=ft.FontWeight.W_600)
                ]
            )
        ]

        total_botes_periodo = sum(m.get("botes", 0) for m in muns) or 1

        for m in muns:
            botes_m = m.get("botes", 0)
            pct = round((botes_m / total_botes_periodo) * 100.0, 1)
            items.append(
                ft.Container(
                    content=ft.Column(
                        spacing=6,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(m.get("municipio", ""), size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                    ft.Text(f"{format_number_es(botes_m)} Botes Reparados ({pct}%)", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN)
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
                                    ft.Text(f"💧 {format_number_es(m.get('lps', 0), 2)} L/s", size=10, weight=ft.FontWeight.W_600, color=COLOR_ELECTRIC_BLUE),
                                    ft.Text(f"🌊 {format_number_es(m.get('lpd', 0))} L/día", size=10, weight=ft.FontWeight.W_600, color=COLOR_NAVY_DARK),
                                    ft.Text(f"👥 {format_number_es(m.get('beneficiarios', 0))} hab.", size=10, color=COLOR_TEXT_MUTED)
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

    # PESTAÑA 1: Bitácora Detallada de Filtraciones (2.423)
    def build_tab_bitacora():
        nonlocal bitacora_search_query, bitacora_solo_1x10

        filts = state.get_filtered_filtraciones(
            municipio=state.cero_botes_municipality,
            solo_1x10=bitacora_solo_1x10,
            search=bitacora_search_query
        )

        search_tf = ft.TextField(
            label="Buscar por Comunidad o Dirección...",
            value=bitacora_search_query,
            dense=True,
            text_size=11,
            expand=True,
            on_change=lambda e: update_bitacora_filters(search=e.control.value)
        )

        check_1x10 = ft.Checkbox(
            label="Solo Casos 1x10",
            value=bitacora_solo_1x10,
            on_change=lambda e: update_bitacora_filters(solo_1x10=e.control.value)
        )

        def update_bitacora_filters(search=None, solo_1x10=None):
            nonlocal bitacora_search_query, bitacora_solo_1x10
            if search is not None:
                bitacora_search_query = search
            if solo_1x10 is not None:
                bitacora_solo_1x10 = solo_1x10
            render_tab_content()
            page.update()

        filter_box = ft.Container(
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Row([search_tf, check_1x10], spacing=8),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(f"Mostrando {len(filts)} reparaciones de filtraciones", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                            ft.Text(f"{state.cero_botes_municipality}", size=10, color=COLOR_TEXT_MUTED)
                        ]
                    )
                ]
            ),
            padding=8,
            bgcolor="#F8FAFC",
            border_radius=8,
            border=ft.Border.all(1, COLOR_BORDER)
        )

        cards = [filter_box]
        for f in filts[:120]:
            is_1x10 = f.get("es_1x10", False)
            st_color = COLOR_STATUS_GREEN if is_1x10 else COLOR_ELECTRIC_BLUE
            st_bg = "#DCFCE7" if is_1x10 else "#EFF6FF"
            st_txt = "CASO 1X10" if is_1x10 else "REPORTE COMUNAL"

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
                                            content=ft.Text(f"#{f.get('item', f.get('id', '-'))}", size=11, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                            bgcolor=COLOR_NAVY_DARK,
                                            padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                            border_radius=4
                                        ),
                                        ft.Text(f.get("municipio", ""), size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                        ft.Text(f"• {f.get('fecha', '')}", size=10, color=COLOR_TEXT_MUTED)
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
                        ft.Text(f.get("comunidad", "-"), size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Text(f.get("direccion", "Sin dirección"), size=10, color=COLOR_TEXT_SECONDARY, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(f"Ø {f.get('diametro', '-')} | 💧 {format_number_es(f.get('caudal_lps', 0), 2)} L/s", size=10, weight=ft.FontWeight.W_600, color=COLOR_ELECTRIC_BLUE),
                                ft.Text(f"Ente: {f.get('ente_ejecutor', '-')}", size=10, color=COLOR_TEXT_MUTED)
                            ]
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.TextButton(
                                    content=ft.Text("Ver Ficha Completa", size=11),
                                    icon=ft.Icons.VISIBILITY_ROUNDED,
                                    on_click=lambda e, item=f: open_filtracion_detail_dialog(item)
                                )
                            ]
                        )
                    ]
                ),
                bgcolor=COLOR_SURFACE_WHITE,
                padding=8,
                border_radius=8,
                border=ft.Border.all(1, COLOR_BORDER),
                ink=True,
                on_click=lambda e, item=f: open_filtracion_detail_dialog(item)
            )
            cards.append(card)

        if len(filts) > 120:
            cards.append(
                ft.Container(
                    content=ft.Text(f"Mostrando los primeros 120 de {len(filts)} registros. Utilice el buscador para afinar la consulta.", size=11, color=COLOR_TEXT_MUTED, text_align=ft.TextAlign.CENTER),
                    padding=10,
                    alignment=ft.Alignment(0, 0)
                )
            )

        return ft.ListView(controls=cards, spacing=8, expand=True)

    # PESTAÑA 2: Evolución Anual (2022–2026) y Entes Ejecutores
    def build_tab_evolucion():
        evol_data = state.get_cero_botes_evolucion_anual()
        evol = evol_data.get("evolucion", {})
        entes = evol_data.get("entes", {})

        items = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Evolución Anual de Botes Reparados (2022–2026)", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                    ft.Text("Histórico Multianual", size=11, color=COLOR_TEXT_MUTED, weight=ft.FontWeight.W_600)
                ]
            )
        ]

        # Tarjetas de los 5 años
        year_cards = []
        for y in ["2022", "2023", "2024", "2025", "2026"]:
            val = evol.get(y, 0)
            year_cards.append(
                ft.Container(
                    content=ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(y, size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED),
                            ft.Text(format_number_es(val), size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                            ft.Text("Botes Reparados", size=9, color=COLOR_STATUS_GREEN, weight=ft.FontWeight.W_600)
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
                    ft.Text("Desglose de Filtraciones por Ente Ejecutor", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                    ft.Text("Gestión Institucional", size=11, color=COLOR_ELECTRIC_BLUE, weight=ft.FontWeight.W_600)
                ]
            )
        )

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
                                    ft.Text(f"{format_number_es(count)} Reparaciones ({pct}%)", size=11, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_BLUE)
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
        tot_filtraciones = len(state.cero_botes_data.get("filtraciones", [])) if state.cero_botes_data else 2423
        tab_names = [
            ("Resumen por Municipio", 0),
            (f"Bitácora Filtraciones ({format_number_es(tot_filtraciones)})", 1),
            ("Evolución Anual (2022–2026)", 2)
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
            tab_content_area.content = build_tab_resumen_municipio()
        elif active_tab_index == 1:
            tab_content_area.content = build_tab_bitacora()
        else:
            tab_content_area.content = build_tab_evolucion()

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
                        content=ft.Text("+ Registrar Bote Reparado", size=12),
                        icon=ft.Icons.ADD_TASK_ROUNDED,
                        style=ft.ButtonStyle(bgcolor=COLOR_ELECTRIC_BLUE, color="#FFFFFF"),
                        on_click=lambda e: open_add_repair_dialog(),
                        expand=True
                    ),
                    ft.OutlinedButton(
                        content=ft.Text("Importar Excel Cero Botes (.xlsx)", size=12),
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

    # Inicialización
    refresh_upper_kpis()
    render_tab_chips()
    render_tab_content()

    logo_path = "assets/logo_cero_botes.png"
    leading_logo = ft.Image(
        src="logo_cero_botes.png",
        width=36,
        height=36,
        fit="contain"
    ) if os.path.exists(logo_path) else ft.Icon(
        ft.Icons.PLUMBING_ROUNDED,
        color="#FFFFFF",
        size=24
    )

    header = create_institutional_header(
        title="Plan Cero Botes de Agua",
        subtitle="Corrección Integral de Fugas y Recuperación Hídrica",
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
            controls=[dropdown_municipio, dropdown_year]
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
