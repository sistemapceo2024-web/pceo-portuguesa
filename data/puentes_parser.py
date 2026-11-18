"""
Lector y Procesador Oficial del Plan de Recuperación y Construcción de Puentes y Alcantarillas (.xlsx)
Puesto de Comando Estratégico Operacional del Estado Portuguesa (PCEO)
Archivo Oficial: ACUMULADOS PUENTES Y ALCANTARILLAS 23-24-25-26.xlsx
"""
import os
import re
import openpyxl
from datetime import datetime
from typing import Dict, List, Any, Optional

def clean_str(val: Any) -> str:
    if val is None:
        return ""
    return str(val).strip()

def clean_float(val: Any, default: Optional[float] = None) -> Optional[float]:
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

def normalize_mun_name(raw: str) -> str:
    """Extrae y normaliza el nombre del municipio eliminando sufijos de año (2023, 2024, etc.)."""
    if not raw:
        return "Portuguesa"
    s = re.sub(r'202[3-6]', '', raw).strip().upper()
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
    return s.title()

class PuentesParser:
    """Lector inteligente del consolidado de Puentes, Alcantarillas y Cajones de Paso."""

    def __init__(self, file_path: str = "ACUMULADOS PUENTES Y ALCANTARILLAS 23-24-25-26.xlsx"):
        self.file_path = file_path

    def parse_all(self) -> Dict[str, Any]:
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Archivo Excel no encontrado: {self.file_path}")

        wb = openpyxl.load_workbook(self.file_path, data_only=True)

        # 1. Recopilar banco de memorias técnicas de todas las pestañas detalladas
        memos_banco = self._extract_technical_memos(wb)

        # 2. Cargar listado general acumulado (hoja 'LISTADO  ACUMUL X INICIO')
        obras = self._parse_listado_acumulado(wb, memos_banco)

        # 3. Calcular estadísticas consolidadas estadales, por municipio y anuales
        totales = self._calculate_totals(obras)
        por_municipio = self._calculate_by_municipality(obras)
        por_año = self._calculate_by_year(obras)

        # 4. Frentes prioritarios (obras en desarrollo y paralizadas)
        frentes_prioritarios = [o for o in obras if o["estatus"] in ["EN DESARROLLO", "PARALIZADO"]]

        return {
            "archivo": os.path.basename(self.file_path),
            "fecha_carga": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "totales_estatales": totales,
            "obras": obras,
            "por_municipio": por_municipio,
            "por_año": por_año,
            "frentes_prioritarios": frentes_prioritarios
        }

    def _extract_technical_memos(self, wb: openpyxl.Workbook) -> List[Dict[str, Any]]:
        """Extrae todas las memorias descriptivas técnicas de las pestañas anuales."""
        memos = []
        target_sheets = [
            'PUENTES 2026', 'ALCANTARILLA 2026', 'RESUMEN 2026 P,A,C',
            'PUENTES 2025', 'ALCANTARILLA 2025', 'CAJON DE PASO 2025', 'RESUMEN 2025 P,A,C ',
            'PUENTE 2024', 'ALCANTARILLA 2024', 'RESUMEN 2024 P,A,C',
            'PUENTES 2023', 'ALCANTARILLAS X MUNCP 2023', 'CAJONES X MUNCP 2023', 'RESUMEN 2023 P,A,C'
        ]

        keywords = [
            'CONCRETO', 'ACERO', 'TUBERIA', 'TUBERÍA', 'MAQUINARIA', 'INGENIERO',
            'ACTIVIDADES', 'EXCAVACION', 'EXCAVACIÓN', 'RELLENO', 'BOLSACRETO',
            'DESCRIPCION', 'DESCRIPCIÓN', 'OBSERVACIONES', 'PERSONAL', 'RESIDENTE'
        ]

        for s in target_sheets:
            if s not in wb.sheetnames:
                continue
            ws = wb[s]
            for r in range(1, ws.max_row + 1):
                for c in range(1, ws.max_column + 1):
                    val = clean_str(ws.cell(r, c).value)
                    if len(val) >= 70 and any(kw in val.upper() for kw in keywords):
                        # Extraer textos de toda la fila para cruce
                        row_texts = [clean_str(ws.cell(r, col).value) for col in range(1, ws.max_column + 1)]
                        memos.append({
                            "sheet": s,
                            "row": r,
                            "memo": val,
                            "context": " | ".join(t for t in row_texts if t and t != val)
                        })
        return memos

    def _find_matching_memo(self, obra_title: str, mun: str, memos_banco: List[Dict[str, Any]]) -> Optional[str]:
        """Busca la memoria técnica más afín por coincidencia de palabras clave y municipio."""
        if not obra_title:
            return None

        # Limpiar palabras irrelevantes
        stop_words = {'PLAN', 'DE', 'RECUPERACIÓN', 'RECUPERACION', 'Y', 'CONSTRUCCIÓN', 'CONSTRUCCION', 'EN', 'EL', 'LA', 'LOS', 'LAS', 'DEL', 'POR', 'SOBRE', 'SECTOR', 'ESTADO', 'PORTUGUESA', 'MUNICIPIO'}
        words = [w for w in re.split(r'\W+', obra_title.upper()) if len(w) >= 4 and w not in stop_words]

        best_memo = None
        best_score = 0

        for item in memos_banco:
            memo_txt = item["memo"].upper()
            ctx_txt = item["context"].upper()
            score = 0

            # Coincidencia de municipio suma puntos
            if mun.upper() in ctx_txt or mun.upper() in memo_txt:
                score += 2

            # Coincidencia de palabras clave de la obra
            for w in words[:6]:
                if w in memo_txt:
                    score += 3
                elif w in ctx_txt:
                    score += 2

            if score > best_score and score >= 5:
                best_score = score
                best_memo = item["memo"]

        return best_memo

    def _parse_listado_acumulado(self, wb: openpyxl.Workbook, memos_banco: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Lee las 154 obras de la hoja 'LISTADO  ACUMUL X INICIO' (filas 21 a 177)."""
        if "LISTADO  ACUMUL X INICIO" not in wb.sheetnames:
            return []

        ws = wb["LISTADO  ACUMUL X INICIO"]
        obras = []

        for r in range(21, ws.max_row + 1):
            c1 = ws.cell(r, 1).value
            if not isinstance(c1, int):
                continue

            orden = int(c1)
            item_n = clean_int(ws.cell(r, 2).value, default=1)
            nombre = clean_str(ws.cell(r, 3).value).replace("\n", " ").strip()
            mun_raw = clean_str(ws.cell(r, 6).value)
            municipio = normalize_mun_name(mun_raw)

            # Determinación oficial del año según el rango de orden y texto de municipio
            if orden <= 86:
                year = "2023"
            elif orden <= 98:
                year = "2024"
            elif orden <= 132:
                year = "2025"
            else:
                year = "2026"

            fechas = clean_str(ws.cell(r, 7).value).replace("\n", " ").strip()
            if not fechas:
                fechas = f"Año {year}"

            raw_avance = ws.cell(r, 8).value
            est_raw = clean_str(ws.cell(r, 10).value).upper()
            obra_raw = clean_str(ws.cell(r, 9).value).upper()

            # Tipo de Obra
            if "PUENTE" in obra_raw:
                tipo_obra = "PUENTE"
            elif "ALCANTARILLA" in obra_raw:
                tipo_obra = "ALCANTARILLA"
            elif "CAJON" in obra_raw or "CAJÓN" in obra_raw:
                tipo_obra = "CAJON"
            else:
                tipo_obra = "PUENTE"

            # Avance y Estatus con Regla Oficial de Limpieza:
            # Si avance es 1.0 (100%), es EJECUTADO sin importar texto residual de año anterior
            if raw_avance == 1 or raw_avance == 1.0 or raw_avance == "1":
                estatus = "EJECUTADO"
                avance_val = 1.0
                pct_avance = 100
            elif "PARALIZ" in est_raw or "SUSPEND" in est_raw:
                estatus = "PARALIZADO"
                avance_val = clean_float(raw_avance, default=0.50)
                pct_avance = int(round((avance_val or 0.50) * 100))
            else:
                estatus = "EN DESARROLLO"
                avance_val = clean_float(raw_avance, default=0.75)
                pct_avance = int(round((avance_val or 0.75) * 100))

            # Memoria Técnica
            memoria = self._find_matching_memo(nombre, municipio, memos_banco)

            obras.append({
                "id": orden,
                "orden": orden,
                "items": item_n,
                "nombre": nombre,
                "municipio_raw": mun_raw,
                "municipio": municipio,
                "year": year,
                "fechas": fechas,
                "avance": avance_val,
                "pct_avance": pct_avance,
                "tipo_obra": tipo_obra,
                "estatus": estatus,
                "memoria_tecnica": memoria,
                "notas_inspeccion": ""
            })

        return obras

    def _calculate_totals(self, obras: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula los totales estadales oficiales."""
        tot = len(obras)
        ejec = sum(1 for o in obras if o["estatus"] == "EJECUTADO")
        desarr = sum(1 for o in obras if o["estatus"] == "EN DESARROLLO")
        paral = sum(1 for o in obras if o["estatus"] == "PARALIZADO")

        puentes = sum(1 for o in obras if o["tipo_obra"] == "PUENTE")
        alcant = sum(1 for o in obras if o["tipo_obra"] == "ALCANTARILLA")
        cajones = sum(1 for o in obras if o["tipo_obra"] == "CAJON")

        pct_ejec = round((ejec / tot) * 100, 1) if tot > 0 else 0.0

        return {
            "total_obras": tot,               # 154
            "ejecutadas": ejec,               # 145
            "en_desarrollo": desarr,          # 5
            "paralizadas": paral,             # 4
            "puentes": puentes,               # 78
            "alcantarillas": alcant,          # 66
            "cajones": cajones,               # 10
            "pct_ejecutado": pct_ejec         # 94.2%
        }

    def _calculate_by_municipality(self, obras: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Agrupa las obras por municipio."""
        resumen = {}
        for o in obras:
            m = o["municipio"]
            if m not in resumen:
                resumen[m] = {
                    "municipio": m,
                    "total": 0,
                    "puentes": 0,
                    "alcantarillas": 0,
                    "cajones": 0,
                    "ejecutadas": 0,
                    "en_desarrollo": 0,
                    "paralizadas": 0,
                    "obras": []
                }
            r = resumen[m]
            r["total"] += 1
            if o["tipo_obra"] == "PUENTE":
                r["puentes"] += 1
            elif o["tipo_obra"] == "ALCANTARILLA":
                r["alcantarillas"] += 1
            elif o["tipo_obra"] == "CAJON":
                r["cajones"] += 1

            if o["estatus"] == "EJECUTADO":
                r["ejecutadas"] += 1
            elif o["estatus"] == "EN DESARROLLO":
                r["en_desarrollo"] += 1
            elif o["estatus"] == "PARALIZADO":
                r["paralizadas"] += 1
            r["obras"].append(o)

        return resumen

    def _calculate_by_year(self, obras: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Agrupa las obras por año (2023, 2024, 2025, 2026)."""
        years = ["2023", "2024", "2025", "2026"]
        anual = {}
        for y in years:
            y_obras = [o for o in obras if o["year"] == y]
            tot = len(y_obras)
            ejec = sum(1 for o in y_obras if o["estatus"] == "EJECUTADO")
            desarr = sum(1 for o in y_obras if o["estatus"] == "EN DESARROLLO")
            paral = sum(1 for o in y_obras if o["estatus"] == "PARALIZADO")
            puentes = sum(1 for o in y_obras if o["tipo_obra"] == "PUENTE")
            alcant = sum(1 for o in y_obras if o["tipo_obra"] == "ALCANTARILLA")
            cajones = sum(1 for o in y_obras if o["tipo_obra"] == "CAJON")

            anual[y] = {
                "year": y,
                "total": tot,
                "ejecutadas": ejec,
                "en_desarrollo": desarr,
                "paralizadas": paral,
                "puentes": puentes,
                "alcantarillas": alcant,
                "cajones": cajones,
                "pct_ejecutado": round((ejec / tot) * 100, 1) if tot > 0 else 0.0
            }
        return anual
