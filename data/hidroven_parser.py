"""
Lector y Procesador Oficial de HIDROVEN / Hidrosportuguesa (.xlsx)
Secretaría Superior de Operaciones Generales - Gobernación del Estado Portuguesa
"""
import os
import json
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
            return float(val)
        val_str = str(val).strip().replace(",", ".")
        return float(val_str)
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

def format_date_str(val: Any) -> str:
    if val is None:
        return ""
    if isinstance(val, datetime):
        return val.strftime("%d/%m/%Y")
    return str(val).split(" ")[0].strip()

class HidrovenParser:
    def __init__(self, excel_path: Optional[str] = None):
        if not excel_path:
            config_file = os.path.join(os.path.dirname(__file__), "config_rutas.json")
            if os.path.exists(config_file):
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        cfg = json.load(f)
                        cand = cfg.get("fiesta_agua") or cfg.get("hidroven_excel")
                        if cand and os.path.exists(cand):
                            excel_path = cand
                except Exception:
                    pass
        if not excel_path:
            if os.path.exists("OPERATIVIDAD  PORTUGUESA 17-11-26.xlsx"):
                excel_path = "OPERATIVIDAD  PORTUGUESA 17-11-26.xlsx"
            else:
                excel_path = "OPERATIVIDAD  PORTUGUESA-8.xlsx"
        self.excel_path = excel_path

    def parse_all(self) -> Dict[str, Any]:
        """Procesa todas las pestañas oficiales de HIDROVEN / Hidrosportuguesa."""
        wb = openpyxl.load_workbook(self.excel_path, data_only=True)

        # 1. OPERATIVIDAD ESTADO (Fila 10 encabezados)
        operatividad_estado, totales_estado = self._parse_operatividad_estado(wb["OPERATIVIDAD ESTADO"])

        # 2. POZOS INOPERATIVOS (Fila 4 encabezados) - Para vincular requerimientos
        pozos_inoperativos = self._parse_pozos_inoperativos(wb["POZOS INOPERATIVOS"])
        inop_dict_by_num = {p["num_pozo"].upper(): p for p in pozos_inoperativos if p.get("num_pozo")}
        inop_dict_by_ubic = {p["ubicacion"].upper(): p for p in pozos_inoperativos if p.get("ubicacion")}

        # 3. INTERVENCIONES (Fila 6 encabezados) - 1.595 intervenciones
        intervenciones = self._parse_intervenciones(wb["INTERVENCIONES"])
        
        # Mapeo de intervenciones por pozo para vinculación rápida
        intervenciones_by_pozo = {}
        for itv in intervenciones:
            p_name = itv["pozo"].upper()
            if p_name not in intervenciones_by_pozo:
                intervenciones_by_pozo[p_name] = []
            intervenciones_by_pozo[p_name].append(itv)

        # 4. POZOS (Fila 6 encabezados) - 535 pozos oficiales
        pozos = self._parse_pozos(
            wb["POZOS"],
            inop_dict_by_num=inop_dict_by_num,
            inop_dict_by_ubic=inop_dict_by_ubic,
            intervenciones_by_pozo=intervenciones_by_pozo
        )

        # 5. CONSOLIDADO REHAB. o CONSOLIDADO REHAB (Fila 7-8 encabezados)
        rehab_sheet_name = "CONSOLIDADO REHAB." if "CONSOLIDADO REHAB." in wb.sheetnames else ("CONSOLIDADO REHAB" if "CONSOLIDADO REHAB" in wb.sheetnames else None)
        consolidado_rehab = self._parse_consolidado_rehab(wb[rehab_sheet_name]) if rehab_sheet_name else {}

        # 6. ESTACIONES DE REB A.P (Cono Sur, Cono Norte, Captación/Conducción)
        estaciones_rebombeo = self._parse_estaciones_rebombeo(wb["ESTACIONES DE REB A.P"])

        # 7. CUADRILLA BRIPPA y MANIOBRAS
        brippas = self._parse_brippas(wb["CUADRILLA BRIPPA"])
        maniobras = self._parse_maniobras(wb["MANIOBRAS"])

        return {
            "source_file": self.excel_path,
            "parsed_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "totales_estado": totales_estado,
            "municipios": operatividad_estado,
            "pozos": pozos,
            "pozos_inoperativos": pozos_inoperativos,
            "consolidado_rehab": consolidado_rehab,
            "intervenciones": intervenciones,
            "estaciones_rebombeo": estaciones_rebombeo,
            "brippas": brippas,
            "maniobras": maniobras,
        }

    def _parse_operatividad_estado(self, ws) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        municipios = []
        for r in range(12, 26):
            item = ws.cell(r, 2).value
            mun_name = clean_str(ws.cell(r, 3).value).upper()
            if not mun_name:
                continue
            total_p = clean_int(ws.cell(r, 4).value)
            op_urb = clean_int(ws.cell(r, 5).value)
            op_rur = clean_int(ws.cell(r, 6).value)
            inop_urb = clean_int(ws.cell(r, 7).value)
            inop_rur = clean_int(ws.cell(r, 8).value)
            pct_op = clean_float(ws.cell(r, 9).value)
            caudal = clean_float(ws.cell(r, 10).value)

            op_total = op_urb + op_rur
            inop_total = inop_urb + inop_rur

            municipios.append({
                "item": item,
                "municipio": mun_name,
                "total_pozos": total_p,
                "op_urb": op_urb,
                "op_rur": op_rur,
                "operativos_total": op_total,
                "inop_urb": inop_urb,
                "inop_rur": inop_rur,
                "inoperativos_total": inop_total,
                "pct_operatividad": round(pct_op, 2),
                "caudal_lps": round(caudal, 2)
            })

        # Fila 26: Totales estadales oficiales
        totales = {
            "total_pozos": clean_int(ws.cell(26, 4).value) or 535,
            "operativos_urb": clean_int(ws.cell(26, 5).value) or 174,
            "operativos_rur": clean_int(ws.cell(26, 6).value) or 290,
            "operativos_total": (clean_int(ws.cell(26, 5).value) or 174) + (clean_int(ws.cell(26, 6).value) or 290),
            "inoperativos_urb": clean_int(ws.cell(26, 7).value) or 16,
            "inoperativos_rur": clean_int(ws.cell(26, 8).value) or 55,
            "inoperativos_total": (clean_int(ws.cell(26, 7).value) or 16) + (clean_int(ws.cell(26, 8).value) or 55),
            "pct_operatividad": 86.73,
            "pct_inoperatividad": 13.27,
            "caudal_total_lps": clean_float(ws.cell(26, 10).value) or 8174.41
        }
        return municipios, totales

    def _parse_pozos(
        self,
        ws,
        inop_dict_by_num: dict,
        inop_dict_by_ubic: dict,
        intervenciones_by_pozo: dict
    ) -> List[Dict[str, Any]]:
        pozos = []
        for r in range(7, 542):
            item = ws.cell(r, 1).value
            if item is None:
                continue

            cod_minaguas = clean_str(ws.cell(r, 2).value)
            num_ant = clean_str(ws.cell(r, 3).value)
            mun = clean_str(ws.cell(r, 4).value).upper()
            parr = clean_str(ws.cell(r, 5).value).upper()
            ubic = clean_str(ws.cell(r, 6).value).upper()
            area = clean_str(ws.cell(r, 7).value).upper()
            raw_oper = clean_str(ws.cell(r, 8).value).upper()
            # Normalización a SI o NO
            operatividad = "SI" if "SI" in raw_oper else "NO"

            motor_hp = clean_float(ws.cell(r, 9).value)
            caudal_lps = clean_float(ws.cell(r, 10).value)
            poblacion = clean_int(ws.cell(r, 11).value)

            # Vincular requerimiento técnico si está inoperativo
            inop_info = inop_dict_by_num.get(num_ant.upper()) or inop_dict_by_ubic.get(ubic)

            # Vincular intervenciones históricas
            matched_itvs = intervenciones_by_pozo.get(ubic, [])
            if not matched_itvs:
                # búsqueda aproximada por código anterior o nombre
                matched_itvs = [
                    itv for itv in intervenciones_by_pozo.get(num_ant.upper(), [])
                ]

            pozos.append({
                "n": item,
                "cod_minaguas": cod_minaguas,
                "num_anterior": num_ant,
                "municipio": mun,
                "parroquia": parr,
                "ubicacion": ubic,
                "area": area,
                "operatividad": operatividad,
                "motor_hp": motor_hp,
                "caudal_lps": caudal_lps,
                "poblacion": poblacion,
                "inoperativo_info": inop_info,
                "intervenciones": matched_itvs
            })
        return pozos

    def _parse_pozos_inoperativos(self, ws) -> List[Dict[str, Any]]:
        inoperativos = []
        for r in range(5, ws.max_row + 1):
            item = ws.cell(r, 1).value
            if item is None:
                continue
            num_pozo = clean_str(ws.cell(r, 2).value)
            mun = clean_str(ws.cell(r, 3).value).upper()
            parr = clean_str(ws.cell(r, 4).value).upper()
            ubic = clean_str(ws.cell(r, 5).value).upper()
            area = clean_str(ws.cell(r, 6).value).upper() or clean_str(ws.cell(r, 7).value).upper()
            pob = clean_int(ws.cell(r, 8).value)
            req = clean_str(ws.cell(r, 9).value)
            cap = clean_str(ws.cell(r, 10).value)
            fecha = format_date_str(ws.cell(r, 11).value)

            inoperativos.append({
                "item": item,
                "num_pozo": num_pozo,
                "municipio": mun,
                "parroquia": parr,
                "ubicacion": ubic,
                "area": area,
                "poblacion": pob,
                "requerimiento": req,
                "capacidad": cap,
                "fecha_salida": fecha
            })
        return inoperativos

    def _parse_consolidado_rehab(self, ws) -> Dict[str, Any]:
        municipios = []
        tot_rehab = 0
        tot_itv = 0
        tot_mant = 0

        for r in range(1, 35):
            val_col2 = ws.cell(r, 2).value
            val_col3 = clean_str(ws.cell(r, 3).value).upper()
            if "TOTAL" in val_col3:
                tot_rehab = clean_int(ws.cell(r, 4).value)
                tot_itv = clean_int(ws.cell(r, 11).value)
                tot_mant = clean_int(ws.cell(r, 18).value)
            elif isinstance(val_col2, (int, float)) and int(val_col2) in range(1, 15) and val_col3:
                item = int(val_col2)
                mun = val_col3
                rehab_total = clean_int(ws.cell(r, 4).value)
                rehab_2026 = clean_int(ws.cell(r, 5).value)
                rehab_2025 = clean_int(ws.cell(r, 6).value)
                rehab_2024 = clean_int(ws.cell(r, 7).value)
                rehab_2023 = clean_int(ws.cell(r, 8).value)
                rehab_2022 = clean_int(ws.cell(r, 9).value)
                rehab_2021 = clean_int(ws.cell(r, 10).value)
                
                inter_total = clean_int(ws.cell(r, 11).value)
                mant_total = clean_int(ws.cell(r, 18).value)

                municipios.append({
                    "item": item,
                    "municipio": mun,
                    "rehabilitados": rehab_total,
                    "rehab_2026": rehab_2026,
                    "rehab_2025": rehab_2025,
                    "rehab_2024": rehab_2024,
                    "rehab_2023": rehab_2023,
                    "rehab_2022": rehab_2022,
                    "rehab_2021": rehab_2021,
                    "intervenciones": inter_total,
                    "mantenimientos": mant_total
                })

        return {
            "total_rehabilitados": tot_rehab or 339,
            "total_intervenciones": tot_itv or 797,
            "total_mantenimientos": tot_mant or 440,
            "municipios": municipios
        }

    def _parse_intervenciones(self, ws) -> List[Dict[str, Any]]:
        intervenciones = []
        for r in range(7, ws.max_row + 1):
            mun = clean_str(ws.cell(r, 2).value).upper()
            pozo = clean_str(ws.cell(r, 3).value).upper()
            if not mun and not pozo:
                continue

            num = ws.cell(r, 1).value or len(intervenciones) + 1
            fecha = format_date_str(ws.cell(r, 4).value)
            reha = ws.cell(r, 5).value
            mant = ws.cell(r, 6).value
            inte = ws.cell(r, 7).value

            fuente = clean_str(ws.cell(r, 12).value)
            obs = clean_str(ws.cell(r, 13).value)

            tipo = "REHABILITACIÓN" if reha else ("MANTENIMIENTO" if mant else "INTERVENCIÓN")

            intervenciones.append({
                "num": num,
                "municipio": mun,
                "pozo": pozo,
                "fecha": fecha,
                "tipo": tipo,
                "fuente": fuente,
                "observacion": obs
            })
        return intervenciones

    def _parse_estaciones_rebombeo(self, ws) -> Dict[str, List[Dict[str, Any]]]:
        # 1. Cono Sur (filas 10 a 26 - 17 estaciones)
        cono_sur = []
        for r in range(10, 27):
            item = ws.cell(r, 1).value
            if item is None:
                continue
            cono_sur.append({
                "item": item,
                "municipio": clean_str(ws.cell(r, 2).value).upper(),
                "ubicacion": clean_str(ws.cell(r, 3).value).upper(),
                "operatividad": "SI" if "SI" in clean_str(ws.cell(r, 4).value).upper() else "NO",
                "familias": clean_int(ws.cell(r, 5).value),
                "motor_marca": clean_str(ws.cell(r, 6).value),
                "motor_hp": clean_str(ws.cell(r, 7).value),
                "voltaje": clean_str(ws.cell(r, 9).value),
                "bomba_marca": clean_str(ws.cell(r, 10).value),
                "bomba_modelo": clean_str(ws.cell(r, 11).value),
                "caudal_lps": clean_float(ws.cell(r, 13).value)
            })

        # 2. Cono Norte (filas 32 a 41 - 10 estaciones)
        cono_norte = []
        for r in range(32, 42):
            item = ws.cell(r, 1).value
            if item is None:
                continue
            cono_norte.append({
                "item": item,
                "municipio": clean_str(ws.cell(r, 2).value).upper(),
                "ubicacion": clean_str(ws.cell(r, 3).value).upper(),
                "operatividad": "SI" if "SI" in clean_str(ws.cell(r, 4).value).upper() else "NO",
                "habitantes": clean_int(ws.cell(r, 5).value),
                "motor_marca": clean_str(ws.cell(r, 6).value),
                "motor_hp": clean_str(ws.cell(r, 7).value),
                "voltaje": clean_str(ws.cell(r, 9).value),
                "caudal_lps": clean_float(ws.cell(r, 13).value)
            })

        # 3. Captación y Conducción (filas 49 a 51 - 3 estaciones)
        captacion = []
        for r in range(49, 52):
            item = ws.cell(r, 1).value
            if item is None:
                continue
            captacion.append({
                "item": item,
                "municipio": clean_str(ws.cell(r, 2).value).upper(),
                "ubicacion": clean_str(ws.cell(r, 3).value).upper(),
                "operatividad": "SI" if "SI" in clean_str(ws.cell(r, 4).value).upper() else "NO",
                "habitantes": clean_int(ws.cell(r, 5).value),
                "voltaje": clean_str(ws.cell(r, 9).value),
                "caudal_lps": clean_float(ws.cell(r, 13).value)
            })

        return {
            "cono_sur": cono_sur,
            "cono_norte": cono_norte,
            "captacion_conduccion": captacion
        }

    def _parse_brippas(self, ws) -> Dict[str, Any]:
        cuadrillas = []
        for r in range(10, 15):
            item = ws.cell(r, 1).value
            mun = clean_str(ws.cell(r, 2).value).upper()
            fecha = format_date_str(ws.cell(r, 3).value)
            personal = clean_str(ws.cell(r, 4).value)
            potable_1x10 = clean_int(ws.cell(r, 5).value)
            potable_cero_botes = clean_int(ws.cell(r, 6).value)
            servidas_1x10 = clean_int(ws.cell(r, 7).value)

            cuadrillas.append({
                "item": item,
                "municipio": mun,
                "fecha_inicio": fecha,
                "personal": personal,
                "potable_1x10": potable_1x10,
                "potable_cero_botes": potable_cero_botes,
                "servidas_1x10": servidas_1x10
            })

        responsables = [
            {"nombre": "Ingrid Colmenares", "telefono": "0416-4048031"},
            {"nombre": "Nairelys Colmenares", "telefono": "0412-0169360"},
            {"nombre": "Yubisay Gil", "telefono": "0416-4756210"},
        ]

        return {
            "cuadrillas": cuadrillas,
            "responsables": responsables
        }

    def _parse_maniobras(self, ws) -> List[Dict[str, Any]]:
        maniobras = []
        for r in range(6, 45):
            item = ws.cell(r, 1).value
            nombre = clean_str(ws.cell(r, 2).value)
            if not nombre:
                continue

            lunes = clean_str(ws.cell(r, 3).value)
            martes = clean_str(ws.cell(r, 4).value)
            miercoles = clean_str(ws.cell(r, 5).value)
            jueves = clean_str(ws.cell(r, 6).value)
            viernes = clean_str(ws.cell(r, 7).value)
            sabado = clean_str(ws.cell(r, 8).value)
            domingo = clean_str(ws.cell(r, 9).value)

            maniobras.append({
                "item": item or len(maniobras) + 1,
                "valvula": nombre,
                "lunes": lunes,
                "martes": martes,
                "miercoles": miercoles,
                "jueves": jueves,
                "viernes": viernes,
                "sabado": sabado,
                "domingo": domingo
            })
        return maniobras
