"""
Modelos de Datos para la Secretaría Superior de Operaciones Generales
"""
from dataclasses import dataclass, field
from typing import List, Optional
import datetime

ROLE_MASTER = "MASTER"
ROLE_ANALISTA = "ANALISTA"
ROLE_EJECUTIVO = "EJECUTIVO"

# Compatibilidad histórica
ROLE_EDITOR = "ANALISTA"
ROLE_VIEWER = "EJECUTIVO"

@dataclass
class GovernmentPlan:
    id: str
    title: str
    subtitle: str
    icon_name: str
    status_label: str       # 'Operativo', 'En Ejecución', 'Inoperativo'
    main_metric: str        # e.g., '535 Pozos (87%)'
    secondary_metric: str   # e.g., '27 Estaciones Rebombeo'
    tertiary_metric: str    # e.g., '3 Plantas Potabilizadoras'
    progress: float         # 0.0 to 1.0
    description: str
    is_interactive: bool = False

@dataclass
class WellRecord:
    id: str
    code: str
    name: str
    municipality: str
    parish: str
    sector: str
    status: str             # 'Operativo', 'Inoperativo', 'En Mantenimiento'
    flow_lps: float         # Litros por segundo
    depth_m: float          # Profundidad en metros
    hp_motor: int           # Caballos de fuerza motor
    beneficiaries: int      # Habitantes beneficiados
    last_service_date: str
    technician_notes: str = ""

@dataclass
class FacilityRecord:
    id: str
    name: str
    facility_type: str      # 'Planta Potabilizadora' o 'Estación de Rebombeo'
    municipality: str
    location: str
    status: str             # 'Operativo' o 'Inoperativo'
    capacity_lps: float
    pumps_operating: int
    pumps_total: int
    failure_reason: Optional[str] = None
    action_plan: Optional[str] = None

@dataclass
class DrillingProject:
    id: str
    code: str
    name: str
    municipality: str
    sector: str
    status: str             # 'Ejecutado / Inaugurado', 'En Perforación', 'Equipamiento Eléctrico'
    progress: int           # 0 - 100 %
    estimated_lps: float
    depth_m: float
    contractor: str
    estimated_delivery: str

@dataclass
class ReportLog:
    id: str
    timestamp: str
    author: str
    role: str
    item_type: str          # 'Pozo', 'Planta', 'Rebombeo', 'Perforación'
    item_name: str
    municipality: str
    action: str
    notes: str
