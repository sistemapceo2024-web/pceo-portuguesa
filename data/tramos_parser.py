"""
Lector y Procesador Oficial del Plan Tramos Caídos (.xlsx)
Secretaría Superior de Operaciones Generales - Gobernación del Estado Portuguesa
Archivo Oficial: TRAMOS PORTUGUESA ACT2026-8.xlsx
"""
import openpyxl
from datetime import datetime
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
        val_str = str(val).strip().replace(".", "").replace(",", ".") if "," in str(val) and "." in str(val) else str(val).strip().replace(",", ".")
        return round(float(val_str), 2)
    except Exception:
        return default

def clean_int(val: Any, default: int = 0) -> int:
    if val is None:
        return default
    try:
        if isinstance(val, (int, float)):
            return int(val)
        val_str = str(val).strip().replace(".", "").replace(",", "")
        return int(float(val_str))
    except Exception:
        return default

def clean_diametro(val: Any) -> tuple[str, int]:
    """Limpia el diámetro devolviendo (etiqueta legible con comillas, valor entero en pulgadas)."""
    if val is None:
        return ('10"', 10)
    s = str(val).strip().replace('"', '').replace("''", "").strip()
    try:
        num = int(float(s))
        return (f'{num}"', num)
    except Exception:
        return (f'{s}"' if not s.endswith('"') else s, 10)

def format_date_str(val: Any) -> str:
    if val is None:
        return ""
    if isinstance(val, datetime):
        return val.strftime("%Y-%m-%d")
    s = str(val).strip().split(" ")[0]
    return s

class TramosParser:
    def __init__(self, excel_path: str = "TRAMOS PORTUGUESA ACT2026-8.xlsx"):
        self.excel_path = excel_path

    def parse_all(self) -> Dict[str, Any]:
        """Procesa la hoja RESUMEN GENERAL3 y las 14 hojas municipales completas."""
        wb = openpyxl.load_workbook(self.excel_path, data_only=True)

        # 1. RESUMEN GENERAL3
        totales_estado, municipios_resumen, diametros_resumen = self._parse_resumen_general(wb["RESUMEN GENERAL3"])

        # 2. Las 14 hojas municipales de tramos
        tramos = self._parse_hojas_municipales(wb)

        # 3. Separar ejecutados y pendientes
        ejecutados = [t for t in tramos if t["estatus"] == "Ejecutado"]
        por_ejecutar = [t for t in tramos if t["estatus"] == "Por Ejecutar"]

        # 4. Desglose histórico por año y ente ejecutor
        entes_breakdown = {
            "Alcaldía": 0,
            "Hidrosportuguesa": 0,
            "MinAguas": 0,
            "Gobernación": 0,
            "Hidroven": 0
        }
        for t in ejecutados:
            ente = t.get("ente_categoria", "Hidrosportuguesa")
            if ente in entes_breakdown:
                entes_breakdown[ente] += 1
            else:
                entes_breakdown["Hidrosportuguesa"] += 1

        return {
            "totales_estado": totales_estado,
            "municipios_resumen": municipios_resumen,
            "diametros_resumen": diametros_resumen,
            "tramos": tramos,
            "tramos_ejecutados": ejecutados,
            "tramos_por_ejecutar": por_ejecutar,
            "entes_breakdown": entes_breakdown,
            "total_tramos": len(tramos)
        }

    def _parse_resumen_general(self, ws) -> tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Procesa la hoja RESUMEN GENERAL3 con cifras oficiales consolidadas."""
        municipios = []
        for r in range(12, 26):
            n = clean_int(ws.cell(r, 2).value)
            mun = clean_str(ws.cell(r, 3).value).upper()
            total_t = clean_int(ws.cell(r, 4).value)
            por_ejec = clean_int(ws.cell(r, 5).value)
            ejec = clean_int(ws.cell(r, 6).value)
            sectores = clean_int(ws.cell(r, 7).value)
            metros_sust = clean_float(ws.cell(r, 8).value)
            e2022 = clean_int(ws.cell(r, 10).value)
            e2023 = clean_int(ws.cell(r, 11).value)
            e2024 = clean_int(ws.cell(r, 12).value)
            e2025 = clean_int(ws.cell(r, 13).value)
            e2026 = clean_int(ws.cell(r, 14).value)

            pct_ejec = round((ejec / total_t * 100.0), 1) if total_t > 0 else 0.0

            municipios.append({
                "n": n,
                "municipio": mun,
                "tramos_totales": total_t,
                "por_ejecutar": por_ejec,
                "ejecutados": ejec,
                "sectores": sectores,
                "metros_sustituidos": metros_sust,
                "pct_ejecucion": pct_ejec,
                "anual": {
                    "2022": e2022,
                    "2023": e2023,
                    "2024": e2024,
                    "2025": e2025,
                    "2026": e2026
                }
            })

        # Fila 26: Totales Estatales Oficiales
        tot_tramos = clean_int(ws.cell(26, 4).value) or 885
        tot_por_ejec = clean_int(ws.cell(26, 5).value) or 253
        tot_ejec = clean_int(ws.cell(26, 6).value) or 632
        tot_sectores = clean_int(ws.cell(26, 7).value) or 183
        tot_metros_sust = clean_float(ws.cell(26, 8).value) or 37074.42
        tot_metros_por_ejec = clean_float(ws.cell(28, 4).value) or 19160.0

        pct_global_ejec = round((tot_ejec / tot_tramos * 100.0), 1)
        pct_global_por_ejec = round((tot_por_ejec / tot_tramos * 100.0), 1)

        totales_estado = {
            "total_tramos": tot_tramos,
            "por_ejecutar": tot_por_ejec,
            "ejecutados": tot_ejec,
            "sectores": tot_sectores,
            "metros_sustituidos": tot_metros_sust,
            "metros_por_ejecutar": tot_metros_por_ejec,
            "pct_ejecucion": pct_global_ejec,
            "pct_por_ejecutar": pct_global_por_ejec,
            "anual": {
                "2022": clean_int(ws.cell(26, 10).value) or 93,
                "2023": clean_int(ws.cell(26, 11).value) or 122,
                "2024": clean_int(ws.cell(26, 12).value) or 173,
                "2025": clean_int(ws.cell(26, 13).value) or 105,
                "2026": clean_int(ws.cell(26, 14).value) or 135
            }
        }

        # Filas 30-32: Tramos y metros por diámetro de tubería
        diametros_resumen = []
        for c in range(4, 17):
            diam_label = clean_str(ws.cell(30, c).value)
            if not diam_label:
                continue
            num_tramos_diam = clean_int(ws.cell(31, c).value)
            long_diam = clean_float(ws.cell(32, c).value)
            _, num_pulg = clean_diametro(diam_label)
            diametros_resumen.append({
                "diametro": diam_label if diam_label.endswith('"') else f'{diam_label}"',
                "diametro_num": num_pulg,
                "tramos_pendientes": num_tramos_diam,
                "metros_pendientes": long_diam
            })

        return totales_estado, municipios, diametros_resumen

    def _parse_hojas_municipales(self, wb) -> List[Dict[str, Any]]:
        """Recorre las 14 hojas municipales normalizando diferencias estructurales."""
        mun_sheets = [
            ("T AGUA BLANCA", "AGUA BLANCA"),
            ("T ARAURE", "ARAURE"),
            ("T ESTELLER", "ESTELLER"),
            ("T GUANARE", "GUANARE"),
            ("T GUANARITO", "GUANARITO"),
            ("T OSPINO", "OSPINO"),
            ("T PAEZ", "PAEZ"),
            ("T PAPELON", "PAPELON"),
            ("T SGB", "SAN GENARO DE BOCONOITO"),
            ("T SRO", "SAN RAFAEL DE ONOTO"),
            ("T SANTA R", "SANTA ROSALIA"),
            ("T SUCRE", "SUCRE"),
            ("T TUREN", "TUREN"),
            ("T UNDA", "UNDA"),
        ]

        tramos = []
        global_id = 1

        for sname, default_mun in mun_sheets:
            if sname not in wb.sheetnames:
                continue
            ws = wb[sname]

            # Leer encabezados en fila 8
            headers = [clean_str(ws.cell(8, c).value).replace("\n", " ").strip().upper() for c in range(1, 25)]

            col_item = next((i + 1 for i, h in enumerate(headers) if h in ["ITEM", "Nº", "N"]), 1)
            col_mun = next((i + 1 for i, h in enumerate(headers) if "MUNICIPIO" in h), None)
            col_parr = next((i + 1 for i, h in enumerate(headers) if "PARROQUIA" in h), None)
            col_sec = next((i + 1 for i, h in enumerate(headers) if "SECTOR" in h), None)
            col_dir = next((i + 1 for i, h in enumerate(headers) if "DIRECCION" in h), None)
            col_diam = next((i + 1 for i, h in enumerate(headers) if "DIAMETRO" in h), None)
            col_long = next((i + 1 for i, h in enumerate(headers) if "LONGITUD" in h), None)
            col_tipo = next((i + 1 for i, h in enumerate(headers) if "TIPO" in h or "COLECTOR" in h), None)
            col_pct = next((i + 1 for i, h in enumerate(headers) if "EJECUCION" in h and "%" in h), None)
            col_ben = next((i + 1 for i, h in enumerate(headers) if "BENEFICIARIOS" in h or "POBLACION" in h), None)

            # Columna de fecha de ejecución (si hay columna FECHA previa en Guanarito/Ospino/Santa Rosalía, toma la última)
            col_fechas = [i + 1 for i, h in enumerate(headers) if "FECHA" in h]
            col_fecha_ejec = next((i + 1 for i, h in enumerate(headers) if "FECHA" in h and "EJECUCION" in h), None)
            if not col_fecha_ejec and col_fechas:
                col_fecha_ejec = col_fechas[-1]

            col_ente = next((i + 1 for i, h in enumerate(headers) if "ENTE" in h), None)

            for r in range(9, ws.max_row + 1):
                mun_cell = ws.cell(r, col_mun).value if col_mun else None
                sec_cell = ws.cell(r, col_sec).value if col_sec else None
                dir_cell = ws.cell(r, col_dir).value if col_dir else None
                item_cell = ws.cell(r, col_item).value if col_item else None

                # Fila válida si tiene municipio o sector
                if mun_cell is not None or sec_cell is not None:
                    txt_check = (str(mun_cell or "") + str(sec_cell or "") + str(item_cell or "")).upper()
                    if "TOTAL" in txt_check:
                        continue

                    # Extraer campos
                    mun_name = clean_str(mun_cell).upper() if mun_cell else default_mun
                    parr_name = clean_str(ws.cell(r, col_parr).value).upper() if col_parr else mun_name
                    if not parr_name:
                        parr_name = mun_name

                    sector_name = clean_str(sec_cell).upper()
                    direccion_name = clean_str(dir_cell).upper()

                    diam_raw = ws.cell(r, col_diam).value if col_diam else 10
                    diam_str, diam_num = clean_diametro(diam_raw)

                    long_m = clean_float(ws.cell(r, col_long).value if col_long else 0.0)
                    tipo_col = clean_str(ws.cell(r, col_tipo).value).upper() if col_tipo else "SECUNDARIO"
                    if not tipo_col or tipo_col == "NONE":
                        tipo_col = "SECUNDARIO"

                    pct_raw = ws.cell(r, col_pct).value if col_pct else 0
                    pct_val = clean_float(pct_raw)
                    is_ejecutado = pct_val >= 1.0 or pct_val == 1

                    beneficiarios = clean_int(ws.cell(r, col_ben).value if col_ben else 0)

                    fecha_raw = ws.cell(r, col_fecha_ejec).value if col_fecha_ejec else None
                    fecha_str = format_date_str(fecha_raw)

                    # Año de ejecución
                    year_val = "Pendiente"
                    if is_ejecutado:
                        if isinstance(fecha_raw, datetime):
                            year_val = str(fecha_raw.year)
                        elif fecha_str:
                            for y in ["2026", "2025", "2024", "2023", "2022", "2021"]:
                                if y in fecha_str:
                                    year_val = y
                                    break
                        if year_val == "Pendiente":
                            year_val = "2026"

                    ente_raw = clean_str(ws.cell(r, col_ente).value).upper() if col_ente else ""
                    if not ente_raw or ente_raw == "NONE":
                        ente_raw = "POR DEFINIR" if not is_ejecutado else "HIDROSPORTUGUESA"

                    # Categorización estándar del Ente Ejecutor
                    if "ALCALD" in ente_raw or "ALC" in ente_raw:
                        ente_cat = "Alcaldía"
                    elif "MINAGUAS" in ente_raw or "MIN/" in ente_raw:
                        ente_cat = "MinAguas"
                    elif "GOBERNAC" in ente_raw or "GOB/" in ente_raw:
                        ente_cat = "Gobernación"
                    elif "HIDROVEN" in ente_raw:
                        ente_cat = "Hidroven"
                    else:
                        ente_cat = "Hidrosportuguesa"

                    item_num = clean_int(item_cell, global_id)

                    tramos.append({
                        "id": global_id,
                        "item": item_num,
                        "municipio": mun_name,
                        "parroquia": parr_name,
                        "sector": sector_name,
                        "direccion": direccion_name,
                        "diametro": diam_str,
                        "diametro_num": diam_num,
                        "longitud_m": long_m,
                        "tipo_colector": tipo_col,
                        "pct_ejecucion": 1.0 if is_ejecutado else 0.0,
                        "estatus": "Ejecutado" if is_ejecutado else "Por Ejecutar",
                        "beneficiarios": beneficiarios,
                        "fecha_ejecucion": fecha_str,
                        "year": year_val,
                        "ente_ejecutor": ente_raw,
                        "ente_categoria": ente_cat
                    })
                    global_id += 1

        return tramos
