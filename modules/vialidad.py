"""
Módulo Detallado: Vialidad Rural y Urbana
Secretaría Superior de Operaciones Generales - Gobernación del Estado Portuguesa
"""
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
from components.semaphore import create_semaphore_badge
from data.water_data import MUNICIPALITIES_LIST
from data.cero_botes_data import YEARS_LIST
from data.state import AppState

def build_vialidad_view(
    page: ft.Page,
    on_back_to_summary,
    on_switch_role,
    on_logout
) -> ft.Control:
    state = AppState()
    selected_mun = "Todos los Municipios"
    selected_yr = "Acumulado Total"

    kpis_row = ft.Row(spacing=8)
    content_area = ft.Container(expand=True)

    def refresh_upper_kpis():
        kpis_row.controls.clear()
        kpis = [
            ('Caminos Agrícolas', '1.450 km', 'Rehabilitados', 'ft.Icons.ALT_ROUTE_ROUNDED', '#0284C7'),
            ('Maquinarias', '65', 'Patroles y Orugas', 'ft.Icons.PRECISION_MANUFACTURING_ROUNDED', '#16A34A'),
            ('Caseríos Conectados', '320', 'Rutas de Cosecha', 'ft.Icons.AGRICULTURE_ROUNDED', '#D97706'),
            ('Productores', '18.500', 'Apoyados', 'ft.Icons.PEOPLE_ALT_ROUNDED', '#7C3AED'),
        ]
        for name, val, sub, icon_data, color_str in kpis:
            kpis_row.controls.append(
                ft.Container(
                    content=ft.Column(
                        spacing=2,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(name, size=10, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED),
                                    ft.Icon(icon_data, size=14, color=color_str)
                                ]
                            ),
                            ft.Text(val, size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                            ft.Text(sub, size=9, weight=ft.FontWeight.W_600, color=color_str)
                        ]
                    ),
                    bgcolor="#F8FAFC",
                    padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                    border_radius=8,
                    border=ft.Border.all(1, COLOR_BORDER),
                    expand=True
                )
            )

    def render_content():
        items = [
            ft.Container(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Despliegue Operativo e Intervenciones", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Text(f"{selected_mun} • {selected_yr}", size=11, color="#64748B")
                    ]
                ),
                padding=ft.Padding.symmetric(vertical=4)
            )
        ]

        muns_to_show = [selected_mun] if selected_mun != "Todos los Municipios" else [m for m in MUNICIPALITIES_LIST if m != "Todos los Municipios"]
        for m_name in muns_to_show:
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
                                        ft.Icon(ft.Icons.ALT_ROUTE_ROUNDED, size=16, color=COLOR_ELECTRIC_BLUE),
                                        ft.Text(f"Municipio {m_name}", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                                    ]
                                ),
                                create_semaphore_badge("Operativo / Ejecutado", compact=True)
                            ]
                        ),
                        ft.Text(
                            "Operatividad y fiscalización técnica continua en campo por la Gobernación de Portuguesa.",
                            size=11,
                            color=COLOR_TEXT_SECONDARY
                        )
                    ]
                ),
                bgcolor=COLOR_SURFACE_WHITE,
                padding=10,
                border_radius=8,
                border=ft.Border.all(1, COLOR_BORDER)
            )
            items.append(card)

        content_area.content = ft.ListView(controls=items, spacing=8, expand=True)

    def full_refresh():
        refresh_upper_kpis()
        render_content()
        page.update()

    def open_add_dialog():
        mun_opts = [ft.DropdownOption(m, m) for m in MUNICIPALITIES_LIST if m != "Todos los Municipios"]
        mun_dd = ft.Dropdown(value=mun_opts[0].key, options=mun_opts, label="Municipio", dense=True)
        yr_opts = [ft.DropdownOption(y, y) for y in YEARS_LIST if y != "Acumulado Total"]
        yr_dd = ft.Dropdown(value="2026", options=yr_opts, label="Año", dense=True)
        cant_field = ft.TextField(label="Metas / Cantidad a Asentar", value="1", dense=True)
        notes_field = ft.TextField(label="Observaciones Técnicas", hint_text="Comunidad, especificaciones...", dense=True)

        def save_action(e):
            page.pop_dialog()
            full_refresh()
            page.show_dialog(
                ft.SnackBar(content=ft.Text("Registro institucional guardado exitosamente.", color="#FFFFFF"), bgcolor=COLOR_NAVY_DARK)
            )
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([ft.Icon(ft.Icons.ALT_ROUTE_ROUNDED, color=COLOR_ELECTRIC_BLUE), ft.Text("Vialidad Rural y Urbana", size=16, weight=ft.FontWeight.BOLD)]),
            content=ft.Container(
                content=ft.Column(tight=True, spacing=8, controls=[mun_dd, yr_dd, cant_field, notes_field]),
                width=380
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog() or page.update()),
                ft.FilledButton("Guardar", style=ft.ButtonStyle(bgcolor=COLOR_ELECTRIC_BLUE, color="#FFFFFF"), on_click=save_action)
            ]
        )
        page.show_dialog(dialog)
        page.update()

    mun_filter = ft.Dropdown(
        value=selected_mun,
        options=[ft.DropdownOption(m, m if m != "Todos los Municipios" else "🏛️ Todos los Municipios") for m in MUNICIPALITIES_LIST],
        label="Municipio",
        dense=True,
        expand=True
    )
    def on_m_select(e):
        nonlocal selected_mun
        selected_mun = e.control.value
        full_refresh()
    mun_filter.on_select = on_m_select

    year_filter = ft.Dropdown(
        value=selected_yr,
        options=[ft.DropdownOption(y, f"📅 {y}") for y in YEARS_LIST],
        label="Año",
        dense=True,
        width=150
    )
    def on_y_select(e):
        nonlocal selected_yr
        selected_yr = e.control.value
        full_refresh()
    year_filter.on_select = on_y_select

    filter_bar = ft.Container(
        content=ft.Row([mun_filter, year_filter]),
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        bgcolor=COLOR_SURFACE_WHITE,
        border_radius=8,
        border=ft.Border.all(1, COLOR_BORDER)
    )

    editor_bar = None
    if state.is_editor():
        editor_bar = ft.Container(
            content=ft.FilledButton(
                "+ Registrar Mantenimiento de Camino Rural",
                icon=ft.Icons.ADD_TASK_ROUNDED,
                style=ft.ButtonStyle(bgcolor=COLOR_ELECTRIC_BLUE, color="#FFFFFF"),
                on_click=lambda e: open_add_dialog(),
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

    refresh_upper_kpis()
    render_content()

    header = create_institutional_header(
        title="Vialidad Rural y Urbana",
        subtitle="Caminos de Penetración Agrícola y Conectividad Productiva",
        current_role=state.current_role,
        show_back_button=True,
        on_back_click=lambda e: on_back_to_summary(),
        on_switch_role_click=on_switch_role,
        on_logout_click=on_logout
    )

    return ft.Column(
        spacing=0,
        expand=True,
        controls=[
            header,
            ft.Container(
                content=ft.Column(
                    spacing=10,
                    controls=[filter_bar, kpis_row, content_area],
                    expand=True
                ),
                padding=12,
                expand=True
            ),
            editor_bar
        ]
    )
