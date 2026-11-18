"""
Módulo Detallado: Plan de Recuperación y Construcción de Puentes y Alcantarillas
Puesto de Comando Estratégico Operacional del Estado Portuguesa (PCEO)
Infraestructura Vial, Puentes, Alcantarillas y Cajones de Paso (2023 - 2026)
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
from data.water_data import MUNICIPALITIES_LIST
from data.state import AppState
from modules.excel_import_panel import ExcelImportPanel

def fmt_es(val: int | float, dec: int = 0) -> str:
    """Formatea números con separador de miles en punto y decimal en coma."""
    if val is None:
        return "0"
    if dec > 0:
        return f"{float(val):,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{int(round(float(val))):,}".replace(",", ".")

def build_puentes_view(
    page: ft.Page,
    on_back_to_summary,
    on_switch_role,
    on_logout
) -> ft.Control:
    """Construye la vista interactiva oficial del Plan Puentes y Alcantarillas."""
    state = AppState()

    # Estado local de navegación y filtros
    active_tab = 0  # 0 a 3
    selected_mun = state.puentes_municipality
    selected_tipo = state.puentes_tipo
    selected_yr = state.puentes_year
    search_query = ""

    # Buscadores locales
    search_mun_query = ""

    # Áreas dinámicas
    kpis_container = ft.Row(spacing=8)
    tab_content_area = ft.Container(expand=True)
    tab_chips_row = ft.Row(scroll=ft.ScrollMode.ADAPTIVE, spacing=6)

    # -------------------------------------------------------------
    # DIÁLOGOS Y NOTIFICACIONES (SOLO MASTER Y ANALISTA)
    # -------------------------------------------------------------
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

    # Modal de Ficha Técnica Completa con Memoria Descriptiva de Ingeniería
    def open_ficha_tecnica_dialog(obra: dict):
        obra_id = obra.get("id")
        nombre = obra.get("nombre", "Obra sin nombre")
        tipo = obra.get("tipo_obra", "PUENTE")
        mun = obra.get("municipio", "Portuguesa")
        year = obra.get("year", "2026")
        fechas = obra.get("fechas", "En proceso")
        estatus = obra.get("estatus", "EN DESARROLLO")
        pct = obra.get("pct_avance", 100)
        memoria = obra.get("memoria_tecnica") or "Memoria descriptiva técnica en proceso de consolidación por ESINSEP y Ministerio de Transporte."
        notas = obra.get("notas_inspeccion", "")

        status_color = COLOR_STATUS_GREEN if estatus == "EJECUTADO" else (COLOR_STATUS_AMBER if estatus == "EN DESARROLLO" else COLOR_STATUS_RED)

        def close_dialog(e=None):
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.DESCRIPTION_ROUNDED, color=COLOR_ELECTRIC_BLUE, size=24),
                ft.Text("Ficha Técnica de Ingeniería", size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
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
                                content=ft.Text(f"Obra #{obra_id} • {tipo}", size=11, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                bgcolor=COLOR_ELECTRIC_BLUE if tipo == "PUENTE" else (COLOR_STATUS_GREEN if tipo == "ALCANTARILLA" else COLOR_STATUS_AMBER),
                                border_radius=4
                            ),
                            ft.Container(
                                content=ft.Text(f"{estatus} ({pct}%)", size=11, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                bgcolor=status_color,
                                border_radius=4
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(nombre, size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Container(
                            content=ft.Row([
                                ft.Row([
                                    ft.Icon(ft.Icons.LOCATION_CITY_ROUNDED, size=14, color=COLOR_ELECTRIC_BLUE),
                                    ft.Text(f"{mun} • Año {year}", size=11, color=COLOR_NAVY_DARK, weight=ft.FontWeight.W_500)
                                ], spacing=4),
                                ft.Row([
                                    ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED, size=14, color=COLOR_TEXT_MUTED),
                                    ft.Text(fechas, size=11, color=COLOR_TEXT_MUTED)
                                ], spacing=4)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            padding=8,
                            bgcolor="#F8FAFC",
                            border_radius=6,
                            border=ft.Border.all(1, "#E2E8F0")
                        ),
                        ft.Text("Memoria Descriptiva y Detalle Técnico:", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Container(
                            content=ft.Column([
                                ft.Text(memoria, size=11, color=COLOR_TEXT_PRIMARY, selectable=True)
                            ], scroll=ft.ScrollMode.ADAPTIVE),
                            height=170,
                            padding=10,
                            bgcolor="#F1F5F9",
                            border_radius=8,
                            border=ft.Border.all(1, "#CBD5E1")
                        ),
                        ft.Text(f"Bitácora / Notas de Inspección: {notas or 'Sin notas adicionales registradas.'}", size=10, color=COLOR_TEXT_MUTED, italic=True)
                    ]
                )
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cerrar", color=COLOR_TEXT_SECONDARY),
                    on_click=close_dialog
                ),
                (ft.FilledButton(
                    content=ft.Text("Editar Avance", color="#FFFFFF", weight=ft.FontWeight.BOLD),
                    bgcolor=COLOR_ELECTRIC_BLUE,
                    on_click=lambda e: (close_dialog(), open_actualizar_obra_dialog(obra))
                ) if state.is_editor() else ft.Container())
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        if hasattr(page, "open"):
            page.open(dlg)
        elif hasattr(page, "show_dialog"):
            page.show_dialog(dlg)
        else:
            page.dialog = dlg
            dlg.open = True
            page.update()

    # Modal para Actualizar Avance y Estatus de una Obra (Solo Master y Analista)
    def open_actualizar_obra_dialog(obra: dict):
        if not state.is_editor():
            show_feedback_snack("Acceso denegado: Función reservada para roles Master y Analista.", is_error=True)
            return

        obra_id = obra.get("id")
        estatus_actual = obra.get("estatus", "EN DESARROLLO")
        pct_actual = obra.get("pct_avance", 100)

        estatus_dropdown = ft.Dropdown(
            label="Estatus de la Obra",
            value=estatus_actual,
            options=[
                ft.dropdown.Option("EJECUTADO"),
                ft.dropdown.Option("EN DESARROLLO"),
                ft.dropdown.Option("PARALIZADO")
            ],
            border_color="#CBD5E1",
            focused_border_color=COLOR_ELECTRIC_BLUE,
            height=45,
            text_size=13
        )

        avance_field = ft.TextField(
            label="% Avance Físico (0 - 100)",
            value=str(pct_actual),
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color="#CBD5E1",
            focused_border_color=COLOR_ELECTRIC_BLUE,
            height=45,
            text_size=13
        )

        fechas_field = ft.TextField(
            label="Fechas de Inicio / Culminación",
            value=obra.get("fechas", ""),
            hint_text="Ej. I: 15/02/26 C: 20/05/26",
            border_color="#CBD5E1",
            focused_border_color=COLOR_ELECTRIC_BLUE,
            height=45,
            text_size=13
        )

        notas_field = ft.TextField(
            label="Notas Técnicas de Inspección",
            value=obra.get("notas_inspeccion", ""),
            hint_text="Detalles del vaciado, materiales, pruebas de carga o causas de paralización",
            multiline=True,
            min_lines=2,
            border_color="#CBD5E1",
            focused_border_color=COLOR_ELECTRIC_BLUE,
            text_size=12
        )

        def close_dialog(e=None):
            dlg_edit.open = False
            page.update()

        def confirm_update(e=None):
            nuevo_est = estatus_dropdown.value or "EJECUTADO"
            try:
                pct_num = float(avance_field.value.strip() or "100")
                if pct_num > 100:
                    pct_num = 100
                elif pct_num < 0:
                    pct_num = 0
            except ValueError:
                pct_num = 100.0

            nuevo_avance = pct_num / 100.0
            if nuevo_est == "EJECUTADO":
                nuevo_avance = 1.0

            notas_txt = notas_field.value.strip()
            fechas_txt = fechas_field.value.strip() or obra.get("fechas", "")

            ok = state.update_puente_obra(
                obra_id=obra_id,
                nuevo_estatus=nuevo_est,
                nuevo_avance=nuevo_avance,
                notas=notas_txt,
                fecha_culminacion=fechas_txt
            )
            if ok:
                close_dialog()
                full_refresh()
                show_feedback_snack(f"Obra #{obra_id} actualizada: {nuevo_est} ({int(round(nuevo_avance*100))}%).")
            else:
                show_feedback_snack("Error al actualizar la obra.", is_error=True)

        dlg_edit = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.EDIT_NOTE_ROUNDED, color=COLOR_ELECTRIC_BLUE, size=24),
                ft.Text(f"Actualizar Obra #{obra_id}", size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
            ], spacing=8),
            content=ft.Container(
                width=450,
                content=ft.Column(
                    tight=True,
                    spacing=8,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Text(obra.get("nombre", "")[:75] + "...", size=11, color=COLOR_TEXT_SECONDARY, weight=ft.FontWeight.W_500),
                        estatus_dropdown,
                        avance_field,
                        fechas_field,
                        notas_field
                    ]
                )
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cancelar", color=COLOR_TEXT_SECONDARY),
                    on_click=close_dialog
                ),
                ft.FilledButton(
                    content=ft.Text("Guardar Cambios", color="#FFFFFF", weight=ft.FontWeight.BOLD),
                    bgcolor=COLOR_STATUS_GREEN,
                    on_click=confirm_update
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        if hasattr(page, "open"):
            page.open(dlg_edit)
        elif hasattr(page, "show_dialog"):
            page.show_dialog(dlg_edit)
        else:
            page.dialog = dlg_edit
            dlg_edit.open = True
            page.update()

    # Modal para Registrar Nueva Obra (+ Nueva Obra)
    def open_nueva_obra_modal(e=None):
        if not state.is_editor():
            show_feedback_snack("Acceso denegado: Función reservada para roles Master y Analista.", is_error=True)
            return

        muns_options = [m for m in MUNICIPALITIES_LIST if m != "Todos los Municipios"]

        nombre_field = ft.TextField(
            label="Nombre Completo de la Obra",
            hint_text="Ej. Construcción de puente sobre el río...",
            border_color="#CBD5E1",
            focused_border_color=COLOR_ELECTRIC_BLUE,
            text_size=12
        )

        mun_dropdown = ft.Dropdown(
            label="Municipio",
            value="Guanare",
            options=[ft.dropdown.Option(m) for m in muns_options],
            border_color="#CBD5E1",
            focused_border_color=COLOR_ELECTRIC_BLUE,
            height=45,
            text_size=13
        )

        tipo_dropdown = ft.Dropdown(
            label="Tipo de Obra",
            value="PUENTE",
            options=[
                ft.dropdown.Option("PUENTE"),
                ft.dropdown.Option("ALCANTARILLA"),
                ft.dropdown.Option("CAJON")
            ],
            border_color="#CBD5E1",
            focused_border_color=COLOR_ELECTRIC_BLUE,
            height=45,
            text_size=13
        )

        year_dropdown = ft.Dropdown(
            label="Año de Inicio",
            value="2026",
            options=[
                ft.dropdown.Option("2026"),
                ft.dropdown.Option("2025"),
                ft.dropdown.Option("2024"),
                ft.dropdown.Option("2023")
            ],
            border_color="#CBD5E1",
            focused_border_color=COLOR_ELECTRIC_BLUE,
            height=45,
            text_size=13
        )

        estatus_dropdown = ft.Dropdown(
            label="Estatus Inicial",
            value="EN DESARROLLO",
            options=[
                ft.dropdown.Option("EN DESARROLLO"),
                ft.dropdown.Option("EJECUTADO"),
                ft.dropdown.Option("PARALIZADO")
            ],
            border_color="#CBD5E1",
            focused_border_color=COLOR_ELECTRIC_BLUE,
            height=45,
            text_size=13
        )

        avance_field = ft.TextField(
            label="% Avance Inicial (0 - 100)",
            value="25",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color="#CBD5E1",
            focused_border_color=COLOR_ELECTRIC_BLUE,
            height=45,
            text_size=13
        )

        notas_field = ft.TextField(
            label="Memoria / Observaciones Iniciales",
            hint_text="Detalles técnicos de tubería, concreto o acero",
            multiline=True,
            min_lines=2,
            border_color="#CBD5E1",
            focused_border_color=COLOR_ELECTRIC_BLUE,
            text_size=12
        )

        def close_modal(ev=None):
            modal_dlg.open = False
            page.update()

        def save_nueva_obra(ev=None):
            nombre = nombre_field.value.strip()
            if not nombre:
                show_feedback_snack("Debe ingresar el nombre de la obra.", is_error=True)
                return

            mun = mun_dropdown.value or "Guanare"
            tipo = tipo_dropdown.value or "PUENTE"
            yr = year_dropdown.value or "2026"
            est = estatus_dropdown.value or "EN DESARROLLO"
            try:
                pct = float(avance_field.value.strip() or "25")
            except ValueError:
                pct = 25.0
            av = pct / 100.0 if est != "EJECUTADO" else 1.0
            notas = notas_field.value.strip()

            rec = state.add_puente_obra(
                nombre=nombre,
                municipio=mun,
                tipo_obra=tipo,
                year=yr,
                estatus=est,
                avance=av,
                notas=notas
            )
            close_modal()
            full_refresh()
            show_feedback_snack(f"Nueva obra registrada con ID #{rec.get('id')}.")

        modal_dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED, color=COLOR_ELECTRIC_BLUE, size=22),
                ft.Text("Registrar Nueva Obra de Vialidad", size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
            ], spacing=8),
            content=ft.Container(
                width=460,
                content=ft.Column(
                    tight=True,
                    spacing=8,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        nombre_field,
                        ft.Row([mun_dropdown, tipo_dropdown], spacing=8),
                        ft.Row([year_dropdown, estatus_dropdown], spacing=8),
                        avance_field,
                        notas_field
                    ]
                )
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cancelar", color=COLOR_TEXT_SECONDARY),
                    on_click=close_modal
                ),
                ft.FilledButton(
                    content=ft.Text("Registrar Obra", color="#FFFFFF", weight=ft.FontWeight.BOLD),
                    bgcolor=COLOR_ELECTRIC_BLUE,
                    on_click=save_nueva_obra
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        if hasattr(page, "open"):
            page.open(modal_dlg)
        elif hasattr(page, "show_dialog"):
            page.show_dialog(modal_dlg)
        else:
            page.dialog = modal_dlg
            modal_dlg.open = True
            page.update()

    # Panel de Importación de Excel sin congelamiento
    import_panel_obj = ExcelImportPanel(
        page=page,
        title="Importar Excel Puentes y Alcantarillas (.xlsx)",
        default_file="ACUMULADOS PUENTES Y ALCANTARILLAS 23-24-25-26.xlsx",
        on_load_callback=state.reload_puentes_excel,
        on_success_callback=lambda: full_refresh(),
        accent_color=COLOR_ELECTRIC_BLUE
    )

    def import_excel_dialog(e=None):
        import_panel_obj.toggle(e)

    # -------------------------------------------------------------
    # 4 TARJETAS KPI DINÁMICAS SUPERIORES
    # -------------------------------------------------------------
    def refresh_upper_kpis():
        kpis_container.controls.clear()
        kpis = state.get_puentes_kpis(selected_mun, selected_tipo, selected_yr)

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
            make_kpi(
                "Total Obras",
                f"{fmt_es(kpis['total_obras'])}",
                f"{kpis['puentes']} Puentes • {kpis['alcantarillas']} Alcant. • {kpis['cajones']} Cajones",
                ft.Icons.WAVES_ROUNDED,
                "#EFF6FF",
                COLOR_ELECTRIC_BLUE,
                "#BFDBFE"
            ),
            make_kpi(
                "Obras Ejecutadas",
                f"{fmt_es(kpis['ejecutadas'])}",
                f"{kpis['pct_ejecutado']}% de efectividad total",
                ft.Icons.CHECK_CIRCLE_ROUNDED,
                "#F0FDF4",
                COLOR_STATUS_GREEN,
                "#BBF7D0"
            ),
            make_kpi(
                "En Desarrollo",
                f"{fmt_es(kpis['en_desarrollo'])}",
                "Frentes de trabajo activos",
                ft.Icons.PENDING_ACTIONS_ROUNDED,
                "#FFFBEB",
                COLOR_STATUS_AMBER,
                "#FDE68A"
            ),
            make_kpi(
                "Paralizadas / Suspend.",
                f"{fmt_es(kpis['paralizadas'])}",
                "Requieren reactivación",
                ft.Icons.PAUSE_CIRCLE_ROUNDED,
                "#FEF2F2",
                COLOR_STATUS_RED,
                "#FECACA"
            ),
        ]

    # -------------------------------------------------------------
    # CONSTRUCCIÓN DE LAS 4 PESTAÑAS
    # -------------------------------------------------------------

    # PESTAÑA 0: Resumen por Municipio
    def build_tab_resumen_municipio() -> ft.Control:
        data = state.puentes_data or {}
        por_mun = data.get("por_municipio", {})

        search_mun_field = ft.TextField(
            hint_text="Buscar municipio...",
            prefix_icon=ft.Icons.SEARCH_ROUNDED,
            value=search_mun_query,
            height=38,
            text_size=12,
            border_color="#CBD5E1",
            focused_border_color=COLOR_ELECTRIC_BLUE,
            expand=True,
            on_change=lambda e: on_search_mun(e.control.value)
        )

        def on_search_mun(q: str):
            nonlocal search_mun_query
            search_mun_query = q.strip().lower()
            render_tab_content()

        # Filtrar municipios
        items = []
        for mun_name, m_info in por_mun.items():
            if search_mun_query and search_mun_query not in mun_name.lower():
                continue
            items.append(m_info)

        # Ordenar por total descendente
        items.sort(key=lambda x: x.get("total", 0), reverse=True)

        filas = []
        for it in items:
            filas.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.LOCATION_CITY_ROUNDED, size=14, color=COLOR_ELECTRIC_BLUE),
                                ft.Text(it["municipio"], size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                            ], spacing=6),
                            width=160
                        ),
                        ft.Container(ft.Text(fmt_es(it.get("total", 0)), size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK), width=80, alignment=ft.Alignment(1, 0)),
                        ft.Container(ft.Text(fmt_es(it.get("puentes", 0)), size=12, color=COLOR_ELECTRIC_BLUE), width=85, alignment=ft.Alignment(1, 0)),
                        ft.Container(ft.Text(fmt_es(it.get("alcantarillas", 0)), size=12, color=COLOR_STATUS_GREEN), width=95, alignment=ft.Alignment(1, 0)),
                        ft.Container(ft.Text(fmt_es(it.get("cajones", 0)), size=12, color=COLOR_STATUS_AMBER), width=80, alignment=ft.Alignment(1, 0)),
                        ft.Container(ft.Text(fmt_es(it.get("ejecutadas", 0)), size=12, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN), width=90, alignment=ft.Alignment(1, 0)),
                        ft.Container(
                            ft.Text(
                                f"{it.get('en_desarrollo', 0)} / {it.get('paralizadas', 0)}",
                                size=11,
                                weight=ft.FontWeight.BOLD if (it.get('en_desarrollo', 0) + it.get('paralizadas', 0) > 0) else ft.FontWeight.NORMAL,
                                color=COLOR_STATUS_AMBER if it.get('en_desarrollo', 0) > 0 else (COLOR_STATUS_RED if it.get('paralizadas', 0) > 0 else COLOR_TEXT_MUTED)
                            ),
                            width=120,
                            alignment=ft.Alignment(1, 0)
                        ),
                    ], spacing=10),
                    padding=ft.Padding.symmetric(horizontal=10, vertical=8),
                    border=ft.Border(bottom=ft.BorderSide(1, "#F1F5F9")),
                    bgcolor="#FFFFFF"
                )
            )

        tot = data.get("totales_estatales", {})
        fila_total = ft.Container(
            content=ft.Row([
                ft.Container(ft.Text("TOTAL PORTUGUESA", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK), width=160),
                ft.Container(ft.Text(fmt_es(tot.get("total_obras", 154)), size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK), width=80, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text(fmt_es(tot.get("puentes", 78)), size=12, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_BLUE), width=85, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text(fmt_es(tot.get("alcantarillas", 66)), size=12, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN), width=95, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text(fmt_es(tot.get("cajones", 10)), size=12, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_AMBER), width=80, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text(fmt_es(tot.get("ejecutadas", 145)), size=12, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN), width=90, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text(f"{tot.get('en_desarrollo', 5)} / {tot.get('paralizadas', 4)}", size=11, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_AMBER), width=120, alignment=ft.Alignment(1, 0)),
            ], spacing=10),
            padding=ft.Padding.symmetric(horizontal=10, vertical=10),
            bgcolor="#F8FAFC",
            border_radius=8,
            border=ft.Border.all(1, "#E2E8F0")
        )

        header_tabla = ft.Container(
            content=ft.Row([
                ft.Container(ft.Text("Municipio", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=160),
                ft.Container(ft.Text("Total Obras", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=80, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text("Puentes", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=85, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text("Alcantarillas", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=95, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text("Cajones", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=80, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text("Ejecutadas", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=90, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text("Desarr. / Paral.", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=120, alignment=ft.Alignment(1, 0)),
            ], spacing=10),
            padding=ft.Padding.symmetric(horizontal=10, vertical=8),
            bgcolor="#F1F5F9",
            border_radius=6
        )

        return ft.Column(
            spacing=10,
            expand=True,
            controls=[
                ft.Row([
                    search_mun_field,
                    ft.Text(f"{len(items)} Municipios con Obras", size=11, color=COLOR_TEXT_MUTED)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                header_tabla,
                ft.Container(
                    content=ft.ListView(controls=filas, spacing=0),
                    expand=True,
                    border=ft.Border.all(1, "#E2E8F0"),
                    border_radius=8
                ),
                fila_total
            ]
        )

    # PESTAÑA 1: Inventario General de Obras (154)
    def build_tab_inventario_obras() -> ft.Control:
        data = state.puentes_data or {}
        obras = data.get("obras", [])

        # Aplicar filtros superiores
        filtradas = []
        for o in obras:
            if selected_mun and selected_mun != "Todos los Municipios" and selected_mun != "Todos":
                if o.get("municipio") != selected_mun:
                    continue
            if selected_tipo and selected_tipo != "Todas":
                if "PUENTE" in selected_tipo.upper() and o.get("tipo_obra") != "PUENTE":
                    continue
                if "ALCANTARILLA" in selected_tipo.upper() and o.get("tipo_obra") != "ALCANTARILLA":
                    continue
                if "CAJON" in selected_tipo.upper() and o.get("tipo_obra") != "CAJON":
                    continue
            if selected_yr and selected_yr != "Todos (2023-2026)" and selected_yr != "Todos":
                if o.get("year") != selected_yr:
                    continue
            if search_query:
                txt = f"{o.get('nombre', '')} {o.get('municipio', '')} {o.get('tipo_obra', '')} {o.get('fechas', '')}".lower()
                if search_query not in txt:
                    continue
            filtradas.append(o)

        cards = []
        for o in filtradas:
            tipo = o.get("tipo_obra", "PUENTE")
            est = o.get("estatus", "EJECUTADO")
            pct = o.get("pct_avance", 100)

            tipo_color = COLOR_ELECTRIC_BLUE if tipo == "PUENTE" else (COLOR_STATUS_GREEN if tipo == "ALCANTARILLA" else COLOR_STATUS_AMBER)
            status_color = COLOR_STATUS_GREEN if est == "EJECUTADO" else (COLOR_STATUS_AMBER if est == "EN DESARROLLO" else COLOR_STATUS_RED)

            card = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Row([
                            ft.Container(
                                content=ft.Text(tipo, size=10, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                bgcolor=tipo_color,
                                border_radius=4
                            ),
                            ft.Text(f"#{o.get('id')}", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED),
                            ft.Text(f"{o.get('municipio')} • Año {o.get('year')}", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                        ], spacing=6),
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(
                                    ft.Icons.CHECK_CIRCLE_ROUNDED if est == "EJECUTADO" else (ft.Icons.PENDING_ACTIONS_ROUNDED if est == "EN DESARROLLO" else ft.Icons.PAUSE_CIRCLE_ROUNDED),
                                    size=12,
                                    color="#FFFFFF"
                                ),
                                ft.Text(est, size=10, weight=ft.FontWeight.BOLD, color="#FFFFFF")
                            ], spacing=4),
                            padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                            bgcolor=status_color,
                            border_radius=4
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(o.get("nombre", ""), size=12, weight=ft.FontWeight.W_500, color=COLOR_NAVY_DARK),
                    ft.Row([
                        ft.Row([
                            ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED, size=12, color=COLOR_TEXT_MUTED),
                            ft.Text(o.get("fechas", "-"), size=10, color=COLOR_TEXT_MUTED)
                        ], spacing=4),
                        ft.Row([
                            ft.ProgressBar(value=(pct / 100.0), color=status_color, bgcolor="#E2E8F0", height=6, width=100),
                            ft.Text(f"{pct}%", size=10, weight=ft.FontWeight.BOLD, color=status_color)
                        ], spacing=6)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=1, color="#F1F5F9"),
                    ft.Row([
                        ft.TextButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.DESCRIPTION_ROUNDED, size=13, color=COLOR_ELECTRIC_BLUE),
                                ft.Text("Ver Ficha Técnica", size=11, color=COLOR_ELECTRIC_BLUE, weight=ft.FontWeight.BOLD)
                            ], spacing=4),
                            on_click=lambda e, item=o: open_ficha_tecnica_dialog(item)
                        ),
                        (ft.TextButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.EDIT_NOTE_ROUNDED, size=13, color=COLOR_NAVY_DARK),
                                ft.Text("Actualizar Avance", size=11, color=COLOR_NAVY_DARK, weight=ft.FontWeight.BOLD)
                            ], spacing=4),
                            on_click=lambda e, item=o: open_actualizar_obra_dialog(item)
                        ) if state.is_editor() else ft.Container())
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ], spacing=6),
                padding=10,
                bgcolor="#FFFFFF",
                border_radius=8,
                border=ft.Border.all(1, "#E2E8F0")
            )
            cards.append(card)

        return ft.Column(
            spacing=10,
            expand=True,
            controls=[
                ft.Row([
                    ft.Text(f"Mostrando {len(cards)} de {len(obras)} obras", size=11, color=COLOR_TEXT_MUTED),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(
                    content=ft.ListView(controls=cards, spacing=8),
                    expand=True
                )
            ]
        )

    # PESTAÑA 2: Frentes Activos y Paralizados (9)
    def build_tab_frentes_prioritarios() -> ft.Control:
        data = state.puentes_data or {}
        obras = data.get("obras", [])

        en_desarrollo = [o for o in obras if o["estatus"] == "EN DESARROLLO"]
        paralizadas = [o for o in obras if o["estatus"] == "PARALIZADO"]

        def make_frente_card(o: dict, is_paralizado: bool = False):
            bg_col = "#FEF2F2" if is_paralizado else "#FFFBEB"
            brd_col = "#FECACA" if is_paralizado else "#FDE68A"
            icon_d = ft.Icons.PAUSE_CIRCLE_ROUNDED if is_paralizado else ft.Icons.PENDING_ACTIONS_ROUNDED
            tag_col = COLOR_STATUS_RED if is_paralizado else COLOR_STATUS_AMBER

            return ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Row([
                            ft.Icon(icon_d, size=16, color=tag_col),
                            ft.Text(f"Obra #{o.get('id')} • {o.get('tipo_obra')}", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ], spacing=6),
                        ft.Container(
                            content=ft.Text(f"{o.get('pct_avance')}% • {o.get('estatus')}", size=10, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                            padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                            bgcolor=tag_col,
                            border_radius=4
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(o.get("nombre", ""), size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                    ft.Row([
                        ft.Text(f"Ubicación: {o.get('municipio')} • Año {o.get('year')}", size=10, color=COLOR_TEXT_SECONDARY),
                        ft.Text(f"Fechas: {o.get('fechas')}", size=10, color=COLOR_TEXT_MUTED)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([
                        ft.TextButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.DESCRIPTION_ROUNDED, size=12, color=COLOR_ELECTRIC_BLUE),
                                ft.Text("Ver Ficha Técnica", size=10, color=COLOR_ELECTRIC_BLUE, weight=ft.FontWeight.BOLD)
                            ], spacing=4),
                            on_click=lambda e, item=o: open_ficha_tecnica_dialog(item)
                        ),
                        (ft.FilledButton(
                            content=ft.Text("Actualizar Ficha", size=10, color="#FFFFFF", weight=ft.FontWeight.BOLD),
                            bgcolor=tag_col,
                            height=28,
                            on_click=lambda e, item=o: open_actualizar_obra_dialog(item)
                        ) if state.is_editor() else ft.Container())
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ], spacing=4),
                padding=10,
                bgcolor=bg_col,
                border_radius=8,
                border=ft.Border.all(1, brd_col)
            )

        cards_desarr = [make_frente_card(o, False) for o in en_desarrollo]
        cards_paral = [make_frente_card(o, True) for o in paralizadas]

        return ft.Column(
            spacing=10,
            expand=True,
            scroll=ft.ScrollMode.ADAPTIVE,
            controls=[
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.PENDING_ACTIONS_ROUNDED, size=16, color=COLOR_STATUS_AMBER),
                        ft.Text(f"Frentes de Trabajo en Desarrollo ({len(en_desarrollo)})", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                    ], spacing=6),
                    padding=ft.Padding.symmetric(vertical=4)
                ),
                ft.Column(controls=cards_desarr, spacing=6),
                ft.Divider(height=10, color="#E2E8F0"),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.PAUSE_CIRCLE_ROUNDED, size=16, color=COLOR_STATUS_RED),
                        ft.Text(f"Obras Paralizadas / Suspendidas para Reactivación ({len(paralizadas)})", size=13, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_RED)
                    ], spacing=6),
                    padding=ft.Padding.symmetric(vertical=4)
                ),
                ft.Column(controls=cards_paral, spacing=6),
            ]
        )

    # PESTAÑA 3: Evolución Anual (2023–2026)
    def build_tab_evolucion_anual() -> ft.Control:
        data = state.puentes_data or {}
        anual = data.get("por_año", {})

        years_order = ["2023", "2024", "2025", "2026"]
        kpi_cards = []
        for y in years_order:
            y_info = anual.get(y, {})
            tot_y = y_info.get("total", 0)
            ej_y = y_info.get("ejecutadas", 0)
            des_y = y_info.get("en_desarrollo", 0)
            par_y = y_info.get("paralizadas", 0)
            p_y = y_info.get("puentes", 0)
            a_y = y_info.get("alcantarillas", 0)
            c_y = y_info.get("cajones", 0)

            kpi_cards.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED, size=14, color=COLOR_NAVY_DARK),
                            ft.Text(f"Año {y}", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
                        ], spacing=4),
                        ft.Text(f"{tot_y} Obras", size=18, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_BLUE),
                        ft.Text(f"{p_y} Puentes • {a_y} Alcant. • {c_y} Cajones", size=9, color=COLOR_TEXT_SECONDARY),
                        ft.Row([
                            ft.Container(
                                content=ft.Text(f"{ej_y} Ejecutadas", size=9, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                bgcolor=COLOR_STATUS_GREEN,
                                border_radius=4
                            ),
                            (ft.Container(
                                content=ft.Text(f"{des_y} En Desarr.", size=9, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                bgcolor=COLOR_STATUS_AMBER,
                                border_radius=4
                            ) if des_y > 0 else ft.Container()),
                            (ft.Container(
                                content=ft.Text(f"{par_y} Paralizadas", size=9, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                                bgcolor=COLOR_STATUS_RED,
                                border_radius=4
                            ) if par_y > 0 else ft.Container())
                        ], spacing=4)
                    ], spacing=4),
                    padding=10,
                    bgcolor="#F8FAFC",
                    border_radius=8,
                    border=ft.Border.all(1, "#E2E8F0"),
                    expand=True
                )
            )

        filas_tabla = []
        for y in years_order:
            y_info = anual.get(y, {})
            filas_tabla.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(ft.Text(f"Año {y}", size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK), width=80),
                        ft.Container(ft.Text(str(y_info.get("total", 0)), size=12, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK), width=70, alignment=ft.Alignment(1, 0)),
                        ft.Container(ft.Text(str(y_info.get("puentes", 0)), size=12, color=COLOR_ELECTRIC_BLUE), width=80, alignment=ft.Alignment(1, 0)),
                        ft.Container(ft.Text(str(y_info.get("alcantarillas", 0)), size=12, color=COLOR_STATUS_GREEN), width=95, alignment=ft.Alignment(1, 0)),
                        ft.Container(ft.Text(str(y_info.get("cajones", 0)), size=12, color=COLOR_STATUS_AMBER), width=75, alignment=ft.Alignment(1, 0)),
                        ft.Container(ft.Text(str(y_info.get("ejecutadas", 0)), size=12, weight=ft.FontWeight.BOLD, color=COLOR_STATUS_GREEN), width=85, alignment=ft.Alignment(1, 0)),
                        ft.Container(ft.Text(str(y_info.get("en_desarrollo", 0)), size=12, color=COLOR_STATUS_AMBER), width=90, alignment=ft.Alignment(1, 0)),
                        ft.Container(ft.Text(str(y_info.get("paralizadas", 0)), size=12, color=COLOR_STATUS_RED), width=85, alignment=ft.Alignment(1, 0)),
                        ft.Container(
                            content=ft.Row([
                                ft.ProgressBar(value=y_info.get("pct_ejecutado", 0) / 100.0, color=COLOR_STATUS_GREEN, bgcolor="#E2E8F0", height=6, width=80),
                                ft.Text(f"{y_info.get('pct_ejecutado', 0)}%", size=11, color=COLOR_TEXT_MUTED)
                            ], spacing=6),
                            expand=True
                        )
                    ], spacing=10),
                    padding=ft.Padding.symmetric(horizontal=10, vertical=8),
                    border=ft.Border(bottom=ft.BorderSide(1, "#F1F5F9")),
                    bgcolor="#FFFFFF"
                )
            )

        header_tabla = ft.Container(
            content=ft.Row([
                ft.Container(ft.Text("Año", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=80),
                ft.Container(ft.Text("Total", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=70, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text("Puentes", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=80, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text("Alcantarillas", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=95, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text("Cajones", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=75, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text("Ejecutadas", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=85, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text("En Desarr.", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=90, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text("Paralizadas", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), width=85, alignment=ft.Alignment(1, 0)),
                ft.Container(ft.Text("Efectividad", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_MUTED), expand=True),
            ], spacing=10),
            padding=ft.Padding.symmetric(horizontal=10, vertical=8),
            bgcolor="#F1F5F9",
            border_radius=6
        )

        return ft.Column(
            spacing=10,
            expand=True,
            scroll=ft.ScrollMode.ADAPTIVE,
            controls=[
                ft.Row(controls=kpi_cards, spacing=8),
                ft.Text("Comparativa Histórica de Ejecución (2023–2026)", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                header_tabla,
                ft.Container(
                    content=ft.Column(controls=filas_tabla, spacing=0),
                    border=ft.Border.all(1, "#E2E8F0"),
                    border_radius=8
                )
            ]
        )

    # -------------------------------------------------------------
    # CONTROLADOR DE PESTAÑAS Y NAVEGACIÓN
    # -------------------------------------------------------------
    tabs_labels = [
        ("Resumen Municipal", ft.Icons.LOCATION_CITY_ROUNDED),
        ("Inventario General (154)", ft.Icons.WAVES_ROUNDED),
        ("Frentes Activos y Paralizados (9)", ft.Icons.PENDING_ACTIONS_ROUNDED),
        ("Evolución Anual (2023–2026)", ft.Icons.CALENDAR_MONTH_ROUNDED),
    ]

    def render_tab_chips():
        tab_chips_row.controls.clear()
        for idx, (label, icon_d) in enumerate(tabs_labels):
            is_active = (active_tab == idx)
            tab_chips_row.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(icon_d, size=14, color="#FFFFFF" if is_active else COLOR_NAVY_DARK),
                        ft.Text(
                            label,
                            size=12,
                            weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
                            color="#FFFFFF" if is_active else COLOR_NAVY_DARK
                        )
                    ], spacing=6),
                    padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                    bgcolor=COLOR_NAVY_DARK if is_active else "#F1F5F9",
                    border_radius=20,
                    ink=True,
                    on_click=lambda e, ti=idx: set_tab(ti)
                )
            )

    def set_tab(ti: int):
        nonlocal active_tab
        active_tab = ti
        render_tab_chips()
        render_tab_content()
        page.update()

    def render_tab_content():
        if active_tab == 0:
            tab_content_area.content = build_tab_resumen_municipio()
        elif active_tab == 1:
            tab_content_area.content = build_tab_inventario_obras()
        elif active_tab == 2:
            tab_content_area.content = build_tab_frentes_prioritarios()
        elif active_tab == 3:
            tab_content_area.content = build_tab_evolucion_anual()
        page.update()

    def full_refresh():
        refresh_upper_kpis()
        render_tab_chips()
        render_tab_content()
        page.update()

    # -------------------------------------------------------------
    # BARRA SUPERIOR DE FILTROS Y ACCIONES
    # -------------------------------------------------------------
    mun_dropdown = ft.Dropdown(
        value=selected_mun,
        options=[ft.dropdown.Option(m) for m in MUNICIPALITIES_LIST],
        height=38,
        text_size=12,
        border_color="#CBD5E1",
        focused_border_color=COLOR_ELECTRIC_BLUE,
        width=170,
        on_select=lambda e: on_select_mun(e.control.value)
    )

    def on_select_mun(m: str):
        nonlocal selected_mun
        selected_mun = m
        state.set_puentes_filters(municipality=m)
        full_refresh()

    tipo_dropdown = ft.Dropdown(
        value=selected_tipo,
        options=[
            ft.dropdown.Option("Todas"),
            ft.dropdown.Option("Puentes (78)"),
            ft.dropdown.Option("Alcantarillas (66)"),
            ft.dropdown.Option("Cajones de Paso (10)")
        ],
        height=38,
        text_size=12,
        border_color="#CBD5E1",
        focused_border_color=COLOR_ELECTRIC_BLUE,
        width=160,
        on_select=lambda e: on_select_tipo(e.control.value)
    )

    def on_select_tipo(t: str):
        nonlocal selected_tipo
        selected_tipo = t
        state.set_puentes_filters(tipo=t)
        full_refresh()

    years_options = ["Todos (2023-2026)", "2026", "2025", "2024", "2023"]
    year_dropdown = ft.Dropdown(
        value=selected_yr,
        options=[ft.dropdown.Option(y) for y in years_options],
        height=38,
        text_size=12,
        border_color="#CBD5E1",
        focused_border_color=COLOR_ELECTRIC_BLUE,
        width=150,
        on_select=lambda e: on_select_year(e.control.value)
    )

    def on_select_year(y: str):
        nonlocal selected_yr
        selected_yr = y
        state.set_puentes_filters(year=y)
        full_refresh()

    search_field = ft.TextField(
        hint_text="Buscar obra por nombre o sector...",
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        value=search_query,
        height=38,
        text_size=12,
        border_color="#CBD5E1",
        focused_border_color=COLOR_ELECTRIC_BLUE,
        expand=True,
        on_change=lambda e: on_search(e.control.value)
    )

    def on_search(q: str):
        nonlocal search_query
        search_query = q.strip().lower()
        render_tab_content()

    # Botones protegidos por rol (Master y Analista)
    editor_actions = []
    if state.is_editor():
        btn_nuevo = ft.FilledButton(
            content=ft.Row([
                ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED, size=15, color="#FFFFFF"),
                ft.Text("+ Nueva Obra", size=11, color="#FFFFFF", weight=ft.FontWeight.BOLD)
            ], spacing=4),
            bgcolor=COLOR_STATUS_GREEN,
            height=36,
            on_click=open_nueva_obra_modal
        )

        btn_import = ft.OutlinedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.UPLOAD_FILE_ROUNDED, size=15, color=COLOR_ELECTRIC_BLUE),
                ft.Text("Importar Excel (.xlsx)", size=11, color=COLOR_ELECTRIC_BLUE, weight=ft.FontWeight.BOLD)
            ], spacing=4),
            height=36,
            on_click=import_excel_dialog
        )
        editor_actions.extend([btn_nuevo, btn_import])

    filter_bar = ft.Container(
        content=ft.Row([
            ft.Row([
                ft.Text("Municipio:", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                mun_dropdown,
                ft.Text("Tipo:", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                tipo_dropdown,
                ft.Text("Año:", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                year_dropdown,
            ], spacing=6),
            ft.Row(editor_actions, spacing=6)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.Padding.symmetric(horizontal=12, vertical=8),
        bgcolor="#FFFFFF",
        border_radius=10,
        border=ft.Border.all(1, "#E2E8F0")
    )

    search_bar = ft.Container(
        content=ft.Row([
            search_field
        ]),
        padding=ft.Padding.symmetric(horizontal=12, vertical=4)
    )

    # -------------------------------------------------------------
    # LOGO INSTITUCIONAL Y ENCABEZADO
    # -------------------------------------------------------------
    logo_path = "logo_puentes.png" if os.path.exists("assets/logo_puentes.png") else None
    leading_logo = (
        ft.Image(src=logo_path, width=42, height=42, fit="contain")
        if logo_path else ft.Icon(ft.Icons.WAVES_ROUNDED, size=28, color=COLOR_ELECTRIC_BLUE)
    )
    header_box = create_institutional_header(
        title="Plan Puentes y Alcantarillas",
        subtitle="Puesto de Comando Estratégico Operacional del Estado Portuguesa • PCEO",
        show_back_button=True,
        on_back_click=lambda e: on_back_to_summary(),
        on_logout_click=lambda e: on_logout(),
        on_switch_role_click=on_switch_role,
        show_user_chip=True,
        leading_logo=leading_logo
    )

    # Inicializar componentes
    refresh_upper_kpis()
    render_tab_chips()
    render_tab_content()

    # Contenedor raíz
    return ft.Container(
        content=ft.Column(
            spacing=10,
            expand=True,
            controls=[
                header_box,
                import_panel_obj.panel_container,
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
