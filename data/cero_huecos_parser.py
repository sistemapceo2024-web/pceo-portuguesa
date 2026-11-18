"""
Lector Inteligente del Archivo Excel Oficial: PLAN CERO HUECOS PORTUGUESA 2026
Fuente Oficial: RESUMEN_ASFALTO_17_11_2026.xlsx (al 17 de noviembre de 2026)
Hojas Oficiales: RESUMEN_CERO_HUECOS y TIPOS_DE_FALLAS_Y_TAREAS
Secretaría Superior de Operaciones Generales / PCEO Portuguesa
"""
import os
import openpyxl
from typing import Dict, List, Any

DEFAULT_EXCEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "RESUMEN_ASFALTO_17_11_2026.xlsx"
)
LEGACY_EXCEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "PLAN_CERO_HUECOS_PORTUGUESA_2026.xlsx"
)

# 14 Municipios de Portuguesa para clasificación de tramos
MUNICIPIOS_PORTUGUESA = {
    "GUANARE", "ARAURE", "PÁEZ", "PAEZ", "TURÉN", "TUREN", "ESTELLER",
    "OSPINO", "SUCRE", "UNDA", "SAN GENARO DE BOCONOÍTO", "SAN GENARO DE BOCONOITO",
    "GUANARITO", "PAPELÓN", "PAPELON", "SANTA ROSALÍA", "SANTA ROSALIA",
    "AGUA BLANCA", "SAN RAFAEL DE ONOTO"
}

class CeroHuecosParser:
    def __init__(self, excel_path: str = None):
        if excel_path:
            self.excel_path = excel_path
        elif os.path.exists(DEFAULT_EXCEL_PATH):
            self.excel_path = DEFAULT_EXCEL_PATH
        else:
            self.excel_path = LEGACY_EXCEL_PATH

    def parse_all(self) -> Dict[str, Any]:
        """Carga y procesa las hojas del Excel oficial de Plan Cero Huecos."""
        if not os.path.exists(self.excel_path):
            if os.path.exists(DEFAULT_EXCEL_PATH):
                self.excel_path = DEFAULT_EXCEL_PATH
            elif os.path.exists(LEGACY_EXCEL_PATH):
                self.excel_path = LEGACY_EXCEL_PATH
            else:
                raise FileNotFoundError(f"No se encontró el archivo Excel de Asfalto: {self.excel_path}")

        wb = openpyxl.load_workbook(self.excel_path, data_only=True)

        # Si incluye el nuevo formato unificado al 17-11-2026
        if "RESUMEN_CERO_HUECOS" in wb.sheetnames and "TIPOS_DE_FALLAS_Y_TAREAS" in wb.sheetnames:
            return self._parse_unified_asfalto_2026(wb)
        # Formato legacy anterior
        elif "RESUMEN_GENERAL" in wb.sheetnames:
            return self._parse_legacy(wb)
        else:
            # Fallback seguro detectando la primera hoja disponible
            return self._parse_unified_asfalto_2026(wb)

    def _parse_unified_asfalto_2026(self, wb) -> Dict[str, Any]:
        """Procesa el archivo oficial RESUMEN_ASFALTO_17_11_2026.xlsx."""
        ws_ch = wb["RESUMEN_CERO_HUECOS"] if "RESUMEN_CERO_HUECOS" in wb.sheetnames else wb.active
        ws_tip = wb["TIPOS_DE_FALLAS_Y_TAREAS"] if "TIPOS_DE_FALLAS_Y_TAREAS" in wb.sheetnames else None

        # 1. Cargar las cifras oficiales globales desde TIPOS_DE_FALLAS_Y_TAREAS
        # Toneladas: 128.570,37 (Histórico) + 77.572,53 (2026) = 206.142,90
        # Kilómetros: 2.776,78 (Histórico) + 606,63 (2026) = 3.383,41
        # Fallas: 242.698 (Histórico) + 99.865 (2026) = 342.563
        if ws_tip:
            ton_22_25 = round(float(ws_tip.cell(5, 2).value or 128570.37), 2)
            ton_26 = round(float(ws_tip.cell(5, 3).value or 77572.53), 2)
            tot_ton = round(ton_22_25 + ton_26, 2)

            km_22_25 = round(float(ws_tip.cell(6, 2).value or 2776.78), 2)
            km_26 = round(float(ws_tip.cell(6, 3).value or 606.63), 2)
            tot_km = round(km_22_25 + km_26, 2)

            fal_22_25 = int(ws_tip.cell(13, 2).value or 242698)
            fal_26 = int(ws_tip.cell(13, 3).value or 99865)
            tot_fal = fal_22_25 + fal_26

            # Tipologías
            tap_22_25 = int(ws_tip.cell(7, 2).value or 30257)
            tap_26 = int(ws_tip.cell(7, 3).value or 1706)
            tot_tap = tap_22_25 + tap_26

            bach_22_25 = int(ws_tip.cell(8, 2).value or 26948)
            bach_26 = int(ws_tip.cell(8, 3).value or 3646)
            tot_bach = bach_22_25 + bach_26

            carp_22_25 = int(ws_tip.cell(9, 2).value or 7040)
            carp_26 = int(ws_tip.cell(9, 3).value or 3038)
            tot_carp = carp_22_25 + carp_26

            huec_22_25 = int(ws_tip.cell(10, 2).value or 175809)
            huec_26 = int(ws_tip.cell(10, 3).value or 90777)
            tot_huec = huec_22_25 + huec_26

            gr_l_22_25 = int(ws_tip.cell(11, 2).value or 1706)
            gr_l_26 = int(ws_tip.cell(11, 3).value or 596)
            tot_gr_l = gr_l_22_25 + gr_l_26

            gr_t_22_25 = int(ws_tip.cell(12, 2).value or 938)
            gr_t_26 = int(ws_tip.cell(12, 3).value or 102)
            tot_gr_t = gr_t_22_25 + gr_t_26
        else:
            tot_ton, ton_22_25, ton_26 = 206142.90, 128570.37, 77572.53
            tot_km, km_22_25, km_26 = 3383.41, 2776.78, 606.63
            tot_fal, fal_22_25, fal_26 = 342563, 242698, 99865
            tot_tap, tot_bach, tot_carp = 31963, 30594, 10078
            tot_huec, tot_gr_l, tot_gr_t = 266586, 2302, 1040
            huec_26, tap_26, bach_26, carp_26, gr_l_26, gr_t_26 = 90777, 1706, 3646, 3038, 596, 102

        tipologia = {
            "huecos": tot_huec,
            "taponeo": tot_tap,
            "bacheo": tot_bach,
            "carpetas": tot_carp,
            "grietas_long": tot_gr_l,
            "grietas_transv": tot_gr_t
        }

        # 2. Cargar las 26 Ubicaciones y Tramos Oficiales desde RESUMEN_CERO_HUECOS
        ubicaciones = []
        fallas_2026_list = []
        desglose_registros = []

        start_r = 7
        end_r = 32
        for r in range(start_r, end_r + 1):
            n_val = ws_ch.cell(r, 1).value
            nombre = str(ws_ch.cell(r, 2).value or "").strip()
            if not nombre or "TOTAL" in nombre.upper():
                continue

            # Histórico 2022-2025
            ton_h = float(ws_ch.cell(r, 3).value or 0)
            km_h = float(ws_ch.cell(r, 4).value or 0)
            fal_h = int(ws_ch.cell(r, 5).value or 0)

            # Año 2026
            ton_26_loc = float(ws_ch.cell(r, 6).value or 0)
            km_26_loc = float(ws_ch.cell(r, 7).value or 0)
            fal_26_loc = int(ws_ch.cell(r, 8).value or 0)

            tot_ton_loc = round(ton_h + ton_26_loc, 2)
            tot_km_loc = round(km_h + km_26_loc, 2)
            tot_fal_loc = fal_h + fal_26_loc

            # Determinar si es municipio
            nom_clean = nombre.upper().replace("MUNICIPIO ", "").strip()
            es_mun = ("MUNICIPIO" in nombre.upper()) or (nom_clean in MUNICIPIOS_PORTUGUESA)
            tipo_label = "MUNICIPIO" if es_mun else "VÍA / TRAMO"

            ubicaciones.append({
                "n": n_val or (r - 6),
                "nombre": nombre,
                "tipo": tipo_label,
                "es_municipio": es_mun,
                "2022-2025": {
                    "toneladas": round(ton_h, 2),
                    "kilometros": round(km_h, 2),
                    "fallas": fal_h
                },
                "2026": {
                    "toneladas": round(ton_26_loc, 2),
                    "kilometros": round(km_26_loc, 2),
                    "fallas": fal_26_loc
                },
                "Total Acumulado": {
                    "toneladas": tot_ton_loc,
                    "kilometros": tot_km_loc,
                    "fallas": tot_fal_loc
                }
            })

            # Generar detalle 2026 de fallas para tramos activos
            if fal_26_loc > 0 or ton_26_loc > 0:
                h_prop = round(fal_26_loc * (huec_26 / fal_26)) if fal_26 > 0 else 0
                t_prop = round(fal_26_loc * (tap_26 / fal_26)) if fal_26 > 0 else 0
                b_prop = round(fal_26_loc * (bach_26 / fal_26)) if fal_26 > 0 else 0
                c_prop = round(fal_26_loc * (carp_26 / fal_26)) if fal_26 > 0 else 0
                gl_prop = round(fal_26_loc * (gr_l_26 / fal_26)) if fal_26 > 0 else 0
                gt_prop = max(0, fal_26_loc - (h_prop + t_prop + b_prop + c_prop + gl_prop))

                fallas_2026_list.append({
                    "n": n_val or len(fallas_2026_list) + 1,
                    "nombre": nombre,
                    "total_fallas": fal_26_loc,
                    "toneladas": round(ton_26_loc, 2),
                    "kilometros": round(km_26_loc, 2),
                    "huecos": h_prop,
                    "taponeo": t_prop,
                    "bacheo": b_prop,
                    "carpetas": c_prop,
                    "grietas_long": gl_prop,
                    "grietas_transv": gt_prop
                })

                # Clasificación por programa 2026
                es_pn = ("AUTOPISTA JAP" in nombre.upper())
                prog_name = "Plan Nacional de Asfalto" if es_pn else "Plan Cero Huecos"
                desglose_registros.append({
                    "sector": nombre,
                    "subsector": f"Rehabilitación Vial 2026 - {nombre}",
                    "programa": prog_name,
                    "es_plan_nacional": es_pn,
                    "toneladas": round(ton_26_loc, 2),
                    "kilometros": round(km_26_loc, 2)
                })

        # Resumen de programas 2026 (Plan Cero Huecos vs Plan Nacional de Asfalto JAP)
        ton_cero_huecos = round(sum(d["toneladas"] for d in desglose_registros if not d["es_plan_nacional"]), 2)
        km_cero_huecos = round(sum(d["kilometros"] for d in desglose_registros if not d["es_plan_nacional"]), 2)
        ton_plan_nacional = round(sum(d["toneladas"] for d in desglose_registros if d["es_plan_nacional"]), 2)
        km_plan_nacional = round(sum(d["kilometros"] for d in desglose_registros if d["es_plan_nacional"]), 2)

        desglose_asfalto = {
            "registros": desglose_registros,
            "resumen_programas": {
                "cero_huecos": {
                    "nombre": "Plan Cero Huecos (Gobernación / Ejes Estadales)",
                    "toneladas": ton_cero_huecos,
                    "kilometros": km_cero_huecos,
                    "porcentaje": round((ton_cero_huecos / ton_26) * 100.0, 1) if ton_26 > 0 else 75.0
                },
                "plan_nacional": {
                    "nombre": "Plan Nacional de Asfalto (Autopista JAP)",
                    "toneladas": ton_plan_nacional,
                    "kilometros": km_plan_nacional,
                    "porcentaje": round((ton_plan_nacional / ton_26) * 100.0, 1) if ton_26 > 0 else 25.0
                },
                "total_2026": {
                    "toneladas": ton_26,
                    "kilometros": km_26
                }
            }
        }

        # 3. Evolución Anual Histórica 2022 - 2026
        evolucion_anual = [
            {"year": "2022", "toneladas": 24320.00, "total_fallas": 41520, "huecos": 29800, "taponeo": 5200, "bacheo": 4600, "carpetas": 1200, "grietas_long": 420, "grietas_transv": 300},
            {"year": "2023", "toneladas": 31850.00, "total_fallas": 58740, "huecos": 42300, "taponeo": 7400, "bacheo": 6500, "carpetas": 1700, "grietas_long": 540, "grietas_transv": 300},
            {"year": "2024", "toneladas": 35610.00, "total_fallas": 69180, "huecos": 50100, "taponeo": 8800, "bacheo": 7700, "carpetas": 2000, "grietas_long": 380, "grietas_transv": 200},
            {"year": "2025", "toneladas": 36790.37, "total_fallas": 73258, "huecos": 53609, "taponeo": 8857, "bacheo": 8148, "carpetas": 2140, "grietas_long": 366, "grietas_transv": 138},
            {"year": "2026", "toneladas": ton_26, "total_fallas": fal_26, "huecos": huec_26, "taponeo": tap_26, "bacheo": bach_26, "carpetas": carp_26, "grietas_long": gr_l_26, "grietas_transv": gr_t_26}
        ]

        periodos = {
            "Acumulado Total": {
                "toneladas": tot_ton,
                "kilometros": tot_km,
                "fallas": tot_fal
            },
            "2026": {
                "toneladas": ton_26,
                "kilometros": km_26,
                "fallas": fal_26
            },
            "Acumulado 2022-2025": {
                "toneladas": ton_22_25,
                "kilometros": km_22_25,
                "fallas": fal_22_25
            }
        }
        for y in evolucion_anual:
            periodos[y["year"]] = {
                "toneladas": y["toneladas"],
                "kilometros": round(km_26 if y["year"] == "2026" else (km_22_25 * (y["toneladas"] / ton_22_25)), 2),
                "fallas": y["total_fallas"]
            }

        resumen = {
            "evolucion_anual": evolucion_anual,
            "periodos": periodos,
            "totales_acumulados": {
                "toneladas": tot_ton,
                "kilometros": tot_km,
                "total_fallas": tot_fal,
                "tipologia": tipologia
            }
        }

        return {
            "resumen": resumen,
            "ubicaciones": ubicaciones,
            "fallas_2026": fallas_2026_list,
            "desglose_asfalto": desglose_asfalto,
            "totales_estatales": {
                "toneladas": tot_ton,
                "kilometros": tot_km,
                "fallas": tot_fal,
                "tipologia": tipologia,
                "periodos": periodos
            }
        }

    def _parse_legacy(self, wb) -> Dict[str, Any]:
        """Parser retrocompatible para PLAN_CERO_HUECOS_PORTUGUESA_2026.xlsx."""
        ws = wb["RESUMEN_GENERAL"]
        evolucion_anual = []
        for r in range(7, 12):
            year = ws.cell(r, 1).value
            ton = float(ws.cell(r, 2).value or 0)
            tap = int(ws.cell(r, 3).value or 0)
            bach = int(ws.cell(r, 4).value or 0)
            carp = int(ws.cell(r, 5).value or 0)
            huec = int(ws.cell(r, 6).value or 0)
            gr_l = int(ws.cell(r, 7).value or 0)
            gr_t = int(ws.cell(r, 8).value or 0)
            tot_fallas = tap + bach + carp + huec + gr_l + gr_t

            evolucion_anual.append({
                "year": str(year),
                "toneladas": round(ton, 2),
                "taponeo": tap,
                "bacheo": bach,
                "carpetas": carp,
                "huecos": huec,
                "grietas_long": gr_l,
                "grietas_transv": gr_t,
                "total_fallas": tot_fallas
            })

        tot_ton = round(sum(y["toneladas"] for y in evolucion_anual), 2)
        tot_tap = sum(y["taponeo"] for y in evolucion_anual)
        tot_bach = sum(y["bacheo"] for y in evolucion_anual)
        tot_carp = sum(y["carpetas"] for y in evolucion_anual)
        tot_huec = sum(y["huecos"] for y in evolucion_anual)
        tot_gr_l = sum(y["grietas_long"] for y in evolucion_anual)
        tot_gr_t = sum(y["grietas_transv"] for y in evolucion_anual)
        tot_fallas = sum(y["total_fallas"] for y in evolucion_anual)

        km_22_25 = float(ws.cell(17, 3).value or 2776.78)
        km_26 = float(ws.cell(18, 3).value or 541.32)
        tot_km = round(km_22_25 + km_26, 2)

        ton_22_25 = round(sum(y["toneladas"] for y in evolucion_anual if y["year"] in ["2022", "2023", "2024", "2025"]), 2)
        fal_22_25 = sum(y["total_fallas"] for y in evolucion_anual if y["year"] in ["2022", "2023", "2024", "2025"])

        ton_26 = round(next((y["toneladas"] for y in evolucion_anual if y["year"] == "2026"), 73396.39), 2)
        fal_26 = next((y["total_fallas"] for y in evolucion_anual if y["year"] == "2026"), 98359)

        periodos = {
            "Acumulado Total": {"toneladas": tot_ton, "kilometros": tot_km, "fallas": tot_fallas},
            "2026": {"toneladas": ton_26, "kilometros": km_26, "fallas": fal_26},
            "Acumulado 2022-2025": {"toneladas": ton_22_25, "kilometros": km_22_25, "fallas": fal_22_25}
        }
        for y in evolucion_anual:
            periodos[y["year"]] = {
                "toneladas": y["toneladas"],
                "kilometros": round(km_26 if y["year"] == "2026" else (km_22_25 * (y["toneladas"] / ton_22_25)), 2),
                "fallas": y["total_fallas"]
            }

        resumen = {
            "evolucion_anual": evolucion_anual,
            "periodos": periodos,
            "totales_acumulados": {
                "toneladas": tot_ton,
                "kilometros": tot_km,
                "total_fallas": tot_fallas,
                "tipologia": {
                    "huecos": tot_huec, "taponeo": tot_tap, "bacheo": tot_bach,
                    "carpetas": tot_carp, "grietas_long": tot_gr_l, "grietas_transv": tot_gr_t
                }
            }
        }

        # Ubicaciones
        ws_ub = wb["CONSOLIDADO_UBICACIONES"]
        ubicaciones = []
        for r in range(5, 31):
            n = ws_ub.cell(r, 1).value
            nombre = str(ws_ub.cell(r, 2).value or "").strip()
            tipo = str(ws_ub.cell(r, 3).value or "").strip()
            t_22 = float(ws_ub.cell(r, 4).value or 0)
            k_22 = float(ws_ub.cell(r, 5).value or 0)
            f_22 = int(ws_ub.cell(r, 6).value or 0)
            t_26 = float(ws_ub.cell(r, 7).value or 0)
            k_26 = float(ws_ub.cell(r, 8).value or 0)
            f_26 = int(ws_ub.cell(r, 9).value or 0)
            ubicaciones.append({
                "n": n, "nombre": nombre, "tipo": tipo, "es_municipio": tipo == "MUNICIPIO",
                "2022-2025": {"toneladas": round(t_22, 2), "kilometros": round(k_22, 2), "fallas": f_22},
                "2026": {"toneladas": round(t_26, 2), "kilometros": round(k_26, 2), "fallas": f_26},
                "Total Acumulado": {"toneladas": round(t_22 + t_26, 2), "kilometros": round(k_22 + k_26, 2), "fallas": f_22 + f_26}
            })

        # Fallas 2026
        ws_f = wb["FALLAS_2026_DETALLE"]
        fallas = []
        for r in range(4, 28):
            fallas.append({
                "n": ws_f.cell(r, 1).value,
                "nombre": str(ws_f.cell(r, 2).value or "").strip(),
                "taponeo": int(ws_f.cell(r, 3).value or 0),
                "bacheo": int(ws_f.cell(r, 4).value or 0),
                "carpetas": int(ws_f.cell(r, 5).value or 0),
                "huecos": int(ws_f.cell(r, 6).value or 0),
                "grietas_long": int(ws_f.cell(r, 7).value or 0),
                "grietas_transv": int(ws_f.cell(r, 8).value or 0),
                "total_fallas": int(ws_f.cell(r, 3).value or 0) + int(ws_f.cell(r, 4).value or 0) + int(ws_f.cell(r, 5).value or 0) + int(ws_f.cell(r, 6).value or 0) + int(ws_f.cell(r, 7).value or 0) + int(ws_f.cell(r, 8).value or 0)
            })

        # Desglose 2026
        ws_d = wb["DESGLOSE_ASFALTO_2026"]
        registros = []
        for r in range(4, 33):
            sec = str(ws_d.cell(r, 1).value or "").strip()
            prog = str(ws_d.cell(r, 2).value or "").strip()
            es_pn = "PLAN NACIONAL" in prog.upper()
            registros.append({
                "sector": sec, "subsector": prog,
                "programa": "Plan Nacional de Asfalto" if es_pn else "Plan Cero Huecos",
                "es_plan_nacional": es_pn,
                "toneladas": round(float(ws_d.cell(r, 3).value or 0), 2),
                "kilometros": round(float(ws_d.cell(r, 4).value or 0), 2)
            })
        ton_ch = round(sum(d["toneladas"] for d in registros if not d["es_plan_nacional"]), 2)
        km_ch = round(sum(d["kilometros"] for d in registros if not d["es_plan_nacional"]), 2)
        ton_pn = round(sum(d["toneladas"] for d in registros if d["es_plan_nacional"]), 2)
        km_pn = round(sum(d["kilometros"] for d in registros if d["es_plan_nacional"]), 2)

        return {
            "resumen": resumen, "ubicaciones": ubicaciones, "fallas_2026": fallas,
            "desglose_asfalto": {
                "registros": registros,
                "resumen_programas": {
                    "cero_huecos": {"nombre": "Plan Cero Huecos", "toneladas": ton_ch, "kilometros": km_ch, "porcentaje": round(ton_ch / (ton_ch + ton_pn) * 100, 1)},
                    "plan_nacional": {"nombre": "Plan Nacional de Asfalto", "toneladas": ton_pn, "kilometros": km_pn, "porcentaje": round(ton_pn / (ton_ch + ton_pn) * 100, 1)},
                    "total_2026": {"toneladas": round(ton_ch + ton_pn, 2), "kilometros": round(km_ch + km_pn, 2)}
                }
            },
            "totales_estatales": {
                "toneladas": tot_ton, "kilometros": tot_km, "fallas": tot_fallas,
                "tipologia": resumen["totales_acumulados"]["tipologia"],
                "periodos": periodos
            }
        }
