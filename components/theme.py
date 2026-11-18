"""
Tema Institucional y Estilos Visuales - Soporte Bimodal (Modo Oscuro Ejecutivo / Modo Claro Institucional)
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

# Paletas cromáticas oficiales (Bimodal: Oscuro Ejecutivo vs. Claro Institucional)
DARK_PALETTE = {
    "COLOR_NAVY_DARK": "#070D1B",
    "COLOR_NAVY_MEDIUM": "#0B132B",
    "COLOR_NAVY_LIGHT": "#162A4D",
    "COLOR_ELECTRIC_BLUE": "#0066FF",
    "COLOR_ELECTRIC_LIGHT": "#38BDF8",
    "COLOR_BG_LIGHT": "#070D1B",           # Fondo general estelar
    "COLOR_SURFACE_WHITE": "#111E38",       # Tarjetas con superficie oscura sólida
    "COLOR_SURFACE_ELEVATED": "#172649",    # Contenedores internos elevados
    "COLOR_BORDER": "#1E293B",              # Bordes oscuros sutiles
    "COLOR_BORDER_STRONG": "#334155",
    "COLOR_TEXT_PRIMARY": "#FFFFFF",        # Estrictamente blanco puro
    "COLOR_TEXT_SECONDARY": "#E2E8F0",      # Gris claro de alto contraste
    "COLOR_TEXT_MUTED": "#94A3B8",          # Metadatos y etiquetas secundarias
    "COLOR_STATUS_GREEN": "#22C55E",
    "COLOR_STATUS_GREEN_BG": "#064E3B40",
    "COLOR_STATUS_GREEN_BORDER": "#16A34A80",
    "COLOR_STATUS_AMBER": "#F59E0B",
    "COLOR_STATUS_AMBER_BG": "#78350F40",
    "COLOR_STATUS_AMBER_BORDER": "#D9770680",
    "COLOR_STATUS_RED": "#EF4444",
    "COLOR_STATUS_RED_BG": "#7F1D1D40",
    "COLOR_STATUS_RED_BORDER": "#DC262680",
}

LIGHT_PALETTE = {
    "COLOR_NAVY_DARK": "#0F172A",
    "COLOR_NAVY_MEDIUM": "#1E293B",
    "COLOR_NAVY_LIGHT": "#2563EB",
    "COLOR_ELECTRIC_BLUE": "#0066FF",
    "COLOR_ELECTRIC_LIGHT": "#0284C7",
    "COLOR_BG_LIGHT": "#F1F5F9",           # Fondo general limpio y profesional
    "COLOR_SURFACE_WHITE": "#FFFFFF",       # Tarjetas blancas puras
    "COLOR_SURFACE_ELEVATED": "#F8FAFC",    # Superficies elevadas claras
    "COLOR_BORDER": "#E2E8F0",              # Bordes definidos claros
    "COLOR_BORDER_STRONG": "#CBD5E1",
    "COLOR_TEXT_PRIMARY": "#0F172A",        # Textos oscuros legibles
    "COLOR_TEXT_SECONDARY": "#334155",      # Textos secundarios oscuros
    "COLOR_TEXT_MUTED": "#64748B",          # Textos atenuados legibles
    "COLOR_STATUS_GREEN": "#16A34A",
    "COLOR_STATUS_GREEN_BG": "#DCFCE7",
    "COLOR_STATUS_GREEN_BORDER": "#86EFAC",
    "COLOR_STATUS_AMBER": "#D97706",
    "COLOR_STATUS_AMBER_BG": "#FEF3C7",
    "COLOR_STATUS_AMBER_BORDER": "#FDE68A",
    "COLOR_STATUS_RED": "#DC2626",
    "COLOR_STATUS_RED_BG": "#FEE2E2",
    "COLOR_STATUS_RED_BORDER": "#FCA5A5",
}

# Inicializar por defecto en Modo Oscuro Ejecutivo
CURRENT_THEME_IS_DARK = True

COLOR_NAVY_DARK = DARK_PALETTE["COLOR_NAVY_DARK"]
COLOR_NAVY_MEDIUM = DARK_PALETTE["COLOR_NAVY_MEDIUM"]
COLOR_NAVY_LIGHT = DARK_PALETTE["COLOR_NAVY_LIGHT"]
COLOR_ELECTRIC_BLUE = DARK_PALETTE["COLOR_ELECTRIC_BLUE"]
COLOR_ELECTRIC_LIGHT = DARK_PALETTE["COLOR_ELECTRIC_LIGHT"]
COLOR_BG_LIGHT = DARK_PALETTE["COLOR_BG_LIGHT"]
COLOR_SURFACE_WHITE = DARK_PALETTE["COLOR_SURFACE_WHITE"]
COLOR_SURFACE_ELEVATED = DARK_PALETTE["COLOR_SURFACE_ELEVATED"]
COLOR_BORDER = DARK_PALETTE["COLOR_BORDER"]
COLOR_BORDER_STRONG = DARK_PALETTE["COLOR_BORDER_STRONG"]
COLOR_TEXT_PRIMARY = DARK_PALETTE["COLOR_TEXT_PRIMARY"]
COLOR_TEXT_SECONDARY = DARK_PALETTE["COLOR_TEXT_SECONDARY"]
COLOR_TEXT_MUTED = DARK_PALETTE["COLOR_TEXT_MUTED"]
COLOR_STATUS_GREEN = DARK_PALETTE["COLOR_STATUS_GREEN"]
COLOR_STATUS_GREEN_BG = DARK_PALETTE["COLOR_STATUS_GREEN_BG"]
COLOR_STATUS_GREEN_BORDER = DARK_PALETTE["COLOR_STATUS_GREEN_BORDER"]
COLOR_STATUS_AMBER = DARK_PALETTE["COLOR_STATUS_AMBER"]
COLOR_STATUS_AMBER_BG = DARK_PALETTE["COLOR_STATUS_AMBER_BG"]
COLOR_STATUS_AMBER_BORDER = DARK_PALETTE["COLOR_STATUS_AMBER_BORDER"]
COLOR_STATUS_RED = DARK_PALETTE["COLOR_STATUS_RED"]
COLOR_STATUS_RED_BG = DARK_PALETTE["COLOR_STATUS_RED_BG"]
COLOR_STATUS_RED_BORDER = DARK_PALETTE["COLOR_STATUS_RED_BORDER"]

class ThemeManager:
    """Gestor de Estado Global del Tema (Bimodal: Oscuro Ejecutivo / Claro Institucional)."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance.is_dark = CURRENT_THEME_IS_DARK
        return cls._instance

    @property
    def is_dark_mode(self) -> bool:
        return CURRENT_THEME_IS_DARK

    @property
    def bg(self) -> str:
        return COLOR_BG_LIGHT

    @property
    def surface(self) -> str:
        return COLOR_SURFACE_WHITE

    @property
    def surface_elevated(self) -> str:
        return COLOR_SURFACE_ELEVATED

    @property
    def border(self) -> str:
        return COLOR_BORDER

    @property
    def border_strong(self) -> str:
        return COLOR_BORDER_STRONG

    @property
    def text_primary(self) -> str:
        return COLOR_TEXT_PRIMARY

    @property
    def text_secondary(self) -> str:
        return COLOR_TEXT_SECONDARY

    @property
    def text_muted(self) -> str:
        return COLOR_TEXT_MUTED

    def set_theme(self, is_dark: bool):
        set_theme_mode(is_dark)

    def toggle(self):
        set_theme_mode(not CURRENT_THEME_IS_DARK)

theme = ThemeManager()

def is_dark_mode() -> bool:
    """Devuelve True si el tema actual es Modo Oscuro Ejecutivo."""
    return CURRENT_THEME_IS_DARK

def set_theme_mode(is_dark: bool):
    """Actualiza dinámicamente la paleta de colores en components.theme y en los módulos importados."""
    global CURRENT_THEME_IS_DARK
    CURRENT_THEME_IS_DARK = is_dark
    theme.is_dark = is_dark
    palette = DARK_PALETTE if is_dark else LIGHT_PALETTE

    this_mod = sys.modules.get("components.theme")
    for k, v in palette.items():
        globals()[k] = v
        if this_mod:
            setattr(this_mod, k, v)

    # Propagar dinámicamente a todos los módulos dependientes cargados
    for mod_name, mod in list(sys.modules.items()):
        if mod and (mod_name.startswith("modules.") or mod_name.startswith("components.") or mod_name == "main"):
            for k, v in palette.items():
                if hasattr(mod, k):
                    setattr(mod, k, v)

def get_status_colors(status_type: str) -> dict:
    """Devuelve el conjunto de colores según el semáforo institucional adaptado al tema actual."""
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

def create_theme_toggle_switch(on_change=None, is_dark: bool = None) -> ft.Container:
    """
    Crea el control oficial permanente de alternancia de tema (Sol / Luna).
    Permite alternar al instante entre Modo Oscuro Ejecutivo y Modo Claro Institucional.
    """
    if is_dark is None:
        is_dark = is_dark_mode()

    def handle_toggle(val: bool):
        if on_change:
            on_change(val)
        else:
            from data.state import AppState
            AppState().set_theme(val)

    icon_sun = ft.Icon(
        ft.Icons.WB_SUNNY_ROUNDED,
        size=15,
        color="#F59E0B" if not is_dark else "#94A3B8"
    )
    icon_moon = ft.Icon(
        ft.Icons.NIGHTLIGHT_ROUNDED,
        size=15,
        color="#38BDF8" if is_dark else "#94A3B8"
    )

    switch_ctrl = ft.Switch(
        value=is_dark,
        active_color="#0066FF",
        active_track_color="#1E3A8A",
        inactive_thumb_color="#F59E0B",
        inactive_track_color="#FED7AA",
        on_change=lambda e: handle_toggle(e.control.value),
        scale=0.75
    )

    return ft.Container(
        content=ft.Row(
            spacing=4,
            tight=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                icon_sun,
                switch_ctrl,
                icon_moon
            ]
        ),
        padding=ft.Padding.symmetric(horizontal=8, vertical=2),
        bgcolor=COLOR_SURFACE_ELEVATED if is_dark else "#EFF6FF",
        border_radius=20,
        border=ft.Border.all(1, COLOR_BORDER if is_dark else "#BFDBFE"),
        tooltip=f"Tema: {'Oscuro Ejecutivo' if is_dark else 'Claro Institucional'}. Clic para alternar."
    )
