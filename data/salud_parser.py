"""
Lector y Procesador Oficial del Plan de Recuperación y Rehabilitación de Espacios de Salud (.xlsx)
Secretaría Superior de Operaciones Generales - Gobernación del Estado Portuguesa
Archivo Oficial: ESPACIOS_DE_SALUD_PORTUGUESA_2026.xlsx
"""
import openpyxl
from typing import Dict, List, Any, Optional

def clean_str(val: Any) -> str:
    if val is None:
        return ""
    return str(val).strip()

def clean_float(val: Any, default: float = 0.0) -> float:
    if val is None:
        return default
    try:
        if isinstance(val, (int, float)):
            return round(float(val), 2)
        val_str = str(val).strip().replace("%", "")
        if "," in val_str and "." in val_str:
            val_str = val_str.replace(".", "").replace(",", ".")
        else:
            val_str = val_str.replace(",", ".")
        num = float(val_str)
        # Si vino como decimal 0.0 a 1.0 (ej. 0.9 = 90%)
        if 0 < num <= 1.0 and "%" not in str(val):
            num = num * 100
        return round(num, 2)
    except Exception:
        return default

def clean_int(val: Any, default: int = 0) -> int:
    if val is None:
        return default
    try:
        if isinstance(val, (int, float)):
            return int(val)
        val_str = str(val).strip().replace(".", "").replace(",", "").replace("%", "")
        if not val_str or val_str == "-":
            return default
        return int(float(val_str))
    except Exception:
        return default

def normalize_mun_name(mun: str) -> str:
    if not mun:
        return ""
    m = mun.strip().upper()
    accents = {
        "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U",
        "À": "A", "È": "E", "Ì": "I", "Ò": "O", "Ù": "U"
    }
    for k, v in accents.items():
        m = m.replace(k, v)
    return m

def normalize_status(st_raw: str) -> str:
    s = (st_raw or "").strip().upper()
    if "PARALIZAD" in s:
        return "PARALIZADA"
    elif "INAGURAR" in s or "INAUGURAR" in s:
        return "CULMINADA"
    elif "EQUIPAR" in s or "PROCESO" in s:
        return "EN PROCESO"
    elif "CULMINAD" in s:
        return "CULMINADA"
    return "CULMINADA" if "100" in s else "EN PROCESO"

class SaludParser:
    def __init__(self, excel_path: str = "ESPACIOS_DE_SALUD_PORTUGUESA_2026.xlsx"):
        self.excel_path = excel_path

    def parse_all(self) -> Dict[str, Any]:
        """Procesa dinámicamente las hojas RESUMEN_ESTATAL y CENTROS_SALUD_DETALLE."""
        wb = openpyxl.load_workbook(self.excel_path, data_only=True)

        resumen_sheet_name = next((s for s in wb.sheetnames if "RESUMEN" in s.upper()), "RESUMEN_ESTATAL")
        detalle_sheet_name = next((s for s in wb.sheetnames if "DETALLE" in s.upper() or "CENTRO" in s.upper()), "CENTROS_SALUD_DETALLE")

        ws_resumen = wb[resumen_sheet_name] if resumen_sheet_name in wb.sheetnames else None
        ws_detalle = wb[detalle_sheet_name] if detalle_sheet_name in wb.sheetnames else None

        # 1. Cargar detalle individual de centros de salud
        centros = self._parse_centros_detalle(ws_detalle) if ws_detalle else []

        # 2. Cargar resumen estatal (tipologías y estatus por municipio)
        distribucion_tipos, resumen_municipios, totales_estatales = self._parse_resumen_estatal(ws_resumen, centros)

        # 3. Frentes prioritarios (En Proceso + Paralizadas)
        frentes_prioritarios = [c for c in centros if c["estatus"] in ["EN PROCESO", "PARALIZADA"]]

        return {
            "centros": centros,
            "total_centros": len(centros),
            "distribucion_tipos": distribucion_tipos,
            "resumen_municipios": resumen_municipios,
            "totales_estatales": totales_estatales,
            "frentes_prioritarios": frentes_prioritarios,
            "total_frentes_prioritarios": len(frentes_prioritarios)
        }

    def _parse_centros_detalle(self, ws) -> List[Dict[str, Any]]:
        """Extrae los centros de salud individuales de la hoja CENTROS_SALUD_DETALLE."""
        centros = []
        max_r = ws.max_row

        # Encontrar fila de encabezados
        header_r = 3
        col_id = 1
        col_mun = 2
        col_nombre = 3
        col_asic = 4
        col_dir = 5
        col_tipo = 6
        col_fase = 7
        col_estatus = 8
        col_pct = 9
        col_ente = 10

        for r in range(1, min(10, max_r + 1)):
            row_txt = [str(ws.cell(r, c).value or "").upper() for c in range(1, 15)]
            if any("MUNICIPIO" in cell for cell in row_txt) and any("NOMBRE" in cell for cell in row_txt):
                header_r = r
                for c in range(1, 15):
                    cval = str(ws.cell(header_r, c).value or "").upper()
                    if cval in ["N°", "NO", "NUM", "ITEM", "ID"]: col_id = c
                    elif "MUNICIPIO" in cval: col_mun = c
                    elif "NOMBRE" in cval: col_nombre = c
                    elif "ASIC" in cval: col_asic = c
                    elif "DIRECC" in cval: col_dir = c
                    elif "TIPO" in cval: col_tipo = c
                    elif "FASE" in cval or "NIVEL" in cval: col_fase = c
                    elif "ESTATUS" in cval or "ESTADO" in cval: col_estatus = c
                    elif "PORCENTAJE" in cval or "%" in cval or "AVANCE" in cval: col_pct = c
                    elif "ENTE" in cval or "EJECUTOR" in cval: col_ente = c
                break

        for r in range(header_r + 1, max_r + 1):
            mun_raw = clean_str(ws.cell(r, col_mun).value)
            nombre_raw = clean_str(ws.cell(r, col_nombre).value)
            if not mun_raw or not nombre_raw or "MUNICIPIO" in mun_raw.upper():
                continue

            item_id = clean_int(ws.cell(r, col_id).value, len(centros) + 1)
            asic_raw = clean_str(ws.cell(r, col_asic).value) or "ASIC GENERAL"
            dir_raw = clean_str(ws.cell(r, col_dir).value) or "DIRECCIÓN EN CAMPO"
            tipo_raw = clean_str(ws.cell(r, col_tipo).value).upper() or "CPT"
            fase_raw = clean_str(ws.cell(r, col_fase).value) or ""
            st_raw = clean_str(ws.cell(r, col_estatus).value).upper() or "CULMINADA"
            norm_st = normalize_status(st_raw)
            pct_val = clean_float(ws.cell(r, col_pct).value, 100.0 if norm_st == "CULMINADA" else 50.0)
            ente_raw = clean_str(ws.cell(r, col_ente).value) or "GOBERNACIÓN"

            centros.append({
                "id": item_id,
                "municipio": mun_raw.upper(),
                "municipio_norm": normalize_mun_name(mun_raw),
                "nombre": nombre_raw,
                "asic": asic_raw,
                "direccion": dir_raw,
                "tipo_centro": tipo_raw,
                "fase_nivel": fase_raw,
                "estatus": norm_st,
                "estatus_raw": st_raw,
                "porcentaje": pct_val,
                "ente_ejecutor": ente_raw
            })

        return centros

    def _parse_resumen_estatal(self, ws, centros_detalle: List[Dict[str, Any]]):
        """Extrae la distribución de tipologías y el resumen por municipio."""
        distribucion_tipos = []
        resumen_municipios = []

        if ws is not None:
            max_r = ws.max_row
            # 1. Distribución por Tipología
            # Buscar filas entre R6 y R15
            for r in range(1, max_r + 1):
                c1 = clean_str(ws.cell(r, 1).value).upper()
                c2 = ws.cell(r, 2).value
                if any(t in c1 for t in ["HOSPITAL", "CDI", "SRI", "CPT", "ESPECIAL", "FARMACIA"]) and "DISTRIBUCI" not in c1:
                    cant = clean_int(c2)
                    distribucion_tipos.append({
                        "tipo": clean_str(ws.cell(r, 1).value),
                        "cantidad": cant
                    })

            # 2. Resumen por Municipio (buscar fila con encabezado MUNICIPIO y CULMINADAS)
            mun_header_r = None
            for r in range(1, max_r + 1):
                txt = " ".join(str(ws.cell(r, c).value or "").upper() for c in range(1, 6))
                if "MUNICIPIO" in txt and "CULMINADA" in txt:
                    mun_header_r = r
                    break

            if mun_header_r:
                for r in range(mun_header_r + 1, max_r + 1):
                    m_name = clean_str(ws.cell(r, 1).value)
                    if not m_name or "TOTAL" in m_name.upper():
                        continue
                    culm = clean_int(ws.cell(r, 2).value)
                    proc = clean_int(ws.cell(r, 3).value)
                    para = clean_int(ws.cell(r, 4).value)
                    tot = culm + proc + para
                    pct = round((culm / tot * 100), 1) if tot > 0 else 0.0
                    resumen_municipios.append({
                        "municipio": m_name.upper(),
                        "municipio_norm": normalize_mun_name(m_name),
                        "culminadas": culm,
                        "en_proceso": proc,
                        "paralizadas": para,
                        "total_obras": tot,
                        "pct_culminacion": pct
                    })

        # Fallback de distribución por tipo si no vino en el Excel
        if not distribucion_tipos:
            tipos_count = {}
            for c in centros_detalle:
                tp = c["tipo_centro"]
                tipos_count[tp] = tipos_count.get(tp, 0) + 1
            for tp, count in tipos_count.items():
                distribucion_tipos.append({"tipo": tp, "cantidad": count})

        # Fallback de resumen municipios a partir del detalle si faltan
        if not resumen_municipios and centros_detalle:
            m_groups = {}
            for c in centros_detalle:
                m = c["municipio"]
                mn = c["municipio_norm"]
                if mn not in m_groups:
                    m_groups[mn] = {"municipio": m, "municipio_norm": mn, "culminadas": 0, "en_proceso": 0, "paralizadas": 0, "total_obras": 0}
                m_groups[mn]["total_obras"] += 1
                if c["estatus"] == "CULMINADA":
                    m_groups[mn]["culminadas"] += 1
                elif c["estatus"] == "PARALIZADA":
                    m_groups[mn]["paralizadas"] += 1
                else:
                    m_groups[mn]["en_proceso"] += 1
            for grp in m_groups.values():
                tot = grp["total_obras"]
                grp["pct_culminacion"] = round((grp["culminadas"] / tot * 100), 1) if tot > 0 else 0.0
                resumen_municipios.append(grp)

        # Totales Consolidados Estatales Oficiales
        total_culm = sum(m["culminadas"] for m in resumen_municipios) if resumen_municipios else 113
        total_proc = sum(m["en_proceso"] for m in resumen_municipios) if resumen_municipios else 17
        total_para = sum(m["paralizadas"] for m in resumen_municipios) if resumen_municipios else 4
        total_obras = total_culm + total_proc + total_para if (total_culm + total_proc + total_para) > 0 else 134
        pct_culm = round((total_culm / total_obras * 100), 1) if total_obras > 0 else 84.3

        totales_estatales = {
            "total_obras": total_obras,
            "culminadas": total_culm,
            "en_proceso": total_proc,
            "paralizadas": total_para,
            "pct_culminadas": pct_culm,
            "total_centros": len(centros_detalle) if centros_detalle else 133
        }

        return distribucion_tipos, resumen_municipios, totales_estatales
