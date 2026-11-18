"""
Lector y Procesador Oficial del Plan Fiesta de la Luz (.xlsx)
Puesto de Comando Estratégico Operacional del Estado Portuguesa (PCEO)
Archivo Oficial: PLAN_FIESTA_DE_LA_LUZ_PORTUGUESA_2026.xlsx
"""
import os
import openpyxl
from datetime import datetime
from typing import Dict, List, Any, Optional

def clean_str(val: Any) -> str:
    if val is None:
        return ""
    return str(val).strip()

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

def normalize_mun_name(raw: str) -> str:
    """Normaliza nombres de municipios de Portuguesa a sus 14 nombres oficiales con tildes."""
    if not raw:
        return ""
    s = raw.strip().upper()
    if "AGUA BLAN" in s:
        return "Agua Blanca"
    if "ARAURE" in s:
        return "Araure"
    if "ESTELLER" in s:
        return "Esteller"
    if "GUANARITO" in s:
        return "Guanarito"
    if "GUANARE" in s:
        return "Guanare"
    if "OSPINO" in s:
        return "Ospino"
    if "PAEZ" in s or "PÁEZ" in s:
        return "Páez"
    if "PAPELON" in s or "PAPELÓN" in s:
        return "Papelón"
    if "BOCONO" in s or "SAN GENARO" in s:
        return "San Genaro de Boconoíto"
    if "ONOTO" in s or "SAN RAFAEL" in s:
        return "San Rafael de Onoto"
    if "ROSALIA" in s or "ROSALÍA" in s:
        return "Santa Rosalía"
    if "SUCRE" in s:
        return "Sucre"
    if "TUREN" in s or "TURÉN" in s:
        return "Turén"
    if "UNDA" in s:
        return "Unda"
    return raw.strip().title()

class FiestaLuzParser:
    """Lector inteligente del archivo Excel oficial del Plan Fiesta de la Luz."""

    def __init__(self, file_path: str = "PLAN_FIESTA_DE_LA_LUZ_PORTUGUESA_2026.xlsx"):
        self.file_path = file_path

    def parse_all(self) -> Dict[str, Any]:
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Archivo Excel no encontrado: {self.file_path}")

        wb = openpyxl.load_workbook(self.file_path, data_only=True)

        resumen_data = self._parse_resumen_ejecutivo(wb)
        luminarias_data = self._parse_luminarias_municipio(wb)
        puntos_resumen = self._parse_puntos_apagados_resumen(wb)
        puntos_detalle = self._parse_puntos_apagados_detalle(wb)
        tx_municipio_data = self._parse_tx_instalados_municipio(wb)
        tx_2026_detalle = self._parse_tx_instalados_2026_detalle(wb)
        tx_fallados_detalle = self._parse_tx_fallados_detalle(wb)

        # Totales consolidados estadales
        totales = resumen_data.get("totales_estatales", {})

        return {
            "archivo": os.path.basename(self.file_path),
            "fecha_carga": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "totales_estatales": totales,
            "municipios_resumen": resumen_data.get("municipios", {}),
            "luminarias_historico": luminarias_data,
            "puntos_apagados_resumen": puntos_resumen,
            "puntos_apagados_detalle": puntos_detalle,
            "tx_instalados_historico": tx_municipio_data.get("historico", {}),
            "tx_capacidades_estatal": tx_municipio_data.get("capacidades_kva", {}),
            "tx_instalados_2026_detalle": tx_2026_detalle,
            "tx_fallados_detalle": tx_fallados_detalle
        }

    def _parse_resumen_ejecutivo(self, wb: openpyxl.Workbook) -> Dict[str, Any]:
        """Lee la hoja RESUMEN_EJECUTIVO (filas 6 a 19 para los 14 municipios)."""
        if "RESUMEN_EJECUTIVO" not in wb.sheetnames:
            return {"totales_estatales": {}, "municipios": {}}

        ws = wb["RESUMEN_EJECUTIVO"]
        municipios = {}

        tot_lum = 0
        tot_apag = 0
        tot_tx_inst = 0
        tot_tx_corp = 0
        tot_tx_gob = 0
        tot_tx_fall = 0
        tot_tx_fall_c = 0
        tot_tx_fall_s = 0
        tot_sectores = 0
        tot_ben_lum = 0
        tot_ben_tx = 0

        for r in range(6, 20):
            raw_m = ws.cell(r, 2).value
            if not raw_m:
                continue
            mun = normalize_mun_name(str(raw_m))
            lum = clean_int(ws.cell(r, 3).value)
            apag = clean_int(ws.cell(r, 4).value)
            tx_tot = clean_int(ws.cell(r, 5).value)
            tx_corp = clean_int(ws.cell(r, 6).value)
            tx_gob = clean_int(ws.cell(r, 7).value)
            tx_fall = clean_int(ws.cell(r, 8).value)
            tx_fall_c = clean_int(ws.cell(r, 9).value)
            tx_fall_s = clean_int(ws.cell(r, 10).value)
            sectores = clean_int(ws.cell(r, 11).value)
            ben_lum = clean_int(ws.cell(r, 12).value)
            ben_tx = clean_int(ws.cell(r, 13).value)

            tot_lum += lum
            tot_apag += apag
            tot_tx_inst += tx_tot
            tot_tx_corp += tx_corp
            tot_tx_gob += tx_gob
            tot_tx_fall += tx_fall
            tot_tx_fall_c += tx_fall_c
            tot_tx_fall_s += tx_fall_s
            tot_sectores += sectores
            tot_ben_lum += ben_lum
            tot_ben_tx += ben_tx

            municipios[mun] = {
                "municipio": mun,
                "luminarias": lum,
                "puntos_apagados": apag,
                "tx_instalados": tx_tot,
                "tx_corpoelec": tx_corp,
                "tx_gobernacion": tx_gob,
                "tx_fallados": tx_fall,
                "tx_fallados_con_codigo": tx_fall_c,
                "tx_fallados_sin_codigo": tx_fall_s,
                "sectores": sectores,
                "beneficiarios_luminarias": ben_lum,
                "beneficiarios_tx": ben_tx
            }

        totales = {
            "luminarias": tot_lum,               # 150.233
            "puntos_apagados": tot_apag,          # 6.113
            "tx_instalados": tot_tx_inst,         # 3.444
            "tx_corpoelec": tot_tx_corp,          # 2.012
            "tx_gobernacion": tot_tx_gob,        # 1.432
            "tx_fallados": tot_tx_fall,           # 75
            "tx_fallados_con_codigo": tot_tx_fall_c, # 35
            "tx_fallados_sin_codigo": tot_tx_fall_s, # 40
            "sectores": tot_sectores,             # 3.080
            "beneficiarios_luminarias": tot_ben_lum, # 882.154
            "beneficiarios_tx": tot_ben_tx,       # 451.985
            "beneficiarios_totales": tot_ben_lum
        }

        return {"totales_estatales": totales, "municipios": municipios}

    def _parse_luminarias_municipio(self, wb: openpyxl.Workbook) -> Dict[str, Any]:
        """Lee LUMINARIAS_MUNICIPIO (filas 4 a 17) con desglose anual Gob/Alc y Corpoelec."""
        if "LUMINARIAS_MUNICIPIO" not in wb.sheetnames:
            return {}

        ws = wb["LUMINARIAS_MUNICIPIO"]
        municipios_lum = {}
        gob_anual = {"2022": 0, "2023": 0, "2024": 0, "2025": 0, "2026": 0}
        corp_anual = {"2023": 0, "2024": 0}

        for r in range(4, 18):
            raw_m = ws.cell(r, 2).value
            if not raw_m:
                continue
            mun = normalize_mun_name(str(raw_m))

            g22 = clean_int(ws.cell(r, 3).value)
            g23 = clean_int(ws.cell(r, 4).value)
            g24 = clean_int(ws.cell(r, 5).value)
            g25 = clean_int(ws.cell(r, 6).value)
            g26 = clean_int(ws.cell(r, 7).value)
            sub_gob = g22 + g23 + g24 + g25 + g26

            c23 = clean_int(ws.cell(r, 9).value)
            c24 = clean_int(ws.cell(r, 10).value)
            sub_corp = c23 + c24

            total = sub_gob + sub_corp
            sectores = clean_int(ws.cell(r, 13).value)
            beneficiarios = clean_int(ws.cell(r, 14).value)
            poblacion = clean_int(ws.cell(r, 15).value)

            gob_anual["2022"] += g22
            gob_anual["2023"] += g23
            gob_anual["2024"] += g24
            gob_anual["2025"] += g25
            gob_anual["2026"] += g26

            corp_anual["2023"] += c23
            corp_anual["2024"] += c24

            municipios_lum[mun] = {
                "municipio": mun,
                "gob_alc": {
                    "2022": g22, "2023": g23, "2024": g24, "2025": g25, "2026": g26,
                    "subtotal": sub_gob
                },
                "corpoelec": {
                    "2023": c23, "2024": c24, "subtotal": sub_corp
                },
                "total": total,
                "sectores": sectores,
                "beneficiarios": beneficiarios,
                "poblacion": poblacion
            }

        gob_subtotal = sum(gob_anual.values())
        corp_subtotal = sum(corp_anual.values())
        total_estatal = gob_subtotal + corp_subtotal

        return {
            "estatal": {
                "gob_alc": {**gob_anual, "subtotal": gob_subtotal},
                "corpoelec": {**corp_anual, "subtotal": corp_subtotal},
                "total": total_estatal,
                "pct_gob_alc": round((gob_subtotal / total_estatal) * 100, 1) if total_estatal else 0,
                "pct_corpoelec": round((corp_subtotal / total_estatal) * 100, 1) if total_estatal else 0,
                "totales_por_año": {
                    "2022": gob_anual["2022"],
                    "2023": gob_anual["2023"] + corp_anual["2023"],
                    "2024": gob_anual["2024"] + corp_anual["2024"],
                    "2025": gob_anual["2025"],
                    "2026": gob_anual["2026"],
                    "total": total_estatal
                }
            },
            "por_municipio": municipios_lum
        }

    def _parse_puntos_apagados_resumen(self, wb: openpyxl.Workbook) -> List[Dict[str, Any]]:
        """Lee PUNTOS_APAGADOS_RESUMEN (filas 4 a 17)."""
        if "PUNTOS_APAGADOS_RESUMEN" not in wb.sheetnames:
            return []

        ws = wb["PUNTOS_APAGADOS_RESUMEN"]
        resumen = []
        for r in range(4, 18):
            raw_m = ws.cell(r, 2).value
            if not raw_m:
                continue
            mun = normalize_mun_name(str(raw_m))
            lum = clean_int(ws.cell(r, 3).value)
            bom = clean_int(ws.cell(r, 4).value)
            ref = clean_int(ws.cell(r, 5).value)
            tot = lum + bom + ref
            potencia = clean_str(ws.cell(r, 7).value)
            resumen.append({
                "municipio": mun,
                "luminarias": lum,
                "bombillos": bom,
                "reflectores": ref,
                "total": tot,
                "potencia": potencia,
                "year": 2026
            })
        return resumen

    def _parse_puntos_apagados_detalle(self, wb: openpyxl.Workbook) -> List[Dict[str, Any]]:
        """Lee los 228 sectores detallados en PUNTOS_APAGADOS_DETALLE (filas 4 a 231)."""
        if "PUNTOS_APAGADOS_DETALLE" not in wb.sheetnames:
            return []

        ws = wb["PUNTOS_APAGADOS_DETALLE"]
        detalle = []
        for r in range(4, ws.max_row + 1):
            item_val = ws.cell(r, 1).value
            if item_val is None:
                continue
            mun_raw = clean_str(ws.cell(r, 2).value)
            if not mun_raw:
                continue
            mun = normalize_mun_name(mun_raw)
            sector = clean_str(ws.cell(r, 3).value)
            cantidad = clean_int(ws.cell(r, 4).value)
            potencia = clean_str(ws.cell(r, 5).value)
            observacion = clean_str(ws.cell(r, 6).value)

            detalle.append({
                "item": clean_int(item_val),
                "municipio": mun,
                "sector": sector,
                "cantidad": cantidad,
                "potencia": potencia,
                "observacion": observacion
            })
        return detalle

    def _parse_tx_instalados_municipio(self, wb: openpyxl.Workbook) -> Dict[str, Any]:
        """Lee TX_INSTALADOS_MUNICIPIO (filas 4 a 17) y tabla de KVA (filas 21-22)."""
        if "TX_INSTALADOS_MUNICIPIO" not in wb.sheetnames:
            return {"historico": {}, "capacidades_kva": {}}

        ws = wb["TX_INSTALADOS_MUNICIPIO"]
        historico = {}
        tot_corp_anual = {"2022": 0, "2023": 0, "2024": 0, "2025": 0, "2026": 0}
        tot_gob_anual = {"2022": 0, "2023": 0, "2024": 0, "2025": 0, "2026": 0}

        for r in range(4, 18):
            raw_m = ws.cell(r, 2).value
            if not raw_m:
                continue
            mun = normalize_mun_name(str(raw_m))

            c22, g22 = clean_int(ws.cell(r, 3).value), clean_int(ws.cell(r, 4).value)
            c23, g23 = clean_int(ws.cell(r, 6).value), clean_int(ws.cell(r, 7).value)
            c24, g24 = clean_int(ws.cell(r, 9).value), clean_int(ws.cell(r, 10).value)
            c25, g25 = clean_int(ws.cell(r, 12).value), clean_int(ws.cell(r, 13).value)
            c26, g26 = clean_int(ws.cell(r, 15).value), clean_int(ws.cell(r, 16).value)

            tot_corp = c22 + c23 + c24 + c25 + c26
            tot_gob = g22 + g23 + g24 + g25 + g26
            total_mun = tot_corp + tot_gob
            beneficiarios = clean_int(ws.cell(r, 21).value)

            tot_corp_anual["2022"] += c22
            tot_corp_anual["2023"] += c23
            tot_corp_anual["2024"] += c24
            tot_corp_anual["2025"] += c25
            tot_corp_anual["2026"] += c26

            tot_gob_anual["2022"] += g22
            tot_gob_anual["2023"] += g23
            tot_gob_anual["2024"] += g24
            tot_gob_anual["2025"] += g25
            tot_gob_anual["2026"] += g26

            historico[mun] = {
                "municipio": mun,
                "2022": {"corp": c22, "gob": g22, "tot": c22 + g22},
                "2023": {"corp": c23, "gob": g23, "tot": c23 + g23},
                "2024": {"corp": c24, "gob": g24, "tot": c24 + g24},
                "2025": {"corp": c25, "gob": g25, "tot": c25 + g25},
                "2026": {"corp": c26, "gob": g26, "tot": c26 + g26},
                "total_corpoelec": tot_corp,
                "total_gobernacion": tot_gob,
                "total": total_mun,
                "beneficiarios": beneficiarios
            }

        # Capacidades KVA en filas 21 a 22
        capacidades = {}
        for c in range(2, 10):
            k_label = clean_str(ws.cell(21, c).value)
            k_val = clean_int(ws.cell(22, c).value)
            if k_label:
                capacidades[k_label] = k_val

        tot_estatal_anual = {
            y: {
                "corp": tot_corp_anual[y],
                "gob": tot_gob_anual[y],
                "tot": tot_corp_anual[y] + tot_gob_anual[y]
            }
            for y in ["2022", "2023", "2024", "2025", "2026"]
        }
        tot_estatal_anual["total"] = {
            "corp": sum(tot_corp_anual.values()),
            "gob": sum(tot_gob_anual.values()),
            "tot": sum(tot_corp_anual.values()) + sum(tot_gob_anual.values())
        }

        return {
            "historico": {
                "por_municipio": historico,
                "estatal": tot_estatal_anual
            },
            "capacidades_kva": capacidades
        }

    def _parse_tx_instalados_2026_detalle(self, wb: openpyxl.Workbook) -> List[Dict[str, Any]]:
        """Lee los 843 registros detallados de 2026 en TX_INSTALADOS_2026_DETALLE."""
        if "TX_INSTALADOS_2026_DETALLE" not in wb.sheetnames:
            return []

        ws = wb["TX_INSTALADOS_2026_DETALLE"]
        detalle = []
        for r in range(4, ws.max_row + 1):
            item_val = ws.cell(r, 1).value
            if item_val is None:
                continue
            mun_raw = clean_str(ws.cell(r, 2).value)
            if not mun_raw:
                continue
            mun = normalize_mun_name(mun_raw)
            fecha_val = ws.cell(r, 3).value
            if isinstance(fecha_val, datetime):
                fecha = fecha_val.strftime("%Y-%m-%d")
            else:
                fecha = clean_str(fecha_val)

            cantidad = clean_int(ws.cell(r, 4).value, default=1)
            capacidad = clean_float(ws.cell(r, 5).value)
            tension = clean_str(ws.cell(r, 6).value)
            direccion = clean_str(ws.cell(r, 7).value)
            ente = clean_str(ws.cell(r, 8).value)
            codigo_serial = clean_str(ws.cell(r, 9).value)

            # Clasificación simple de Ente
            ente_cat = "Corpoelec"
            ente_u = ente.upper()
            if "ALCALD" in ente_u:
                ente_cat = "Alcaldía"
            elif "GOBERN" in ente_u:
                ente_cat = "Gobernación"
            elif "COMUNA" in ente_u or "CONSEJO" in ente_u:
                ente_cat = "Poder Popular"

            detalle.append({
                "item": clean_int(item_val),
                "municipio": mun,
                "fecha": fecha,
                "cantidad": cantidad,
                "capacidad_kva": capacidad,
                "tension": tension,
                "direccion_sector": direccion,
                "ente_ejecutor": ente,
                "ente_categoria": ente_cat,
                "codigo_serial": codigo_serial
            })
        return detalle

    def _parse_tx_fallados_detalle(self, wb: openpyxl.Workbook) -> List[Dict[str, Any]]:
        """Lee los 73 registros (75 transformadores fallados) en TX_FALLADOS_DETALLE."""
        if "TX_FALLADOS_DETALLE" not in wb.sheetnames:
            return []

        ws = wb["TX_FALLADOS_DETALLE"]
        fallados = []
        for r in range(4, ws.max_row + 1):
            item_val = ws.cell(r, 1).value
            if item_val is None:
                continue
            estatus_cod = clean_str(ws.cell(r, 2).value).upper()
            if not estatus_cod:
                estatus_cod = "SIN CODIGO"
            codigo_1x10 = clean_str(ws.cell(r, 3).value)
            fecha_val = ws.cell(r, 4).value
            if isinstance(fecha_val, datetime):
                fecha_rep = fecha_val.strftime("%Y-%m-%d")
            else:
                fecha_rep = clean_str(fecha_val)

            mun_raw = clean_str(ws.cell(r, 5).value)
            mun = normalize_mun_name(mun_raw)
            parroquia = clean_str(ws.cell(r, 6).value)
            direccion = clean_str(ws.cell(r, 7).value)
            capacidad = clean_float(ws.cell(r, 8).value)
            tension = clean_str(ws.cell(r, 9).value)
            cantidad = clean_int(ws.cell(r, 10).value, default=1)
            usuario = clean_str(ws.cell(r, 11).value)
            telefono = clean_str(ws.cell(r, 12).value)

            fallados.append({
                "id": f"TXF-{clean_int(item_val)}",
                "item": clean_int(item_val),
                "estatus_codigo": estatus_cod,
                "codigo_1x10": codigo_1x10,
                "fecha_reporte": fecha_rep,
                "municipio": mun,
                "parroquia": parroquia,
                "direccion_sector": direccion,
                "capacidad_kva": capacidad,
                "tension": tension,
                "cantidad": cantidad,
                "usuario_reportante": usuario,
                "telefono": telefono,
                "atendido": False,
                "fecha_instalacion": None,
                "ente_atendio": None
            })
        return fallados
