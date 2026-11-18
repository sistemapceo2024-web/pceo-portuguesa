"""
Semáforos de Estado Institucional (Material Design 3)
Verde: Operativo / Ejecutado
Ámbar: En Ejecución / Por Inaugurar
Rojo: Inoperativo / Paralizado
"""
import flet as ft
from components.theme import (
    COLOR_STATUS_GREEN,
    COLOR_STATUS_GREEN_BG,
    COLOR_STATUS_GREEN_BORDER,
    COLOR_STATUS_AMBER,
    COLOR_STATUS_AMBER_BG,
    COLOR_STATUS_AMBER_BORDER,
    COLOR_STATUS_RED,
    COLOR_STATUS_RED_BG,
    COLOR_STATUS_RED_BORDER,
    get_status_colors
)

def create_semaphore_badge(status_label: str, compact: bool = False) -> ft.Container:
    """Crea una pastilla institucional de estado semaforizado."""
    colors = get_status_colors(status_label)
    
    if compact:
        return ft.Container(
            content=ft.Row(
                spacing=5,
                tight=True,
                controls=[
                    ft.Container(
                        width=8,
                        height=8,
                        border_radius=4,
                        bgcolor=colors["text"]
                    ),
                    ft.Text(
                        status_label,
                        size=11,
                        weight=ft.FontWeight.W_600,
                        color=colors["text"]
                    )
                ]
            ),
            padding=ft.Padding.symmetric(horizontal=8, vertical=3),
            bgcolor=colors["bg"],
            border=ft.Border.all(1, colors["border"]),
            border_radius=12
        )

    return ft.Container(
        content=ft.Row(
            spacing=6,
            tight=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(colors["icon"], size=14, color=colors["text"]),
                ft.Text(
                    status_label,
                    size=12,
                    weight=ft.FontWeight.W_700,
                    color=colors["text"]
                )
            ]
        ),
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        bgcolor=colors["bg"],
        border=ft.Border.all(1, colors["border"]),
        border_radius=16
    )

def create_status_dot(status_label: str, size: int = 10) -> ft.Container:
    """Punto de semáforo simple para listas o tablas."""
    colors = get_status_colors(status_label)
    return ft.Container(
        width=size,
        height=size,
        border_radius=size // 2,
        bgcolor=colors["text"],
        tooltip=status_label
    )
