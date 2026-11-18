"""
Tema Institucional y Estilos Visuales
Secretaría Superior de Operaciones Generales de Portuguesa
Puesto de Comando Estratégico Operacional del Estado Portuguesa (PCEO)
"""
import sys
import flet as ft

# Compatibilidad cruzada Flet 0.x y Flet 1.x
if not hasattr(ft, "colors") and hasattr(ft, "Colors"):
    ft.colors = ft.Colors
if not hasattr(ft, "border") and hasattr(ft, "Border"):
    ft.border = ft.Border

# Paleta cromática oficial institucional (Modo Claro Profesional)
COLOR_NAVY_DARK = "#0A192F"           # Azul Marino Profundo Institucional
COLOR_NAVY_MEDIUM = "#0F284E"
COLOR_NAVY_LIGHT = "#1E3A8A"
COLOR_ELECTRIC_BLUE = "#0066FF"       # Azul Eléctrico
COLOR_ELECTRIC_LIGHT = "#0284C7"      # Azul Claro de Acento
COLOR_BG_LIGHT = "#F4F6F9"            # Fondo General Limpio Institucional
COLOR_SURFACE_WHITE = "#FFFFFF"       # Superficie de Tarjetas y Tablas Blanca Pura
COLOR_SURFACE_ELEVATED = "#EFF6FF"    # Superficies Elevadas / Destacadas
COLOR_BORDER = "#E2E8F0"              # Bordes Delimitadores Suaves
COLOR_BORDER_STRONG = "#CBD5E1"
COLOR_TEXT_PRIMARY = "#0A192F"        # Tipografía Principal Oscura de Alto Contraste
COLOR_TEXT_SECONDARY = "#475569"      # Tipografía Secundaria Gris Azulada
COLOR_TEXT_MUTED = "#64748B"          # Metadatos y Etiquetas de Apoyo

# Semáforo de estatus institucional
COLOR_STATUS_GREEN = "#16A34A"
COLOR_STATUS_GREEN_BG = "#DCFCE7"
COLOR_STATUS_GREEN_BORDER = "#86EFAC"

COLOR_STATUS_AMBER = "#D97706"
COLOR_STATUS_AMBER_BG = "#FEF3C7"
COLOR_STATUS_AMBER_BORDER = "#FDE68A"

COLOR_STATUS_RED = "#DC2626"
COLOR_STATUS_RED_BG = "#FEE2E2"
COLOR_STATUS_RED_BORDER = "#FCA5A5"

def is_dark_mode() -> bool:
    """Compatibilidad: Modo oscuro desactivado por defecto."""
    return False

def get_status_colors(status_type: str) -> dict:
    """Devuelve el conjunto de colores según el semáforo institucional."""
    status_lower = str(status_type).lower() if status_type else ""
    if any(k in status_lower for k in ["operativo", "ejecutado", "activo", "culminado", "100%", "inaugurado"]):
        return {
            "text": COLOR_STATUS_GREEN,
            "bg": COLOR_STATUS_GREEN_BG,
            "border": COLOR_STATUS_GREEN_BORDER,
            "icon": ft.Icons.CHECK_CIRCLE_ROUNDED,
            "label": "Operativo / Ejecutado"
        }
    elif any(k in status_lower for k in ["ejecución", "ejecucion", "inaugurar", "proceso", "mantenimiento", "en curso", "avance"]):
        return {
            "text": COLOR_STATUS_AMBER,
            "bg": COLOR_STATUS_AMBER_BG,
            "border": COLOR_STATUS_AMBER_BORDER,
            "icon": ft.Icons.PENDING_ACTIONS_ROUNDED,
            "label": "En Ejecución / Por Inaugurar"
        }
    else:  # Inoperativo / Paralizado
        return {
            "text": COLOR_STATUS_RED,
            "bg": COLOR_STATUS_RED_BG,
            "border": COLOR_STATUS_RED_BORDER,
            "icon": ft.Icons.ERROR_ROUNDED,
            "label": "Inoperativo / Paralizado"
        }
