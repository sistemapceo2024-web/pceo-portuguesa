"""
Diálogos de Acción para el Equipo Técnico (Editor)
Secretaría Superior de Operaciones Generales
"""
import flet as ft
from components.theme import (
    COLOR_NAVY_DARK,
    COLOR_ELECTRIC_BLUE,
    COLOR_SURFACE_WHITE,
    COLOR_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_STATUS_GREEN,
    COLOR_STATUS_AMBER,
    COLOR_STATUS_RED
)
from data.water_data import MUNICIPALITIES_LIST
from data.state import AppState

def open_update_well_dialog(page: ft.Page, state: AppState, on_success=None, preselected_well_id=None):
    """Abre el diálogo modal para que el Equipo Técnico actualice el estatus de un pozo."""
    wells = state.sample_wells
    
    selected_well_id = preselected_well_id or (wells[0].id if wells else "")
    current_well = next((w for w in wells if w.id == selected_well_id), wells[0] if wells else None)
    
    well_options = [
        ft.DropdownOption(
            key=w.id,
            text=f"[{w.municipality}] {w.code} - {w.name} ({w.status})"
        )
        for w in wells
    ]

    status_dropdown = ft.Dropdown(
        value=current_well.status if current_well else "Operativo",
        options=[
            ft.DropdownOption("Operativo", "🟢 Operativo (En Servicio)"),
            ft.DropdownOption("En Mantenimiento", "🟠 En Mantenimiento Técnico"),
            ft.DropdownOption("Inoperativo", "🔴 Inoperativo (Paralizado / Falla)"),
        ],
        label="Nuevo Estatus Operativo",
        border_radius=8,
        dense=True
    )

    technician_field = ft.TextField(
        value="Ing. Cuadrilla Portuguesa",
        label="Técnico / Inspector Responsable",
        border_radius=8,
        dense=True
    )

    notes_field = ft.TextField(
        label="Diagnóstico / Observaciones Técnicas",
        hint_text="Detalle mediciones eléctricas, amperaje, caudal en LPS o causa de inoperatividad...",
        multiline=True,
        min_lines=2,
        max_lines=3,
        border_radius=8,
        dense=True
    )

    def on_well_dropdown_change(e):
        nonlocal selected_well_id
        selected_well_id = e.control.value
        w = next((x for x in wells if x.id == selected_well_id), None)
        if w:
            status_dropdown.value = w.status
            status_dropdown.update()

    well_dropdown = ft.Dropdown(
        value=selected_well_id,
        options=well_options,
        on_select=on_well_dropdown_change,
        label="Seleccionar Pozo a Intervenir",
        border_radius=8,
        dense=True
    )

    def close_dialog(e):
        page.pop_dialog()
        page.update()

    def submit_update(e):
        if not selected_well_id:
            return

        success = state.update_well_status(
            well_id=selected_well_id,
            new_status=status_dropdown.value,
            notes=notes_field.value or "Actualización de rutina por equipo técnico.",
            technician=technician_field.value or "Equipo Técnico"
        )

        page.pop_dialog()
        
        # Mostrar notificación de éxito
        feedback = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, color="#FFFFFF"),
                ft.Text(f"Estatus actualizado a '{status_dropdown.value}' exitosamente.", color="#FFFFFF")
            ]),
            bgcolor=COLOR_NAVY_DARK,
            behavior=ft.SnackBarBehavior.FLOATING
        )
        page.show_dialog(feedback)
        page.update()

        if on_success:
            on_success()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            spacing=8,
            controls=[
                ft.Icon(ft.Icons.PUMP_ROUNDED if hasattr(ft.Icons, 'PUMP_ROUNDED') else ft.Icons.WATER_DROP_ROUNDED, color=COLOR_ELECTRIC_BLUE),
                ft.Text("Actualizar Estatus de Pozo", size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
            ]
        ),
        content=ft.Container(
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    ft.Text(
                        "Panel de Edición Técnica - Fiesta del Agua",
                        size=12,
                        color="#64748B"
                    ),
                    well_dropdown,
                    status_dropdown,
                    technician_field,
                    notes_field
                ]
            ),
            width=420,
            padding=ft.Padding.all(8)
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=close_dialog),
            ft.FilledButton(
                "Guardar Actualización",
                icon=ft.Icons.SAVE_ROUNDED,
                style=ft.ButtonStyle(
                    bgcolor=COLOR_ELECTRIC_BLUE,
                    color="#FFFFFF"
                ),
                on_click=submit_update
            )
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=12)
    )

    page.show_dialog(dialog)
    page.update()


def open_new_report_dialog(page: ft.Page, state: AppState, on_success=None):
    """Abre el diálogo modal para registrar un nuevo reporte técnico de operaciones."""
    category_dropdown = ft.Dropdown(
        value="Pozo Profundo",
        options=[
            ft.DropdownOption("Pozo Profundo", "💧 Pozo Profundo"),
            ft.DropdownOption("Estación de Rebombeo", "⚙️ Estación de Rebombeo"),
            ft.DropdownOption("Planta Potabilizadora", "🏭 Planta Potabilizadora"),
            ft.DropdownOption("Nueva Perforación", "🏗️ Nueva Perforación"),
        ],
        label="Categoría del Activo",
        border_radius=8,
        dense=True
    )

    municipalities_opts = [
        ft.DropdownOption(m, m) for m in MUNICIPALITIES_LIST if m != "Todos los Municipios"
    ]
    mun_dropdown = ft.Dropdown(
        value=municipalities_opts[0].key,
        options=municipalities_opts,
        label="Municipio de Portuguesa",
        border_radius=8,
        dense=True
    )

    name_field = ft.TextField(
        label="Identificador o Nombre del Activo",
        hint_text="Ej: Pozo El Rodeo, Rebombeo Curpa...",
        border_radius=8,
        dense=True
    )

    action_dropdown = ft.Dropdown(
        value="Inspección Técnica Diagnóstica",
        options=[
            ft.DropdownOption("Inspección Técnica Diagnóstica", "Inspección Técnica Diagnóstica"),
            ft.DropdownOption("Sustitución de Motor Eléctrico", "Sustitución de Motor Eléctrico"),
            ft.DropdownOption("Reemplazo de Bomba Sumergible", "Reemplazo de Bomba Sumergible"),
            ft.DropdownOption("Aforo Hidráulico y Medición de Caudal", "Aforo Hidráulico y Medición de Caudal"),
            ft.DropdownOption("Mantenimiento y Calibración de Tablero", "Mantenimiento y Calibración de Tablero"),
            ft.DropdownOption("Limpieza Química de Pozo con Compresor", "Limpieza Química de Pozo"),
        ],
        label="Tipo de Intervención Realizada",
        border_radius=8,
        dense=True
    )

    notes_field = ft.TextField(
        label="Detalles y Resultados del Reporte",
        hint_text="Caudal medido, estado de líneas eléctricas, personal desplegado...",
        multiline=True,
        min_lines=2,
        max_lines=3,
        border_radius=8,
        dense=True
    )

    technician_field = ft.TextField(
        value="Ing. Inspector Portuguesa",
        label="Nombre del Técnico / Ingeniero",
        border_radius=8,
        dense=True
    )

    def close_dialog(e):
        page.pop_dialog()
        page.update()

    def submit_report(e):
        if not name_field.value:
            name_field.error_text = "Ingrese el nombre del activo"
            name_field.update()
            return

        state.register_maintenance_report(
            item_type=category_dropdown.value,
            item_name=name_field.value,
            municipality=mun_dropdown.value,
            action=action_dropdown.value,
            notes=notes_field.value or "Sin observaciones adicionales.",
            technician=technician_field.value or "Equipo Técnico"
        )

        page.pop_dialog()

        feedback = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, color="#FFFFFF"),
                ft.Text("Reporte de campo registrado exitosamente en bitácora oficial.", color="#FFFFFF")
            ]),
            bgcolor=COLOR_NAVY_DARK,
            behavior=ft.SnackBarBehavior.FLOATING
        )
        page.show_dialog(feedback)
        page.update()

        if on_success:
            on_success()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            spacing=8,
            controls=[
                ft.Icon(ft.Icons.POST_ADD_ROUNDED, color=COLOR_ELECTRIC_BLUE),
                ft.Text("Registrar Nuevo Reporte Técnico", size=16, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK)
            ]
        ),
        content=ft.Container(
            content=ft.Column(
                tight=True,
                spacing=10,
                controls=[
                    category_dropdown,
                    mun_dropdown,
                    name_field,
                    action_dropdown,
                    technician_field,
                    notes_field
                ]
            ),
            width=420,
            padding=ft.Padding.all(8)
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=close_dialog),
            ft.FilledButton(
                "Registrar Reporte",
                icon=ft.Icons.CHECK_ROUNDED,
                style=ft.ButtonStyle(
                    bgcolor=COLOR_ELECTRIC_BLUE,
                    color="#FFFFFF"
                ),
                on_click=submit_report
            )
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=12)
    )

    page.show_dialog(dialog)
    page.update()
