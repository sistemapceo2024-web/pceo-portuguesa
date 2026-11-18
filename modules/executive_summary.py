"""
Módulo Pantalla Principal: Resumen Ejecutivo y Menú Lateral de Municipios
Puesto de Comando Estratégico Operacional del Estado Portuguesa (PCEO)
Gobernación del Estado Portuguesa
"""
import os
import flet as ft
from components.theme import (
    COLOR_NAVY_DARK,
    COLOR_NAVY_LIGHT,
    COLOR_ELECTRIC_BLUE,
    COLOR_ELECTRIC_LIGHT,
    COLOR_SURFACE_WHITE,
    COLOR_SURFACE_ELEVATED,
    COLOR_BG_LIGHT,
    COLOR_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    COLOR_STATUS_GREEN,
    COLOR_STATUS_AMBER,
    COLOR_STATUS_RED,
    create_theme_toggle_switch,
    is_dark_mode
)
from components.header import create_institutional_header
from components.kpi_card import create_plan_kpi_card
from components.print_municipal_report import open_print_preview_dialog
from data.government_plans import GOVERNMENT_PLANS
from data.state import AppState, normalize_name
from datetime import datetime

MUNICIPIOS_ORDEN = [
    "Guanare",
    "Páez",
    "Araure",
    "Turén",
    "Esteller",
    "Ospino",
    "Sucre",
    "Unda",
    "San Genaro de Boconoíto",
    "Guanarito",
    "Santa Rosalía",
    "Agua Blanca",
    "San Rafael de Onoto",
    "Papelón"
]

def build_executive_summary_view(
    page: ft.Page,
    on_open_plan,
    on_switch_role,
    on_logout,
    on_open_users=None,
    on_theme_toggle=None
) -> ft.Control:
    """Construye la vista de Resumen Ejecutivo con Menú Lateral Inteligente de Municipios."""
    state = AppState()
    current_selected_mun = {"value": "TODOS"}

    header = create_institutional_header(
        title="Puesto de Comando Estratégico Operacional del Estado Portuguesa (PCEO)",
        subtitle=None,
        show_back_button=False,
        show_user_chip=False,
        on_theme_toggle=on_theme_toggle
    )

    # -------------------------------------------------------------
    # 1. CONTENIDO CENTRAL: CONSOLIDADO GENERAL ESTATAL (TODOS)
    # -------------------------------------------------------------
    escudo_widget = (
        ft.Image(src="logo_pceo.png", width=34, height=34, fit=ft.BoxFit.CONTAIN)
        if os.path.exists("assets/logo_pceo.png")
        else ft.Icon(ft.Icons.SHIELD_ROUNDED, color=COLOR_ELECTRIC_BLUE, size=24)
    )

    title_bar = ft.Container(
        content=ft.Row(
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    content=escudo_widget,
                    padding=ft.Padding.all(4),
                    bgcolor=COLOR_SURFACE_ELEVATED,
                    border_radius=8,
                    border=ft.Border.all(1, "#1E3A8A")
                ),
                ft.Text(
                    "Planes de Gobierno - Gobernación del Estado Portuguesa",
                    size=15,
                    weight=ft.FontWeight.BOLD,
                    color=COLOR_TEXT_PRIMARY,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS
                )
            ]
        ),
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        bgcolor=COLOR_SURFACE_WHITE,
        border_radius=12,
        border=ft.Border.all(1, COLOR_BORDER),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=10,
            color="#30000000",
            offset=ft.Offset(0, 3)
        )
    )

    cards_list = []
    for plan in GOVERNMENT_PLANS:
        card = create_plan_kpi_card(
            plan=plan,
            on_click=lambda e, pid=plan.id: on_open_plan(pid)
        )
        cards_list.append(card)

    state_scroll_view = ft.ListView(
        controls=[
            title_bar,
            *cards_list,
            ft.Container(height=24)
        ],
        spacing=12,
        padding=14,
        expand=True
    )

    # -------------------------------------------------------------
    # 2. HELPER PARA NAVEGAR A UN PLAN CON FILTRO MUNICIPAL ACTIVO
    # -------------------------------------------------------------
    def navigate_to_module_with_mun(plan_id: str, mun: str):
        if mun and mun != "TODOS":
            if plan_id == "fiesta_agua":
                state.active_municipality = mun
            elif plan_id == "cero_botes":
                state.cero_botes_municipality = mun
            elif plan_id == "tramos_caidos":
                state.tramos_municipality = mun
            elif plan_id == "ruta_hidrojet":
                state.hidrojet_municipality = mun
            elif plan_id == "fiesta_luz":
                state.fiesta_luz_municipality = mun
            elif plan_id == "puentes":
                state.puentes_municipality = mun
            elif plan_id == "salud":
                state.salud_municipality = mun
            elif plan_id in ["educacion", "escuelas"]:
                state.escuelas_municipality = mun
            elif plan_id in ["canchas", "cancha_para_todos"]:
                state.canchas_municipality = mun
            elif plan_id in ["canalizacion", "canalizaciones"]:
                state.canalizacion_municipality = mun
            elif plan_id in ["construye_casa", "construye_tu_casa"]:
                state.casas_municipality = mun
        on_open_plan(plan_id)

    # -------------------------------------------------------------
    # 3. CONSTRUCTOR DEL DASHBOARD CONSOLIDADO POR MUNICIPIO
    # -------------------------------------------------------------
    def build_mini_kpi_card(title: str, value: str, subtitle: str, icon: str, icon_color: str, icon_bg: str) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                spacing=6,
                horizontal_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Row(
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                content=ft.Icon(icon, size=16, color=icon_color),
                                width=30,
                                height=30,
                                border_radius=6,
                                bgcolor=COLOR_SURFACE_ELEVATED,
                                alignment=ft.Alignment(0, 0)
                            ),
                            ft.Container(
                                content=ft.Text(title, size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                expand=True
                            )
                        ]
                    ),
                    ft.Text(value, size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
                    ft.Text(subtitle, size=10, color=COLOR_TEXT_SECONDARY, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)
                ]
            ),
            bgcolor=COLOR_SURFACE_WHITE,
            padding=12,
            border_radius=10,
            border=ft.Border(
                top=ft.BorderSide(3, icon_color),
                left=ft.BorderSide(1, COLOR_BORDER),
                right=ft.BorderSide(1, COLOR_BORDER),
                bottom=ft.BorderSide(1, COLOR_BORDER)
            ),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=8, color="#25000000", offset=ft.Offset(0, 3)),
            expand=True
        )

    def build_municipio_dashboard(mun: str) -> ft.Control:
        # Extracción de datos oficiales para el municipio
        pozos = state.get_kpis(mun)
        botes = state.get_cero_botes_kpis(mun, "Acumulado Total")
        tramos = state.get_tramos_caidos_kpis(mun)
        hidro = state.get_hidrojet_kpis(mun, "Acumulado Total")
        luz = state.get_fiesta_luz_kpis(mun)
        pue = state.get_puentes_kpis(mun)
        salud = state.get_salud_kpis(mun)
        esc = state.get_escuelas_kpis(mun)
        can = state.get_canchas_kpis(mun)
        casas = state.get_casas_kpis(mun)
        canal = state.get_canalizacion_kpis(mun)

        # Cero Huecos (sumar ubicaciones que coinciden con el municipio)
        m_norm = normalize_name(mun)
        ubs = state.cero_huecos_data.get("ubicaciones", []) if state.cero_huecos_data else []
        matched_ubs = [u for u in ubs if m_norm in normalize_name(u.get("nombre", ""))]
        ton_asf = sum(u.get("Total Acumulado", {}).get("toneladas", 0) for u in matched_ubs)
        fallas_asf = sum(u.get("Total Acumulado", {}).get("fallas", 0) for u in matched_ubs)

        # Totales físicos de obras en la localidad
        culm_total = (
            salud.get("culminadas", 0) +
            esc.get("culminadas", 0) +
            can.get("culminadas", 0) +
            pue.get("ejecutadas", 0) +
            tramos.get("ejecutados", 0) +
            casas.get("ejecutadas", 0) +
            canal.get("ejecutadas", 0)
        )
        proc_total = (
            salud.get("en_proceso", 0) +
            esc.get("en_ejecucion", 0) +
            can.get("en_ejecucion", 0) +
            pue.get("en_desarrollo", 0) +
            tramos.get("por_ejecutar", 0) +
            casas.get("proyeccion_ejecucion", 0) +
            canal.get("en_desarrollo", 0)
        )
        para_total = (
            salud.get("paralizadas", 0) +
            esc.get("paralizadas", 0) +
            can.get("paralizadas", 0) +
            pue.get("paralizadas", 0) +
            canal.get("paralizadas", 0)
        )
        total_obras = culm_total + proc_total + para_total
        pct_culm = round((culm_total / total_obras * 100), 1) if total_obras > 0 else 0.0
        pct_proc = round((proc_total / total_obras * 100), 1) if total_obras > 0 else 0.0
        pct_para = round((para_total / total_obras * 100), 1) if total_obras > 0 else 0.0

        # 1. Definición estructurada de planes y datos para el reporte
        plans_data = [
            {
                "id": "fiesta_agua",
                "name": "Fiesta del Agua",
                "icon": ft.Icons.WATER_DROP_ROUNDED,
                "color": "#0284C7",
                "bg": "#E0F2FE",
                "metric": f"{pozos['pozos_operativos']} Pozos Operativos / {pozos['total_pozos']} Totales",
                "detail": f"{pozos['pct_operativo']}% Operatividad • {pozos['plantas_op']} Plantas • {pozos['rebombeo_op']} Rebombeos",
                "status": f"{pozos['pct_operativo']}% Op",
                "status_color": "#16A34A" if pozos['pct_operativo'] >= 80 else "#D97706"
            },
            {
                "id": "cero_botes",
                "name": "Plan Cero Botes de Agua",
                "icon": ft.Icons.PLUMBING_ROUNDED,
                "color": "#2563EB",
                "bg": "#EFF6FF",
                "metric": f"{botes['botes']:,.0f} Botes Reparados",
                "detail": f"{botes['caudal_lps']:,.1f} Lps recuperados • {botes['beneficiarios']:,.0f} Beneficiarios",
                "status": "Activo",
                "status_color": "#16A34A"
            },
            {
                "id": "tramos_caidos",
                "name": "Plan Tramos Caídos",
                "icon": ft.Icons.ENGINEERING_ROUNDED,
                "color": "#0D9488",
                "bg": "#CCFBF1",
                "metric": f"{tramos['ejecutados']} Tramos Ejecutados de {tramos['tramos_totales']}",
                "detail": f"{tramos['metros_sustituidos']:,.1f} m sustituidos • {tramos['por_ejecutar']} pendientes",
                "status": f"{tramos['pct_ejecutado']}%",
                "status_color": "#16A34A" if tramos['pct_ejecutado'] >= 75 else "#D97706"
            },
            {
                "id": "ruta_hidrojet",
                "name": "Ruta del Hidrojet",
                "icon": ft.Icons.CLEANING_SERVICES_ROUNDED,
                "color": "#0891B2",
                "bg": "#CFFAFE",
                "metric": f"{hidro['metros_liberados']:,.1f} m Liberados",
                "detail": f"{hidro['bocas_de_visita']} Bocas de visita • {hidro['empotramientos']} Empotramientos",
                "status": f"{hidro['dias_trabajados']} Jornadas",
                "status_color": "#0284C7"
            },
            {
                "id": "cero_huecos",
                "name": "Plan Cero Huecos",
                "icon": ft.Icons.DIRECTIONS_CAR_ROUNDED,
                "color": "#D97706",
                "bg": "#FEF3C7",
                "metric": f"{ton_asf:,.1f} Toneladas de Asfalto",
                "detail": f"{fallas_asf:,.0f} Fallas viales atendidas en el municipio",
                "status": "Operativo",
                "status_color": "#16A34A"
            },
            {
                "id": "fiesta_luz",
                "name": "Fiesta de la Luz",
                "icon": ft.Icons.LIGHTBULB_ROUNDED,
                "color": "#CA8A04",
                "bg": "#FEF9C3",
                "metric": f"{luz['luminarias']:,.0f} Luminarias Instaladas",
                "detail": f"{luz['tx_instalados']} Transformadores • {luz['puntos_apagados']} Puntos apagados",
                "status": f"{luz['sectores']} Sectores",
                "status_color": "#0284C7"
            },
            {
                "id": "puentes",
                "name": "Puentes y Alcantarillas",
                "icon": ft.Icons.CONSTRUCTION_ROUNDED,
                "color": "#4F46E5",
                "bg": "#EEF2FF",
                "metric": f"{pue['ejecutadas']} Obras Culminadas de {pue['total_obras']}",
                "detail": f"{pue['puentes']} Puentes • {pue['alcantarillas']} Alcantarillas • {pue['paralizadas']} Paralizadas",
                "status": f"{pue['pct_ejecutado']}%",
                "status_color": "#16A34A" if pue['pct_ejecutado'] >= 80 else "#D97706"
            },
            {
                "id": "salud",
                "name": "Espacios de Salud",
                "icon": ft.Icons.LOCAL_HOSPITAL_ROUNDED,
                "color": "#E11D48",
                "bg": "#FFE4E6",
                "metric": f"{salud['culminadas']} Centros Rehabilitados de {salud['total_obras']}",
                "detail": f"{salud['en_proceso']} En proceso • {salud['paralizadas']} Paralizados",
                "status": f"{salud['pct_culminadas']}%",
                "status_color": "#16A34A" if salud['pct_culminadas'] >= 80 else "#D97706"
            },
            {
                "id": "educacion",
                "name": "Centros Educativos",
                "icon": ft.Icons.SCHOOL_ROUNDED,
                "color": "#16A34A",
                "bg": "#DCFCE7",
                "metric": f"{esc['culminadas']} Escuelas Rehabilitadas de {esc['total_centros']}",
                "detail": f"{esc['en_ejecucion']} En proceso • {esc['paralizadas']} Paralizadas",
                "status": f"{esc['pct_culminadas']}%",
                "status_color": "#16A34A" if esc['pct_culminadas'] >= 80 else "#D97706"
            },
            {
                "id": "canchas",
                "name": "Una Cancha para Todos",
                "icon": ft.Icons.SPORTS_BASKETBALL_ROUNDED,
                "color": "#7C3AED",
                "bg": "#F3E8FF",
                "metric": f"{can['culminadas']} Canchas Culminadas de {can['total_intervenidas']}",
                "detail": f"{can['en_ejecucion']} En ejecución • {can['paralizadas']} Paralizadas",
                "status": f"{can['pct_culminadas']}%",
                "status_color": "#16A34A" if can['pct_culminadas'] >= 80 else "#D97706"
            },
            {
                "id": "construye_tu_casa",
                "name": "Construye Tu Casa",
                "icon": ft.Icons.HOUSE_ROUNDED,
                "color": "#D97706",
                "bg": "#FEF3C7",
                "metric": f"{casas['ejecutadas']} Viviendas Ejecutadas / {casas['total_viviendas']} Totales",
                "detail": f"{casas['proyeccion_ejecucion']} En Ejecución • Ente: FONDEREVI",
                "status": f"{casas['pct_ejecutadas']}%",
                "status_color": "#16A34A" if casas['pct_ejecutadas'] >= 50 else ("#D97706" if casas['pct_ejecutadas'] > 0 else "#64748B")
            },
            {
                "id": "canalizacion",
                "name": "Canalización y Bermas",
                "icon": ft.Icons.WATER_ROUNDED,
                "color": "#0284C7",
                "bg": "#E0F2FE",
                "metric": f"{canal['longitud_canalizada_km']:,.2f} km Canalizados",
                "detail": f"{canal['ejecutadas']} Obras Ejecutadas • {canal['bermas']} Bermas • {canal['frentes']} Frentes Activos",
                "status": f"{canal['ejecutadas']} Ejec",
                "status_color": "#16A34A" if canal['ejecutadas'] > 0 else "#64748B"
            }
        ]

        # Estructura del reporte oficial para impresión
        demo = state.get_municipio_demografia(mun)
        report_data = {
            "municipio": mun,
            "fecha": datetime.now().strftime("%d/%m/%Y"),
            "demografia": demo,
            "kpis": {
                "pozos_op": f"{pozos['pozos_operativos']}",
                "pozos_tot": f"{pozos['total_pozos']}",
                "pozos_pct": f"{pozos['pct_operativo']}",
                "asf_ton": f"{ton_asf:,.1f}",
                "asf_fallas": f"{fallas_asf:,.0f}",
                "luz_lum": f"{luz['luminarias']:,.0f}",
                "luz_tx": f"{luz['tx_instalados']}",
                "aguas_m": f"{tramos['metros_sustituidos']:,.0f}",
                "hidro_m": f"{hidro['metros_liberados']:,.0f}",
                "pue_culm": f"{pue['ejecutadas']}",
                "pue_tot": f"{pue['total_obras']}",
                "sal_culm": f"{salud['culminadas']}",
                "sal_tot": f"{salud['total_obras']}",
                "sal_pct": f"{salud['pct_culminadas']}",
                "esc_culm": f"{esc['culminadas']}",
                "esc_tot": f"{esc['total_centros']}",
                "esc_pct": f"{esc['pct_culminadas']}",
                "can_culm": f"{can['culminadas']}",
                "can_tot": f"{can['total_intervenidas']}",
                "casas_culm": f"{casas['ejecutadas']}",
                "casas_tot": f"{casas['total_viviendas']}",
                "casas_proc": f"{casas['proyeccion_ejecucion']}",
                "canal_km": f"{canal['longitud_canalizada_km']:,.2f}",
                "canal_culm": f"{canal['ejecutadas']}",
                "canal_bermas": f"{canal['bermas']}",
            },
            "obras": {
                "total": total_obras,
                "culm": culm_total,
                "pct_culm": pct_culm,
                "proc": proc_total,
                "pct_proc": pct_proc,
                "para": para_total,
                "pct_para": pct_para
            },
            "planes": plans_data
        }

        def handle_print(e):
            open_print_preview_dialog(page, report_data)

        # 2. Cabecera municipal estilizada con botón de impresión institucional
        mun_header = ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                content=ft.Icon(ft.Icons.LOCATION_CITY_ROUNDED, size=24, color="#FFFFFF"),
                                width=42,
                                height=42,
                                bgcolor=COLOR_ELECTRIC_BLUE,
                                border_radius=10,
                                alignment=ft.Alignment(0, 0),
                                shadow=ft.BoxShadow(spread_radius=0, blur_radius=8, color="#0066FF40", offset=ft.Offset(0, 2))
                            ),
                            ft.Column(
                                spacing=2,
                                horizontal_alignment=ft.CrossAxisAlignment.START,
                                controls=[
                                    ft.Row(
                                        spacing=8,
                                        controls=[
                                            ft.Text(f"Municipio {mun}", size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
                                            ft.Container(
                                                content=ft.Text("CONSOLIDADO MUNICIPAL", size=9, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_LIGHT),
                                                padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                                bgcolor=COLOR_SURFACE_ELEVATED,
                                                border_radius=6,
                                                border=ft.Border.all(1, "#1E3A8A")
                                            )
                                        ]
                                    ),
                                    ft.Text("Puesto de Comando Estratégico Operacional • Gestión y Obras Consolidadas", size=11, color=COLOR_TEXT_MUTED)
                                ]
                            )
                        ]
                    ),
                    ft.Row(
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.FilledButton(
                                content=ft.Row(
                                    spacing=6,
                                    tight=True,
                                    controls=[
                                        ft.Icon(ft.Icons.PRINT_ROUNDED, size=15, color="#FFFFFF"),
                                        ft.Text("Imprimir Reporte Municipal", size=12, weight=ft.FontWeight.BOLD, color="#FFFFFF")
                                    ]
                                ),
                                style=ft.ButtonStyle(
                                    bgcolor=COLOR_ELECTRIC_BLUE,
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    padding=ft.Padding.symmetric(horizontal=14, vertical=8)
                                ),
                                tooltip="Imprimir / Exportar Reporte Ejecutivo en Formato Carta Horizontal (Landscape)",
                                on_click=handle_print
                            ),
                            ft.FilledButton(
                                content=ft.Row(
                                    spacing=6,
                                    tight=True,
                                    controls=[
                                        ft.Icon(ft.Icons.PUBLIC_ROUNDED, size=15, color=COLOR_ELECTRIC_LIGHT),
                                        ft.Text("Consolidado General", size=12, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_LIGHT)
                                    ]
                                ),
                                style=ft.ButtonStyle(
                                    bgcolor=COLOR_SURFACE_ELEVATED,
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    padding=ft.Padding.symmetric(horizontal=12, vertical=8)
                                ),
                                on_click=lambda e: select_municipio("TODOS")
                            )
                        ]
                    )
                ]
            ),
            padding=ft.Padding.symmetric(horizontal=16, vertical=12),
            bgcolor=COLOR_SURFACE_WHITE,
            border_radius=12,
            border=ft.Border.all(1, COLOR_BORDER),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=8, color="#25000000", offset=ft.Offset(0, 2))
        )

        # Ficha sociopolítica y demográfica oficial (INE 2026)
        def build_demo_chip(title: str, val: str, sub: str, icon_name, color: str, bg: str):
            return ft.Container(
                content=ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            content=ft.Icon(icon_name, size=15, color=color),
                            width=28,
                            height=28,
                            border_radius=6,
                            bgcolor=COLOR_SURFACE_ELEVATED,
                            alignment=ft.Alignment(0, 0)
                        ),
                        ft.Column(
                            spacing=1,
                            horizontal_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Text(title, size=8.5, weight=ft.FontWeight.W_600, color=COLOR_TEXT_MUTED),
                                ft.Text(val, size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
                                ft.Text(sub, size=8, color=COLOR_TEXT_SECONDARY, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)
                            ]
                        )
                    ]
                ),
                padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                bgcolor="#0B1528" if is_dark_mode() else "#F8FAFC",
                border_radius=8,
                border=ft.Border.all(1, COLOR_BORDER),
                expand=True
            )

        demografia_card = ft.Container(
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Row(
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Icon(ft.Icons.ANALYTICS_ROUNDED, size=18, color=COLOR_ELECTRIC_LIGHT),
                                    ft.Text("Ficha Sociopolítica, Territorial y Demográfica Oficial (INE 2026)", size=12.5, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
                                ]
                            ),
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.VERIFIED_ROUNDED, size=12, color=COLOR_ELECTRIC_LIGHT),
                                    ft.Text("DATOS OFICIALES INE • PCEO", size=9, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_LIGHT)
                                ], spacing=3, tight=True),
                                padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                                bgcolor=COLOR_SURFACE_ELEVATED,
                                border_radius=6,
                                border=ft.Border.all(1, "#1E3A8A")
                            )
                        ]
                    ),
                    ft.Row(
                        spacing=8,
                        controls=[
                            build_demo_chip("CAPITAL", demo.get("capital", mun), "Cabecera", ft.Icons.LOCATION_ON_ROUNDED, "#38BDF8", "#0284C7"),
                            build_demo_chip("EXTENSIÓN", f"{demo.get('extension_km2_fmt', '0')} km²", "Superficie", ft.Icons.SQUARE_FOOT_ROUNDED, "#2DD4BF", "#0D9488"),
                            build_demo_chip("PARROQUIAS", f"{demo.get('parroquias', '0')} Parr.", "División Pol.", ft.Icons.MAP_ROUNDED, "#2DD4BF", "#0D9488"),
                            build_demo_chip("POBLACIÓN (INE)", f"{demo.get('poblacion_ine_fmt', '0')}", "Habitantes", ft.Icons.PEOPLE_ROUNDED, "#60A5FA", "#2563EB"),
                            build_demo_chip("FAMILIAS", f"{demo.get('familias_ine_fmt', '0')}", "Hogares INE", ft.Icons.FAMILY_RESTROOM_ROUNDED, "#60A5FA", "#2563EB"),
                        ]
                    ),
                    ft.Row(
                        spacing=8,
                        controls=[
                            build_demo_chip("COMUNAS", f"{demo.get('comunas_fmt', '0')}", "Poder Popular", ft.Icons.ACCOUNT_BALANCE_ROUNDED, "#A78BFA", "#7C3AED"),
                            build_demo_chip("CONSEJOS COM.", f"{demo.get('consejos_comunales_fmt', '0')}", "Organizados", ft.Icons.GROUPS_ROUNDED, "#A78BFA", "#7C3AED"),
                            build_demo_chip("UBCH", f"{demo.get('ubch_fmt', '0')}", "Centros Elec.", ft.Icons.FLAG_ROUNDED, "#F87171", "#DC2626"),
                            build_demo_chip("JEFES CLAP", f"{demo.get('jefes_clap_fmt', '0')}", "Alimentación", ft.Icons.SHOPPING_BASKET_ROUNDED, "#FB923C", "#EA580C"),
                            build_demo_chip("JEFES DE CALLE", f"{demo.get('jefes_calle_fmt', '0')}", f"{demo.get('comunidades_rurales_fmt', '0')} Rurales", ft.Icons.DIRECTIONS_WALK_ROUNDED, "#FBBF24", "#D97706"),
                        ]
                    )
                ]
            ),
            padding=12,
            bgcolor=COLOR_SURFACE_WHITE,
            border_radius=10,
            border=ft.Border.all(1, COLOR_BORDER),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=8, color="#25000000", offset=ft.Offset(0, 2))
        )

        # 2. Grid de 8 KPIs Principales
        kpis_row_1 = ft.Row(
            spacing=10,
            controls=[
                build_mini_kpi_card("Pozos de Agua", f"{pozos['pozos_operativos']} Operativos", f"{pozos['total_pozos']} Pozos ({pozos['pct_operativo']}% Op) • {pozos['rebombeo_op']} Reb.", ft.Icons.WATER_DROP_ROUNDED, "#0284C7", "#E0F2FE"),
                build_mini_kpi_card("Asfaltado Urbano", f"{ton_asf:,.1f} Toneladas", f"{fallas_asf:,.0f} Fallas viales atendidas", ft.Icons.DIRECTIONS_CAR_ROUNDED, "#D97706", "#FEF3C7"),
                build_mini_kpi_card("Fiesta de la Luz", f"{luz['luminarias']:,.0f} Luminarias", f"{luz['tx_instalados']} Transformadores instalados", ft.Icons.LIGHTBULB_ROUNDED, "#CA8A04", "#FEF9C3"),
                build_mini_kpi_card("Aguas Servidas", f"{tramos['metros_sustituidos']:,.0f} m Colectores", f"{hidro['metros_liberados']:,.0f} m Hidrojet • {hidro['bocas_de_visita']} Bocas", ft.Icons.PLUMBING_ROUNDED, "#0D9488", "#CCFBF1"),
            ]
        )
        kpis_row_2 = ft.Row(
            spacing=10,
            controls=[
                build_mini_kpi_card("Puentes y Vialidad", f"{pue['ejecutadas']} Culminadas", f"{pue['total_obras']} Obras ({pue['puentes']} Ptes / {pue['alcantarillas']} Alc)", ft.Icons.CONSTRUCTION_ROUNDED, "#4F46E5", "#EEF2FF"),
                build_mini_kpi_card("Espacios de Salud", f"{salud['culminadas']} Centros Rehab.", f"{salud['total_obras']} Obras ({salud['pct_culminadas']}% Culm.)", ft.Icons.LOCAL_HOSPITAL_ROUNDED, "#E11D48", "#FFE4E6"),
                build_mini_kpi_card("Centros Educativos", f"{esc['culminadas']} Escuelas Rehab.", f"{esc['total_centros']} Instituciones ({esc['pct_culminadas']}% Culm.)", ft.Icons.SCHOOL_ROUNDED, "#16A34A", "#DCFCE7"),
                build_mini_kpi_card("Canchas Deportivas", f"{can['culminadas']} Culminadas", f"{can['total_intervenidas']} Canchas ({can['pct_culminadas']}% Culm.)", ft.Icons.SPORTS_BASKETBALL_ROUNDED, "#7C3AED", "#F3E8FF"),
            ]
        )

        # 3. Gráfica de Progreso y Estatus de Obras (Segmented Bar)
        seg_controls = []
        if culm_total > 0:
            seg_controls.append(ft.Container(expand=culm_total, bgcolor="#16A34A", tooltip=f"Culminadas: {culm_total} ({pct_culm}%)"))
        if proc_total > 0:
            seg_controls.append(ft.Container(expand=proc_total, bgcolor="#D97706", tooltip=f"En Proceso: {proc_total} ({pct_proc}%)"))
        if para_total > 0:
            seg_controls.append(ft.Container(expand=para_total, bgcolor="#DC2626", tooltip=f"Paralizadas: {para_total} ({pct_para}%)"))
        if not seg_controls:
            seg_controls.append(ft.Container(expand=1, bgcolor="#CBD5E1"))

        progress_card = ft.Container(
            content=ft.Column(
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(f"Estatus Consolidado de Infraestructura y Obras ({total_obras} Frentes)", size=13, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
                            ft.Text(f"{pct_culm}% Eficiencia Global", size=12, weight=ft.FontWeight.BOLD, color="#4ADE80")
                        ]
                    ),
                    ft.Container(
                        content=ft.Row(controls=seg_controls, spacing=2),
                        height=12,
                        border_radius=6,
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        bgcolor="#1E293B"
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Container(
                                content=ft.Row(
                                    spacing=6,
                                    tight=True,
                                    controls=[
                                        ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, size=15, color="#4ADE80"),
                                        ft.Text(f"{culm_total} Culminadas ({pct_culm}%)", size=11, weight=ft.FontWeight.BOLD, color="#4ADE80")
                                    ]
                                ),
                                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                                bgcolor="#064E3B40",
                                border_radius=6,
                                border=ft.Border.all(1, "#16A34A60")
                            ),
                            ft.Container(
                                content=ft.Row(
                                    spacing=6,
                                    tight=True,
                                    controls=[
                                        ft.Icon(ft.Icons.PENDING_ACTIONS_ROUNDED, size=15, color="#FBBF24"),
                                        ft.Text(f"{proc_total} En Proceso ({pct_proc}%)", size=11, weight=ft.FontWeight.BOLD, color="#FBBF24")
                                    ]
                                ),
                                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                                bgcolor="#78350F40",
                                border_radius=6,
                                border=ft.Border.all(1, "#D9770660")
                            ),
                            ft.Container(
                                content=ft.Row(
                                    spacing=6,
                                    tight=True,
                                    controls=[
                                        ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, size=15, color="#F87171"),
                                        ft.Text(f"{para_total} Paralizadas ({pct_para}%)", size=11, weight=ft.FontWeight.BOLD, color="#F87171")
                                    ]
                                ),
                                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                                bgcolor="#7F1D1D40",
                                border_radius=6,
                                border=ft.Border.all(1, "#DC262660")
                            )
                        ]
                    )
                ]
            ),
            bgcolor=COLOR_SURFACE_WHITE,
            padding=14,
            border_radius=10,
            border=ft.Border.all(1, COLOR_BORDER),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=8, color="#25000000", offset=ft.Offset(0, 2))
        )

        # 4. Tabla Resumen de Planes Operativos en esa localidad
        table_rows = []
        for p in plans_data:
            row_control = ft.Container(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                    content=ft.Icon(p["icon"], size=18, color=p["color"]),
                                    width=36,
                                    height=36,
                                    border_radius=8,
                                    bgcolor=COLOR_SURFACE_ELEVATED,
                                    alignment=ft.Alignment(0, 0)
                                ),
                                ft.Column(
                                    spacing=2,
                                    horizontal_alignment=ft.CrossAxisAlignment.START,
                                    controls=[
                                        ft.Text(p["name"], size=13, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
                                        ft.Text(p["detail"], size=10, color=COLOR_TEXT_MUTED)
                                    ]
                                )
                            ]
                        ),
                        ft.Row(
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Text(p["metric"], size=12, weight=ft.FontWeight.W_600, color=COLOR_TEXT_PRIMARY),
                                ft.Container(
                                    content=ft.Text(p["status"], size=10, weight=ft.FontWeight.BOLD, color=p["status_color"]),
                                    padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                    bgcolor=COLOR_SURFACE_ELEVATED,
                                    border_radius=6,
                                    border=ft.Border.all(1, COLOR_BORDER)
                                ),
                                ft.FilledButton(
                                    content=ft.Row(
                                        spacing=4,
                                        tight=True,
                                        controls=[
                                            ft.Text("Ver Módulo", size=11, weight=ft.FontWeight.BOLD),
                                            ft.Icon(ft.Icons.ARROW_FORWARD_ROUNDED, size=14)
                                        ]
                                    ),
                                    style=ft.ButtonStyle(
                                        bgcolor=COLOR_ELECTRIC_BLUE,
                                        color="#FFFFFF",
                                        padding=ft.Padding.symmetric(horizontal=10, vertical=6),
                                        shape=ft.RoundedRectangleBorder(radius=6)
                                    ),
                                    on_click=lambda e, pid=p["id"]: navigate_to_module_with_mun(pid, mun)
                                )
                            ]
                        )
                    ]
                ),
                padding=ft.Padding.symmetric(horizontal=12, vertical=10),
                border_radius=8,
                bgcolor="#0B1528" if is_dark_mode() else "#F8FAFC",
                border=ft.Border.all(1, COLOR_BORDER)
            )
            table_rows.append(row_control)

        table_card = ft.Container(
            content=ft.Column(
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Resumen de Planes Activos en la Localidad", size=13, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
                            ft.Text(f"{len(plans_data)} Planes Operativos", size=11, color=COLOR_TEXT_MUTED)
                        ]
                    ),
                    *table_rows
                ]
            ),
            padding=14,
            bgcolor=COLOR_SURFACE_WHITE,
            border_radius=10,
            border=ft.Border.all(1, COLOR_BORDER),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=8, color="#25000000", offset=ft.Offset(0, 2))
        )

        return ft.ListView(
            controls=[
                mun_header,
                demografia_card,
                kpis_row_1,
                kpis_row_2,
                progress_card,
                table_card,
                ft.Container(height=24)
            ],
            spacing=12,
            padding=14,
            expand=True
        )

    # -------------------------------------------------------------
    # 4. CONTENEDOR CENTRAL REACTIVO CON ANIMACIÓN FLUIDA
    # -------------------------------------------------------------
    state_scroll_view.key = "mun_todos"
    central_animated_switcher = ft.AnimatedSwitcher(
        content=state_scroll_view,
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=250,
        reverse_duration=150,
        switch_in_curve=ft.AnimationCurve.EASE_OUT,
        switch_out_curve=ft.AnimationCurve.EASE_IN,
        expand=True
    )
    central_content_container = ft.Container(
        content=central_animated_switcher,
        expand=True
    )

    # -------------------------------------------------------------
    # 5. MENÚ LATERAL IZQUIERDO DE MUNICIPIOS (DESPLEGABLE / COLAPSABLE)
    # -------------------------------------------------------------
    is_municipios_expanded = {"value": False}  # Oculto / contraído por defecto

    expand_arrow_icon = ft.Icon(
        ft.Icons.KEYBOARD_ARROW_DOWN_ROUNDED,
        size=18,
        color=COLOR_TEXT_MUTED
    )

    municipios_items_col = ft.Column(spacing=3)
    municipios_dropdown_container = ft.Container(
        content=municipios_items_col,
        visible=False,
        padding=ft.Padding.only(left=2)
    )

    general_item_container = ft.Container()

    def select_municipio(mun_target: str):
        current_selected_mun["value"] = mun_target
        if mun_target != "TODOS":
            is_municipios_expanded["value"] = True
            municipios_dropdown_container.visible = True
            expand_arrow_icon.icon = ft.Icons.KEYBOARD_ARROW_UP_ROUNDED
            expand_arrow_icon.color = COLOR_ELECTRIC_LIGHT
            territorio_header.bgcolor = COLOR_SURFACE_ELEVATED
            territorio_header.border = ft.Border.all(1, "#2563EB")
        rebuild_sidebar()
        if mun_target == "TODOS":
            state_scroll_view.key = "mun_todos"
            central_animated_switcher.content = state_scroll_view
        else:
            mun_view = build_municipio_dashboard(mun_target)
            mun_view.key = f"mun_{mun_target}"
            central_animated_switcher.content = mun_view
        page.update()

    def toggle_municipios(e=None):
        is_municipios_expanded["value"] = not is_municipios_expanded["value"]
        municipios_dropdown_container.visible = is_municipios_expanded["value"]
        expand_arrow_icon.icon = (
            ft.Icons.KEYBOARD_ARROW_UP_ROUNDED
            if is_municipios_expanded["value"]
            else ft.Icons.KEYBOARD_ARROW_DOWN_ROUNDED
        )
        expand_arrow_icon.color = (
            COLOR_ELECTRIC_LIGHT
            if is_municipios_expanded["value"]
            else COLOR_TEXT_MUTED
        )
        territorio_header.bgcolor = COLOR_SURFACE_ELEVATED if is_municipios_expanded["value"] else COLOR_SURFACE_WHITE
        territorio_header.border = ft.Border.all(1, "#2563EB" if is_municipios_expanded["value"] else COLOR_BORDER)
        page.update()

    territorio_header = ft.Container(
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            content=ft.Icon(ft.Icons.MAP_ROUNDED, size=16, color=COLOR_ELECTRIC_LIGHT),
                            padding=ft.Padding.all(6),
                            bgcolor="#0B132B" if is_dark_mode() else "#EFF6FF",
                            border_radius=6,
                            border=ft.Border.all(1, "#1E3A8A" if is_dark_mode() else "#BFDBFE")
                        ),
                        ft.Column(
                            spacing=1,
                            horizontal_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Text(
                                    "TERRITORIO",
                                    size=9,
                                    weight=ft.FontWeight.BOLD,
                                    color=COLOR_ELECTRIC_LIGHT,
                                    style=ft.TextStyle(letter_spacing=1.1)
                                ),
                                ft.Text(
                                    "14 Municipios",
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color=COLOR_TEXT_PRIMARY
                                )
                            ]
                        )
                    ]
                ),
                expand_arrow_icon
            ]
        ),
        padding=ft.Padding.symmetric(horizontal=10, vertical=8),
        bgcolor=COLOR_SURFACE_WHITE,
        border_radius=8,
        border=ft.Border.all(1, COLOR_BORDER),
        on_click=toggle_municipios,
        tooltip="Clic para desplegar / contraer los 14 municipios"
    )

    def build_sidebar_item(label: str, value: str, icon: str) -> ft.Container:
        is_active = (current_selected_mun["value"] == value)
        
        bg_col = COLOR_ELECTRIC_BLUE if is_active else "transparent"
        txt_col = "#FFFFFF" if is_active else COLOR_TEXT_SECONDARY
        ic_col = "#FFFFFF" if is_active else (COLOR_ELECTRIC_LIGHT if value == "TODOS" else COLOR_TEXT_MUTED)
        f_weight = ft.FontWeight.BOLD if is_active else ft.FontWeight.W_500

        return ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(icon, size=16, color=ic_col),
                            ft.Text(label, size=12, weight=f_weight, color=txt_col)
                        ]
                    ),
                    ft.Icon(
                        ft.Icons.CHEVRON_RIGHT_ROUNDED,
                        size=14,
                        color="#FFFFFF" if is_active else (COLOR_TEXT_MUTED if is_dark_mode() else "#94A3B8")
                    )
                ]
            ),
            padding=ft.Padding.symmetric(horizontal=10, vertical=7),
            border_radius=8,
            bgcolor=bg_col,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=8, color="#0066FF50", offset=ft.Offset(0, 2)) if is_active else None,
            on_click=lambda e, v=value: select_municipio(v),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
        )

    def rebuild_sidebar():
        # Actualizar botón de Consolidado General
        general_item_container.content = build_sidebar_item(
            "Estado Portuguesa (General)", "TODOS", ft.Icons.PUBLIC_ROUNDED
        )

        # Actualizar lista de los 14 municipios
        municipios_items_col.controls.clear()
        for m in MUNICIPIOS_ORDEN:
            municipios_items_col.controls.append(
                build_sidebar_item(m, m, ft.Icons.LOCATION_CITY_ROUNDED)
            )

    rebuild_sidebar()

    # -------------------------------------------------------------
    # 5.1 PERFIL DE USUARIO Y CONFIGURACIÓN (PIE FIJO DE LA BARRA LATERAL)
    # -------------------------------------------------------------
    active_role = state.current_role
    active_user_name = state.get_user_display_name()
    short_name = active_user_name.split("—")[0].strip() if active_user_name else "Usuario"

    if active_role == "MASTER":
        role_label = "MASTER"
        role_color = "#A855F7"
        role_bg_light = "#7C3AED33"
        role_icon = ft.Icons.ADMIN_PANEL_SETTINGS_ROUNDED
    elif active_role in ["ANALISTA", "Equipo Técnico (Editor)"]:
        role_label = "ANALISTA"
        role_color = COLOR_ELECTRIC_LIGHT
        role_bg_light = "#0066FF33"
        role_icon = ft.Icons.BUILD_ROUNDED
    else:
        role_label = "EJECUTIVO"
        role_color = "#94A3B8"
        role_bg_light = "#33415540"
        role_icon = ft.Icons.VISIBILITY_ROUNDED

    user_action_buttons = []
    if active_role == "MASTER":
        user_action_buttons.append(
            ft.IconButton(
                icon=ft.Icons.SETTINGS_ROUNDED,
                icon_color=COLOR_ELECTRIC_LIGHT,
                icon_size=19,
                tooltip="Gestión de Usuarios y Configuración",
                on_click=on_open_users if on_open_users else (lambda e: on_open_plan("usuarios"))
            )
        )
        if on_switch_role:
            user_action_buttons.append(
                ft.IconButton(
                    icon=ft.Icons.SWAP_HORIZ_ROUNDED,
                    icon_color=COLOR_TEXT_MUTED,
                    icon_size=18,
                    tooltip="Alternar Rol Rápido (Master)",
                    on_click=on_switch_role
                )
            )

    if on_logout:
        user_action_buttons.append(
            ft.IconButton(
                icon=ft.Icons.LOGOUT_ROUNDED,
                icon_color="#EF4444",
                icon_size=18,
                tooltip="Cerrar Sesión",
                on_click=on_logout
            )
        )

    user_footer_container = ft.Container(
        content=ft.Column(
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Divider(color=COLOR_BORDER, height=1),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            spacing=8,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                    content=ft.Icon(role_icon, size=18, color="#FFFFFF"),
                                    width=34,
                                    height=34,
                                    border_radius=17,
                                    bgcolor=role_color,
                                    alignment=ft.Alignment(0, 0)
                                ),
                                ft.Column(
                                    spacing=1,
                                    horizontal_alignment=ft.CrossAxisAlignment.START,
                                    controls=[
                                        ft.Text(
                                            short_name,
                                            size=11,
                                            weight=ft.FontWeight.BOLD,
                                            color=COLOR_TEXT_PRIMARY,
                                            max_lines=1,
                                            overflow=ft.TextOverflow.ELLIPSIS
                                        ),
                                        ft.Container(
                                            content=ft.Text(role_label, size=9, weight=ft.FontWeight.BOLD, color=role_color),
                                            padding=ft.Padding.symmetric(horizontal=5, vertical=1),
                                            bgcolor=role_bg_light,
                                            border_radius=4,
                                            border=ft.Border.all(1, role_color + "40")
                                        )
                                    ]
                                )
                            ],
                            expand=True
                        ),
                        ft.Row(
                            spacing=0,
                            tight=True,
                            controls=user_action_buttons
                        )
                    ]
                )
            ]
        ),
        padding=ft.Padding.only(top=6)
    )

    sidebar_container = ft.Container(
        width=250,
        content=ft.Column(
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Container(
                    content=ft.Column(
                        spacing=8,
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                        scroll=ft.ScrollMode.ADAPTIVE,
                        controls=[
                            general_item_container,
                            ft.Divider(color=COLOR_BORDER, height=1),
                            territorio_header,
                            municipios_dropdown_container
                        ]
                    ),
                    expand=True
                ),
                user_footer_container
            ]
        ),
        padding=10,
        bgcolor="#0B132B" if is_dark_mode() else "#FFFFFF",
        border=ft.Border(right=ft.BorderSide(1, COLOR_BORDER))
    )

    # -------------------------------------------------------------
    # 6. LAYOUT PRINCIPAL: HEADER SUPERIOR + (SIDEBAR + CONTENIDO)
    # -------------------------------------------------------------
    return ft.Column(
        spacing=0,
        expand=True,
        controls=[
            header,
            ft.Row(
                spacing=0,
                expand=True,
                controls=[
                    sidebar_container,
                    central_content_container
                ]
            )
        ]
    )
