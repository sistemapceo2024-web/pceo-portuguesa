"""
Módulo Detallado: Plan Ruta del Hidrojet
Secretaría Superior de Operaciones Generales - Gobernación del Estado Portuguesa
Carga Oficial: AGUAS SERVIDAS PORTUGUESA 2026-6.xlsx
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

YEARS_HIDROJET = [
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

def build_ruta_hidrojet_view(
    page: ft.Page,
    on_back_to_summary,
    on_switch_role,
    on_logout
) -> ft.Control:
    """Construye la vista interactiva completa del Plan Ruta del Hidrojet."""
    state = AppState()

    active_tab_index = 0
    kpis_row = ft.Row(spacing=8)
    tab_content_area = ft.Container(expand=True)
    tab_chips_row = ft.Row(scroll=ft.ScrollMode.ADAPTIVE, spacing=6)

    # Filtros de Bitácora (Pestaña 1)
    bitacora_search_query = ""
    bitacora_categoria_filtro = "Todos"

    import_panel_obj = ExcelImportPanel(
        page=page,
        title="Importar Excel Ruta del Hidrojet (.xlsx)",
        default_file="AGUAS SERVIDAS PORTUGUESA 2026-6.xlsx",
        on_load_callback=state.reload_hidrojet_excel,
        on_success_callback=lambda: full_refresh(),
        accent_color=COLOR_ELECTRIC_BLUE
    )

    # Modal de Ficha Técnica de Jornada Hidrojet
    def open_jornada_detail_dialog(j: dict):
        cat = j.get("categoria_trabajo", "Colectores")
        cat_bg = "#EFF6FF" if cat == "Colectores" else ("#DCFCE7" if cat == "Empotramientos" else "#FEF3C7")
        cat_color = COLOR_ELECTRIC_BLUE if cat == "Colectores" else (COLOR_STATUS_GREEN if cat == "Empotramientos" else COLOR_STATUS_AMBER)

        details_rows = [
            ft.Row([
                ft.Text("Municipio:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=120),
                ft.Text(j.get("municipio", "-"), size=12, weight=ft.FontWeight.W_600, color=COLOR_NAVY_DARK, expand=True)
            ]),
            ft.Row([
                ft.Text("Comunidad:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=120),
                ft.Text(j.get("comunidad", "-"), size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK, expand=True)
            ]),
            ft.Row([
                ft.Text("Dirección / Tramo:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=120),
                ft.Text(j.get("direccion", "Sin dirección especificada"), size=11, color=COLOR_TEXT_PRIMARY, expand=True)
            ]),
            ft.Divider(height=1, color=COLOR_BORDER),
            ft.Row([
                ft.Text("Fecha Operación:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=120),
                ft.Text(j.get("fecha", "-"), size=12, color=COLOR_TEXT_PRIMARY)
            ]),
            ft.Row([
                ft.Text("Trabajo Realizado:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=120),
                ft.Text(j.get("trabajo_realizado", "Mantenimiento"), size=11, weight=ft.FontWeight.W_600, color=COLOR_NAVY_DARK, expand=True)
            ]),
            ft.Row([
                ft.Text("Longitud Liberada:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=120),
                ft.Text(f"{format_number_es(j.get('longitud_m', 0), 1)} metros", size=12, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_BLUE)
            ]),
            ft.Row([
                ft.Text("Bocas de Visita:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=120),
                ft.Text(f"{format_number_es(j.get('bocas', 0))} atendidas", size=12, color=COLOR_TEXT_PRIMARY)
            ]),
            ft.Row([
                ft.Text("Empotramientos:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=120),
                ft.Text(f"{format_number_es(j.get('empotramientos', 0))} destapados", size=12, color=COLOR_TEXT_PRIMARY)
            ]),
            ft.Row([
                ft.Text("Beneficiarios:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=120),
                ft.Text(f"{format_number_es(j.get('beneficiarios', 0))} hab.", size=12, weight=ft.FontWeight.W_600, color=COLOR_NAVY_DARK)
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
                            ft.Icon(ft.Icons.CLEANING_SERVICES_ROUNDED, color=COLOR_ELECTRIC_BLUE),
                            ft.Text(f"Jornada Hidrojet #{j.get('item', j.get('id', '-'))}", size=15, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                        ]
                    ),
                    ft.Container(
                        content=ft.Text(cat.upper(), size=10, weight=ft.FontWeight.BOLD, color=cat_color),
                        bgcolor=cat_bg,
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

    # Modal para registrar nueva jornada (Editor)
    def open_add_jornada_dialog():
        mun_opts = [ft.DropdownOption(m, m) for m in MUNICIPALITIES_LIST if m != "Todos los Municipios"]
        mun_dd = ft.Dropdown(value="GUANARE", options=mun_opts, label="Municipio", dense=True)

        fecha_field = ft.TextField(
            label="Fecha de Operación",
            value=datetime.now().strftime("%Y-%m-%d"),
            dense=True,
            text_size=12
        )

        com_field = ft.TextField(label="Comunidad / Sector", hint_text="Ej: Barrio San José", dense=True)
        dir_field = ft.TextField(label="Dirección / Calle / Carrera", hint_text="Ej: Av. 3 entre calles 15 y 16", dense=True)

        trabajo_dd = ft.Dropdown(
            label="Tipo de Trabajo Realizado",
            value="MANTENIMIENTO DE COLECTORES, BOCAS DE VISITA LIBERADAS",
            options=[
                ft.DropdownOption("MANTENIMIENTO DE COLECTORES, BOCAS DE VISITA LIBERADAS", "Colectores y Bocas de Visita"),
                ft.DropdownOption("MANTENIMIENTO DE EMPOTRAMIENTO", "Mantenimiento de Empotramiento"),
                ft.DropdownOption("MANTENIMIENTO DE TANQUILLA", "Mantenimiento de Tanquilla"),
                ft.DropdownOption("MANTENIMIENTO DE COLECTORES, BOCAS DE VISITA LIBERADAS, EMPOTRAMIENTOS LIBERADOS", "Colectores + BV + Empotramientos"),
            ],
            dense=True
        )

        long_field = ft.TextField(label="Longitud Liberada (Metros)", value="100", dense=True, keyboard_type=ft.KeyboardType.NUMBER)
        bocas_field = ft.TextField(label="Bocas de Visita Atendidas", value="1", dense=True, keyboard_type=ft.KeyboardType.NUMBER)
        emp_field = ft.TextField(label="Empotramientos Destapados", value="0", dense=True, keyboard_type=ft.KeyboardType.NUMBER)
        ben_field = ft.TextField(label="Personas Beneficiadas", value="80", dense=True, keyboard_type=ft.KeyboardType.NUMBER)

        def save_jornada(e):
            try:
                l_val = float(long_field.value or 0)
                bv_val = int(bocas_field.value or 0)
                emp_val = int(emp_field.value or 0)
                ben_val = int(ben_field.value or 0)
            except ValueError:
                return

            com_val = (com_field.value or "").strip()
            if not com_val:
                return

            state.add_hidrojet_operation(
                fecha=fecha_field.value,
                municipio=mun_dd.value,
                comunidad=com_val,
                direccion=dir_field.value or com_val,
                trabajo_realizado=trabajo_dd.value,
                longitud_m=l_val,
                bocas=bv_val,
                empotramientos=emp_val,
                beneficiarios=ben_val
            )
            page.pop_dialog()
            full_refresh()
            page.show_dialog(
                ft.SnackBar(content=ft.Text("Jornada Hidrojet registrada exitosamente.", color="#FFFFFF"), bgcolor=COLOR_STATUS_GREEN)
            )
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.ADD_TASK_ROUNDED, color=COLOR_ELECTRIC_BLUE),
                ft.Text("Registrar Jornada de Hidrojet", size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
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
                        trabajo_dd,
                        ft.Row([long_field, bocas_field], spacing=8),
                        ft.Row([emp_field, ben_field], spacing=8)
                    ]
                ),
                width=420,
                height=420
            ),
            actions=[
                ft.TextButton(content=ft.Text("Cancelar"), on_click=lambda e: page.pop_dialog() or page.update()),
                ft.FilledButton(
                    content=ft.Text("Guardar Jornada"),
                    style=ft.ButtonStyle(bgcolor=COLOR_ELECTRIC_BLUE, color="#FFFFFF"),
                    on_click=save_jornada
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=12)
        )
        page.show_dialog(dialog)
        page.update()

    # Dropdowns de filtros superiores
    def on_municipio_select(e):
        state.hidrojet_municipality = e.control.value
        full_refresh()

    def on_year_select(e):
        state.hidrojet_year = e.control.value
        full_refresh()

    dropdown_municipio = ft.Dropdown(
        value=state.hidrojet_municipality,
        options=[ft.DropdownOption(m, m if m != "Todos los Municipios" else "🏛️ Todos los Municipios") for m in MUNICIPALITIES_LIST],
        label="Municipio",
        dense=True,
        expand=True,
        on_select=on_municipio_select
    )

    dropdown_year = ft.Dropdown(
        value=state.hidrojet_year,
        options=[ft.DropdownOption(k, v) for k, v in YEARS_HIDROJET],
        label="Período",
        dense=True,
        expand=True,
        on_select=on_year_select
    )

    # 4 Tarjetas KPI Superiores Dinámicas
    def refresh_upper_kpis():
        kpis = state.get_hidrojet_kpis(state.hidrojet_municipality, state.hidrojet_year)
        kpis_row.controls.clear()

        # 1. Colectores Liberados
        kpis_row.controls.append(
            ft.Container(
                content=ft.Column(
                    spacing=2,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text("Colectores Liberados", size=10, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED),
                                ft.Icon(ft.Icons.CLEANING_SERVICES_ROUNDED, size=14, color=COLOR_ELECTRIC_BLUE)
                            ]
                        ),
                        ft.Text(f"{format_number_es(kpis['metros_liberados'], 1)} m", size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Text(f"{kpis['year']}", size=9, weight=ft.FontWeight.W_600, color=COLOR_ELECTRIC_BLUE)
                    ]
                ),
                bgcolor="#EFF6FF",
                padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                border_radius=8,
                border=ft.Border.all(1, "#BFDBFE"),
                expand=True
            )
        )

        # 2. Bocas de Visita
        kpis_row.controls.append(
            ft.Container(
                content=ft.Column(
                    spacing=2,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text("Bocas de Visita", size=10, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED),
                                ft.Icon(ft.Icons.RADIO_BUTTON_CHECKED_ROUNDED, size=14, color=COLOR_STATUS_GREEN)
                            ]
                        ),
                        ft.Text(format_number_es(kpis["bocas_de_visita"]), size=16, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN),
                        ft.Text("Desobstruidas", size=9, weight=ft.FontWeight.W_600, color=COLOR_STATUS_GREEN)
                    ]
                ),
                bgcolor="#F0FDF4",
                padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                border_radius=8,
                border=ft.Border.all(1, "#BBF7D0"),
                expand=True
            )
        )

        # 3. Empotramientos
        kpis_row.controls.append(
            ft.Container(
                content=ft.Column(
                    spacing=2,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text("Empotramientos", size=10, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED),
                                ft.Icon(ft.Icons.PLUMBING_ROUNDED, size=14, color=COLOR_NAVY_DARK)
                            ]
                        ),
                        ft.Text(format_number_es(kpis["empotramientos"]), size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Text("Destapados", size=9, weight=ft.FontWeight.W_600, color=COLOR_NAVY_DARK)
                    ]
                ),
                bgcolor="#F8FAFC",
                padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                border_radius=8,
                border=ft.Border.all(1, COLOR_BORDER),
                expand=True
            )
        )

        # 4. Beneficiarios
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
        muns = state.get_hidrojet_municipios_resumen(state.hidrojet_year)
        items = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(f"Ruta Hidrojet por Municipio ({state.hidrojet_year})", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                    ft.Text(f"{len(muns)} Municipios", size=11, color=COLOR_TEXT_MUTED, weight=ft.FontWeight.W_600)
                ]
            )
        ]

        total_metros = sum(m.get("longitud_m", 0.0) for m in muns) or 1.0

        for m in muns:
            metros_m = m.get("longitud_m", 0.0)
            pct = round((metros_m / total_metros) * 100.0, 1)
            items.append(
                ft.Container(
                    content=ft.Column(
                        spacing=6,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(m.get("municipio", ""), size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                    ft.Text(f"{format_number_es(metros_m, 1)} m Liberados ({pct}%)", size=11, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_BLUE)
                                ]
                            ),
                            ft.ProgressBar(
                                value=pct / 100.0 if pct > 0 else 0.0,
                                color=COLOR_ELECTRIC_BLUE,
                                bgcolor="#E2E8F0",
                                height=6
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(f"🔘 {format_number_es(m.get('bocas', 0))} BV", size=10, weight=ft.FontWeight.W_600, color=COLOR_STATUS_GREEN),
                                    ft.Text(f"🔧 {format_number_es(m.get('empotramientos', 0))} Emp.", size=10, weight=ft.FontWeight.W_600, color=COLOR_NAVY_DARK),
                                    ft.Text(f"📍 {format_number_es(m.get('sectores', 0))} Sectores", size=10, color=COLOR_TEXT_MUTED),
                                    ft.Text(f"📅 {format_number_es(m.get('dias_trabajados', 0))} Días", size=10, color=COLOR_TEXT_MUTED)
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

    # PESTAÑA 1: Bitácora de Jornadas Hidrojet (743)
    def build_tab_bitacora():
        nonlocal bitacora_search_query, bitacora_categoria_filtro

        jornadas = state.get_filtered_jornadas_hidrojet(
            municipio=state.hidrojet_municipality,
            categoria=bitacora_categoria_filtro,
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

        cat_dd = ft.Dropdown(
            label="Tipo de Trabajo",
            value=bitacora_categoria_filtro,
            options=[
                ft.DropdownOption("Todos", "Todos los Trabajos"),
                ft.DropdownOption("Colectores", "Colectores"),
                ft.DropdownOption("Empotramientos", "Empotramientos"),
                ft.DropdownOption("Tanquillas", "Tanquillas")
            ],
            dense=True,
            width=150,
            on_select=lambda e: update_bitacora_filters(cat=e.control.value)
        )

        def update_bitacora_filters(search=None, cat=None):
            nonlocal bitacora_search_query, bitacora_categoria_filtro
            if search is not None:
                bitacora_search_query = search
            if cat is not None:
                bitacora_categoria_filtro = cat
            render_tab_content()
            page.update()

        filter_box = ft.Container(
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Row([search_tf, cat_dd], spacing=8),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(f"Mostrando {len(jornadas)} operaciones Hidrojet (2026)", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                            ft.Text(f"{state.hidrojet_municipality}", size=10, color=COLOR_TEXT_MUTED)
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
        for j in jornadas[:120]:
            cat = j.get("categoria_trabajo", "Colectores")
            cat_bg = "#EFF6FF" if cat == "Colectores" else ("#DCFCE7" if cat == "Empotramientos" else "#FEF3C7")
            cat_color = COLOR_ELECTRIC_BLUE if cat == "Colectores" else (COLOR_STATUS_GREEN if cat == "Empotramientos" else COLOR_STATUS_AMBER)

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
                                            content=ft.Text(f"#{j.get('item', j.get('id', '-'))}", size=11, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                            bgcolor=COLOR_NAVY_DARK,
                                            padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                            border_radius=4
                                        ),
                                        ft.Text(j.get("municipio", ""), size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                        ft.Text(f"• {j.get('fecha', '')}", size=10, color=COLOR_TEXT_MUTED)
                                    ]
                                ),
                                ft.Container(
                                    content=ft.Text(cat.upper(), size=10, weight=ft.FontWeight.BOLD, color=cat_color),
                                    bgcolor=cat_bg,
                                    padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                    border_radius=4
                                )
                            ]
                        ),
                        ft.Text(j.get("comunidad", "-"), size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Text(j.get("direccion", "Sin dirección"), size=10, color=COLOR_TEXT_SECONDARY, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(f"📏 {format_number_es(j.get('longitud_m', 0), 1)} m liberados", size=10, weight=ft.FontWeight.W_600, color=COLOR_ELECTRIC_BLUE),
                                ft.Text(f"BV: {j.get('bocas', 0)} | Emp: {j.get('empotramientos', 0)}", size=10, color=COLOR_TEXT_MUTED),
                                ft.Text(f"👥 {format_number_es(j.get('beneficiarios', 0))} hab.", size=10, color=COLOR_NAVY_DARK)
                            ]
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.TextButton(
                                    content=ft.Text("Ver Ficha Completa", size=11),
                                    icon=ft.Icons.VISIBILITY_ROUNDED,
                                    on_click=lambda e, item=j: open_jornada_detail_dialog(item)
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
                on_click=lambda e, item=j: open_jornada_detail_dialog(item)
            )
            cards.append(card)

        if len(jornadas) > 120:
            cards.append(
                ft.Container(
                    content=ft.Text(f"Mostrando los primeros 120 de {len(jornadas)} registros. Utilice el buscador para afinar la consulta.", size=11, color=COLOR_TEXT_MUTED, text_align=ft.TextAlign.CENTER),
                    padding=10,
                    alignment=ft.Alignment(0, 0)
                )
            )

        return ft.ListView(controls=cards, spacing=8, expand=True)

    # PESTAÑA 2: Evolución Anual (2022–2026)
    def build_tab_evolucion():
        evol = state.get_hidrojet_evolucion_anual()
        items = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Evolución Anual Ruta del Hidrojet (2022–2026)", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                    ft.Text("Histórico Multianual", size=11, color=COLOR_TEXT_MUTED, weight=ft.FontWeight.W_600)
                ]
            )
        ]

        # Tarjetas de los 5 años
        year_cards = []
        for y in ["2022", "2023", "2024", "2025", "2026"]:
            val_m = evol.get(y, {}).get("longitud_m", 0.0)
            year_cards.append(
                ft.Container(
                    content=ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(y, size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED),
                            ft.Text(f"{format_number_es(val_m, 0)} m", size=15, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                            ft.Text("Liberados", size=9, color=COLOR_ELECTRIC_BLUE, weight=ft.FontWeight.W_600)
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
                    ft.Text("Indicadores Clave por Año", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                    ft.Text("Bocas, Empotramientos y Beneficiarios", size=11, color=COLOR_TEXT_MUTED)
                ]
            )
        )

        # Tablas visuales por año
        for y in ["2026", "2025", "2024", "2023", "2022"]:
            data_y = evol.get(y, {})
            items.append(
                ft.Container(
                    content=ft.Column(
                        spacing=4,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(f"Año {y}", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                    ft.Text(f"{format_number_es(data_y.get('longitud_m', 0), 1)} Metros Liberados", size=11, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_BLUE)
                                ]
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(f"🔘 {format_number_es(data_y.get('bocas', 0))} Bocas de Visita", size=10, weight=ft.FontWeight.W_600, color=COLOR_STATUS_GREEN),
                                    ft.Text(f"🔧 {format_number_es(data_y.get('empotramientos', 0))} Empotramientos", size=10, color=COLOR_NAVY_DARK),
                                    ft.Text(f"👥 {format_number_es(data_y.get('beneficiarios', 0))} Beneficiarios", size=10, color=COLOR_TEXT_MUTED),
                                    ft.Text(f"📍 {format_number_es(data_y.get('sectores', 0))} Sectores", size=10, color=COLOR_TEXT_MUTED)
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

    def render_tab_chips():
        tab_chips_row.controls.clear()
        tot_jornadas = len(state.hidrojet_data.get("jornadas", [])) if state.hidrojet_data else 743
        tab_names = [
            ("Resumen por Municipio", 0),
            (f"Bitácora Jornadas ({format_number_es(tot_jornadas)})", 1),
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
                        content=ft.Text("+ Registrar Jornada Hidrojet", size=12),
                        icon=ft.Icons.ADD_TASK_ROUNDED,
                        style=ft.ButtonStyle(bgcolor=COLOR_ELECTRIC_BLUE, color="#FFFFFF"),
                        on_click=lambda e: open_add_jornada_dialog(),
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

    # Inicialización
    refresh_upper_kpis()
    render_tab_chips()
    render_tab_content()

    logo_path = "assets/logo_ruta_hidrojet.png"
    leading_logo = ft.Image(
        src="logo_ruta_hidrojet.png",
        width=36,
        height=36,
        fit="contain"
    ) if os.path.exists(logo_path) else ft.Icon(
        ft.Icons.CLEANING_SERVICES_ROUNDED,
        color="#FFFFFF",
        size=24
    )

    header = create_institutional_header(
        title="Plan Ruta del Hidrojet",
        subtitle="Desobstrucción y Saneamiento con Camiones Vacuum",
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
