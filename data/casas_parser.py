"""
Lector Inteligente del Plan Construye Tu Casa
Fuente oficial: CONSTRUYE_TU_CASA_PORTUGUESA_2026.xlsx
Hojas: RESUMEN_VIVIENDAS y DETALLE_URBANISMOS
Ente Ejecutor: FONDEREVI (Fondo para el Desarrollo Habitacional del Estado Portuguesa)
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

def format_number_es(val) -> str:
    """Formatea número entero o float con separador de miles español (punto)."""
    if val is None:
        return "0"
    try:
        n = float(val)
        if n.is_integer():
            return f"{int(n):,}".replace(",", ".")
        return f"{n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(val)

# Detalle oficial de los 24 urbanismos y proyectos habitacionales por municipio
URBANISMOS_DETALLE = {
    "aguablanca": [
        {"urbanismo": "Urb. Manuelita Sáenz (1era Etapa)", "sector": "Manuelita Sáenz", "ejecutadas": 28, "en_ejecucion": 0, "por_iniciar": 0, "estatus": "Culminada", "observaciones": "Fase I culminada"},
        {"urbanismo": "Urb. Manuelita Sáenz (2da Etapa)", "sector": "Manuelita Sáenz", "ejecutadas": 0, "en_ejecucion": 22, "por_iniciar": 0, "estatus": "En Ejecución", "observaciones": "Proyección FONDEREVI"},
        {"urbanismo": "Urb. Hugo R. Chávez", "sector": "Hugo R. Chávez", "ejecutadas": 0, "en_ejecucion": 48, "por_iniciar": 0, "estatus": "En Ejecución", "observaciones": "Proyección FONDEREVI"}
    ],
    "araure": [
        {"urbanismo": "Villas de San José", "sector": "Villas de San José", "ejecutadas": 31, "en_ejecucion": 0, "por_iniciar": 0, "estatus": "Culminada", "observaciones": "Culminada"},
        {"urbanismo": "Huracán Rojo", "sector": "Huracán Rojo", "ejecutadas": 12, "en_ejecucion": 0, "por_iniciar": 0, "estatus": "Culminada", "observaciones": "Culminada"},
        {"urbanismo": "Las Espigas", "sector": "Las Espigas", "ejecutadas": 0, "en_ejecucion": 160, "por_iniciar": 0, "estatus": "En Ejecución", "observaciones": "Frente de trabajo activo"},
        {"urbanismo": "Primavera Bolivariana", "sector": "Primavera Bolivariana", "ejecutadas": 0, "en_ejecucion": 36, "por_iniciar": 0, "estatus": "En Ejecución", "observaciones": "Frente de trabajo activo"}
    ],
    "esteller": [
        {"urbanismo": "Bastianelly", "sector": "Bastianelly - Píritu", "ejecutadas": 1, "en_ejecucion": 0, "por_iniciar": 0, "estatus": "Culminada", "observaciones": "Culminada"}
    ],
    "guanare": [
        {"urbanismo": "Barrio La Florida", "sector": "La Florida", "ejecutadas": 1, "en_ejecucion": 0, "por_iniciar": 0, "estatus": "Culminada", "observaciones": "Culminada"},
        {"urbanismo": "4 de Febrero", "sector": "4 de Febrero", "ejecutadas": 26, "en_ejecucion": 0, "por_iniciar": 0, "estatus": "Culminada", "observaciones": "Culminada"},
        {"urbanismo": "La Granja (Torre A y B)", "sector": "La Granja", "ejecutadas": 64, "en_ejecucion": 0, "por_iniciar": 0, "estatus": "Culminada", "observaciones": "Culminada"},
        {"urbanismo": "Los Mangos", "sector": "Los Mangos", "ejecutadas": 14, "en_ejecucion": 0, "por_iniciar": 0, "estatus": "Culminada", "observaciones": "Culminada"},
        {"urbanismo": "La Granja (Torre C)", "sector": "La Granja", "ejecutadas": 0, "en_ejecucion": 32, "por_iniciar": 0, "estatus": "En Ejecución", "observaciones": "Frente de trabajo activo"}
    ],
    "ospino": [
        {"urbanismo": "La Rampa", "sector": "La Rampa", "ejecutadas": 2, "en_ejecucion": 0, "por_iniciar": 0, "estatus": "Culminada", "observaciones": "Culminada"},
        {"urbanismo": "La Aparición", "sector": "La Aparición", "ejecutadas": 1, "en_ejecucion": 0, "por_iniciar": 0, "estatus": "Culminada", "observaciones": "Culminada"},
        {"urbanismo": "Peaje Ospino", "sector": "Peaje Ospino", "ejecutadas": 1, "en_ejecucion": 0, "por_iniciar": 0, "estatus": "Culminada", "observaciones": "Culminada"}
    ],
    "paez": [
        {"urbanismo": "La Villa Pimpinela", "sector": "Pimpinela", "ejecutadas": 1, "en_ejecucion": 0, "por_iniciar": 0, "estatus": "Culminada", "observaciones": "Culminada"},
        {"urbanismo": "El Guamo Pimpinela", "sector": "Pimpinela", "ejecutadas": 1, "en_ejecucion": 0, "por_iniciar": 0, "estatus": "Culminada", "observaciones": "Culminada"},
        {"urbanismo": "Bella Vista", "sector": "Bella Vista", "ejecutadas": 32, "en_ejecucion": 0, "por_iniciar": 0, "estatus": "Culminada", "observaciones": "Culminada"},
        {"urbanismo": "Las Garzas", "sector": "Las Garzas", "ejecutadas": 0, "en_ejecucion": 52, "por_iniciar": 0, "estatus": "En Ejecución", "observaciones": "Frente de trabajo activo"},
        {"urbanismo": "La Sorguera", "sector": "La Sorguera", "ejecutadas": 0, "en_ejecucion": 60, "por_iniciar": 0, "estatus": "En Ejecución", "observaciones": "Frente de trabajo activo"}
    ],
    "sanrafaeldeonoto": [
        {"urbanismo": "San Rafael (Ampliación de Vivienda)", "sector": "San Rafael", "ejecutadas": 1, "en_ejecucion": 0, "por_iniciar": 0, "estatus": "Culminada", "observaciones": "Culminada"},
        {"urbanismo": "Urb. Hugo Chávez II", "sector": "Hugo Chávez II", "ejecutadas": 31, "en_ejecucion": 0, "por_iniciar": 0, "estatus": "Culminada", "observaciones": "Culminada"}
    ],
    "sucre": [
        {"urbanismo": "Las Cruces (Sector Los Caobos)", "sector": "Los Caobos - Biscucuy", "ejecutadas": 5, "en_ejecucion": 0, "por_iniciar": 0, "estatus": "Culminada", "observaciones": "Culminada"}
    ]
}
# Alias con guion bajo para compatibilidad
URBANISMOS_DETALLE["agua_blanca"] = URBANISMOS_DETALLE["aguablanca"]
URBANISMOS_DETALLE["san_rafael_de_onoto"] = URBANISMOS_DETALLE["sanrafaeldeonoto"]

class CasasParser:
    """Lector inteligente para el Plan Construye Tu Casa leyendo RESUMEN_VIVIENDAS y DETALLE_URBANISMOS."""

    DEFAULT_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "CONSTRUYE_TU_CASA_PORTUGUESA_2026.xlsx"
    )
    UPDATES_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "casas_actualizadas.json"
    )

    def __init__(self, excel_path: str = None):
        self.excel_path = excel_path or self.DEFAULT_PATH
        self._cache = None

    def parse_all(self, force_reload: bool = False) -> dict:
        """Carga y procesa las viviendas oficiales de RESUMEN_VIVIENDAS y DETALLE_URBANISMOS."""
        if self._cache and not force_reload:
            return self._cache

        municipios_data = []
        frentes_list = []
        totales = {
            "ejecutadas": 252,
            "proyeccion_ejecucion": 410,
            "por_iniciar": 0,
            "total_general": 662,
            "ente_ejecutor": "FONDEREVI",
            "municipios_activos": 8
        }

        # 1. Leer Excel oficial si existe
        if os.path.exists(self.excel_path):
            try:
                wb = openpyxl.load_workbook(self.excel_path, data_only=True)

                # A. Procesar Hoja DETALLE_URBANISMOS
                detalle_por_mun = defaultdict(list)
                if "DETALLE_URBANISMOS" in wb.sheetnames:
                    ws_det = wb["DETALLE_URBANISMOS"]
                    for r in range(5, ws_det.max_row + 1):
                        m_raw = ws_det.cell(row=r, column=1).value
                        if not m_raw or "TOTAL" in str(m_raw).upper():
                            continue
                        m_str = str(m_raw).strip()
                        m_canon = self._format_mun_name(m_str)
                        urb_name = str(ws_det.cell(row=r, column=2).value or "").strip()
                        if not urb_name:
                            continue
                        est_raw = str(ws_det.cell(row=r, column=3).value or "").strip()
                        cant = int(ws_det.cell(row=r, column=4).value or 0)
                        obs = str(ws_det.cell(row=r, column=5).value or "").strip()

                        is_ejecutada = ("EJECUTADA" in est_raw.upper() and "EN" not in est_raw.upper())
                        st_norm = "Culminada" if is_ejecutada else "En Ejecución"

                        item = {
                            "urbanismo": urb_name,
                            "municipio": m_canon,
                            "sector": urb_name,
                            "estatus_raw": est_raw,
                            "estatus": st_norm,
                            "ejecutadas": cant if is_ejecutada else 0,
                            "en_ejecucion": cant if not is_ejecutada else 0,
                            "por_iniciar": 0,
                            "cantidad": cant,
                            "total": cant,
                            "pct_avance": 100.0 if is_ejecutada else 0.0,
                            "ente": "FONDEREVI",
                            "observaciones": obs or ("Culminada" if is_ejecutada else "Frente de trabajo activo")
                        }
                        detalle_por_mun[normalize_mun_name(m_canon)].append(item)

                # B. Procesar Hoja RESUMEN_VIVIENDAS
                ws_res = wb["RESUMEN_VIVIENDAS"] if "RESUMEN_VIVIENDAS" in wb.sheetnames else wb.active
                tot_ejec = 0
                tot_proy = 0
                tot_inic = 0

                for r in range(6, 14):
                    row = [cell.value for cell in ws_res[r]]
                    if not row or len(row) < 5:
                        continue

                    mun_raw = str(row[1] or "").strip()
                    if not mun_raw or "TOTAL" in mun_raw.upper():
                        continue

                    ejec = int(row[2] or 0)
                    proy = int(row[3] or 0)
                    inic = int(row[4] or 0)
                    tot_row = ejec + proy + inic

                    tot_ejec += ejec
                    tot_proy += proy
                    tot_inic += inic

                    mun_canonical = self._format_mun_name(mun_raw)
                    mun_key = normalize_mun_name(mun_canonical)

                    # Obtener urbanismos desde DETALLE_URBANISMOS o desde el baseline
                    urbanismos = detalle_por_mun.get(mun_key)
                    if not urbanismos:
                        urbanismos = URBANISMOS_DETALLE.get(mun_key, [])

                    obs_text = f"{len(urbanismos)} Urbanismos / Proyectos atendidos" if urbanismos else "Frentes de autoconstrucción comunitaria"

                    municipios_data.append({
                        "numero": int(row[0] or (r - 5)),
                        "municipio": mun_canonical,
                        "municipio_raw": mun_raw,
                        "ejecutadas": ejec,
                        "proyeccion_ejecucion": proy,
                        "por_iniciar": inic,
                        "total": tot_row,
                        "pct_ejecutado": round((ejec / tot_row * 100), 1) if tot_row > 0 else 0.0,
                        "observaciones": obs_text,
                        "urbanismos": urbanismos
                    })

                tot_gen = tot_ejec + tot_proy + tot_inic
                totales["ejecutadas"] = tot_ejec if tot_ejec > 0 else 252
                totales["proyeccion_ejecucion"] = tot_proy if tot_proy > 0 else 410
                totales["por_iniciar"] = tot_inic
                totales["total_general"] = tot_gen if tot_gen > 0 else 662
                totales["municipios_activos"] = len(municipios_data)

            except Exception as e:
                print(f"[CasasParser Excel Error]: {e}, utilizando baseline oficial.")
                municipios_data = self._build_baseline_municipios()
        else:
            municipios_data = self._build_baseline_municipios()

        # 2. Generar lista aplanada de frentes y urbanismos individuales
        for m in municipios_data:
            mun_name = m["municipio"]
            urbs = m.get("urbanismos", [])
            for u in urbs:
                tot_u = u["ejecutadas"] + u["en_ejecucion"] + u.get("por_iniciar", 0)
                st = u.get("estatus") or ("Culminada" if u["en_ejecucion"] == 0 else "En Ejecución")
                frentes_list.append({
                    "urbanismo": u["urbanismo"],
                    "municipio": mun_name,
                    "sector": u.get("sector", u["urbanismo"]),
                    "ejecutadas": u["ejecutadas"],
                    "en_ejecucion": u["en_ejecucion"],
                    "por_iniciar": u.get("por_iniciar", 0),
                    "total": tot_u,
                    "cantidad": tot_u,
                    "pct_avance": round((u["ejecutadas"] / tot_u * 100), 1) if tot_u > 0 else 0.0,
                    "estatus": st,
                    "estatus_raw": u.get("estatus_raw", st),
                    "ente": "FONDEREVI",
                    "observaciones": u.get("observaciones", "Construcción comunitaria FONDEREVI.")
                })

        # 3. Aplicar actualizaciones persistidas en JSON si existen
        if os.path.exists(self.UPDATES_PATH):
            try:
                with open(self.UPDATES_PATH, "r", encoding="utf-8") as f:
                    updates = json.load(f)
                    modifs = updates.get("modificaciones", {})
                    for f_item in frentes_list:
                        u_key = f"{normalize_mun_name(f_item['municipio'])}_{normalize_mun_name(f_item['urbanismo'])}"
                        if u_key in modifs:
                            f_item.update(modifs[u_key])

                    nuevos = updates.get("nuevos_frentes", [])
                    for n in nuevos:
                        frentes_list.append(n)
            except Exception as err:
                print(f"[CasasParser JSON Error]: {err}")

        # Recalcular totales consolidados
        tot_ejec_final = sum(m["ejecutadas"] for m in municipios_data)
        tot_proy_final = sum(m["proyeccion_ejecucion"] for m in municipios_data)
        tot_gen_final = tot_ejec_final + tot_proy_final

        result = {
            "municipios": municipios_data,
            "frentes": frentes_list,
            "ente_ejecutor": "FONDEREVI",
            "totales": {
                "ejecutadas": tot_ejec_final,
                "proyeccion_ejecucion": tot_proy_final,
                "por_iniciar": 0,
                "total_general": tot_gen_final,
                "ente_ejecutor": "FONDEREVI",
                "municipios_activos": len(municipios_data)
            }
        }
        self._cache = result
        return result

    def get_all_data(self) -> dict:
        """Alias para parse_all."""
        return self.parse_all()

    def get_kpis(self, municipio: str = "Todos los Municipios", estatus: str = "Todos") -> dict:
        """Calcula los KPIs filtrados dinámicamente."""
        data = self.parse_all()
        frentes = data.get("frentes", [])
        muns_data = data.get("municipios", [])

        # Filtrado por municipio
        if municipio and municipio != "Todos los Municipios":
            m_norm = normalize_mun_name(municipio)
            frentes = [f for f in frentes if normalize_mun_name(f["municipio"]) == m_norm or m_norm in normalize_mun_name(f["municipio"])]
            muns_filtered = [m for m in muns_data if normalize_mun_name(m["municipio"]) == m_norm or m_norm in normalize_mun_name(m["municipio"])]
        else:
            muns_filtered = muns_data

        # Filtrado por estatus
        if estatus and estatus != "Todos":
            if estatus == "Culminada":
                frentes = [f for f in frentes if f["estatus"] == "Culminada"]
            elif estatus in ("En Ejecución", "Proyección y Ejecución"):
                frentes = [f for f in frentes if f["estatus"] == "En Ejecución"]

        tot_ejec = sum(f["ejecutadas"] for f in frentes) if (municipio != "Todos los Municipios" or estatus != "Todos") else sum(m["ejecutadas"] for m in muns_filtered)
        tot_proy = sum(f["en_ejecucion"] for f in frentes) if (municipio != "Todos los Municipios" or estatus != "Todos") else sum(m["proyeccion_ejecucion"] for m in muns_filtered)
        tot_gen = tot_ejec + tot_proy

        pct_ejec = round((tot_ejec / tot_gen * 100), 1) if tot_gen > 0 else 0.0
        pct_proy = round((tot_proy / tot_gen * 100), 1) if tot_gen > 0 else 0.0

        return {
            "total_general": tot_gen,
            "total_viviendas": tot_gen,
            "ejecutadas": tot_ejec,
            "proyeccion_ejecucion": tot_proy,
            "por_iniciar": 0,
            "pct_ejecutadas": pct_ejec,
            "pct_en_ejecucion": pct_proy,
            "ente_ejecutor": "FONDEREVI",
            "municipios_activos": len(muns_filtered),
            "municipio_activo": municipio
        }

    def get_resumen_municipios(self, municipio: str = "Todos los Municipios") -> List[dict]:
        """Obtiene la lista de municipios filtrada."""
        data = self.parse_all()
        muns = data.get("municipios", [])
        if municipio and municipio != "Todos los Municipios":
            m_norm = normalize_mun_name(municipio)
            muns = [m for m in muns if normalize_mun_name(m["municipio"]) == m_norm or m_norm in normalize_mun_name(m["municipio"])]
        return muns

    def get_frentes_prioritarios(self, municipio: str = "Todos los Municipios") -> List[dict]:
        """Obtiene los frentes de obra actualmente activos en ejecución."""
        data = self.parse_all()
        frentes = [f for f in data.get("frentes", []) if f["en_ejecucion"] > 0]
        if municipio and municipio != "Todos los Municipios":
            m_norm = normalize_mun_name(municipio)
            frentes = [f for f in frentes if normalize_mun_name(f["municipio"]) == m_norm or m_norm in normalize_mun_name(f["municipio"])]
        return frentes

    def get_municipio(self, municipio: str) -> Optional[dict]:
        """Obtiene la información de un municipio específico."""
        res = self.get_resumen_municipios(municipio)
        return res[0] if res else None

    def _format_mun_name(self, raw: str) -> str:
        r = raw.strip().upper()
        mapping = {
            "AGUA BLANCA": "Agua Blanca",
            "ARAURE": "Araure",
            "ESTELLER": "Esteller",
            "GUANARE": "Guanare",
            "OSPINO": "Ospino",
            "PÁEZ": "Páez",
            "PAEZ": "Páez",
            "SAN RAFAEL DE ONOTO": "San Rafael de Onoto",
            "SUCRE": "Sucre"
        }
        return mapping.get(r, raw.strip().title())

    def _build_baseline_municipios(self) -> List[dict]:
        """Construye datos baseline oficiales en caso de que el archivo Excel no esté accesible."""
        base = [
            (1, "Agua Blanca", 28, 70, 0, 98),
            (2, "Araure", 43, 196, 0, 239),
            (3, "Esteller", 1, 0, 0, 1),
            (4, "Guanare", 105, 32, 0, 137),
            (5, "Ospino", 4, 0, 0, 4),
            (6, "Páez", 34, 112, 0, 146),
            (7, "San Rafael de Onoto", 32, 0, 0, 32),
            (8, "Sucre", 5, 0, 0, 5),
        ]
        res = []
        for n, mun, ejec, proy, inic, tot in base:
            mun_key = normalize_mun_name(mun)
            urbs = URBANISMOS_DETALLE.get(mun_key, [])
            res.append({
                "numero": n,
                "municipio": mun,
                "municipio_raw": mun.upper(),
                "ejecutadas": ejec,
                "proyeccion_ejecucion": proy,
                "por_iniciar": inic,
                "total": tot,
                "pct_ejecutado": round(ejec / tot * 100, 1),
                "observaciones": f"{len(urbs)} Urbanismos / Proyectos atendidos",
                "urbanismos": urbs
            })
        return res

    def update_vivienda_frente(self, municipio: str, urbanismo: str, sector: str, ejecutadas: int, en_ejecucion: int, observaciones: str = "") -> dict:
        """Registra o actualiza un frente habitacional en casas_actualizadas.json."""
        tot = ejecutadas + en_ejecucion
        st = "Culminada" if en_ejecucion == 0 else "En Ejecución"
        u_key = f"{normalize_mun_name(municipio)}_{normalize_mun_name(urbanismo)}"

        updates = {"modificaciones": {}, "nuevos_frentes": []}
        if os.path.exists(self.UPDATES_PATH):
            try:
                with open(self.UPDATES_PATH, "r", encoding="utf-8") as f:
                    updates = json.load(f)
            except Exception:
                pass

        registro = {
            "urbanismo": urbanismo,
            "municipio": municipio,
            "sector": sector,
            "ejecutadas": ejecutadas,
            "en_ejecucion": en_ejecucion,
            "total": tot,
            "cantidad": tot,
            "pct_avance": round(ejecutadas / tot * 100, 1) if tot > 0 else 0.0,
            "estatus": st,
            "observaciones": observaciones
        }

        updates["modificaciones"][u_key] = registro
        os.makedirs(os.path.dirname(self.UPDATES_PATH), exist_ok=True)
        with open(self.UPDATES_PATH, "w", encoding="utf-8") as f:
            json.dump(updates, f, indent=2, ensure_ascii=False)

        self._cache = None
        return registro
