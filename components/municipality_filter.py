"""
Selector Desplegable de los 14 Municipios de Portuguesa (Material Design 3)
Secretaría Superior de Operaciones Generales
"""
import flet as ft
from components.theme import (
    COLOR_NAVY_DARK,
    COLOR_ELECTRIC_BLUE,
    COLOR_SURFACE_WHITE,
    COLOR_BORDER,
    COLOR_TEXT_PRIMARY
)
from data.water_data import MUNICIPALITIES_LIST

def create_municipality_dropdown(selected_value: str, on_change_callback) -> ft.Container:
    """Crea el componente selector de los 14 municipios del estado Portuguesa."""
    options = [
        ft.DropdownOption(
            key=mun,
            text=mun if mun != "Todos los Municipios" else "🏛️ Todos los 14 Municipios"
        )
        for mun in MUNICIPALITIES_LIST
    ]

    dropdown = ft.Dropdown(
        value=selected_value,
        options=options,
        on_select=on_change_callback,
        border_radius=10,
        text_size=13,
        bgcolor=COLOR_SURFACE_WHITE,
        dense=True,
        content_padding=ft.Padding.symmetric(horizontal=12, vertical=8),
        leading_icon=ft.Icons.LOCATION_CITY_ROUNDED,
        color=COLOR_TEXT_PRIMARY,
        label="Filtrar por Municipio de Portuguesa",
        label_style=ft.TextStyle(size=11, color="#64748B"),
        expand=True
    )

    return ft.Container(
        content=ft.Row(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    content=ft.Icon(ft.Icons.MAP_ROUNDED, color=COLOR_ELECTRIC_BLUE, size=20),
                    padding=ft.Padding.only(left=2)
                ),
                dropdown
            ]
        ),
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        bgcolor=COLOR_SURFACE_WHITE,
        border_radius=12,
        border=ft.Border.all(1, COLOR_BORDER),
    )
