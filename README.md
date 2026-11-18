# Sistema Integrado de Seguimiento Operativo (SIGSO)
### Secretaría Superior de Operaciones Generales • Gobernación del Estado Portuguesa

Aplicación móvil moderna desarrollada en **Python** con **Flet (Material Design 3)**, diseñada para el monitoreo estratégico, fiscalización y seguimiento de las operaciones y planes de gobierno prioritarios en los 14 municipios de Portuguesa.

---

## 🎨 Identidad Visual y Estética Institucional
- **Fondo:** Blanco y gris muy claro (`#F4F6F9` / `#FFFFFF`).
- **Encabezados e Identidad:** Azul Marino Profundo (`#0A192F` / `#0F284E`).
- **Acentos de Interacción:** Azul Eléctrico (`#0066FF`).
- **Semáforos de Estado Normativos:**
  - 🟢 **Verde:** Operativo / Ejecutado (`#16A34A`).
  - 🟠 **Ámbar:** En Ejecución / Por Inaugurar (`#D97706`).
  - 🔴 **Rojo:** Inoperativo / Paralizado (`#DC2626`).

---

## 🏗️ Arquitectura Modular del Proyecto (12 Planes Independientes)

```text
ANTIGRAVITY/
├── components/
│   ├── theme.py                 # Paleta institucional, tipografía y reglas de semáforos
│   ├── header.py                # Barra institucional superior con credenciales y cambio de rol
│   ├── kpi_card.py              # Tarjetas KPI para planes de gobierno y métricas dinámicas
│   ├── semaphore.py             # Pastillas e indicadores visuales de semáforo
│   ├── municipality_filter.py   # Selector desplegable de los 14 municipios de Portuguesa
│   └── action_dialogs.py        # Modales de actualización y bitácora técnica de campo
├── data/
│   ├── models.py                # Modelos de datos (Planes, Pozos, Plantas, Rebombeo, Perforaciones, Reportes)
│   ├── state.py                 # Gestor reactivo de estado con recálculo dinámico de KPIs
│   ├── government_plans.py      # Catálogo oficial de los 12 planes estratégicos de gobierno
│   ├── water_data.py            # Inventario hídrico estadal (535 pozos, 3 plantas, 27 rebombeos, 34 perforaciones)
│   ├── cero_botes_data.py       # Cero Botes (17.120 botes, 3.707,16 Lps, 320.298.624 L/día, 760.492 hab)
│   └── plans_data.py            # Tramos Caídos (877 tramos, 37.048 m) y Ruta del Hidrojet (501.393 m, 5.266 bocas)
├── modules/
│   ├── login.py                 # Pantalla de Login con selector de roles de prueba
│   ├── executive_summary.py     # Resumen Ejecutivo con las 12 tarjetas de planes independientes
│   ├── fiesta_agua.py           # 1. Fiesta del Agua
│   ├── cero_botes.py            # 2. Plan Cero Botes de Agua
│   ├── tramos_caidos.py         # 3. Tramos Caídos (877 tramos, tabla 8" a 36")
│   ├── ruta_hidrojet.py         # 4. Ruta del Hidrojet (501.393 m liberados, 5.266 bocas)
│   ├── fiesta_luz.py            # 5. Fiesta de la Luz (42.500 LED, 185 transformadores)
│   ├── puentes.py               # 6. Recuperación de Puentes (16 puentes, 48 km dragado)
│   ├── cero_hueco.py            # 7. Plan Cero Hueco (38.400 Ton asfalto, Troncal 05)
│   ├── vialidad.py              # 8. Vialidad Rural y Urbana (1.450 km caminos agrícolas)
│   ├── salud.py                 # 9. Espacios de Salud (45 centros de salud recuperados)
│   ├── canchas.py               # 10. Una Cancha para Todos (78 canchas techadas)
│   ├── educacion.py             # 11. Centros Educativos (62 escuelas remodeladas)
│   └── construye_casa.py        # 12. Plan Construye Tu Casa (1.250 viviendas, 820 kits)
├── test_app.py                  # Pruebas automatizadas de lógica y consistencia de datos (10 suites)
├── main.py                      # Punto de entrada de la aplicación y enrutador Flet
└── README.md                    # Documentación técnica
```

---

## 🚀 Implementación de la Fase 1

### 1. Pantalla de Login Institucional
- Selector de roles de prueba interactivo:
  - **Equipo Técnico (Editor):** Concede acceso a actualizar estatus de pozos, registrar reportes y bitácoras de campo.
  - **Despacho Gobernador (Solo Lectura):** Modo de supervisión estratégica. Oculta de forma estricta cualquier botón o disparador de edición.
- Botón de ingreso con navegación directa al Resumen Ejecutivo.

### 2. Resumen Ejecutivo (8 Planes de Gobierno)
Tarjetas KPI con métricas, porcentaje de avance, semáforos e iconos Material Design 3:
1. **Fiesta del Agua** *(Módulo detallado interactivo)*: 535 Pozos (87% Op), 24 Rebombeos, 3 Plantas.
2. **Plan Cero Botes de Agua** *(Módulo detallado interactivo)*: 17.120 Botes Reparados, 3.707,16 Lts/Seg, 760.492 Beneficiarios.
3. **Ruta del Hidrojet:** 142 Colectores Saneados, 385 Bocas de Visita, 92 Comunidades.
4. **Fiesta de la Luz:** 42,500 Luminarias LED, 185 Transformadores, 94% Avenidas Iluminadas.
5. **Plan Cero Hueco:** 38,400 Ton Asfalto, 120 km Troncal 05, 14 Municipios Impactados.
6. **Puentes y Canalización:** 16 Puentes Reparados, 48 km Dragado de Ríos, 12 Dragas en Sitio.
7. **Construye Tu Casa:** 1,250 Casas Culminadas, 820 Kits Entregados, 34 Urbanismos Activos.
8. **Salud / Educación / Canchas:** 45 Centros de Salud, 62 Escuelas Recuperadas, 78 Canchas Techadas.

### 3. Módulo Detallado: Plan Cero Botes de Agua
- **4 Tarjetas KPI Superiores (Cifras Oficiales Exactas):**
  - **Botes Reparados:** 17.120
  - **Caudal Lts/Seg:** 3.707,16 L/s
  - **Caudal Lts/Día:** 320.298.624 L/día (calculado automáticamente como `Lts/Seg * 86.400`)
  - **Beneficiarios:** 760.492 personas protegidas
- **Barra de Doble Filtro:**
  - **Municipio:** Todos los 14 municipios + cada municipio individual.
  - **Año:** Acumulado Total, 2026, 2025, 2024, 2023, 2022, 2021.
- **Datos Reales por Municipio:**
  - Páez: 5.888 botes / 800,49 Lps / 147.294 personas
  - Guanare: 3.707 botes / 1.492,35 Lps / 212.207 personas
  - Araure: 3.318 botes / 554,31 Lps / 192.146 personas
  - Turén: 1.316 botes / 277,11 Lps / 40.831 personas
  - San Rafael de Onoto: 1.119 botes / 141,27 Lps / 25.318 personas
  - Resto de municipios: Esteller, Ospino, Sucre, Guanarito, San Genaro de Boconoíto, Unda, Santa Rosalía, Papelón y Agua Blanca.
- **Acción Técnica de Campo (Modo Editor):**
  - Botón `+ Registrar Reparación de Bote`: el técnico ingresa Municipio, Año, Cantidad de Botes, Caudal (Lts/Seg) y Beneficiarios.
  - Al guardar: calcula en tiempo real el Caudal Lts/Día (`Lts/Seg * 86400`) y actualiza instantáneamente tanto las tarjetas KPI, las tablas detalladas, como la tarjeta del Resumen Ejecutivo.
  - En **Solo Lectura**, el botón de registro está completamente oculto.

### 3. Módulo Detallado: Fiesta del Agua
- **KPIs Superiores Calculados Dinámicamente:**
  - Total Pozos: **535**
  - Operativos: **463 (87%)**
  - Inoperativos: **72 (13%)**
  - Plantas Potabilizadoras: **2 op / 1 inop** (Camburito y Virgen de Coromoto operativas; Boconoíto inoperativa en mantenimiento)
  - Estaciones de Rebombeo: **24 op / 3 inop** (24 operativas; Morador, San Rafael Casco y El Playón en reparación)
- **Filtro de los 14 Municipios de Portuguesa:**
  - *Guanare, Araure, Páez, Turén, Esteller, Ospino, Sucre, Unda, Guanarito, Papelón, San Genaro de Boconoíto, San Rafael de Onoto, Santa Rosalía, Agua Blanca* (más "Todos los Municipios").
  - Al seleccionar un municipio, todos los KPIs superiores y las listas internas se recalculan automáticamente en tiempo real.
- **Pestañas Internas:**
  - **Operatividad por Municipio:** Cuadrícula de rendimiento por municipio y listado de pozos con ficha técnica (caudal LPS, motor HP, beneficiarios, fecha y notas).
  - **Nuevas Perforaciones (34):** Las 34 obras de perforación profunda con contratista, profundidad, caudal estimado, progreso (%) y semáforo.
  - **Plantas y Rebombeo:** Estado de las plantas potabilizadoras y las estaciones de bombeo de la red primaria y secundaria.
- **Control de Permisos por Rol:**
  - En rol **'Equipo Técnico (Editor)'**: Aparecen los botones *"Actualizar Estatus de Pozo"* y *"Registrar Nuevo Reporte"*, además de la acción *"Actualizar Estatus"* en cada pozo. Los cambios impactan los contadores en memoria inmediatamente.
  - En rol **'Despacho Gobernador (Solo Lectura)'**: Se suprimen y ocultan completamente todos los controles de edición, mostrando una barra institucional de consulta ejecutiva.

---

## 💻 Instrucciones para Ejecutar

```bash
# Ejecutar aplicación móvil Flet
python main.py

# O alternativamente con la CLI de Flet
flet run main.py

# Ejecutar batería de pruebas unitarias
python test_app.py
```
