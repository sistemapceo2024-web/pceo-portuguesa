"""
Lector de Datos Sociopolíticos, Territoriales y Demográficos de los 14 Municipios de Portuguesa
Fuente oficial: MUNICIPIOS_PORTUGUESA_DEMOGRAFIA_TERRITORIO.xlsx
Hoja: TERRITORIO_Y_DEMOGRAFIA
Gobernación del Estado Portuguesa • Puesto de Comando Estratégico Operacional (PCEO)
"""
import os
import re
import unicodedata
import openpyxl

def normalize_mun_name(text: str) -> str:
    """Normaliza texto para comparaciones seguras de nombres de municipios."""
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

class MunicipiosParser:
    """Parser para extraer la ficha técnica territorial y demográfica de los municipios."""

    DEFAULT_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "MUNICIPIOS_PORTUGUESA_DEMOGRAFIA_TERRITORIO.xlsx"
    )

    def __init__(self, excel_path: str = None):
        self.excel_path = excel_path or self.DEFAULT_PATH
        self._cache = None

    def parse_all(self, force_reload: bool = False) -> dict:
        """Lee la hoja TERRITORIO_Y_DEMOGRAFIA y estructura los datos de los 14 municipios."""
        if self._cache and not force_reload:
            return self._cache

        if not os.path.exists(self.excel_path):
            return self._build_empty_fallback()

        try:
            wb = openpyxl.load_workbook(self.excel_path, data_only=True)
            sheet_name = "TERRITORIO_Y_DEMOGRAFIA"
            if sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
            else:
                ws = wb.active

            municipios_list = []
            municipios_by_norm = {}

            # Totales del estado
            totales = {
                "extension_km2": 0.0,
                "parroquias": 0,
                "poblacion_ine": 0,
                "familias_ine": 0,
                "comunas": 0,
                "consejos_comunales": 0,
                "comunidades_rurales": 0,
                "ubch": 0,
                "jefes_clap": 0,
                "jefes_calle": 0,
                "total_municipios": 14
            }

            # Filas 6 a 19 corresponden a los 14 municipios
            for r in range(6, 20):
                row_vals = [cell.value for cell in ws[r]]
                if not row_vals or len(row_vals) < 13:
                    continue

                mun_raw = str(row_vals[1] or "").strip()
                if not mun_raw or "TOTAL" in mun_raw.upper():
                    continue

                cap_raw = str(row_vals[2] or "").strip()
                ext = float(row_vals[3] or 0)
                parr = int(row_vals[4] or 0)
                pob = int(row_vals[5] or 0)
                fam = int(row_vals[6] or 0)
                com = int(row_vals[7] or 0)
                cc = int(row_vals[8] or 0)
                rural = int(row_vals[9] or 0)
                ubch = int(row_vals[10] or 0)
                clap = int(row_vals[11] or 0)
                calle = int(row_vals[12] or 0)

                # Nombres canónicos estilizados
                mun_title = self._format_mun_title(mun_raw)
                cap_title = self._format_capital_title(cap_raw)

                m_dict = {
                    "numero": int(row_vals[0] or (r - 5)),
                    "municipio": mun_title,
                    "municipio_raw": mun_raw,
                    "capital": cap_title,
                    "extension_km2": ext,
                    "parroquias": parr,
                    "poblacion_ine": pob,
                    "familias_ine": fam,
                    "comunas": com,
                    "consejos_comunales": cc,
                    "comunidades_rurales": rural,
                    "ubch": ubch,
                    "jefes_clap": clap,
                    "jefes_calle": calle,
                    # Versiones formateadas para UI y reportes
                    "extension_km2_fmt": format_number_es(ext),
                    "poblacion_ine_fmt": format_number_es(pob),
                    "familias_ine_fmt": format_number_es(fam),
                    "comunas_fmt": format_number_es(com),
                    "consejos_comunales_fmt": format_number_es(cc),
                    "comunidades_rurales_fmt": format_number_es(rural),
                    "ubch_fmt": format_number_es(ubch),
                    "jefes_clap_fmt": format_number_es(clap),
                    "jefes_calle_fmt": format_number_es(calle),
                }

                municipios_list.append(m_dict)

                # Mapeo con nombres normalizados y aliases (ej. "unda" -> "José Vicente de Unda")
                norm_mun = normalize_mun_name(mun_raw)
                norm_title = normalize_mun_name(mun_title)
                municipios_by_norm[norm_mun] = m_dict
                municipios_by_norm[norm_title] = m_dict

                if "unda" in norm_mun:
                    municipios_by_norm["unda"] = m_dict
                    municipios_by_norm["josevicentedeunda"] = m_dict
                if "boconoito" in norm_mun:
                    municipios_by_norm["boconoito"] = m_dict
                    municipios_by_norm["sangenaro"] = m_dict
                    municipios_by_norm["sangenarodeboconoito"] = m_dict
                if "onoto" in norm_mun:
                    municipios_by_norm["onoto"] = m_dict
                    municipios_by_norm["sanrafaeldeonoto"] = m_dict
                if "rosalia" in norm_mun:
                    municipios_by_norm["rosalia"] = m_dict
                    municipios_by_norm["santarosalia"] = m_dict

                # Acumulación de totales del estado
                totales["extension_km2"] += ext
                totales["parroquias"] += parr
                totales["poblacion_ine"] += pob
                totales["familias_ine"] += fam
                totales["comunas"] += com
                totales["consejos_comunales"] += cc
                totales["comunidades_rurales"] += rural
                totales["ubch"] += ubch
                totales["jefes_clap"] += clap
                totales["jefes_calle"] += calle

            # Formatear totales generales
            for k in list(totales.keys()):
                if k != "total_municipios":
                    totales[f"{k}_fmt"] = format_number_es(totales[k])

            result = {
                "municipios": municipios_list,
                "municipios_by_norm": municipios_by_norm,
                "totales_estado": totales
            }
            self._cache = result
            return result

        except Exception as err:
            print(f"[MunicipiosParser Error]: {err}")
            return self._build_empty_fallback()

    def get_municipio(self, mun_name: str) -> dict:
        """Obtiene la ficha técnica completa de un municipio por su nombre o alias."""
        data = self.parse_all()
        if not mun_name:
            return {}

        norm = normalize_mun_name(mun_name)
        by_norm = data.get("municipios_by_norm", {})

        if norm in by_norm:
            return by_norm[norm]

        # Búsqueda difusa por contención
        for k, v in by_norm.items():
            if norm in k or k in norm:
                return v

        return {}

    def get_totales_estado(self) -> dict:
        """Obtiene las cifras territoriales y sociopolíticas consolidadas de Portuguesa."""
        data = self.parse_all()
        return data.get("totales_estado", {})

    def _format_mun_title(self, raw: str) -> str:
        r = raw.strip().upper()
        mapping = {
            "GUANARE": "Guanare",
            "PÁEZ": "Páez",
            "PAEZ": "Páez",
            "ARAURE": "Araure",
            "TURÉN": "Turén",
            "TUREN": "Turén",
            "ESTELLER": "Esteller",
            "OSPINO": "Ospino",
            "SUCRE": "Sucre",
            "JOSÉ VICENTE DE UNDA": "Unda",
            "JOSE VICENTE DE UNDA": "Unda",
            "UNDA": "Unda",
            "SAN GENARO DE BOCONOÍTO": "San Genaro de Boconoíto",
            "SAN GENARO DE BOCONOITO": "San Genaro de Boconoíto",
            "GUANARITO": "Guanarito",
            "SANTA ROSALÍA": "Santa Rosalía",
            "SANTA ROSALIA": "Santa Rosalía",
            "AGUA BLANCA": "Agua Blanca",
            "SAN RAFAEL DE ONOTO": "San Rafael de Onoto",
            "PAPELÓN": "Papelón",
            "PAPELON": "Papelón"
        }
        return mapping.get(r, raw.strip().title())

    def _format_capital_title(self, raw: str) -> str:
        r = raw.strip().upper()
        mapping = {
            "GUANARE": "Guanare",
            "ACARIGUA": "Acarigua",
            "ARAURE": "Araure",
            "VILLA BRUZUAL": "Villa Bruzual",
            "PÍRITU": "Píritu",
            "PIRITU": "Píritu",
            "OSPINO": "Ospino",
            "BISCUCUY": "Biscucuy",
            "PARAÍSO DE CHABASQUÉN": "Paraíso de Chabasquén",
            "PARAISO DE CHABASQUEN": "Paraíso de Chabasquén",
            "BOCONOÍTO": "Boconoíto",
            "BOCONOITO": "Boconoíto",
            "GUANARITO": "Guanarito",
            "EL PLAYÓN": "El Playón",
            "EL PLAYON": "El Playón",
            "AGUA BLANCA": "Agua Blanca",
            "SAN RAFAEL DE ONOTO": "San Rafael de Onoto",
            "PAPELÓN": "Papelón",
            "PAPELON": "Papelón"
        }
        return mapping.get(r, raw.strip().title())

    def _build_empty_fallback(self) -> dict:
        return {
            "municipios": [],
            "municipios_by_norm": {},
            "totales_estado": {
                "extension_km2": 15200.0,
                "parroquias": 41,
                "poblacion_ine": 1070599,
                "familias_ine": 267653,
                "comunas": 192,
                "consejos_comunales": 1916,
                "comunidades_rurales": 1091,
                "ubch": 694,
                "jefes_clap": 1914,
                "jefes_calle": 9515,
                "total_municipios": 14
            }
        }
