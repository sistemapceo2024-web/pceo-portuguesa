"""
Módulo Detallado: Plan Una Cancha para Todos
Puesto de Comando Estratégico Operacional del Estado Portuguesa (PCEO)
Secretaría Superior de Operaciones Generales - Gobernación del Estado Portuguesa
Corte Oficial: Noviembre 2026 - 135 Canchas Intervenidas (122 Culminadas, 4 En Ejecución, 9 Paralizadas)
"""
import os
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
from data.water_data import MUNICIPALITIES_LIST
from data.state import AppState
from components.header import create_institutional_header

def get_status_badge_color(estatus: str) -> tuple[str, str, str]:
    st = (estatus or "").upper()
    if "CULMINAD" in st or "EJECUTAD" in st or "100" in st:
        return ("#DCFCE7", "#16A34A", "#86EFAC")
    elif "PARALIZAD" in st:
        return ("#FEE2E2", "#DC2626", "#FCA5A5")
    return ("#FEF3C7", "#D97706", "#FDE68A")

def build_cancha_para_todos_view(
    page: ft.Page,
    on_back_to_summary,
    on_switch_role,
    on_logout
) -> ft.Control:
    state = AppState()

    active_tab = 0  # 0 a 2
    selected_mun = state.canchas_municipality
    selected_estatus = state.canchas_estatus
    search_query = ""
    search_mun_query = ""

    kpis_container = ft.Row(spacing=8)
    tab_content_area = ft.Container(expand=True)
    tab_chips_row = ft.Row(scroll=ft.ScrollMode.ADAPTIVE, spacing=6)

    def show_feedback_snack(message: str, is_error: bool = False):
        snack = ft.SnackBar(
            content=ft.Text(message, color="#FFFFFF", weight=ft.FontWeight.W_500),
            bgcolor=COLOR_STATUS_RED if is_error else COLOR_NAVY_DARK
        )
        if hasattr(page, "open"):
            page.open(snack)
        elif hasattr(page, "show_dialog"):
            page.show_dialog(snack)
        else:
            page.overlay.append(snack)
            snack.open = True
            page.update()

    # Modal: Ficha Técnica de la Cancha Deportiva
    def open_ficha_tecnica_dialog(cancha: dict):
        c_id = cancha.get("id")
        nom = cancha.get("nombre", "Cancha Deportiva")
        mun = cancha.get("municipio", "Portuguesa")
        sec = cancha.get("sector", "Sector General")
        tipo = cancha.get("tipo", "Cancha Techada")
        est = cancha.get("estatus", "CULMINADA")
        pct = cancha.get("porcentaje", 100.0)
        año = cancha.get("año", "2024-2026")
        periodo = cancha.get("periodo", "2026")
        trabajos = cancha.get("trabajos", "Pintura epóxica, tableros de acrílico y luminarias LED")
        notas = cancha.get("notas", "Obra ejecutada en el marco del Plan Una Cancha para Todos.")

        bg_st, col_st, bdr_st = get_status_badge_color(est)

        def close_dialog(e=None):
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.SPORTS_BASKETBALL_ROUNDED, color=COLOR_ELECTRIC_BLUE, size=24),
                ft.Text("Ficha Técnica de Infraestructura Deportiva", size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
            ], spacing=8),
            content=ft.Container(
                width=520,
                content=ft.Column(
                    tight=True,
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Row([
                            ft.Container(
                                content=ft.Text(f"#{c_id} • {tipo}", size=11, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_BLUE),
                                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                bgcolor="#EFF6FF",
                                border_radius=6
                            ),
                            ft.Container(
                                content=ft.Text(f"{est} ({pct}%)", size=11, weight=ft.FontWeight.BOLD, color=col_st),
                                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                bgcolor=bg_st,
                                border=ft.Border.all(1, bdr_st),
                                border_radius=6
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(nom, size=15, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Divider(height=1, color=COLOR_BORDER),
                        ft.Row([
                            ft.Icon(ft.Icons.LOCATION_ON_ROUNDED, size=14, color=COLOR_ELECTRIC_BLUE),
                            ft.Text(f"Municipio: {mun}", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                            ft.Text("•", size=11, color=COLOR_TEXT_MUTED),
                            ft.Icon(ft.Icons.NEAR_ME_ROUNDED, size=14, color=COLOR_TEXT_MUTED),
                            ft.Text(f"Sector: {sec}", size=11, color=COLOR_TEXT_SECONDARY, expand=True)
                        ], spacing=4),
                        ft.Row([
                            ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED, size=14, color=COLOR_STATUS_AMBER),
                            ft.Text(f"Período / Año: {periodo} ({año})", size=11, color=COLOR_TEXT_SECONDARY),
                        ], spacing=4),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Especificaciones de Intervención Técnica:", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                ft.Text(trabajos, size=11, color=COLOR_TEXT_SECONDARY)
                            ], spacing=3),
                            padding=8,
                            bgcolor="#F8FAFC",
                            border_radius=6,
                            border=ft.Border.all(1, "#E2E8F0")
                        ),
                        ft.Row([
                            ft.Text("Nivel de Ejecución:", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                            ft.Text(f"{pct}%", size=11, weight=ft.FontWeight.BOLD, color=col_st)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.ProgressBar(value=pct / 100.0, color=col_st, bgcolor="#E2E8F0", height=8),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Observaciones y Seguimiento PCEO:", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                ft.Text(notas, size=11, color=COLOR_TEXT_MUTED)
                            ], spacing=2),
                            padding=8,
                            bgcolor="#F1F5F9",
                            border_radius=6
                        )
                    ]
                )
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cerrar"),
                    on_click=close_dialog
                )
            ]
        )

        if hasattr(page, "open"):
            page.open(dlg)
        elif hasattr(page, "show_dialog"):
            page.show_dialog(dlg)
        else:
            page.dialog = dlg
            dlg.open = True
            page.update()

    # Modal: Registrar / Actualizar Cancha (MASTER y ANALISTA)
    def open_cancha_modal(cancha: dict = None):
        is_edit = cancha is not None
        c_id = cancha.get("id") if is_edit else None

        nom_field = ft.TextField(
            label="Nombre de la Cancha / Espacio Deportivo *",
            value=cancha.get("nombre", "") if is_edit else "",
            dense=True,
            text_size=11,
            border_radius=8
        )
        mun_dropdown = ft.Dropdown(
            label="Municipio *",
            value=cancha.get("municipio", "Guanare") if is_edit else "Guanare",
            options=[ft.DropdownOption(m) for m in MUNICIPALITIES_LIST if m != "Todos los Municipios"],
            dense=True,
            text_size=11,
            border_radius=8,
            expand=True
        )
        sec_field = ft.TextField(
            label="Sector / Comunidad *",
            value=cancha.get("sector", "") if is_edit else "",
            dense=True,
            text_size=11,
            border_radius=8,
            expand=True
        )
        tipo_dropdown = ft.Dropdown(
            label="Tipo de Espacio *",
            value=cancha.get("tipo", "Cancha Techada de Usos Múltiples") if is_edit else "Cancha Techada de Usos Múltiples",
            options=[
                ft.DropdownOption("Cancha Techada de Usos Múltiples"),
                ft.DropdownOption("Parque Biosaludable Deportivo"),
                ft.DropdownOption("Complejo Polideportivo"),
            ],
            dense=True,
            text_size=11,
            border_radius=8,
            expand=True
        )
        año_field = ft.TextField(
            label="Año",
            value=cancha.get("año", "2026") if is_edit else "2026",
            dense=True,
            text_size=11,
            border_radius=8,
            width=120
        )
        estatus_dropdown = ft.Dropdown(
            label="Estatus *",
            value=cancha.get("estatus", "CULMINADA") if is_edit else "CULMINADA",
            options=[
                ft.DropdownOption("CULMINADA"),
                ft.DropdownOption("EN EJECUCIÓN"),
                ft.DropdownOption("PARALIZADA"),
            ],
            dense=True,
            text_size=11,
            border_radius=8,
            expand=True
        )
        pct_field = ft.TextField(
            label="Porcentaje (%) *",
            value=str(cancha.get("porcentaje", 100)) if is_edit else "100",
            dense=True,
            text_size=11,
            border_radius=8,
            width=120
        )
        trabajos_field = ft.TextField(
            label="Trabajos Realizados / Especificaciones",
            value=cancha.get("trabajos", "") if is_edit else "Pintura epóxica reglamentaria, tableros de acrílico y reflectores LED",
            dense=True,
            text_size=11,
            border_radius=8,
            multiline=True,
            min_lines=2
        )
        notas_field = ft.TextField(
            label="Observaciones Técnicas",
            value=cancha.get("notas", "") if is_edit else "",
            dense=True,
            text_size=11,
            border_radius=8,
            multiline=True,
            min_lines=2
        )

        def close_modal(e=None):
            modal_dlg.open = False
            page.update()

        def save_cancha(e=None):
            nom = nom_field.value.strip()
            if not nom:
                show_feedback_snack("Debe ingresar el nombre de la cancha.", is_error=True)
                return

            mun = mun_dropdown.value
            sec = sec_field.value.strip()
            tipo = tipo_dropdown.value
            año = año_field.value.strip() or "2026"
            est = estatus_dropdown.value
            try:
                pct = float(pct_field.value.replace("%", "").strip())
            except Exception:
                pct = 100.0 if est == "CULMINADA" else (75.0 if est == "EN EJECUCIÓN" else 45.0)
            trab = trabajos_field.value.strip()
            notas = notas_field.value.strip()

            if is_edit:
                success = state.update_cancha(
                    cancha_id=c_id,
                    estatus=est,
                    porcentaje=pct,
                    trabajos=trab,
                    notas=notas
                )
                if success:
                    show_feedback_snack(f"Cancha #{c_id} actualizada exitosamente.")
            else:
                nuevo = state.add_cancha(
                    nombre=nom,
                    municipio=mun,
                    sector=sec,
                    tipo=tipo,
                    estatus=est,
                    porcentaje=pct,
                    trabajos=trab,
                    año=año,
                    notas=notas
                )
                if nuevo:
                    show_feedback_snack(f"Nueva cancha #{nuevo.get('id')} registrada exitosamente.")

            close_modal()
            full_refresh()

        modal_dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.EDIT_ROUNDED if is_edit else ft.Icons.ADD_CIRCLE_ROUNDED, color=COLOR_ELECTRIC_BLUE, size=24),
                ft.Text("Actualizar Avance de la Cancha" if is_edit else "Registrar Nueva Cancha Deportiva", size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
            ], spacing=8),
            content=ft.Container(
                width=520,
                content=ft.Column(
                    tight=True,
                    spacing=8,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        nom_field,
                        ft.Row([mun_dropdown, sec_field], spacing=8),
                        ft.Row([tipo_dropdown, año_field], spacing=8),
                        ft.Row([estatus_dropdown, pct_field], spacing=8),
                        trabajos_field,
                        notas_field
                    ]
                )
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cancelar"),
                    on_click=close_modal
                ),
                ft.FilledButton(
                    content=ft.Text("Guardar Cambios" if is_edit else "Registrar Cancha"),
                    bgcolor=COLOR_ELECTRIC_BLUE,
                    color="#FFFFFF",
                    on_click=save_cancha
                )
            ]
        )

        if hasattr(page, "open"):
            page.open(modal_dlg)
        elif hasattr(page, "show_dialog"):
            page.show_dialog(modal_dlg)
        else:
            page.dialog = modal_dlg
            modal_dlg.open = True
            page.update()

    # 4 TARJETAS KPI DINÁMICAS SUPERIORES
    def refresh_upper_kpis():
        kpis_container.controls.clear()
        kpis = state.get_canchas_kpis(selected_mun, selected_estatus)

        def make_kpi(titulo: str, valor: str, subtitulo: str, icono, color_fondo: str, color_texto: str, color_borde: str):
            return ft.Container(
                content=ft.Column(
                    spacing=2,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row([
                            ft.Icon(icono, size=14, color=color_texto),
                            ft.Text(titulo, size=10, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=4),
                        ft.Text(valor, size=16, weight=ft.FontWeight.BOLD, color=color_texto),
                        ft.Text(subtitulo, size=9, color=COLOR_TEXT_MUTED, text_align=ft.TextAlign.CENTER)
                    ]
                ),
                padding=ft.Padding.symmetric(horizontal=8, vertical=10),
                bgcolor=color_fondo,
                border_radius=10,
                border=ft.Border.all(1, color_borde),
                expand=True
            )

        kpis_container.controls = [
            make_kpi("TOTAL INTERVENIDAS", str(kpis["total_intervenidas"]), "Infraestructura Deportiva", ft.Icons.SPORTS_BASKETBALL_ROUNDED, "#EFF6FF", COLOR_ELECTRIC_BLUE, "#BFDBFE"),
            make_kpi("CULMINADAS", str(kpis["culminadas"]), f"{kpis['pct_culminadas']}% del Total", ft.Icons.CHECK_CIRCLE_ROUNDED, "#DCFCE7", COLOR_STATUS_GREEN, "#86EFAC"),
            make_kpi("EN EJECUCIÓN", str(kpis["en_ejecucion"]), "Frentes Activos", ft.Icons.ENGINEERING_ROUNDED, "#FEF3C7", COLOR_STATUS_AMBER, "#FDE68A"),
            make_kpi("PARALIZADAS", str(kpis["paralizadas"]), "Atención Crítica", ft.Icons.WARNING_AMBER_ROUNDED, "#FEE2E2", COLOR_STATUS_RED, "#FCA5A5")
        ]

    # PESTAÑA 0: CONSOLIDADO POR MUNICIPIO (14 MUNICIPIOS)
    def build_tab_consolidado_municipio() -> ft.Control:
        resumen_list = state.get_canchas_municipios_resumen()

        if search_mun_query:
            sq = search_mun_query.lower()
            resumen_list = [m for m in resumen_list if sq in m["municipio"].lower()]

        rows = []
        for item in resumen_list:
            m_name = item["municipio"]
            c_hist = item.get("ejecutadas_2022_2024", 0)
            c_25 = item.get("ejecutadas_2025", 0)
            c_26 = item.get("ejecutadas_2026", 0)
            ejec = item.get("ejecutadas_total", 0)
            proc = item.get("en_ejecucion", 0)
            para = item.get("paralizadas", 0)
            tot = item.get("total_general", 0)
            pct = item.get("pct_ejecucion", 0.0)

            pct_color = COLOR_STATUS_GREEN if pct >= 80 else (COLOR_STATUS_AMBER if pct >= 50 else COLOR_STATUS_RED)

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Row([
                                ft.Icon(ft.Icons.LOCATION_ON_ROUNDED, size=14, color=COLOR_ELECTRIC_BLUE),
                                ft.Text(m_name, size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                            ], spacing=4)
                        ),
                        ft.DataCell(ft.Container(content=ft.Text(str(c_hist), size=11, color=COLOR_TEXT_SECONDARY), alignment=ft.Alignment(0, 0))),
                        ft.DataCell(ft.Container(content=ft.Text(str(c_25), size=11, color=COLOR_TEXT_SECONDARY), alignment=ft.Alignment(0, 0))),
                        ft.DataCell(ft.Container(content=ft.Text(str(c_26), size=11, color=COLOR_TEXT_SECONDARY), alignment=ft.Alignment(0, 0))),
                        ft.DataCell(ft.Container(content=ft.Text(str(ejec), size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN), alignment=ft.Alignment(0, 0))),
                        ft.DataCell(ft.Container(content=ft.Text(str(proc), size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_AMBER if proc > 0 else COLOR_TEXT_MUTED), alignment=ft.Alignment(0, 0))),
                        ft.DataCell(ft.Container(content=ft.Text(str(para), size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_RED if para > 0 else COLOR_TEXT_MUTED), alignment=ft.Alignment(0, 0))),
                        ft.DataCell(ft.Container(content=ft.Text(str(tot), size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK), alignment=ft.Alignment(0, 0))),
                        ft.DataCell(
                            ft.Row([
                                ft.Container(
                                    content=ft.ProgressBar(value=pct / 100.0, color=pct_color, bgcolor="#E2E8F0", width=45),
                                    alignment=ft.Alignment(0, 0)
                                ),
                                ft.Text(f"{pct}%", size=10, weight=ft.FontWeight.BOLD, color=pct_color)
                            ], spacing=4)
                        )
                    ]
                )
            )

        search_mun_field = ft.TextField(
            hint_text="Buscar municipio...",
            prefix_icon=ft.Icons.SEARCH_ROUNDED,
            dense=True,
            text_size=11,
            border_radius=8,
            border_color=COLOR_BORDER,
            expand=True,
            on_change=lambda e: on_mun_search_change(e.control.value)
        )

        def on_mun_search_change(val: str):
            nonlocal search_mun_query
            search_mun_query = val.strip()
            render_tab_content()
            page.update()

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Municipio", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)),
                ft.DataColumn(ft.Text("22-24", size=10, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED)),
                ft.DataColumn(ft.Text("2025", size=10, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED)),
                ft.DataColumn(ft.Text("2026", size=10, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED)),
                ft.DataColumn(ft.Text("Culm.", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN)),
                ft.DataColumn(ft.Text("En Ejec.", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_AMBER)),
                ft.DataColumn(ft.Text("Para.", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_RED)),
                ft.DataColumn(ft.Text("Total", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)),
                ft.DataColumn(ft.Text("Avance", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)),
            ],
            rows=rows,
            column_spacing=10,
            heading_row_height=34,
            data_row_min_height=36,
            data_row_max_height=40,
            border=ft.Border.all(1, "#E2E8F0"),
            border_radius=8
        )

        return ft.Column(
            spacing=8,
            controls=[
                ft.Row([
                    search_mun_field,
                    ft.Container(
                        content=ft.Text(f"Total: {len(resumen_list)} Municipios (135 Canchas)", size=11, color=COLOR_TEXT_MUTED, weight=ft.FontWeight.W_500),
                        padding=ft.Padding.symmetric(horizontal=8, vertical=4)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(
                    content=ft.Column(
                        scroll=ft.ScrollMode.ADAPTIVE,
                        controls=[table]
                    ),
                    expand=True
                )
            ],
            expand=True
        )

    # PESTAÑA 1: INVENTARIO GENERAL DE CANCHAS (135)
    def build_tab_inventario_canchas() -> ft.Control:
        canchas = state.get_filtered_canchas(selected_mun, selected_estatus, search_query)
        cards = []
        is_editor_role = state.is_editor()

        for c in canchas:
            c_id = c.get("id")
            nom = c.get("nombre")
            mun = c.get("municipio")
            sec = c.get("sector")
            tipo = c.get("tipo")
            est = c.get("estatus")
            pct = c.get("porcentaje")
            año = c.get("año")
            periodo = c.get("periodo", año)
            trab = c.get("trabajos", "")

            bg_st, col_st, bdr_st = get_status_badge_color(est)

            actions = [
                ft.IconButton(
                    icon=ft.Icons.VISIBILITY_ROUNDED,
                    icon_color=COLOR_ELECTRIC_BLUE,
                    icon_size=18,
                    tooltip="Ver Ficha Técnica",
                    on_click=lambda e, item=c: open_ficha_tecnica_dialog(item)
                )
            ]

            if is_editor_role:
                actions.append(
                    ft.IconButton(
                        icon=ft.Icons.EDIT_ROUNDED,
                        icon_color=COLOR_STATUS_AMBER,
                        icon_size=18,
                        tooltip="Actualizar Avance",
                        on_click=lambda e, item=c: open_cancha_modal(item)
                    )
                )

            card = ft.Container(
                content=ft.Column(
                    spacing=5,
                    controls=[
                        ft.Row([
                            ft.Row([
                                ft.Container(
                                    content=ft.Text(f"#{c_id} • {tipo}", size=10, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_BLUE),
                                    padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                    bgcolor="#EFF6FF",
                                    border_radius=4
                                ),
                                ft.Text(f"Municipio {mun}", size=11, color=COLOR_TEXT_MUTED, weight=ft.FontWeight.W_500),
                            ], spacing=6),
                            ft.Container(
                                content=ft.Text(f"{est} ({pct}%)", size=10, weight=ft.FontWeight.BOLD, color=col_st),
                                padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                bgcolor=bg_st,
                                border=ft.Border.all(1, bdr_st),
                                border_radius=4
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(nom, size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Row([
                            ft.Icon(ft.Icons.NEAR_ME_ROUNDED, size=12, color=COLOR_TEXT_MUTED),
                            ft.Text(sec, size=10, color=COLOR_TEXT_SECONDARY, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, expand=True),
                            ft.Text("•", size=10, color=COLOR_TEXT_MUTED),
                            ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED, size=12, color=COLOR_TEXT_MUTED),
                            ft.Text(f"Período: {periodo}", size=10, color=COLOR_TEXT_MUTED)
                        ], spacing=4),
                        ft.Row([
                            ft.Row([
                                ft.Icon(ft.Icons.PALETTE_ROUNDED, size=12, color=COLOR_ELECTRIC_BLUE),
                                ft.Text(trab, size=10, color=COLOR_TEXT_MUTED, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, expand=True)
                            ], spacing=4, expand=True),
                            ft.Row(actions, spacing=0)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ]
                ),
                padding=10,
                bgcolor="#FFFFFF",
                border_radius=8,
                border=ft.Border.all(1, "#E2E8F0"),
                margin=ft.Padding.only(bottom=6)
            )
            cards.append(card)

        if not cards:
            cards.append(
                ft.Container(
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.SEARCH_OFF_ROUNDED, size=36, color=COLOR_TEXT_MUTED),
                            ft.Text("No se encontraron canchas con los filtros actuales.", size=12, color=COLOR_TEXT_MUTED)
                        ]
                    ),
                    padding=20,
                    alignment=ft.Alignment(0, 0)
                )
            )

        return ft.Column(
            spacing=4,
            controls=[
                ft.Container(
                    content=ft.Text(f"Mostrando {len(canchas)} canchas e instalaciones deportivas registradas", size=11, color=COLOR_TEXT_MUTED, weight=ft.FontWeight.W_500),
                    padding=ft.Padding.symmetric(horizontal=4, vertical=2)
                ),
                ft.Container(
                    content=ft.ListView(
                        controls=cards,
                        expand=True,
                        spacing=6
                    ),
                    expand=True
                )
            ],
            expand=True
        )

    # PESTAÑA 2: FRENTES ACTIVOS Y PARALIZADOS (13 FRENTES)
    def build_tab_frentes_prioritarios() -> ft.Control:
        frentes = state.get_canchas_frentes_prioritarios(selected_mun)
        is_editor_role = state.is_editor()

        frentes_cards = []
        for c in frentes:
            c_id = c.get("id")
            nom = c.get("nombre")
            mun = c.get("municipio")
            sec = c.get("sector")
            tipo = c.get("tipo")
            est = c.get("estatus")
            pct = c.get("porcentaje")
            trab = c.get("trabajos", "")

            is_para = est == "PARALIZADA"
            border_c = COLOR_STATUS_RED if is_para else COLOR_STATUS_AMBER
            bg_card = "#FFF5F5" if is_para else "#FFFBEB"

            edit_btn = ft.IconButton(
                icon=ft.Icons.EDIT_ROUNDED,
                icon_color=border_c,
                icon_size=18,
                tooltip="Actualizar Estado del Frente",
                on_click=lambda e, item=c: open_cancha_modal(item)
            ) if is_editor_role else ft.Container()

            card = ft.Container(
                content=ft.Column(
                    spacing=6,
                    controls=[
                        ft.Row([
                            ft.Row([
                                ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED if is_para else ft.Icons.CONSTRUCTION_ROUNDED, color=border_c, size=16),
                                ft.Text(f"Frente #{c_id} • {tipo}", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                ft.Text(f"({mun})", size=11, color=COLOR_TEXT_MUTED)
                            ], spacing=6),
                            ft.Row([
                                ft.Container(
                                    content=ft.Text(f"{est} • {pct}%", size=11, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                    padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                    bgcolor=border_c,
                                    border_radius=4
                                ),
                                edit_btn
                            ], spacing=4)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(nom, size=14, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.ProgressBar(value=pct / 100.0, color=border_c, bgcolor="#E2E8F0", height=6),
                        ft.Row([
                            ft.Icon(ft.Icons.LOCATION_ON_ROUNDED, size=12, color=COLOR_ELECTRIC_BLUE),
                            ft.Text(f"Sector: {sec}", size=11, color=COLOR_NAVY_DARK, weight=ft.FontWeight.W_500),
                        ], spacing=4),
                        ft.Row([
                            ft.Icon(ft.Icons.BUILD_ROUNDED, size=12, color=COLOR_TEXT_MUTED),
                            ft.Text(f"Estado de obra: {trab}", size=10, color=COLOR_TEXT_SECONDARY, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, expand=True)
                        ], spacing=4)
                    ]
                ),
                padding=10,
                bgcolor=bg_card,
                border_radius=8,
                border=ft.Border.all(1.5, border_c),
                margin=ft.Padding.only(bottom=6)
            )
            frentes_cards.append(card)

        if not frentes_cards:
            frentes_cards.append(
                ft.Container(
                    content=ft.Text("No hay frentes en ejecución o paralizados para la selección actual.", size=12, color=COLOR_TEXT_MUTED),
                    padding=20,
                    alignment=ft.Alignment(0, 0)
                )
            )

        return ft.Column(
            spacing=4,
            controls=[
                ft.Container(
                    content=ft.Row([
                        ft.Text(f"Prioridad Gerencial PCEO: {len(frentes)} canchas en seguimiento especial", size=11, color=COLOR_NAVY_DARK, weight=ft.FontWeight.BOLD),
                        ft.Text("4 En Ejecución • 9 Paralizadas", size=10, color=COLOR_STATUS_AMBER, weight=ft.FontWeight.BOLD)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.Padding.symmetric(horizontal=4, vertical=2)
                ),
                ft.Container(
                    content=ft.ListView(
                        controls=frentes_cards,
                        expand=True,
                        spacing=6
                    ),
                    expand=True
                )
            ],
            expand=True
        )

    # RENDERIZADO DE PESTAÑAS (TABS PERSONALIZADOS)
    tabs_def = [
        ("Consolidado por Municipio (14)", ft.Icons.MAP_ROUNDED),
        ("Inventario General Canchas (135)", ft.Icons.SPORTS_BASKETBALL_ROUNDED),
        ("Frentes Activos y Paralizados (13)", ft.Icons.WARNING_AMBER_ROUNDED),
    ]

    def select_tab(index: int):
        nonlocal active_tab
        active_tab = index
        render_tab_chips()
        render_tab_content()
        page.update()

    def render_tab_chips():
        tab_chips_row.controls.clear()
        for idx, (label, icon) in enumerate(tabs_def):
            is_sel = idx == active_tab
            tab_chips_row.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(icon, size=14, color="#FFFFFF" if is_sel else COLOR_NAVY_DARK),
                        ft.Text(label, size=11, weight=ft.FontWeight.BOLD if is_sel else ft.FontWeight.W_500, color="#FFFFFF" if is_sel else COLOR_NAVY_DARK)
                    ], spacing=4),
                    padding=ft.Padding.symmetric(horizontal=10, vertical=6),
                    bgcolor=COLOR_ELECTRIC_BLUE if is_sel else "#F1F5F9",
                    border_radius=8,
                    border=ft.Border.all(1, COLOR_ELECTRIC_BLUE if is_sel else "#CBD5E1"),
                    on_click=lambda e, i=idx: select_tab(i)
                )
            )

    def render_tab_content():
        if active_tab == 0:
            tab_content_area.content = build_tab_consolidado_municipio()
        elif active_tab == 1:
            tab_content_area.content = build_tab_inventario_canchas()
        elif active_tab == 2:
            tab_content_area.content = build_tab_frentes_prioritarios()

    def full_refresh():
        refresh_upper_kpis()
        render_tab_chips()
        render_tab_content()
        page.update()

    # BARRA SUPERIOR DE FILTROS
    mun_filter_dropdown = ft.Dropdown(
        label="Municipio",
        value=selected_mun,
        options=[ft.DropdownOption("Todos los Municipios")] + [ft.DropdownOption(m) for m in MUNICIPALITIES_LIST if m != "Todos los Municipios"],
        dense=True,
        text_size=11,
        border_radius=8,
        border_color=COLOR_BORDER,
        expand=True,
        on_select=lambda e: on_mun_filter_changed(e.control.value)
    )

    estatus_filter_dropdown = ft.Dropdown(
        label="Estatus",
        value=selected_estatus,
        options=[
            ft.DropdownOption("Todos los Estatus"),
            ft.DropdownOption("Culminada (122)"),
            ft.DropdownOption("En Ejecución (4)"),
            ft.DropdownOption("Paralizada (9)"),
        ],
        dense=True,
        text_size=11,
        border_radius=8,
        border_color=COLOR_BORDER,
        expand=True,
        on_select=lambda e: on_estatus_filter_changed(e.control.value)
    )

    def on_mun_filter_changed(val: str):
        nonlocal selected_mun
        selected_mun = val
        state.set_canchas_filters(municipality=val)
        full_refresh()

    def on_estatus_filter_changed(val: str):
        nonlocal selected_estatus
        selected_estatus = val
        state.set_canchas_filters(estatus=val)
        full_refresh()

    filter_bar = ft.Container(
        content=ft.Row([
            mun_filter_dropdown,
            estatus_filter_dropdown,
        ], spacing=8),
        padding=ft.Padding.symmetric(horizontal=12, vertical=4)
    )

    search_bar_field = ft.TextField(
        hint_text="Buscar cancha por nombre, municipio o sector...",
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        dense=True,
        text_size=11,
        border_radius=8,
        border_color=COLOR_BORDER,
        expand=True,
        on_change=lambda e: on_search_text_changed(e.control.value)
    )

    def on_search_text_changed(val: str):
        nonlocal search_query
        search_query = val.strip()
        render_tab_content()
        page.update()

    admin_buttons = []
    if state.is_editor():
        admin_buttons.append(
            ft.FilledButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.ADD_CIRCLE_ROUNDED, size=14, color="#FFFFFF"),
                    ft.Text("+ Registrar / Actualizar Cancha", size=11, weight=ft.FontWeight.BOLD)
                ], spacing=4),
                bgcolor=COLOR_STATUS_GREEN,
                color="#FFFFFF",
                on_click=lambda e: open_cancha_modal(None)
            )
        )

    search_bar = ft.Container(
        content=ft.Row([
            search_bar_field,
            ft.Row(admin_buttons, spacing=6)
        ], spacing=8),
        padding=ft.Padding.symmetric(horizontal=12, vertical=4)
    )

    # Detección de logo oficial
    logo_path = "logo_cancha.png" if os.path.exists("assets/logo_cancha.png") else ("logo_canchas.png" if os.path.exists("assets/logo_canchas.png") else None)
    leading_logo = (
        ft.Image(src=logo_path, width=42, height=42, fit="contain")
        if logo_path else ft.Icon(ft.Icons.SPORTS_BASKETBALL_ROUNDED, size=28, color=COLOR_ELECTRIC_BLUE)
    )
    header_box = create_institutional_header(
        title="Plan Una Cancha para Todos",
        subtitle="Puesto de Comando Estratégico Operacional del Estado Portuguesa • PCEO",
        show_back_button=True,
        on_back_click=lambda e: on_back_to_summary(),
        on_logout_click=lambda e: on_logout(),
        on_switch_role_click=on_switch_role,
        show_user_chip=True,
        leading_logo=leading_logo
    )

    refresh_upper_kpis()
    render_tab_chips()
    render_tab_content()

    return ft.Container(
        content=ft.Column(
            spacing=10,
            expand=True,
            controls=[
                header_box,
                filter_bar,
                search_bar,
                kpis_container,
                ft.Container(
                    content=tab_chips_row,
                    padding=ft.Padding.only(bottom=15)
                ),
                tab_content_area
            ]
        ),
        padding=10,
        expand=True
    )
