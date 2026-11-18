"""
Componente oficial de Importación de Excel sin congelamiento para PCEO.
Panel desplegable directamente debajo del encabezado con selector nativo de Windows vía PowerShell en hilo secundario
y buscador automático de archivos .xlsx que busca ÚNICAMENTE en la carpeta Documentos (búsqueda recursiva),
excluyendo por completo la raíz del proyecto y descargas.
"""
import os
import glob
import subprocess
import threading
from typing import Callable, Optional, List, Dict
import flet as ft

COLOR_NAVY_DARK = "#0F172A"
COLOR_ELECTRIC_BLUE = "#2563EB"
COLOR_STATUS_GREEN = "#16A34A"
COLOR_STATUS_RED = "#DC2626"
COLOR_SURFACE_WHITE = "#FFFFFF"
COLOR_BORDER = "#CBD5E1"

def open_windows_file_dialog(
    on_file_selected: Callable[[str], None],
    on_cancel: Optional[Callable[[], None]] = None,
    title: str = "Seleccionar Archivo Excel (.xlsx)",
    filter_pattern: str = "Excel (*.xlsx)|*.xlsx|Todos los archivos (*.*)|*.*",
    initial_directory: Optional[str] = None
):
    """
    Ejecuta el cuadro de diálogo nativo de Windows (OpenFileDialog) usando PowerShell
    con el flag obligatorio -Sta, InitialDirectory apuntando a Documentos y un formulario
    propietario invisible con TopMost = $true en un hilo secundario independiente.
    """
    def _worker():
        docs_dir = initial_directory or os.path.abspath(os.path.expanduser("~/Documents"))
        init_dir_esc = docs_dir.replace("\\", "\\\\")

        # Formulario propietario invisible con TopMost = $true para forzar foco sobre la ventana de Flet
        ps_cmd = (
            "Add-Type -AssemblyName System.Windows.Forms; "
            "$f = New-Object System.Windows.Forms.Form; "
            "$f.TopMost = $true; "
            "$dlg = New-Object System.Windows.Forms.OpenFileDialog; "
            f"$dlg.Title = '{title}'; "
            f"$dlg.Filter = '{filter_pattern}'; "
            f"$dlg.InitialDirectory = '{init_dir_esc}'; "
            "$dlg.RestoreDirectory = $true; "
            "if ($dlg.ShowDialog($f) -eq [System.Windows.Forms.DialogResult]::OK) { "
            "    Write-Output $dlg.FileName "
            "} "
            "$f.Dispose();"
        )
        cmd = [
            "powershell",
            "-NoProfile",
            "-Sta",
            "-Command",
            ps_cmd
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            path = res.stdout.strip()
            if path and os.path.exists(path):
                on_file_selected(path)
            else:
                if on_cancel:
                    on_cancel()
        except Exception as ex:
            print(f"Error en selector de archivos de Windows: {ex}")
            if on_cancel:
                on_cancel()

    threading.Thread(target=_worker, daemon=True).start()

def get_detected_excel_files() -> List[Dict[str, str]]:
    """
    Escanea y retorna la lista de archivos .xlsx detectados ÚNICAMENTE en:
    Carpeta Documentos del usuario (os.path.expanduser('~/Documents')) de forma recursiva con os.walk,
    excluyendo por completo la carpeta raíz del proyecto y la carpeta Descargas (Downloads).
    Ignorando temporales (~$) y ordenados del más reciente al más antiguo por fecha de modificación.
    """
    found: List[Dict[str, str]] = []
    seen_paths = set()

    docs_dir = os.path.abspath(os.path.expanduser("~/Documents"))
    root_dir = os.path.abspath(".")

    def build_option_label(abs_path: str) -> str:
        dirname = os.path.dirname(abs_path)
        bname = os.path.basename(abs_path)
        rel = os.path.relpath(dirname, docs_dir).replace("\\", "/")
        tag = "Documentos" if rel == "." else rel
        return f"[{tag}] {bname}"

    def register_file(filepath: str):
        abs_p = os.path.abspath(filepath)
        if abs_p in seen_paths or not os.path.exists(abs_p):
            return
        bname = os.path.basename(abs_p)
        if bname.startswith("~$") or not bname.lower().endswith(".xlsx"):
            return
        try:
            mtime = os.path.getmtime(abs_p)
        except Exception:
            mtime = 0
        seen_paths.add(abs_p)
        found.append({
            "label": build_option_label(abs_p),
            "path": abs_p,
            "mtime": mtime
        })

    # Búsqueda recursiva ÚNICAMENTE en la carpeta Documentos (~/Documents)
    try:
        if os.path.exists(docs_dir):
            for r, dirs, files in os.walk(docs_dir):
                # Excluir la raíz del proyecto, carpetas ocultas, descargas, venv, node_modules, etc.
                dirs[:] = [
                    d for d in dirs
                    if not d.startswith(".")
                    and d not in ("venv", "node_modules", "__pycache__")
                    and d.lower() not in ("downloads", "descargas")
                    and os.path.abspath(os.path.join(r, d)) != root_dir
                    and not os.path.abspath(os.path.join(r, d)).startswith(root_dir + os.sep)
                ]
                abs_r = os.path.abspath(r)
                if abs_r == root_dir or abs_r.startswith(root_dir + os.sep):
                    continue
                for f in files:
                    register_file(os.path.join(r, f))
    except Exception as e:
        print(f"Aviso escaneando Documentos: {e}")

    # Ordenar del más reciente al más antiguo por fecha de modificación
    found.sort(key=lambda x: x["mtime"], reverse=True)
    return found

class ExcelImportPanel:
    def __init__(
        self,
        page: ft.Page,
        title: str,
        default_file: str,
        on_load_callback: Callable[[str], bool],
        on_success_callback: Optional[Callable[[], None]] = None,
        accent_color: str = COLOR_ELECTRIC_BLUE
    ):
        self.page = page
        self.title = title
        self.default_file = default_file
        self.on_load_callback = on_load_callback
        self.on_success_callback = on_success_callback
        self.accent_color = accent_color

        self.path_field = ft.TextField(
            label="Ruta o nombre del archivo Excel (.xlsx)",
            value=default_file,
            dense=True,
            expand=True,
            text_size=12,
            border_radius=8,
            border_color=COLOR_BORDER,
            bgcolor="#F8FAFC"
        )

        self.status_text = ft.Text(
            "Seleccione un archivo oficial para actualizar los datos en tiempo real.",
            size=11,
            color="#64748B",
            weight=ft.FontWeight.W_500
        )

        # Dropdown de respaldo visual con etiqueta oficial requerida
        self.dropdown_detected = ft.Dropdown(
            label="Seleccionar archivo .xlsx en Documentos",
            hint_text="Haga clic para ver archivos ordenados por fecha...",
            dense=True,
            expand=True,
            text_size=11,
            border_radius=8,
            border_color=COLOR_BORDER,
            bgcolor="#F8FAFC",
            on_select=self._on_detected_selected
        )
        self._populate_detected_dropdown()

        self.panel_container = self._build_container()

    def _populate_detected_dropdown(self):
        """Llena las opciones del selector rápido con los archivos detectados ordenados por mtime."""
        files = get_detected_excel_files()
        options = []
        for f in files:
            options.append(ft.DropdownOption(key=f["path"], text=f["label"]))
        self.dropdown_detected.options = options

    def refresh_detected_files(self, e=None):
        """Re-escanea Documentos recursivamente y actualiza la lista desplegable."""
        self._populate_detected_dropdown()
        self.status_text.value = f"Lista actualizada: {len(self.dropdown_detected.options)} archivos .xlsx detectados en Documentos (ordenados por fecha)."
        self.status_text.color = self.accent_color
        self.page.update()

    def _on_detected_selected(self, e):
        """Al elegir un archivo del dropdown, lo asigna al campo de texto y lo carga automáticamente."""
        val = self.dropdown_detected.value
        if val and os.path.exists(val):
            self.path_field.value = val
            self.status_text.value = f"Cargando archivo seleccionado: {os.path.basename(val)}..."
            self.status_text.color = self.accent_color
            self.page.update()
            self._execute_import(val)

    def _execute_import(self, file_path: str):
        file_path = (file_path or "").strip().strip('"').strip("'")
        if not file_path or not os.path.exists(file_path):
            self.status_text.value = f"Archivo no encontrado: {file_path}"
            self.status_text.color = COLOR_STATUS_RED
            self.page.update()
            return

        self.status_text.value = f"Procesando {os.path.basename(file_path)}..."
        self.status_text.color = self.accent_color
        self.page.update()

        ok = False
        try:
            ok = self.on_load_callback(file_path)
        except Exception as ex:
            print(f"Error procesando importación: {ex}")
            ok = False

        if ok:
            self.path_field.value = file_path
            self.status_text.value = f"¡Éxito! Base de datos actualizada con: {os.path.basename(file_path)}"
            self.status_text.color = COLOR_STATUS_GREEN
            if self.on_success_callback:
                try:
                    self.on_success_callback()
                except Exception as ex:
                    print(f"Error en callback de éxito: {ex}")
        else:
            self.status_text.value = "Error al procesar el archivo Excel. Verifique el formato y las hojas requeridas."
            self.status_text.color = COLOR_STATUS_RED

        self.page.update()

    def _on_explore_clicked(self, e):
        self.status_text.value = "Abriendo explorador de Windows en carpeta Documentos..."
        self.status_text.color = self.accent_color
        self.page.update()

        def _on_picked(selected_path: str):
            self.path_field.value = selected_path
            self.page.update()
            self._execute_import(selected_path)

        def _on_canceled():
            self.status_text.value = "Selección cancelada en el explorador de Windows."
            self.status_text.color = "#64748B"
            self.page.update()

        open_windows_file_dialog(
            on_file_selected=_on_picked,
            on_cancel=_on_canceled,
            title=f"Importar - {self.title}",
            filter_pattern="Archivos Excel (*.xlsx)|*.xlsx|Todos los archivos (*.*)|*.*",
            initial_directory=os.path.abspath(os.path.expanduser("~/Documents"))
        )

    def _on_load_btn_clicked(self, e):
        target = self.path_field.value.strip() if self.path_field.value else ""
        self._execute_import(target)

    def hide(self, e=None):
        self.panel_container.visible = False
        self.page.update()

    def show(self, e=None):
        self.panel_container.visible = True
        self._populate_detected_dropdown()
        self.status_text.value = "Seleccione un archivo oficial para actualizar los datos en tiempo real."
        self.status_text.color = "#64748B"
        self.page.update()

    def toggle(self, e=None):
        self.panel_container.visible = not self.panel_container.visible
        if self.panel_container.visible:
            self._populate_detected_dropdown()
        self.page.update()

    def _build_container(self) -> ft.Container:
        return ft.Container(
            visible=False,
            bgcolor="#F0FDF4" if "agua" in self.title.lower() or "luz" in self.title.lower() else "#F8FAFC",
            border=ft.Border.all(1.5, self.accent_color),
            border_radius=10,
            padding=ft.Padding.symmetric(horizontal=14, vertical=12),
            margin=ft.Padding.only(left=10, right=10, top=6, bottom=6),
            content=ft.Column(
                spacing=8,
                tight=True,
                controls=[
                    # Fila superior de título y botón Cerrar (X)
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Row([
                                ft.Icon(ft.Icons.UPLOAD_FILE_ROUNDED, color=self.accent_color, size=20),
                                ft.Text(self.title, size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                            ], tight=True, spacing=6),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE_ROUNDED,
                                icon_size=18,
                                icon_color="#64748B",
                                tooltip="Ocultar panel",
                                on_click=self.hide
                            )
                        ]
                    ),
                    # Mensaje de estado / ayuda
                    self.status_text,
                    # Botón azul principal Explorar (con TopMost Form para elevarse al frente e InitialDirectory en Documentos)
                    ft.FilledButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.FOLDER_OPEN_ROUNDED, size=16),
                            ft.Text("Explorar y seleccionar archivo (.xlsx)...", size=12, weight=ft.FontWeight.BOLD)
                        ], tight=True, alignment=ft.MainAxisAlignment.CENTER),
                        style=ft.ButtonStyle(
                            bgcolor=self.accent_color,
                            color="#FFFFFF",
                            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                            shape=ft.RoundedRectangleBorder(radius=8)
                        ),
                        on_click=self._on_explore_clicked
                    ),
                    # Respaldo visual inmediato: Selector desplegable con etiqueta oficial requerida
                    ft.Row(
                        spacing=6,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            self.dropdown_detected,
                            ft.IconButton(
                                icon=ft.Icons.REFRESH_ROUNDED,
                                icon_color=self.accent_color,
                                icon_size=18,
                                tooltip="Actualizar lista de archivos detectados",
                                on_click=self.refresh_detected_files
                            )
                        ]
                    ),
                    # Fila con campo de texto manual y botón Cargar archivo
                    ft.Row(
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            self.path_field,
                            ft.FilledButton(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.CHECK_ROUNDED, size=16),
                                    ft.Text("Cargar archivo", size=12, weight=ft.FontWeight.BOLD)
                                ], tight=True),
                                style=ft.ButtonStyle(
                                    bgcolor=COLOR_NAVY_DARK,
                                    color="#FFFFFF",
                                    padding=ft.Padding.symmetric(horizontal=12, vertical=10),
                                    shape=ft.RoundedRectangleBorder(radius=8)
                                ),
                                on_click=self._on_load_btn_clicked
                            )
                        ]
                    )
                ]
            )
        )
