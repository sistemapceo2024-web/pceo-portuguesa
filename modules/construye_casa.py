"""
Módulo Plan Construye Tu Casa - Redirección a modules.construye_tu_casa
PCEO - Gobernación del Estado Portuguesa
"""
import flet as ft
from modules.construye_tu_casa import build_construye_tu_casa_view

def build_construye_casa_view(
    page: ft.Page,
    on_back_to_summary,
    on_switch_role,
    on_logout
) -> ft.Control:
    """Wrapper para compatibilidad con llamadas a build_construye_casa_view."""
    return build_construye_tu_casa_view(
        page=page,
        on_back_to_summary=on_back_to_summary,
        on_switch_role=on_switch_role,
        on_logout=on_logout
    )
