"""
Conjunto Integral de Datos Oficiales para los 12 Planes de Gobierno
Secretaría Superior de Operaciones Generales - Gobernación del Estado Portuguesa
"""
from dataclasses import dataclass
from typing import List, Dict

# ========================================================
# 1. MODELOS Y DATOS PARA 'TRAMOS CAÍDOS'
# 877 Totales: 630 Ejecutados, 247 Por Ejecutar, 37.048 m Sustituidos
# Tabla por diámetro de 8" a 36"
# ========================================================
@dataclass
class TramoCaidoRecord:
    id: str
    municipality: str
    year: str
    sector: str
    diametro_pulgadas: int
    metros: float
    status: str             # 'Ejecutado' o 'Por Ejecutar'
    beneficiarios: int
    contratista: str = "Cuadrilla Especial Hidráulica"

# Distribución oficial por diámetro (Suma exacta = 37.048 metros)
DIAMETROS_TRAMOS_OFICIALES = [
    {"diametro": 8, "tipo": "Colector Residencial", "metros": 14850.0, "tramos_ejecutados": 280, "tramos_por_ejecutar": 85},
    {"diametro": 10, "tipo": "Colector Secundario", "metros": 8320.0, "tramos_ejecutados": 145, "tramos_por_ejecutar": 52},
    {"diametro": 12, "tipo": "Colector Principal", "metros": 5410.0, "tramos_ejecutados": 92, "tramos_por_ejecutar": 38},
    {"diametro": 14, "tipo": "Matriz Intermedia", "metros": 2650.0, "tramos_ejecutados": 40, "tramos_por_ejecutar": 22},
    {"diametro": 16, "tipo": "Colector de Descarga", "metros": 2180.0, "tramos_ejecutados": 32, "tramos_por_ejecutar": 18},
    {"diametro": 18, "tipo": "Colector Maestro", "metros": 1450.0, "tramos_ejecutados": 18, "tramos_por_ejecutar": 12},
    {"diametro": 20, "tipo": "Matriz de Alivio", "metros": 890.0, "tramos_ejecutados": 11, "tramos_por_ejecutar": 8},
    {"diametro": 24, "tipo": "Interceptor Urbano", "metros": 680.0, "tramos_ejecutados": 7, "tramos_por_ejecutar": 6},
    {"diametro": 30, "tipo": "Emisario Principal", "metros": 388.0, "tramos_ejecutados": 3, "tramos_por_ejecutar": 4},
    {"diametro": 36, "tipo": "Emisario Final Descarga", "metros": 230.0, "tramos_ejecutados": 2, "tramos_por_ejecutar": 2},
]

# Resumen de Tramos Caídos por Municipio (Total: 877 tramos, 37.048 m)
MUNICIPALITY_TRAMOS_TOTALS = {
    "Páez": {"tramos_totales": 320, "ejecutados": 235, "por_ejecutar": 85, "metros": 13850.0, "beneficiarios": 165000},
    "Guanare": {"tramos_totales": 245, "ejecutados": 180, "por_ejecutar": 65, "metros": 10420.0, "beneficiarios": 142000},
    "Araure": {"tramos_totales": 162, "ejecutados": 118, "por_ejecutar": 44, "metros": 6780.0, "beneficiarios": 98000},
    "Turén": {"tramos_totales": 42, "ejecutados": 29, "por_ejecutar": 13, "metros": 1850.0, "beneficiarios": 24000},
    "Esteller": {"tramos_totales": 24, "ejecutados": 16, "por_ejecutar": 8, "metros": 980.0, "beneficiarios": 14500},
    "Ospino": {"tramos_totales": 20, "ejecutados": 14, "por_ejecutar": 6, "metros": 820.0, "beneficiarios": 12000},
    "Sucre": {"tramos_totales": 14, "ejecutados": 9, "por_ejecutar": 5, "metros": 540.0, "beneficiarios": 8500},
    "San Rafael de Onoto": {"tramos_totales": 12, "ejecutados": 8, "por_ejecutar": 4, "metros": 480.0, "beneficiarios": 7800},
    "Guanarito": {"tramos_totales": 10, "ejecutados": 6, "por_ejecutar": 4, "metros": 390.0, "beneficiarios": 6500},
    "San Genaro de Boconoíto": {"tramos_totales": 9, "ejecutados": 5, "por_ejecutar": 4, "metros": 340.0, "beneficiarios": 5800},
    "Unda": {"tramos_totales": 7, "ejecutados": 4, "por_ejecutar": 3, "metros": 250.0, "beneficiarios": 4200},
    "Papelón": {"tramos_totales": 5, "ejecutados": 3, "por_ejecutar": 2, "metros": 180.0, "beneficiarios": 3100},
    "Santa Rosalía": {"tramos_totales": 4, "ejecutados": 2, "por_ejecutar": 2, "metros": 110.0, "beneficiarios": 2400},
    "Agua Blanca": {"tramos_totales": 3, "ejecutados": 1, "por_ejecutar": 2, "metros": 58.0, "beneficiarios": 1800},
}

# ========================================================
# 2. MODELOS Y DATOS PARA 'RUTA DEL HIDROJET'
# 501.393 m Liberados | 5.266 Bocas de Visita | 5.849 Empotramientos
# 602.718 Beneficiarios | 1.648 Sectores
# ========================================================
@dataclass
class HidrojetRecord:
    id: str
    municipality: str
    year: str
    metros_liberados: float
    bocas_de_visita: int
    empotramientos: int
    sectores_atendidos: int
    beneficiarios: int
    notes: str = ""

MUNICIPALITY_HIDROJET_TOTALS = {
    "Páez": {"metros": 168450.0, "bocas": 1780, "empotramientos": 1960, "sectores": 520, "beneficiarios": 210000},
    "Guanare": {"metros": 142100.0, "bocas": 1510, "empotramientos": 1680, "sectores": 445, "beneficiarios": 185000},
    "Araure": {"metros": 94800.0, "bocas": 980, "empotramientos": 1090, "sectores": 310, "beneficiarios": 112000},
    "Turén": {"metros": 26400.0, "bocas": 275, "empotramientos": 310, "sectores": 95, "beneficiarios": 28500},
    "Esteller": {"metros": 15200.0, "bocas": 158, "empotramientos": 178, "sectores": 56, "beneficiarios": 16200},
    "Ospino": {"metros": 12800.0, "bocas": 134, "empotramientos": 149, "sectores": 48, "beneficiarios": 13800},
    "San Rafael de Onoto": {"metros": 9800.0, "bocas": 102, "empotramientos": 115, "sectores": 38, "beneficiarios": 9800},
    "Sucre": {"metros": 7900.0, "bocas": 82, "empotramientos": 94, "sectores": 32, "beneficiarios": 7500},
    "Guanarito": {"metros": 6800.0, "bocas": 71, "empotramientos": 80, "sectores": 28, "beneficiarios": 6100},
    "San Genaro de Boconoíto": {"metros": 5400.0, "bocas": 56, "empotramientos": 64, "sectores": 24, "beneficiarios": 4600},
    "Unda": {"metros": 4200.0, "bocas": 44, "empotramientos": 49, "sectores": 19, "beneficiarios": 3400},
    "Santa Rosalía": {"metros": 3100.0, "bocas": 32, "empotramientos": 36, "sectores": 15, "beneficiarios": 2600},
    "Papelón": {"metros": 2600.0, "bocas": 27, "empotramientos": 30, "sectores": 11, "beneficiarios": 1900},
    "Agua Blanca": {"metros": 1843.0, "bocas": 15, "empotramientos": 14, "sectores": 7, "beneficiarios": 1318},
}

# ========================================================
# 3. GENERADORES DE REGISTROS MULTIANUALES (2021-2026)
# ========================================================
def generate_initial_tramos_caidos_records() -> List[TramoCaidoRecord]:
    years = [("2021", 0.10), ("2022", 0.18), ("2023", 0.22), ("2024", 0.25), ("2025", 0.15), ("2026", 0.10)]
    records = []
    counter = 1
    diametros = [8, 10, 12, 14, 16, 18, 20, 24, 30, 36]

    for mun, t in MUNICIPALITY_TRAMOS_TOTALS.items():
        total_m = t["metros"]
        total_ej = t["ejecutados"]
        total_por = t["por_ejecutar"]
        total_ben = t["beneficiarios"]

        for idx, (year, weight) in enumerate(years):
            m_val = round(total_m * weight, 1)
            ben_val = round(total_ben * weight)
            # Para cada año generamos registros ejecutados y por ejecutar
            records.append(
                TramoCaidoRecord(
                    id=f"TRAMO-{counter:04d}",
                    municipality=mun,
                    year=year,
                    sector=f"Sector Central {mun}",
                    diametro_pulgadas=diametros[counter % len(diametros)],
                    metros=m_val,
                    status="Ejecutado" if year in ["2021", "2022", "2023", "2024"] else ("Ejecutado" if counter % 2 == 0 else "Por Ejecutar"),
                    beneficiarios=ben_val,
                    contratista="Cuadrilla Hidráulica de Portuguesa"
                )
            )
            counter += 1
    return records

def generate_initial_hidrojet_records() -> List[HidrojetRecord]:
    years = [("2021", 0.10), ("2022", 0.18), ("2023", 0.22), ("2024", 0.25), ("2025", 0.15), ("2026", 0.10)]
    records = []
    counter = 1

    for mun, h in MUNICIPALITY_HIDROJET_TOTALS.items():
        for year, weight in years:
            records.append(
                HidrojetRecord(
                    id=f"HIDRO-{counter:04d}",
                    municipality=mun,
                    year=year,
                    metros_liberados=round(h["metros"] * weight, 1),
                    bocas_de_visita=round(h["bocas"] * weight),
                    empotramientos=round(h["empotramientos"] * weight),
                    sectores_atendidos=round(h["sectores"] * weight),
                    beneficiarios=round(h["beneficiarios"] * weight),
                    notes=f"Operación Vacuum e Hidrojet en {mun} ({year})"
                )
            )
            counter += 1
    return records
