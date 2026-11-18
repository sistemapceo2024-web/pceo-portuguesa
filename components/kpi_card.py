"""
Tarjetas KPI Institucionales - Centro de Comando Ejecutivo (Dark Executive Theme)
Secretaría Superior de Operaciones Generales de Portuguesa
Puesto de Comando Estratégico Operacional del Estado Portuguesa (PCEO)
"""
import os
import flet as ft
from components.theme import (
    COLOR_NAVY_DARK,
    COLOR_ELECTRIC_BLUE,
    COLOR_ELECTRIC_LIGHT,
    COLOR_SURFACE_WHITE,
    COLOR_SURFACE_ELEVATED,
    COLOR_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    COLOR_STATUS_GREEN,
    COLOR_STATUS_AMBER,
    COLOR_STATUS_RED,
    get_status_colors
)
from components.semaphore import create_semaphore_badge
from data.models import GovernmentPlan

def get_plan_icon(icon_name: str):
    icon_map = {
        "water_drop_rounded": ft.Icons.WATER_DROP_ROUNDED,
        "plumbing_rounded": ft.Icons.PLUMBING_ROUNDED,
        "engineering_rounded": ft.Icons.ENGINEERING_ROUNDED,
        "cleaning_services_rounded": ft.Icons.CLEANING_SERVICES_ROUNDED,
        "lightbulb_rounded": ft.Icons.LIGHTBULB_ROUNDED,
        "waves_rounded": ft.Icons.WAVES_ROUNDED,
        "traffic_rounded": ft.Icons.TRAFFIC_ROUNDED,
        "alt_route_rounded": ft.Icons.ALT_ROUTE_ROUNDED,
        "local_hospital_rounded": ft.Icons.LOCAL_HOSPITAL_ROUNDED,
        "sports_basketball_rounded": ft.Icons.SPORTS_BASKETBALL_ROUNDED,
        "school_rounded": ft.Icons.SCHOOL_ROUNDED,
        "foundation_rounded": ft.Icons.FOUNDATION_ROUNDED,
        "domain_add_rounded": ft.Icons.DOMAIN_ADD_ROUNDED,
    }
    return icon_map.get(icon_name, ft.Icons.ASSESSMENT_ROUNDED)

def create_plan_kpi_card(plan: GovernmentPlan, on_click=None) -> ft.Container:
    """Crea la tarjeta de resumen para cada uno de los planes de gobierno con estética de Centro de Comando."""
    status_colors = get_status_colors(plan.status_label)

    interactive_hint = None
    if plan.is_interactive:
        interactive_hint = ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=6,
                        controls=[
                            ft.Icon(ft.Icons.TOUCH_APP_ROUNDED, size=14, color=COLOR_ELECTRIC_LIGHT),
                            ft.Text(
                                "Módulo Detallado Disponible",
                                size=11,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_ELECTRIC_LIGHT
                            ),
                        ]
                    ),
                    ft.Icon(ft.Icons.ARROW_FORWARD_IOS_ROUNDED, size=12, color=COLOR_ELECTRIC_LIGHT)
                ]
            ),
            padding=ft.Padding.symmetric(horizontal=10, vertical=6),
            bgcolor=COLOR_SURFACE_ELEVATED,
            border_radius=8,
            border=ft.Border.all(1, "#BFDBFE")
        )

    card_content = ft.Column(
        spacing=10,
        controls=[
            # Cabecera de la Tarjeta
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Row(
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            # Logo personalizado si existe o ícono del plan
                            (lambda: (
                                (lambda logo_src: (
                                    ft.Container(
                                        content=ft.Image(
                                            src=logo_src,
                                            width=48,
                                            height=48,
                                            fit="contain"
                                        ) if logo_src else ft.Icon(
                                            get_plan_icon(plan.icon_name),
                                            color="#FFFFFF",
                                            size=22
                                        ),
                                        bgcolor=None if logo_src else (COLOR_ELECTRIC_BLUE if plan.is_interactive else "#1E293B"),
                                        width=48 if logo_src else 42,
                                        height=48 if logo_src else 42,
                                        border_radius=10,
                                        alignment=ft.Alignment(0, 0)
                                    )
                                ))(
                                    f"logo_{plan.id}.png" if os.path.exists(f"assets/logo_{plan.id}.png")
                                    else ("logo_espacios_salud.png" if ("salud" in plan.id and os.path.exists("assets/logo_espacios_salud.png"))
                                    else ("logo_escuelas.png" if (("educacion" in plan.id or "escuela" in plan.id) and os.path.exists("assets/logo_escuelas.png"))
                                    else ("logo_cero_huecos.png" if ("cero_hueco" in plan.id and os.path.exists("assets/logo_cero_huecos.png"))
                                    else ("logo_casas.png" if ("casa" in plan.id and os.path.exists("assets/logo_casas.png"))
                                    else None))))
                                )
                            ))(),
                            ft.Column(
                                spacing=1,
                                controls=[
                                    ft.Text(
                                        plan.title,
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                        color=COLOR_TEXT_PRIMARY
                                    ),
                                    ft.Text(
                                        plan.subtitle,
                                        size=11,
                                        color=COLOR_TEXT_MUTED,
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS
                                    )
                                ]
                            )
                        ],
                        expand=True
                    ),
                    create_semaphore_badge(plan.status_label, compact=True)
                ]
            ),

            # Métricas Clave (Contenedor Interno de Superficie Profunda)
            ft.Container(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    controls=[
                        ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=1,
                            controls=[
                                ft.Text(plan.main_metric, size=15, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
                                ft.Text("Total Intervenidas" if plan.id == "canchas" else "Principal", size=10, color=COLOR_TEXT_MUTED)
                            ]
                        ),
                        ft.Container(width=1, height=24, bgcolor=COLOR_BORDER),
                        ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=1,
                            controls=[
                                ft.Text(plan.secondary_metric, size=13, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN if plan.id == "canchas" else COLOR_TEXT_PRIMARY),
                                ft.Text("Culminadas" if plan.id == "canchas" else "Secundario", size=10, color=COLOR_STATUS_GREEN if plan.id == "canchas" else COLOR_TEXT_MUTED)
                            ]
                        ),
                        ft.Container(width=1, height=24, bgcolor=COLOR_BORDER),
                        ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=1,
                            controls=[
                                ft.Text(plan.tertiary_metric, size=13, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_AMBER if plan.id == "canchas" else COLOR_TEXT_SECONDARY),
                                ft.Text("Frentes Críticos" if plan.id == "canchas" else "Soporte", size=10, color=COLOR_STATUS_AMBER if plan.id == "canchas" else COLOR_TEXT_MUTED)
                            ]
                        ),
                    ]
                ),
                padding=ft.Padding.symmetric(vertical=10, horizontal=8),
                bgcolor="#F8FAFC",
                border_radius=8,
                border=ft.Border.all(1, COLOR_BORDER)
            ),

            # Barra de Progreso
            ft.Column(
                spacing=4,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Nivel de Ejecución Operativa", size=10, color=COLOR_TEXT_MUTED),
                            ft.Text(f"{int(plan.progress * 100)}%", size=11, weight=ft.FontWeight.BOLD, color=status_colors["text"])
                        ]
                    ),
                    ft.ProgressBar(
                        value=plan.progress,
                        color=status_colors["text"],
                        bgcolor="#E2E8F0",
                        border_radius=4
                    )
                ]
            ),
        ]
    )

    if interactive_hint:
        card_content.controls.append(interactive_hint)

    # Contenedor Exterior con Barra de Acento Superior de 3px y Sombra Suave
    container = ft.Container(
        content=card_content,
        bgcolor=COLOR_SURFACE_WHITE,
        padding=14,
        border_radius=14,
        border=ft.Border(
            top=ft.BorderSide(3, status_colors["text"]),
            left=ft.BorderSide(1.5 if plan.is_interactive else 1, COLOR_ELECTRIC_BLUE if plan.is_interactive else COLOR_BORDER),
            right=ft.BorderSide(1.5 if plan.is_interactive else 1, COLOR_ELECTRIC_BLUE if plan.is_interactive else COLOR_BORDER),
            bottom=ft.BorderSide(1.5 if plan.is_interactive else 1, COLOR_ELECTRIC_BLUE if plan.is_interactive else COLOR_BORDER)
        ),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=12,
            color="#0A0A192F",
            offset=ft.Offset(0, 4)
        ),
        animate=ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT),
        ink=plan.is_interactive,
        on_click=on_click if plan.is_interactive else None
    )

    return container


def create_dynamic_kpi_metric(
    title: str,
    main_value: str,
    subtitle: str,
    icon: ft.Icons,
    accent_color: str,
    bg_tint: str = None
) -> ft.Container:
    """Tarjeta individual para los KPIs superiores dinámicos con barra de acento superior de 3px."""
    return ft.Container(
        content=ft.Column(
            spacing=4,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            title,
                            size=10,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_TEXT_MUTED,
                            max_lines=1
                        ),
                        ft.Icon(icon, size=15, color=accent_color)
                    ]
                ),
                ft.Text(
                    main_value,
                    size=17,
                    weight=ft.FontWeight.BOLD,
                    color=COLOR_TEXT_PRIMARY
                ),
                ft.Text(
                    subtitle,
                    size=10,
                    weight=ft.FontWeight.W_600,
                    color=accent_color
                )
            ]
        ),
        bgcolor=COLOR_SURFACE_WHITE,
        padding=ft.Padding.symmetric(horizontal=12, vertical=10),
        border_radius=10,
        border=ft.Border(
            top=ft.BorderSide(3, accent_color),
            left=ft.BorderSide(1, COLOR_BORDER),
            right=ft.BorderSide(1, COLOR_BORDER),
            bottom=ft.BorderSide(1, COLOR_BORDER)
        ),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            color="#25000000",
            offset=ft.Offset(0, 3)
        ),
        expand=True
    )
