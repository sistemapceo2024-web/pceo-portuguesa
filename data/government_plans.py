"""
Catálogo Oficial de los 12 Planes Independientes de Gobierno
Secretaría Superior de Operaciones Generales - Gobernación del Estado Portuguesa
"""
from typing import List
from data.models import GovernmentPlan

GOVERNMENT_PLANS: List[GovernmentPlan] = [
    # 1. Fiesta del Agua
    GovernmentPlan(
        id="fiesta_agua",
        title="Fiesta del Agua",
        subtitle="Plan Maestro de Pozos, Rebombeo y Potabilización",
        icon_name="water_drop_rounded",
        status_label="Operativo / Ejecutado",
        main_metric="535 Pozos (87% Op)",
        secondary_metric="24 Rebombeos Activos",
        tertiary_metric="3 Plantas Centrales",
        progress=0.87,
        description="Rehabilitación electromecánica, aforo de fuentes subterráneas y distribución continua de agua en los 14 municipios.",
        is_interactive=True
    ),
    # 2. Plan Cero Botes de Agua
    GovernmentPlan(
        id="cero_botes",
        title="Plan Cero Botes de Agua",
        subtitle="Corrección Integral de Fugas y Recuperación Hídrica",
        icon_name="plumbing_rounded",
        status_label="Operativo / Ejecutado",
        main_metric="17.142 Botes",
        secondary_metric="3.708,63 Lts/Seg",
        tertiary_metric="760.672 Beneficiarios",
        progress=0.94,
        description="Atención prioritaria y despliegue técnico para eliminar botes de agua potable y recuperar caudal en los 14 municipios.",
        is_interactive=True
    ),
    # 3. Tramos Caídos
    GovernmentPlan(
        id="tramos_caidos",
        title="Tramos Caídos",
        subtitle="Reconstrucción y Sustitución de Colectores Caídos",
        icon_name="engineering_rounded",
        status_label="En Ejecución / Por Inaugurar",
        main_metric="885 Tramos (632 Ejec)",
        secondary_metric="37.074 m Sustituidos",
        tertiary_metric="19.160 m Pendientes",
        progress=0.714,
        description="Sustitución de colectores colapsados con tubería de alta densidad de 6\" a 42\" pulgadas en comunidades priorizadas.",
        is_interactive=True
    ),
    # 4. Ruta del Hidrojet
    GovernmentPlan(
        id="ruta_hidrojet",
        title="Ruta del Hidrojet",
        subtitle="Desobstrucción y Saneamiento con Camiones Vacuum",
        icon_name="cleaning_services_rounded",
        status_label="Operativo / Ejecutado",
        main_metric="502.018,20 m",
        secondary_metric="5.280 Bocas de Visita",
        tertiary_metric="603.606 Beneficiarios",
        progress=0.92,
        description="Mantenimiento preventivo y correctivo con camiones desobstructores tipo Vacuum e Hidrojet en 1.655 sectores.",
        is_interactive=True
    ),
    # 5. Fiesta de la Luz
    GovernmentPlan(
        id="fiesta_luz",
        title="Plan Fiesta de la Luz",
        subtitle="Alumbrado Público y Recuperación de Transformadores",
        icon_name="lightbulb_rounded",
        status_label="Operativo / Ejecutado",
        main_metric="150.233 Luminarias",
        secondary_metric="6.113 Apagados • 3.444 TX Inst.",
        tertiary_metric="75 TX Fallados",
        progress=0.95,
        description="Plan integral de modernización de alumbrado público LED, sustitución de luminarias y atención de transformadores.",
        is_interactive=True
    ),
    # 6. Recuperación de Puentes
    GovernmentPlan(
        id="puentes",
        title="Plan Puentes y Alcantarillas",
        subtitle="Recuperación y Construcción de Infraestructura Vial",
        icon_name="waves_rounded",
        status_label="Operativo / Ejecutado",
        main_metric="154 Obras",
        secondary_metric="78 Puentes • 66 Alcantarillas",
        tertiary_metric="10 Cajones • 145 Ejecutadas",
        progress=0.94,
        description="Plan maestro de rehabilitación y construcción de puentes, alcantarillas y cajones de paso en los 14 municipios.",
        is_interactive=True
    ),
    # 7. Plan Cero Huecos
    GovernmentPlan(
        id="cero_huecos",
        title="Plan Cero Huecos",
        subtitle="Rehabilitación Asfáltica, Bacheo y Pavimentación",
        icon_name="traffic_rounded",
        status_label="En Ejecución",
        main_metric="206.142,90 Ton Asfalto",
        secondary_metric="3.383,41 km Rehabilitados",
        tertiary_metric="342.563 Fallas Corregidas",
        progress=0.94,
        description="Colocación de asfalto caliente, bacheo continuo y demarcación en las principales arterias viales de Portuguesa.",
        is_interactive=True
    ),
    # 8. Vialidad Rural y Urbana
    GovernmentPlan(
        id="vialidad",
        title="Vialidad Rural y Urbana",
        subtitle="Caminos de Penetración Agrícola y Conectividad",
        icon_name="alt_route_rounded",
        status_label="Operativo / Ejecutado",
        main_metric="1.450 km Caminos",
        secondary_metric="65 Maquinarias Activas",
        tertiary_metric="320 Caseríos Conectados",
        progress=0.84,
        description="Conformación, engranzonado y mantenimiento de vías rurales para garantizar la salida de cosechas agrícolas.",
        is_interactive=True
    ),
    # 9. Espacios de Salud
    GovernmentPlan(
        id="salud",
        title="Espacios de Salud",
        subtitle="Plan de Recuperación y Rehabilitación de la Red Hospitalaria",
        icon_name="local_hospital_rounded",
        status_label="Operativo / Ejecutado",
        main_metric="113 Centros Rehab.",
        secondary_metric="113 Culminadas • 17 En Proceso",
        tertiary_metric="4 Paralizadas (134 Obras)",
        progress=0.843,
        description="Rehabilitación integral, climatización, dotación médica y modernización de Hospitales, CDI, SRI, CPT y Farmacias en los 14 municipios.",
        is_interactive=True
    ),
    # 10. Una Cancha para Todos
    GovernmentPlan(
        id="canchas",
        title="Una Cancha para Todos",
        subtitle="Infraestructura Deportiva y Espacios Comunitarios",
        icon_name="sports_basketball_rounded",
        status_label="Operativo / Ejecutado",
        main_metric="135 Intervenidas",
        secondary_metric="122 Culminadas",
        tertiary_metric="4 En Ejecución • 9 Paralizadas",
        progress=0.904,
        description="Construcción y recuperación de canchas techadas con pintura epóxica, tableros de acrílico e iluminación LED.",
        is_interactive=True
    ),
    # 11. Centros Educativos
    GovernmentPlan(
        id="educacion",
        title="Centros Educativos",
        subtitle="Rehabilitación de Escuelas, Simoncitos y Liceos",
        icon_name="school_rounded",
        status_label="Operativo / Ejecutado",
        main_metric="259 Centros",
        secondary_metric="241 Ejecutados • 16 En Ejecución",
        tertiary_metric="2 Paralizados",
        progress=0.931,
        description="Mantenimiento integral de cubiertas de techo, pintura general, baterías sanitarias y dotación de mobiliario escolar.",
        is_interactive=True
    ),
    # 12. Plan Construye Tu Casa
    GovernmentPlan(
        id="construye_casa",
        title="Plan Construye Tu Casa",
        subtitle="Autoconstrucción Comunitaria y Soluciones Habitacionales (FONDEREVI)",
        icon_name="home_rounded",
        status_label="Operativo / En Ejecución",
        main_metric="662 Viviendas",
        secondary_metric="252 Ejecutadas",
        tertiary_metric="410 Proyección y Ejecución",
        progress=0.381,
        description="Construcción comunitaria de viviendas dignas, urbanismos consolidados y autoconstrucción asistida con FONDEREVI.",
        is_interactive=True
    ),
    # 13. Canalización y Construcción de Bermas
    GovernmentPlan(
        id="canalizacion",
        title="Canalización y Bermas",
        subtitle="Plan de Canalización de Ríos, Quebradas y Bermas Fluviales",
        icon_name="water_rounded",
        status_label="Operativo / Ejecutado",
        main_metric="380.73 Km Canalizados",
        secondary_metric="243 Obras Ejecutadas",
        tertiary_metric="57 Bermas Construidas",
        progress=0.996,
        description="Canalización de cauces fluviales, desobstrucción de quebradas y construcción de muros de berma en puntos críticos.",
        is_interactive=True
    ),
]
