"""
Lector Inteligente del Plan de Canalización y Construcción de Bermas
Fuente oficial: PLAN_CANALIZACION_PORTUGUESA_2026.xlsx
Hojas: RESUMEN_GENERAL y OBRAS_2026
Gobernación del Estado Portuguesa • Puesto de Comando Estratégico Operacional (PCEO)
"""
import os
import json
import re
import unicodedata
import openpyxl
from collections import defaultdict
from typing import Dict, List, Any, Optional

def normalize_mun_name(text: str) -> str:
    """Normaliza texto eliminando acentos/diacríticos y caracteres no alfanuméricos."""
    if not text:
        return ""
    text = str(text).strip().lower()
    text = unicodedata.normalize('NFD', text)
    text = re.sub(r'[\u0300-\u036f]', '', text)
    text = re.sub(r'[^a-z0-9]', '', text)
    return text

def format_number_es(val, dec: int = 0) -> str:
    """Formatea número entero o float con separador de miles español (punto) y decimal (coma)."""
    if val is None:
        return "0"
    try:
        n = float(val)
        if dec > 0:
            return f"{n:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
        if n.is_integer():
            return f"{int(n):,}".replace(",", ".")
        return f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(val)

class CanalizacionParser:
    """Lector inteligente para el Plan de Canalización y Bermas leyendo RESUMEN_GENERAL y OBRAS_2026."""

    DEFAULT_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "PLAN_CANALIZACION_PORTUGUESA_2026.xlsx"
    )
    UPDATES_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "canalizacion_actualizada.json"
    )

    def __init__(self, excel_path: str = None):
        self.excel_path = excel_path or self.DEFAULT_PATH
        self._cache = None

    def parse_all(self, force_reload: bool = False) -> Dict[str, Any]:
        """Lee el Excel completo y fusiona con actualizaciones locales persistidas."""
        if self._cache is not None and not force_reload:
            return self._cache

        resumen_general_rows = []
        obras_2026_rows = []

        # Valores macro oficiales (fallback garantizado)
        # 380.73 Km canalizados | 243 obras ejecutadas | 57 bermas | >700.000 M3
        totales_estatales = {
            "obras_canalizacion": 244,
            "canalizaciones_ejecutadas": 243,
            "canalizaciones_en_desarrollo": 1,
            "canalizaciones_paralizadas": 0,
            "longitud_canalizada_km": 380.73,
            "bermas_construidas": 57,
            "bermas_en_desarrollo": 1,
            "bermas_paralizadas": 0,
            "bermas_totales": 58,
            "longitud_bermas_ml": 39582.0,
            "longitud_bermas_km": 39.58,
            "volumen_excavacion_m3": 329426.78,
            "volumen_removido_m3": 509014.07,
            "volumen_total_m3": 838440.85,
            "total_obras_general": 302
        }

        if os.path.exists(self.excel_path):
            try:
                wb = openpyxl.load_workbook(self.excel_path, data_only=True)
                
                # 1. Leer RESUMEN_GENERAL
                if "RESUMEN_GENERAL" in wb.sheetnames:
                    ws1 = wb["RESUMEN_GENERAL"]
                    for r in range(6, 10):
                        comp = ws1.cell(r, 1).value
                        if not comp:
                            continue
                        ejec = int(ws1.cell(r, 2).value or 0)
                        long_val = float(ws1.cell(r, 3).value or 0)
                        des = int(ws1.cell(r, 4).value or 0)
                        par = int(ws1.cell(r, 5).value or 0)
                        exc = float(ws1.cell(r, 6).value or 0)
                        mat = float(ws1.cell(r, 7).value or 0)
                        tot = int(ws1.cell(r, 8).value or (ejec + des + par))
                        
                        unidad = "KM" if "Canalizaciones" in str(comp) else "ML"
                        resumen_general_rows.append({
                            "componente": str(comp).strip(),
                            "ejecutadas": ejec,
                            "longitud": long_val,
                            "unidad": unidad,
                            "en_desarrollo": des,
                            "paralizadas": par,
                            "excavacion_m3": exc,
                            "material_removido_m3": mat,
                            "total": tot
                        })

                # 2. Leer OBRAS_2026
                if "OBRAS_2026" in wb.sheetnames:
                    ws2 = wb["OBRAS_2026"]
                    for r in range(5, ws2.max_row + 1):
                        num_val = ws2.cell(r, 1).value
                        if num_val is None:
                            continue
                        try:
                            n_int = int(num_val)
                        except Exception:
                            continue

                        comp = str(ws2.cell(r, 2).value or "").strip().upper()
                        nombre = str(ws2.cell(r, 3).value or "").strip()
                        mun = str(ws2.cell(r, 4).value or "").strip()
                        sector = str(ws2.cell(r, 5).value or "").strip()
                        estatus = str(ws2.cell(r, 6).value or "EJECUTADA").strip().upper()
                        long_val = float(ws2.cell(r, 7).value or 0)
                        exc_val = float(ws2.cell(r, 8).value or 0)
                        mat_val = float(ws2.cell(r, 9).value or 0)

                        obras_2026_rows.append({
                            "n": n_int,
                            "componente": "BERMAS" if "BERMA" in comp else "CANALIZACIÓN",
                            "nombre": nombre,
                            "municipio": mun,
                            "sector": sector,
                            "estatus": estatus,
                            "longitud": long_val,
                            "unidad_longitud": "KM",
                            "excavacion_m3": exc_val,
                            "material_removido_m3": mat_val,
                            "id": f"obra_{n_int}"
                        })

                wb.close()
            except Exception as e:
                print(f"Advertencia al leer Excel de Canalización: {e}")

        # Fallback para resumen general si no vino del Excel
        if not resumen_general_rows:
            resumen_general_rows = [
                {
                    "componente": "Canalizaciones - Años Anteriores (21-22-23-25)",
                    "ejecutadas": 200,
                    "longitud": 332.02,
                    "unidad": "KM",
                    "en_desarrollo": 0,
                    "paralizadas": 0,
                    "excavacion_m3": 317002.50,
                    "material_removido_m3": 98618.05,
                    "total": 200
                },
                {
                    "componente": "Canalizaciones - Año 2026",
                    "ejecutadas": 43,
                    "longitud": 48.26,
                    "unidad": "KM",
                    "en_desarrollo": 1,
                    "paralizadas": 0,
                    "excavacion_m3": 0.0,
                    "material_removido_m3": 284965.12,
                    "total": 44
                },
                {
                    "componente": "Construcción de Bermas - Años Anteriores (23-24)",
                    "ejecutadas": 29,
                    "longitud": 28880.0,
                    "unidad": "ML",
                    "en_desarrollo": 0,
                    "paralizadas": 0,
                    "excavacion_m3": 0.0,
                    "material_removido_m3": 7056.0,
                    "total": 29
                },
                {
                    "componente": "Construcción de Bermas - Año 2026",
                    "ejecutadas": 28,
                    "longitud": 10702.0,
                    "unidad": "ML",
                    "en_desarrollo": 1,
                    "paralizadas": 0,
                    "excavacion_m3": 12424.28,
                    "material_removido_m3": 118374.90,
                    "total": 29
                }
            ]

        # Fusionar con actualizaciones guardadas en JSON si existen
        if os.path.exists(self.UPDATES_PATH):
            try:
                with open(self.UPDATES_PATH, "r", encoding="utf-8") as f:
                    updates = json.load(f)
                    
                    # Sobrescribir o añadir obras
                    obras_by_id = {o["id"]: o for o in obras_2026_rows}
                    for u in updates.get("obras_nuevas", []):
                        obras_by_id[u["id"]] = u
                    for uid, mod in updates.get("obras_modificadas", {}).items():
                        if uid in obras_by_id:
                            obras_by_id[uid].update(mod)
                    
                    obras_2026_rows = list(obras_by_id.values())
                    obras_2026_rows.sort(key=lambda x: x.get("n", 999))
            except Exception as e:
                print(f"Aviso al cargar actualizaciones locales de canalización: {e}")

        # Agrupar frentes fluviales por cauce / río
        frentes_fluviales = self._build_frentes_fluviales(obras_2026_rows)

        self._cache = {
            "totales_estatales": totales_estatales,
            "resumen_general": resumen_general_rows,
            "obras_2026": obras_2026_rows,
            "frentes_fluviales": frentes_fluviales
        }
        return self._cache

    def _build_frentes_fluviales(self, obras: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Construye la lista técnica de frentes y cauces fluviales prioritarios."""
        frentes = []
        for o in obras:
            nombre = o.get("nombre", "")
            cauce_tipo = "RÍO"
            if "CAÑO" in nombre.upper():
                cauce_tipo = "CAÑO"
            elif "QUEBRADA" in nombre.upper() or "QBRADA" in nombre.upper():
                cauce_tipo = "QUEBRADA"
            elif "BERMA" in nombre.upper() or "MURO" in nombre.upper():
                cauce_tipo = "MURO DE BERMA"
            elif "CANAL" in nombre.upper() or "DRENAJE" in nombre.upper():
                cauce_tipo = "CANAL DE DRENAJE"

            frentes.append({
                "n": o.get("n"),
                "cauce": nombre,
                "tipo_cauce": cauce_tipo,
                "municipio": o.get("municipio"),
                "sector": o.get("sector"),
                "componente": o.get("componente"),
                "estatus": o.get("estatus"),
                "longitud": o.get("longitud", 0),
                "unidad": o.get("unidad_longitud", "KM"),
                "excavacion_m3": o.get("excavacion_m3", 0),
                "material_removido_m3": o.get("material_removido_m3", 0),
                "es_prioritario": o.get("estatus") == "EN DESARROLLO" or o.get("longitud", 0) >= 1.0 or o.get("excavacion_m3", 0) > 3000
            })
        return frentes

    def get_kpis(self, municipio: str = None, estatus: str = None, componente: str = None) -> Dict[str, Any]:
        """Calcula KPIs dinámicos filtrados por municipio, estatus y componente."""
        data = self.parse_all()
        tots = data["totales_estatales"]
        obras = data["obras_2026"]

        is_all_mun = not municipio or municipio.upper() in ["TODOS", "TODOS LOS MUNICIPIOS"]
        is_all_est = not estatus or estatus.upper() in ["TODOS", "TODOS LOS ESTATUS"]
        is_all_comp = not componente or componente.upper() in ["TODOS", "TODOS LOS COMPONENTES"]

        if is_all_mun and is_all_est and is_all_comp:
            return tots

        # Filtrar obras de 2026 para el criterio especificado
        filtered_obras = obras
        if not is_all_mun:
            m_norm = normalize_mun_name(municipio)
            filtered_obras = [o for o in filtered_obras if m_norm in normalize_mun_name(o.get("municipio", ""))]

        if not is_all_est:
            e_norm = estatus.strip().upper()
            filtered_obras = [o for o in filtered_obras if e_norm in o.get("estatus", "").upper()]

        if not is_all_comp:
            c_norm = "BERMA" if "BERMA" in componente.upper() else "CANAL"
            filtered_obras = [o for o in filtered_obras if c_norm in o.get("componente", "").upper()]

        tot_obras = len(filtered_obras)
        ejec = sum(1 for o in filtered_obras if "EJECUTAD" in o.get("estatus", "").upper())
        des = sum(1 for o in filtered_obras if "DESARROLL" in o.get("estatus", "").upper() or "PROCESO" in o.get("estatus", "").upper())
        par = sum(1 for o in filtered_obras if "PARALIZAD" in o.get("estatus", "").upper())
        
        long_km = sum(o.get("longitud", 0) for o in filtered_obras)
        exc_m3 = sum(o.get("excavacion_m3", 0) for o in filtered_obras)
        mat_m3 = sum(o.get("material_removido_m3", 0) for o in filtered_obras)
        bermas_cnt = sum(1 for o in filtered_obras if o.get("componente") == "BERMAS")
        canales_cnt = sum(1 for o in filtered_obras if o.get("componente") == "CANALIZACIÓN")

        return {
            "obras_canalizacion": canales_cnt,
            "canalizaciones_ejecutadas": ejec,
            "canalizaciones_en_desarrollo": des,
            "canalizaciones_paralizadas": par,
            "longitud_canalizada_km": round(long_km, 2),
            "longitud_km": round(long_km, 2),
            "bermas_construidas": bermas_cnt,
            "bermas_en_desarrollo": 0,
            "bermas_totales": bermas_cnt,
            "volumen_excavacion_m3": round(exc_m3, 2),
            "volumen_removido_m3": round(mat_m3, 2),
            "volumen_total_m3": round(exc_m3 + mat_m3, 2),
            "total_obras": tot_obras,
            "total_obras_general": tot_obras,
            "ejecutadas": ejec,
            "en_desarrollo": des,
            "paralizadas": par,
            "frentes": tot_obras,
            "bermas": bermas_cnt
        }

    def get_obras_filtered(
        self,
        municipio: str = None,
        estatus: str = None,
        componente: str = None,
        query: str = None
    ) -> List[Dict[str, Any]]:
        """Devuelve las obras filtradas por municipio, estatus, componente y buscador."""
        data = self.parse_all()
        obras = data["obras_2026"]

        if municipio and municipio.upper() not in ["TODOS", "TODOS LOS MUNICIPIOS"]:
            m_norm = normalize_mun_name(municipio)
            obras = [o for o in obras if m_norm in normalize_mun_name(o.get("municipio", ""))]

        if estatus and estatus.upper() not in ["TODOS", "TODOS LOS ESTATUS"]:
            e_norm = estatus.strip().upper()
            obras = [o for o in obras if e_norm in o.get("estatus", "").upper()]

        if componente and componente.upper() not in ["TODOS", "TODOS LOS COMPONENTES"]:
            c_norm = "BERMA" if "BERMA" in componente.upper() else "CANAL"
            obras = [o for o in obras if c_norm in o.get("componente", "").upper()]

        if query:
            q = query.strip().lower()
            obras = [
                o for o in obras
                if q in o.get("nombre", "").lower()
                or q in o.get("municipio", "").lower()
                or q in o.get("sector", "").lower()
            ]

        return obras

    def add_or_update_obra(self, obra_data: Dict[str, Any]) -> Dict[str, Any]:
        """Registra o actualiza una obra y la persiste en canalizacion_actualizada.json."""
        data = self.parse_all()
        obras = data["obras_2026"]

        obra_id = obra_data.get("id") or f"obra_{len(obras) + 1}"
        obra_data["id"] = obra_id
        if "n" not in obra_data:
            obra_data["n"] = len(obras) + 1

        # Cargar JSON actual
        stored = {"obras_nuevas": [], "obras_modificadas": {}}
        if os.path.exists(self.UPDATES_PATH):
            try:
                with open(self.UPDATES_PATH, "r", encoding="utf-8") as f:
                    stored = json.load(f)
            except Exception:
                stored = {"obras_nuevas": [], "obras_modificadas": {}}

        # Determinar si es existente o nueva
        existing = next((o for o in obras if o.get("id") == obra_id), None)
        if existing:
            existing.update(obra_data)
            stored.setdefault("obras_modificadas", {})[obra_id] = obra_data
        else:
            obras.append(obra_data)
            stored.setdefault("obras_nuevas", []).append(obra_data)

        # Guardar en disco
        os.makedirs(os.path.dirname(self.UPDATES_PATH), exist_ok=True)
        with open(self.UPDATES_PATH, "w", encoding="utf-8") as f:
            json.dump(stored, f, indent=2, ensure_ascii=False)

        # Invalidar caché
        self._cache = None
        return obra_data
