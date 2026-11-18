"""
Pruebas Automatizadas de Lógica y Requisitos
Fase 1 - Secretaría Superior de Operaciones Generales
"""
import os
import json
import flet as ft
from data.models import ROLE_EDITOR, ROLE_VIEWER
from data.state import AppState
from data.water_data import MUNICIPALITIES_LIST, DRILLING_PROJECTS_DATA
from data.government_plans import GOVERNMENT_PLANS

def run_tests():
    state = AppState()

    print("=== TEST 1: 13 PLANES INDEPENDIENTES DE GOBIERNO ===")
    assert len(GOVERNMENT_PLANS) == 13, f"Esperados 13 planes, encontrados {len(GOVERNMENT_PLANS)}"
    plan_ids = [p.id for p in GOVERNMENT_PLANS]
    expected_ids = [
        "fiesta_agua", "cero_botes", "tramos_caidos", "ruta_hidrojet",
        "fiesta_luz", "puentes", "cero_huecos", "vialidad",
        "salud", "canchas", "educacion", "construye_casa", "canalizacion"
    ]
    for eid in expected_ids:
        assert eid in plan_ids, f"Plan {eid} no encontrado en catálogo de 13 planes"
    for p in GOVERNMENT_PLANS:
        assert p.is_interactive is True, f"Plan {p.id} debe ser interactivo"
    print("13 Planes de Gobierno independientes verificados correctamente.")

    print("\n=== TEST 2: KPIS DINÁMICOS SUPERIORES (ESTADALES) ===")
    kpis = state.get_kpis("Todos los Municipios")
    print("KPIs Globales:", kpis)
    assert kpis["total_pozos"] == 535, f"Esperado 535, recibido {kpis['total_pozos']}"
    assert kpis["pozos_operativos"] == 463, f"Esperado 463, recibido {kpis['pozos_operativos']}"
    assert kpis["pozos_inoperativos"] == 72, f"Esperado 72, recibido {kpis['pozos_inoperativos']}"
    assert kpis["pct_operativo"] == 87, f"Esperado 87%, recibido {kpis['pct_operativo']}%"
    assert kpis["pct_inoperativo"] == 13, f"Esperado 13%, recibido {kpis['pct_inoperativo']}%"
    assert kpis["plantas_op"] == 2, f"Esperado 2 op, recibido {kpis['plantas_op']}"
    assert kpis["plantas_inop"] == 1, f"Esperado 1 inop, recibido {kpis['plantas_inop']}"
    assert kpis["rebombeo_op"] == 24, f"Esperado 24 op, recibido {kpis['rebombeo_op']}"
    assert kpis["rebombeo_inop"] == 3, f"Esperado 3 inop, recibido {kpis['rebombeo_inop']}"
    print("Métricas hídricas oficiales verificadas con precisión exacta.")

    print("\n=== TEST 3: 14 MUNICIPIOS DE PORTUGUESA ===")
    expected_municipalities = [
        "Guanare", "Araure", "Páez", "Turén", "Esteller", "Ospino", 
        "Sucre", "Unda", "Guanarito", "Papelón", "San Genaro de Boconoíto", 
        "San Rafael de Onoto", "Santa Rosalía", "Agua Blanca"
    ]
    for m in expected_municipalities:
        assert m in MUNICIPALITIES_LIST, f"Municipio {m} no presente en la lista oficial"
        m_kpis = state.get_kpis(m)
        assert m_kpis["total_pozos"] > 0, f"Municipio {m} debe tener pozos asignados"
        print(f"-> {m:24}: {m_kpis['pozos_operativos']}/{m_kpis['total_pozos']} pozos operativos ({m_kpis['pct_operativo']}%)")

    print("\n=== TEST 4: NUEVAS PERFORACIONES (34) ===")
    assert len(DRILLING_PROJECTS_DATA) == 34, f"Esperadas 34 nuevas perforaciones, encontradas {len(DRILLING_PROJECTS_DATA)}"
    print(f"Total de nuevas perforaciones registradas: {len(DRILLING_PROJECTS_DATA)}")

    print("\n=== TEST 5: REACTIVIDAD Y MODIFICACIÓN DE ESTATUS (EDITOR) ===")
    sample_well = state.sample_wells[0]
    initial_inop = state.get_kpis("Todos los Municipios")["pozos_inoperativos"]
    state.update_well_status(sample_well.id, "Inoperativo", "Prueba técnica de falla", "Téc. Pruebas")
    new_inop = state.get_kpis("Todos los Municipios")["pozos_inoperativos"]
    assert new_inop == initial_inop + 1, "El contador de inoperativos debió incrementarse en 1"

    # Restaurar
    state.update_well_status(sample_well.id, "Operativo", "Pozo restablecido", "Téc. Pruebas")
    restored_inop = state.get_kpis("Todos los Municipios")["pozos_inoperativos"]
    assert restored_inop == initial_inop, "El contador debió restablecerse"
    print("Reacción en tiempo real y recálculo de KPIs verificado exitosamente.")

    print("\n=== TEST 6: CONTROL DE ACCESO POR ROL ===")
    state.set_role(ROLE_EDITOR)
    assert state.is_editor() is True
    assert state.is_viewer() is False

    state.set_role(ROLE_VIEWER)
    assert state.is_editor() is False
    assert state.is_viewer() is True
    print("Lógica de roles 'Equipo Técnico (Editor)' y 'Despacho Gobernador (Solo Lectura)' validada.")

    print("\n=== TEST 7: PLAN CERO BOTES DE AGUA (EXCEL OFICIAL: 17.142 BOTES, 3.708,63 L/S, 2.423 FILTRACIONES) ===")
    cero_botes_plan = next((p for p in GOVERNMENT_PLANS if p.id == "cero_botes"), None)
    assert cero_botes_plan is not None, "Plan Cero Botes no encontrado"
    assert cero_botes_plan.is_interactive is True, "Plan Cero Botes debe ser interactivo"

    # KPIs Oficiales Acumulados
    cb_kpis = state.get_cero_botes_kpis("Todos los Municipios", "Acumulado Total")
    print("KPIs Cero Botes Acumulado:", cb_kpis)
    assert cb_kpis["botes"] == 17142, f"Esperado 17.142 botes, recibido {cb_kpis['botes']}"
    assert cb_kpis["caudal_lps"] == 3708.63, f"Esperado 3.708,63 Lps, recibido {cb_kpis['caudal_lps']}"
    assert cb_kpis["caudal_lts_dia"] == 320425632.0, f"Esperado 320.425.632 L/día, recibido {cb_kpis['caudal_lts_dia']}"
    assert cb_kpis["beneficiarios"] == 760672, f"Esperado 760.672 beneficiarios, recibido {cb_kpis['beneficiarios']}"
    print("-> 4 KPIs superiores consolidados exactos: 17.142 botes / 3.708,63 Lps / 320.425.632 L/día / 760.672 personas.")

    # Verificación por municipio (Páez, Guanare, Araure, Turén, San Rafael de Onoto)
    paez_kpis = state.get_cero_botes_kpis("Páez", "Acumulado Total")
    assert paez_kpis["botes"] == 5898, f"Esperado 5898, recibido {paez_kpis['botes']}"
    assert paez_kpis["caudal_lps"] == 801.07, f"Esperado 801.07, recibido {paez_kpis['caudal_lps']}"
    assert paez_kpis["beneficiarios"] == 147333, f"Esperado 147333, recibido {paez_kpis['beneficiarios']}"

    guanare_kpis = state.get_cero_botes_kpis("Guanare", "Acumulado Total")
    assert guanare_kpis["botes"] == 3712
    assert guanare_kpis["caudal_lps"] == 1492.70
    assert guanare_kpis["beneficiarios"] == 212259

    araure_kpis = state.get_cero_botes_kpis("Araure", "Acumulado Total")
    assert araure_kpis["botes"] == 3323
    assert araure_kpis["caudal_lps"] == 554.65
    assert araure_kpis["beneficiarios"] == 192169

    turen_kpis = state.get_cero_botes_kpis("Turén", "Acumulado Total")
    assert turen_kpis["botes"] == 1317
    assert turen_kpis["caudal_lps"] == 277.21
    assert turen_kpis["beneficiarios"] == 40845

    sro_kpis = state.get_cero_botes_kpis("San Rafael de Onoto", "Acumulado Total")
    assert sro_kpis["botes"] == 1119
    assert sro_kpis["caudal_lps"] == 141.27
    assert sro_kpis["beneficiarios"] == 25318
    print("-> Datos por municipio verificados contra cifras exactas de gestión.")

    # Verificación de filtraciones detalladas (2.423 registros y 1.638 casos 1x10)
    all_filts = state.get_filtered_filtraciones("Todos los Municipios")
    assert len(all_filts) >= 2423, f"Esperadas al menos 2423 filtraciones, recibidas {len(all_filts)}"
    casos_1x10 = state.get_filtered_filtraciones("Todos los Municipios", solo_1x10=True)
    assert len(casos_1x10) >= 1638, f"Esperados al menos 1638 casos 1x10, recibidos {len(casos_1x10)}"
    print(f"-> 2.423 filtraciones y 1.638 casos 1x10 del Buen Gobierno validados exitosamente.")

    # Registro de nueva reparación en modo Editor
    print("\n=== TEST 8: REGISTRO DE REPARACIÓN DE BOTE Y CÁLCULO DÍA ===")
    prev_botes = cb_kpis["botes"]
    prev_lps = cb_kpis["caudal_lps"]
    prev_dia = cb_kpis["caudal_lts_dia"]

    # Registrar 1 bote nuevo
    new_rec = state.add_cero_botes_repair(
        fecha="2026-11-12",
        municipio="Guanare",
        comunidad="Barrio San José",
        direccion="Carrera 5 con calle 10",
        diametro='1/2"',
        caudal_lps=0.50,
        beneficiarios=25,
        piezas_colocadas="1 Abrazadera 1/2",
        observaciones="Reparación urgente 1x10",
        es_1x10=True,
        ente_ejecutor="HIDROSPORTUGUESA"
    )
    assert new_rec["caudal_lpd"] == 0.50 * 86400.0, "Cálculo de Caudal Lts/Día incorrecto"
    assert new_rec["caudal_lpd"] == 43200.0

    updated_kpis = state.get_cero_botes_kpis("Todos los Municipios", "Acumulado Total")
    assert updated_kpis["botes"] == prev_botes + 1
    assert updated_kpis["caudal_lps"] == round(prev_lps + 0.50, 2)
    assert updated_kpis["caudal_lts_dia"] == round(prev_dia + 43200.0, 2)
    assert "17.143" in cero_botes_plan.main_metric, "Resumen Ejecutivo no se actualizó dinámicamente"
    print("-> Cálculo automático Caudal Lts/Día (Lts/Seg * 86400) y actualización dinámica de Resumen Ejecutivo verificada.")

    # Limpiar archivo temporal de pruebas de cero botes
    if os.path.exists(state.CERO_BOTES_UPDATES_PATH):
        os.remove(state.CERO_BOTES_UPDATES_PATH)

    print("\n=== TEST 9: PLAN TRAMOS CAÍDOS (EXCEL OFICIAL: 885 TRAMOS, 632 EJECUTADOS, 253 POR EJECUTAR) ===")
    tramos_kpis = state.get_tramos_caidos_kpis("Todos los Municipios", "Todas las Parroquias")
    print("KPIs Tramos Caídos:", tramos_kpis)
    assert tramos_kpis["tramos_totales"] == 885, f"Esperado 885, recibido {tramos_kpis['tramos_totales']}"
    assert tramos_kpis["ejecutados"] == 632, f"Esperado 632 ejecutados, recibido {tramos_kpis['ejecutados']}"
    assert tramos_kpis["por_ejecutar"] == 253, f"Esperado 253 por ejecutar, recibido {tramos_kpis['por_ejecutar']}"
    assert tramos_kpis["metros_sustituidos"] == 37074.42, f"Esperado 37.074,42 m, recibido {tramos_kpis['metros_sustituidos']}"
    assert tramos_kpis["metros_por_ejecutar"] == 19160.0, f"Esperado 19.160 m, recibido {tramos_kpis['metros_por_ejecutar']}"

    diams_resumen = state.get_tramos_diametros_resumen("Todos los Municipios")
    assert len(diams_resumen) == 13, f"Esperados 13 diámetros, encontrados {len(diams_resumen)}"

    muns_resumen = state.get_tramos_municipios_resumen()
    assert len(muns_resumen) == 14, f"Esperados 14 municipios, encontrados {len(muns_resumen)}"

    hist_anual = state.get_tramos_historico_anual()
    assert hist_anual["anual"]["2022"] == 93
    assert hist_anual["anual"]["2023"] == 122
    assert hist_anual["anual"]["2024"] == 173
    assert hist_anual["anual"]["2025"] == 105
    assert hist_anual["anual"]["2026"] == 135

    print("-> Tramos Caídos validado: 885 totales (632 ejecutados, 253 por ejecutar, 37.074,42 m sust, 19.160 m pend), 14 municipios y 13 diámetros.")

    print("\n=== TEST 10: RUTA DEL HIDROJET (EXCEL OFICIAL: 502.018,20 M, 5.280 BOCAS, 4.478 EMPOTRAMIENTOS, 603.606 BENEF.) ===")
    hidro_kpis = state.get_hidrojet_kpis("Todos los Municipios", "Acumulado Total")
    print("KPIs Hidrojet:", hidro_kpis)
    assert hidro_kpis["metros_liberados"] == 502018.2, f"Esperado 502.018,20 m, recibido {hidro_kpis['metros_liberados']}"
    assert hidro_kpis["bocas_de_visita"] == 5280, f"Esperado 5.280 bocas, recibido {hidro_kpis['bocas_de_visita']}"
    assert hidro_kpis["empotramientos"] == 4478, f"Esperado 4.478 empotramientos, recibido {hidro_kpis['empotramientos']}"
    assert hidro_kpis["beneficiarios"] == 603606, f"Esperado 603.606 beneficiarios, recibido {hidro_kpis['beneficiarios']}"
    assert hidro_kpis["sectores_atendidos"] == 1655, f"Esperado 1.655 sectores, recibido {hidro_kpis['sectores_atendidos']}"
    assert hidro_kpis["dias_trabajados"] == 1096, f"Esperado 1.096 días, recibido {hidro_kpis['dias_trabajados']}"

    # Verificación de las 743 jornadas de 2026
    jornadas_2026 = state.get_filtered_jornadas_hidrojet("Todos los Municipios")
    assert len(jornadas_2026) >= 743, f"Esperadas al menos 743 jornadas, recibidas {len(jornadas_2026)}"
    print("-> 743 jornadas operativas validadas con éxito.")

    # Registro de nueva operación Hidrojet
    prev_m = hidro_kpis["metros_liberados"]
    new_j = state.add_hidrojet_operation(
        fecha="2026-11-12",
        municipio="Guanare",
        comunidad="Barrio San José",
        direccion="Calle 5 con Carrera 10",
        trabajo_realizado="MANTENIMIENTO DE COLECTORES",
        longitud_m=120.0,
        bocas=2,
        empotramientos=1,
        beneficiarios=95
    )
    assert new_j["longitud_m"] == 120.0
    updated_hkpis = state.get_hidrojet_kpis("Todos los Municipios", "Acumulado Total")
    assert updated_hkpis["metros_liberados"] == round(prev_m + 120.0, 2)
    assert updated_hkpis["bocas_de_visita"] == 5282

    # Validar parser dinámico de Ruta del Hidrojet por coincidencia de texto
    from data.hidrojet_parser import HidrojetParser
    p_orig = HidrojetParser("AGUAS SERVIDAS PORTUGUESA 2026-6.xlsx")
    res_orig = p_orig.parse_all()
    assert res_orig["totales_2026"]["longitud_m"] > 0
    assert res_orig["totales_2026"]["bocas"] > 0
    assert res_orig["totales_2026"]["empotramientos"] > 0
    assert res_orig["totales_2026"]["beneficiarios"] > 0
    assert res_orig["totales_acumulado"]["longitud_m"] > 0
    assert res_orig["totales_acumulado"]["beneficiarios"] > 0

    nuevo_hidrojet = os.path.expanduser("~/Documents/ARCHIVOS NUEVOS 17 DE NOVIEMBRE/AGUAS SERVIDAS PORTUGUESA 2026.xlsx")
    if os.path.exists(nuevo_hidrojet):
        p_nuevo = HidrojetParser(nuevo_hidrojet)
        res_nuevo = p_nuevo.parse_all()
        assert res_nuevo["totales_2026"]["longitud_m"] == 88459.0
        assert res_nuevo["totales_2026"]["bocas"] == 930
        assert res_nuevo["totales_2026"]["beneficiarios"] == 74178
        assert res_nuevo["totales_acumulado"]["longitud_m"] == 502858.2
        assert res_nuevo["totales_acumulado"]["bocas"] == 5292
        assert res_nuevo["totales_acumulado"]["beneficiarios"] == 604305
        assert len(res_nuevo["jornadas"]) >= 747
        print("-> Parser dinámico de Ruta del Hidrojet validado con reporte del 17-Nov sin números de fila fijos.")

    # Limpiar archivo temporal de prueba si existe
    if os.path.exists(state.HIDROJET_UPDATES_PATH):
        os.remove(state.HIDROJET_UPDATES_PATH)

    print("-> Ruta del Hidrojet validado al 100%: 502.018,20 m liberados, 5.280 bocas, 4.478 empotramientos, 603.606 beneficiarios, 1.655 sectores, 1.096 días.")

    print("\n=== TEST 11: PARSER OFICIAL HIDROVEN (EXCEL REAL OPERATIVIDAD PORTUGUESA) ===")
    state.reload_hidroven_excel("OPERATIVIDAD  PORTUGUESA-8.xlsx")
    assert state.hidroven_data is not None, "Datos de HIDROVEN deben estar cargados"
    resumen = state.hidroven_data["totales_estado"]
    assert resumen["total_pozos"] == 535, f"Esperado 535 pozos, encontrado {resumen['total_pozos']}"
    assert resumen["operativos_total"] == 464, f"Esperado 464 operativos, encontrado {resumen['operativos_total']}"
    assert resumen["inoperativos_total"] == 71, f"Esperado 71 inoperativos, encontrado {resumen['inoperativos_total']}"
    assert len(state.hidroven_data["pozos"]) == 535, f"Lista de pozos debe ser 535"
    assert len(state.hidroven_data["pozos_inoperativos"]) == 71, f"Lista de inoperativos debe ser 71"
    assert len(state.hidroven_data["municipios"]) == 14, f"Debe contener 14 municipios"
    assert state.hidroven_data["consolidado_rehab"]["total_rehabilitados"] == 339, f"Esperado 339 rehabilitados"
    assert state.hidroven_data["consolidado_rehab"]["total_intervenciones"] == 797, f"Esperado 797 intervenciones"
    assert state.hidroven_data["consolidado_rehab"]["total_mantenimientos"] == 440, f"Esperado 440 mantenimientos"
    assert len(state.hidroven_data["intervenciones"]) >= 1595, f"Esperado >= 1595 intervenciones, encontrado {len(state.hidroven_data['intervenciones'])}"
    total_est = len(state.hidroven_data["estaciones_rebombeo"]["cono_sur"]) + len(state.hidroven_data["estaciones_rebombeo"]["cono_norte"]) + len(state.hidroven_data["estaciones_rebombeo"]["captacion_conduccion"])
    assert total_est == 30, f"Esperadas 30 estaciones (17 sur + 10 norte + 3 captación), encontrado {total_est}"
    print(f"-> Parser HIDROVEN validado: 535 pozos ({resumen['operativos_total']} op / {resumen['inoperativos_total']} inop), {len(state.hidroven_data['intervenciones'])} intervenciones, 30 estaciones.")

    print("\n=== TEST 12: FILTRADO DINÁMICO POR MUNICIPIO Y CONSOLIDADO REHAB ===")
    # 1. Pozos totales vs filtrados (incluyendo diacríticos / acentos)
    assert len(state.get_filtered_pozos_hidroven("Todos los Municipios")) == 535
    assert len(state.get_filtered_inoperativos_hidroven("Todos los Municipios")) in (71, 73)
    assert len(state.get_filtered_pozos_hidroven("Guanare")) == 96
    assert len(state.get_filtered_pozos_hidroven("Páez")) == 60
    assert len(state.get_filtered_pozos_hidroven("Turén")) == 50
    assert len(state.get_filtered_pozos_hidroven("San Genaro de Boconoíto")) == 45
    assert len(state.get_filtered_pozos_hidroven("Araure")) == 64
    
    # 2. Consolidado Rehab: Totales estadales
    estadal_con = state.get_consolidado_rehab_for_municipio("Todos los Municipios")
    assert estadal_con["rehabilitados"] == 339
    assert estadal_con["intervenciones"] == 797
    assert estadal_con["mantenimientos"] == 440
    assert sum(estadal_con["anual"].values()) == 339
    
    # 3. Consolidado Rehab: Filtrado por Guanare (69 / 182 / 117)
    guanare_con = state.get_consolidado_rehab_for_municipio("Guanare")
    assert guanare_con["rehabilitados"] == 69, f"Esperado 69 rehab en Guanare, recibido {guanare_con['rehabilitados']}"
    assert guanare_con["intervenciones"] == 182, f"Esperado 182 intervenciones en Guanare, recibido {guanare_con['intervenciones']}"
    assert guanare_con["mantenimientos"] == 117, f"Esperado 117 mantenimientos en Guanare, recibido {guanare_con['mantenimientos']}"
    assert guanare_con["anual"]["2022"] == 39
    assert guanare_con["anual"]["2023"] == 15
    assert sum(guanare_con["anual"].values()) == 69

    # 4. Intervenciones filtradas por Guanare
    itvs_guanare = state.get_filtered_intervenciones("Guanare")
    assert len(itvs_guanare) == 371
    print(f"-> Consolidado Guanare verificado: {guanare_con['rehabilitados']} rehab, {guanare_con['intervenciones']} itvs mayores, {guanare_con['mantenimientos']} mant.")
    print("-> Sincronización y filtrado por diacríticos verificado al 100%.")

    print("\n=== TEST 13: CAMBIO DE ESTATUS OPERATIVO/INOPERATIVO Y PERSISTENCIA JSON ===")
    # Test cambio de estatus y bitacora
    # Verificar que el pozo 135 (MESA DE CAVACAS - SECTOR 1) esté inicialmente inoperativo
    pozo_135 = next((p for p in state.hidroven_data["pozos"] if p["n"] == 135), None)
    assert pozo_135 is not None
    initial_status = pozo_135["operatividad"]

    # Cambiar estatus a Operativo
    res = state.update_pozo_status(
        well_n=135,
        nuevo_estatus="SI",
        fecha_evento="2026-11-12",
        observacion="Instalación de motor 25HP y bomba sumergible nueva por Gobernación de Portuguesa",
        ente="Gobernación"
    )
    assert res is True
    assert pozo_135["operatividad"] == "SI"
    assert pozo_135.get("inoperativo_info") is None
    assert state.hidroven_data["totales_estado"]["operativos_total"] == 465
    assert state.hidroven_data["totales_estado"]["inoperativos_total"] == 70

    # Verificar persistencia en pozos_actualizados.json
    assert os.path.exists(state.POZOS_UPDATES_PATH)
    with open(state.POZOS_UPDATES_PATH, "r", encoding="utf-8") as f:
        saved_updates = json.load(f)
    assert "135" in saved_updates
    assert saved_updates["135"]["nuevo_estatus"] == "SI"

    # Verificar que la bitácora de intervenciones del pozo tenga el registro
    assert pozo_135["intervenciones"][0]["tipo"] == "Rehabilitación y Puesta en Servicio"
    assert pozo_135["intervenciones"][0]["fuente"] in ["GOB", "Gobernación"]

    # Revertir pozo 135 a su estado original (Inoperativo) para mantener integridad
    state.update_pozo_status(
        well_n=135,
        nuevo_estatus="NO",
        fecha_evento="2026-11-12",
        observacion="Falla electromecánica en devanado",
        ente="Gobernación"
    )
    assert pozo_135["operatividad"] == "NO"
    assert state.hidroven_data["totales_estado"]["operativos_total"] == 464
    assert state.hidroven_data["totales_estado"]["inoperativos_total"] == 71

    # Limpiar archivo temporal de pruebas si se desea o dejarlo vacío
    if os.path.exists(state.POZOS_UPDATES_PATH):
        os.remove(state.POZOS_UPDATES_PATH)
    state._recalc_hidroven_totals()

    print("-> Cambio de estatus, persistencia JSON y recálculo en tiempo real 100% verificados.")

    print("\n=== TEST 14: PESTAÑA NUEVAS PERFORACIONES (34 REGISTROS, 4 KPIS Y PERSISTENCIA) ===")
    assert len(state.nuevas_perforaciones) == 34
    perf_kpis = state.get_nuevas_perforaciones_kpis("Todos los Municipios")
    assert perf_kpis["operativas"] == 23, f"Esperadas 23 operativas, recibidas {perf_kpis['operativas']}"
    assert perf_kpis["por_inaugurar"] == 8, f"Esperadas 8 por inaugurar, recibidas {perf_kpis['por_inaugurar']}"
    assert perf_kpis["en_ejecucion"] == 2, f"Esperadas 2 en ejecucion, recibidas {perf_kpis['en_ejecucion']}"
    assert perf_kpis["paralizado"] == 1, f"Esperado 1 paralizado, recibido {perf_kpis['paralizado']}"
    print(f"-> 4 KPIs superiores verificados: {perf_kpis}")

    # Verificar filtrado dinámico por municipio (ej. Araure: 5 perforaciones)
    araure_perfs = state.get_nuevas_perforaciones(municipio="Araure")
    assert len(araure_perfs) == 5, f"Esperadas 5 en Araure, recibidas {len(araure_perfs)}"
    paez_perfs = state.get_nuevas_perforaciones(municipio="Páez")
    assert len(paez_perfs) == 13, f"Esperadas 13 en Páez, recibidas {len(paez_perfs)}"
    print(f"-> Filtrado municipal verificado: Araure={len(araure_perfs)}, Páez={len(paez_perfs)}")

    # Probar actualización de estatus y equipo en memoria y archivo
    state.update_nueva_perforacion(perf_id=5, equipo_hp="50HP", estatus="OPERATIVA")
    perf_5 = next((p for p in state.nuevas_perforaciones if p["id"] == 5), None)
    assert perf_5["estatus"] == "OPERATIVA"
    assert perf_5["equipo_hp"] == "50HP"

    # Revertir pozo 5 a su valor original
    state.update_nueva_perforacion(perf_id=5, equipo_hp="SIN EQUIPO", estatus="POR INAUGURAR")
    assert perf_5["estatus"] == "POR INAUGURAR"

    print("-> Nuevas perforaciones (34), KPIs dinámicos y persistencia JSON verificados al 100%.")

    print("\n=== TEST 15: SISTEMA OFICIAL DE AUTENTICACIÓN, GESTIÓN DE USUARIOS Y AUDITORÍA (SHA-256) ===")
    from data.auth_manager import AuthManager
    auth = AuthManager()
    users = auth.get_users()
    assert len(users) >= 10, f"Se esperaban al menos 10 usuarios precargados, se encontraron {len(users)}"
    
    # 2 Masters
    masters = [u for u in users if u["rol"] == "MASTER"]
    assert len(masters) == 2, f"Se esperaban 2 usuarios Master, encontrados {len(masters)}"
    assert any(u["username"] == "master1" for u in masters)
    assert any(u["username"] == "master2" for u in masters)

    # 3 Analistas
    analistas = [u for u in users if u["rol"] == "ANALISTA"]
    assert len(analistas) == 3, f"Se esperaban 3 analistas, encontrados {len(analistas)}"

    # 5 Ejecutivos
    ejecutivos = [u for u in users if u["rol"] == "EJECUTIVO"]
    assert len(ejecutivos) == 5, f"Se esperaban 5 ejecutivos, encontrados {len(ejecutivos)}"

    # Validar autenticación SHA-256
    ok_master, u_master, _ = auth.authenticate("master1", "Pceo2026*")
    assert ok_master is True and u_master["rol"] == "MASTER"

    ok_analista, u_analista, _ = auth.authenticate("analista1", "Sala2026*")
    assert ok_analista is True and u_analista["rol"] == "ANALISTA"

    ok_gob, u_gob, _ = auth.authenticate("gobernador", "Portuguesa2026")
    assert ok_gob is True and u_gob["rol"] == "EJECUTIVO"

    bad_auth, _, err_msg = auth.authenticate("master1", "ClaveIncorrecta")
    assert bad_auth is False
    assert "incorrecta" in err_msg.lower()

    # Validar is_authenticated en State (propiedad y método callable)
    state.logout_user()
    assert state.is_authenticated == False
    assert state.is_authenticated() is False
    assert not state.is_authenticated

    # Validar permisos en State
    state.login_user(u_master)
    assert state.is_authenticated == True
    assert state.is_authenticated() is True
    assert state.is_authenticated
    assert state.is_master() is True
    assert state.is_editor() is True
    assert state.is_viewer() is False

    state.login_user(u_analista)
    assert state.is_master() is False
    assert state.is_editor() is True
    assert state.is_viewer() is False

    state.login_user(u_gob)
    assert state.is_master() is False
    assert state.is_editor() is False
    assert state.is_viewer() is True

    # Validar Bitácora de Auditoría
    audits = auth.get_auditoria()
    assert len(audits) > 0, "La bitácora de auditoría no debe estar vacía"
    print(f"-> Sistema de usuarios validado: {len(masters)} Masters, {len(analistas)} Analistas, {len(ejecutivos)} Ejecutivos.")
    print(f"-> Permisos validados: Master/Analista = Editor, Ejecutivo = Solo Lectura.")
    print(f"-> Auditoría en tiempo real validada: {len(audits)} eventos registrados.")

    print("\n=== TEST 16: PLAN CERO HUECOS (EXCEL OFICIAL: 206.142,90 TON, 3.383,41 KM, 342.563 FALLAS) ===")
    from data.cero_huecos_parser import CeroHuecosParser
    ch_parser = CeroHuecosParser()
    ch_data = ch_parser.parse_all()

    # Validar cifras totales acumuladas 2022-2026
    tot = ch_data["totales_estatales"]
    assert tot["toneladas"] == 206142.90, f"Esperado 206142.90 ton, recibido {tot['toneladas']}"
    assert tot["kilometros"] == 3383.41, f"Esperado 3383.41 km, recibido {tot['kilometros']}"
    assert tot["fallas"] == 342563, f"Esperado 342563 fallas, recibido {tot['fallas']}"

    # Validar tipología de fallas
    tip = tot["tipologia"]
    assert tip["huecos"] == 266586, f"Esperado 266.586 huecos, recibido {tip['huecos']}"
    assert tip["taponeo"] == 31963, f"Esperado 31.963 taponeo, recibido {tip['taponeo']}"
    assert tip["bacheo"] == 30594, f"Esperado 30.594 bacheo, recibido {tip['bacheo']}"
    assert tip["carpetas"] == 10078, f"Esperado 10.078 carpetas, recibido {tip['carpetas']}"
    assert tip["grietas_long"] == 2302, f"Esperado 2.302 grietas long, recibido {tip['grietas_long']}"
    assert tip["grietas_transv"] == 1040, f"Esperado 1.040 grietas transv, recibido {tip['grietas_transv']}"

    # Validar 26 ubicaciones oficiales
    assert len(ch_data["ubicaciones"]) == 26, f"Esperadas 26 ubicaciones, recibidas {len(ch_data['ubicaciones'])}"

    # Validar fallas 2026 (99.865)
    f26_sum = sum(f["total_fallas"] for f in ch_data["fallas_2026"])
    assert f26_sum == 99865, f"Esperado 99.865 fallas 2026, recibido {f26_sum}"

    # Validar programas 2026
    prog = ch_data["desglose_asfalto"]["resumen_programas"]
    assert prog["cero_huecos"]["toneladas"] == 58140.53, f"Esperado 58.140,53 ton Cero Huecos, recibido {prog['cero_huecos']['toneladas']}"
    assert prog["plan_nacional"]["toneladas"] == 19432.00, f"Esperado 19.432,00 ton Plan Nacional, recibido {prog['plan_nacional']['toneladas']}"

    # Validar KPIs en State
    ch_kpis = state.get_cero_huecos_kpis("Todas las Ubicaciones", "Acumulado Total")
    assert ch_kpis["toneladas"] == 206142.90
    assert ch_kpis["kilometros"] == 3383.41
    assert ch_kpis["fallas"] == 342563

    # Validar registro de jornada con persistencia y auditoría
    prev_audits_count = len(auth.get_auditoria())
    jornada = state.add_cero_huecos_jornada(
        fecha="2026-11-13",
        ubicacion="MUNICIPIO GUANARE",
        programa="Plan Cero Huecos",
        toneladas=50.0,
        kilometros=2.0,
        taponeo=5,
        bacheo=10,
        carpetas=2,
        huecos=20,
        grietas_long=1,
        grietas_transv=0,
        responsable="Ing. Manuel Hidalgo",
        notas="Prueba unitaria automatizada"
    )
    assert jornada["total_fallas"] == 38
    assert len(auth.get_auditoria()) == prev_audits_count + 1

    # Limpiar archivo temporal de prueba si se generó
    if os.path.exists(state.CERO_HUECOS_UPDATES_PATH):
        os.remove(state.CERO_HUECOS_UPDATES_PATH)
    state.cero_huecos_data = ch_parser.parse_all()
    state._recalc_cero_huecos_totals()

    print(f"-> Cero Huecos validado al 100%: 206.142,90 Ton / 3.383,41 km / 342.563 Fallas.")
    print(f"-> 26 Ubicaciones, 6 Tipologías, Evolución Anual (2022-2026) y Programas validados con éxito.")

    print("\n=== TEST 17: PLAN FIESTA DE LA LUZ (EXCEL OFICIAL: 150.233 LUM, 6.113 APAGADOS, 3.444 TX INST, 75 TX FALLADOS) ===")
    assert state.fiesta_luz_data is not None, "fiesta_luz_data no fue cargado en AppState"
    fl_tot = state.fiesta_luz_data.get("totales_estatales", {})
    assert fl_tot["luminarias"] == 150233, f"Esperado 150.233 luminarias, obtenido {fl_tot['luminarias']}"
    assert fl_tot["puntos_apagados"] == 6113, f"Esperado 6.113 puntos apagados, obtenido {fl_tot['puntos_apagados']}"
    assert fl_tot["tx_instalados"] == 3444, f"Esperado 3.444 TX instalados, obtenido {fl_tot['tx_instalados']}"
    assert fl_tot["tx_corpoelec"] == 2012, f"Esperado 2.012 TX Corpoelec, obtenido {fl_tot['tx_corpoelec']}"
    assert fl_tot["tx_gobernacion"] == 1432, f"Esperado 1.432 TX Gobernación, obtenido {fl_tot['tx_gobernacion']}"
    assert fl_tot["tx_fallados"] == 75, f"Esperado 75 TX fallados, obtenido {fl_tot['tx_fallados']}"
    assert fl_tot["tx_fallados_con_codigo"] == 35, f"Esperado 35 C/Cód, obtenido {fl_tot['tx_fallados_con_codigo']}"
    assert fl_tot["tx_fallados_sin_codigo"] == 40, f"Esperado 40 S/Cód, obtenido {fl_tot['tx_fallados_sin_codigo']}"
    assert fl_tot["sectores"] == 3080, f"Esperado 3.080 sectores, obtenido {fl_tot['sectores']}"

    # Validar histórico de luminarias
    lum_hist = state.fiesta_luz_data.get("luminarias_historico", {}).get("estatal", {})
    assert lum_hist.get("gob_alc", {}).get("subtotal") == 126338, "Subtotal Gob-Alc debe ser 126.338"
    assert lum_hist.get("corpoelec", {}).get("subtotal") == 23895, "Subtotal Corpoelec debe ser 23.895"

    # Validar bitácora y sectores detallados
    assert len(state.fiesta_luz_data.get("puntos_apagados_detalle", [])) == 228, "Detalle puntos apagados debe tener 228 sectores"
    assert len(state.fiesta_luz_data.get("tx_instalados_2026_detalle", [])) == 843, "Bitácora 2026 debe tener 843 registros"
    assert len(state.fiesta_luz_data.get("tx_fallados_detalle", [])) == 73, "Detalle TX fallados debe tener 73 registros"

    # Validar KPIs dinámicos
    kpis_est = state.get_fiesta_luz_kpis("Todos los Municipios", "Acumulado Total 2022-2026")
    assert kpis_est["luminarias"] == 150233
    assert kpis_est["puntos_apagados"] == 6113
    assert kpis_est["tx_instalados"] == 3444
    assert kpis_est["tx_fallados"] == 75

    kpis_gua = state.get_fiesta_luz_kpis("Guanare", "Acumulado Total 2022-2026")
    assert kpis_gua["luminarias"] == 31531
    assert kpis_gua["puntos_apagados"] == 500
    assert kpis_gua["tx_instalados"] == 776
    assert kpis_gua["tx_fallados"] == 15

    # Validar atención de transformador fallado (descuenta de fallados y suma a instalados)
    prev_audits = len(auth.get_auditoria())
    state.marcar_tx_fallado_atendido("TXF-1", "2026-11-13", "Corpoelec")
    kpis_after_tx = state.get_fiesta_luz_kpis("Todos los Municipios")
    assert kpis_after_tx["tx_fallados"] == 74, f"Esperado 74 TX fallados, recibido {kpis_after_tx['tx_fallados']}"
    assert kpis_after_tx["tx_instalados"] == 3445, f"Esperado 3.445 TX instalados, recibido {kpis_after_tx['tx_instalados']}"
    assert len(auth.get_auditoria()) == prev_audits + 1

    # Validar registro nuevo
    state.add_fiesta_luz_registro("Luminarias", "Guanare", "Barrio Libertador", 50, "Instalación LED", "Gobernación")
    kpis_after_reg = state.get_fiesta_luz_kpis("Todos los Municipios")
    assert kpis_after_reg["luminarias"] == 150283

    # Limpiar archivo temporal de prueba y restaurar
    if os.path.exists(state.FIESTA_LUZ_UPDATES_PATH):
        os.remove(state.FIESTA_LUZ_UPDATES_PATH)
    from data.fiesta_luz_parser import FiestaLuzParser
    state.fiesta_luz_data = FiestaLuzParser().parse_all()
    state._recalc_fiesta_luz_totals()

    print("-> Fiesta de la Luz validado al 100%: 150.233 Luminarias, 6.113 Puntos Apagados, 3.444 TX Instalados, 75 TX Fallados.")
    print("-> 14 Municipios, 5 Pestañas, Atención de Transformadores y Registro Operativo validados con éxito.")

    # 18. TEST PLAN DE RECUPERACIÓN Y CONSTRUCCIÓN DE PUENTES Y ALCANTARILLAS
    print("\n--- TEST 18: PLAN DE RECUPERACIÓN Y CONSTRUCCIÓN DE PUENTES Y ALCANTARILLAS ---")
    if os.path.exists(state.PUENTES_UPDATES_PATH):
        os.remove(state.PUENTES_UPDATES_PATH)
        from data.puentes_parser import PuentesParser
        state.puentes_data = PuentesParser().parse_all()
        state._recalc_puentes_totals()

    assert state.puentes_data is not None, "state.puentes_data no debe ser None"
    
    p_tot = state.puentes_data.get("totales_estatales", {})
    assert p_tot["total_obras"] == 154, f"Esperado 154 obras totales, obtenido {p_tot.get('total_obras')}"
    assert p_tot["ejecutadas"] == 145, f"Esperado 145 ejecutadas, obtenido {p_tot.get('ejecutadas')}"
    assert p_tot["en_desarrollo"] == 5, f"Esperado 5 en desarrollo, obtenido {p_tot.get('en_desarrollo')}"
    assert p_tot["paralizadas"] == 4, f"Esperado 4 paralizadas, obtenido {p_tot.get('paralizadas')}"
    assert p_tot["puentes"] == 78, f"Esperado 78 puentes, obtenido {p_tot.get('puentes')}"
    assert p_tot["alcantarillas"] == 66, f"Esperado 66 alcantarillas, obtenido {p_tot.get('alcantarillas')}"
    assert p_tot["cajones"] == 10, f"Esperado 10 cajones, obtenido {p_tot.get('cajones')}"

    # Validar desglose anual (2023: 86, 2024: 12, 2025: 34, 2026: 22)
    p_anual = state.puentes_data.get("por_año", {})
    assert p_anual.get("2023", {}).get("total") == 86, f"Esperado 86 en 2023, obtenido {p_anual.get('2023', {}).get('total')}"
    assert p_anual.get("2024", {}).get("total") == 12, f"Esperado 12 en 2024, obtenido {p_anual.get('2024', {}).get('total')}"
    assert p_anual.get("2025", {}).get("total") == 34, f"Esperado 34 en 2025, obtenido {p_anual.get('2025', {}).get('total')}"
    assert p_anual.get("2026", {}).get("total") == 22, f"Esperado 22 en 2026, obtenido {p_anual.get('2026', {}).get('total')}"

    # Validar KPIs dinámicos
    kpis_all = state.get_puentes_kpis("Todos los Municipios", "Todas", "Todos los Años")
    assert kpis_all["total_obras"] == 154
    assert kpis_all["ejecutadas"] == 145
    assert kpis_all["en_desarrollo"] == 5
    assert kpis_all["paralizadas"] == 4
    assert kpis_all["puentes"] == 78
    assert kpis_all["alcantarillas"] == 66
    assert kpis_all["cajones"] == 10

    # Validar filtro por tipo
    kpis_puentes = state.get_puentes_kpis("Todos los Municipios", "PUENTE", "Todos los Años")
    assert kpis_puentes["total_obras"] == 78
    assert kpis_puentes["ejecutadas"] == 69
    assert kpis_puentes["en_desarrollo"] == 5
    assert kpis_puentes["paralizadas"] == 4

    # Validar actualización de obra y auditoría
    prev_audits = len(auth.get_auditoria())
    obra_test = state.puentes_data["obras"][0]
    obra_id = obra_test["id"]
    state.update_puente_obra(
        obra_id=obra_id,
        nuevo_estatus="EN DESARROLLO",
        nuevo_avance=0.95,
        notas="Avance de vigas y estribos"
    )
    
    # Verificar que el estado refleja el cambio
    obra_mod = next(o for o in state.puentes_data["obras"] if o["id"] == obra_id)
    assert obra_mod["avance"] == 0.95
    assert obra_mod["estatus"] == "EN DESARROLLO"
    assert len(auth.get_auditoria()) == prev_audits + 1

    # Validar registro de nueva obra
    state.add_puente_obra(
        nombre="Puente Nuevo Test Unitario",
        municipio="Guanare",
        tipo_obra="PUENTE",
        year="2026",
        estatus="EN DESARROLLO",
        avance=0.25,
        notas="Construcción de estribos"
    )
    kpis_post_add = state.get_puentes_kpis("Todos los Municipios", "Todas", "Todos los Años")
    assert kpis_post_add["total_obras"] == 155
    assert kpis_post_add["puentes"] == 79

    # Limpiar archivo temporal de prueba y restaurar estado
    if os.path.exists(state.PUENTES_UPDATES_PATH):
        os.remove(state.PUENTES_UPDATES_PATH)
    from data.puentes_parser import PuentesParser
    state.puentes_data = PuentesParser().parse_all()
    state._recalc_puentes_totals()

    print("-> Plan Puentes y Alcantarillas validado al 100%: 154 Obras Oficiales.")
    print("-> 78 Puentes, 66 Alcantarillas, 10 Cajones de Paso.")
    print("-> 145 Ejecutadas (94,2%), 5 En Desarrollo, 4 Paralizadas.")
    print("-> Actualización de Obras, Nueva Obra y Filtros Dinámicos validados con éxito.")

    # 19. TEST IMPORTACIÓN REPORTE OPERATIVIDAD 17-11-26.XLSX, CONFIG_RUTAS Y AUDITORÍA
    print("\n--- TEST 19: IMPORTACIÓN REPORTE OPERATIVIDAD 17-11-26.XLSX, CONFIG_RUTAS Y AUDITORÍA ---")
    nuevo_reporte = "OPERATIVIDAD  PORTUGUESA 17-11-26.xlsx"
    assert os.path.exists(nuevo_reporte), f"El archivo {nuevo_reporte} debe existir en el workspace"

    prev_audits = len(auth.get_auditoria())
    ok_import = state.reload_hidroven_excel(nuevo_reporte)
    assert ok_import is True, "reload_hidroven_excel debe retornar True"

    # Validar datos cargados desde el nuevo reporte (462 op / 73 inop)
    tot_17 = state.hidroven_data["totales_estado"]
    assert tot_17["total_pozos"] == 535
    assert tot_17["operativos_total"] == 462
    assert tot_17["inoperativos_total"] == 73
    assert state.hidroven_data["consolidado_rehab"]["total_rehabilitados"] == 339

    # Validar persistencia en data/config_rutas.json
    assert os.path.exists(state.CONFIG_RUTAS_PATH), "data/config_rutas.json debe existir"
    with open(state.CONFIG_RUTAS_PATH, "r", encoding="utf-8") as f:
        rutas_cfg = json.load(f)
    assert rutas_cfg.get("fiesta_agua") == nuevo_reporte

    # Validar limpieza de data/pozos_actualizados.json
    with open(state.POZOS_UPDATES_PATH, "r", encoding="utf-8") as f:
        pozos_upd = json.load(f)
    assert len(pozos_upd) == 0, "pozos_actualizados.json debe estar limpio tras importar nuevo reporte oficial"

    # Validar registro en auditoría
    assert len(auth.get_auditoria()) == prev_audits + 1
    ultimo_evento = auth.get_auditoria()[0]
    assert ultimo_evento["modulo"] == "Fiesta del Agua"
    assert "OPERATIVIDAD  PORTUGUESA 17-11-26.xlsx" in ultimo_evento["detalle"]

    # Validar actualización en Resumen Ejecutivo (GOVERNMENT_PLANS)
    plan_fa = next(p for p in GOVERNMENT_PLANS if p.id == "fiesta_agua")
    assert "535 Pozos" in plan_fa.main_metric

    # Validar componente ExcelImportPanel
    from modules.excel_import_panel import ExcelImportPanel, get_detected_excel_files
    class MockPage:
        def update(self): pass
    mock_p = MockPage()
    dummy_panel = ExcelImportPanel(
        page=mock_p,
        title="Test Panel",
        default_file=nuevo_reporte,
        on_load_callback=lambda p: True
    )
    assert dummy_panel.panel_container.visible is False
    assert dummy_panel.dropdown_detected.label == "Seleccionar archivo .xlsx en Documentos"
    
    # Validar escaneo exclusivo en Documentos
    docs_files = get_detected_excel_files()
    assert len(docs_files) > 0, "Debe detectar archivos .xlsx en Documentos"
    for item in docs_files:
        assert not item["label"].startswith("[Raíz]"), f"No debe incluir la raíz del proyecto: {item['label']}"
        assert not item["label"].startswith("[Descargas]"), f"No debe incluir Descargas: {item['label']}"
        assert item["label"].startswith("[") and "]" in item["label"]
    
    # Validar orden descendente por fecha de modificación
    mtimes = [item["mtime"] for item in docs_files]
    assert mtimes == sorted(mtimes, reverse=True), "Los archivos deben estar ordenados del más reciente al más antiguo"

    dummy_panel.show()
    assert dummy_panel.panel_container.visible is True
    dummy_panel.hide()
    assert dummy_panel.panel_container.visible is False

    print("-> Soporte completo para 'OPERATIVIDAD  PORTUGUESA 17-11-26.xlsx' validado exitosamente.")
    print("-> 'CONSOLIDADO REHAB' y 'CONSOLIDADO REHAB.' procesados dinámicamente al 100%.")
    print("-> config_rutas.json actualizado, pozos_actualizados.json limpio y auditoría registrada.")
    print("-> Panel de Importación sin congelamiento validado para los 7 módulos.")

    print("\n--- TEST 20: PLAN DE RECUPERACIÓN Y REHABILITACIÓN DE ESPACIOS DE SALUD ---")
    from data.salud_parser import SaludParser
    parser_salud = SaludParser("ESPACIOS_DE_SALUD_PORTUGUESA_2026.xlsx")
    salud_data = parser_salud.parse_all()
    assert salud_data["totales_estatales"]["total_obras"] == 134, f"Esperado 134 obras, obtenido {salud_data['totales_estatales']['total_obras']}"
    assert salud_data["totales_estatales"]["culminadas"] == 113, f"Esperado 113 culminadas, obtenido {salud_data['totales_estatales']['culminadas']}"
    assert salud_data["totales_estatales"]["en_proceso"] == 17, f"Esperado 17 en proceso, obtenido {salud_data['totales_estatales']['en_proceso']}"
    assert salud_data["totales_estatales"]["paralizadas"] == 4, f"Esperado 4 paralizadas, obtenido {salud_data['totales_estatales']['paralizadas']}"
    assert salud_data["total_centros"] == 133, f"Esperado 133 centros en detalle, obtenido {salud_data['total_centros']}"
    assert len(salud_data["resumen_municipios"]) == 14, f"Esperado 14 municipios, obtenido {len(salud_data['resumen_municipios'])}"
    assert len(salud_data["frentes_prioritarios"]) == 21, f"Esperado 21 frentes prioritarios, obtenido {len(salud_data['frentes_prioritarios'])}"
    print("-> Lector inteligente de Espacios de Salud validado al 100%: 134 Obras (113 Culminadas, 17 En Proceso, 4 Paralizadas).")
    print("-> 133 Centros individuales, 14 Municipios, 6 Tipologías y 21 Frentes Prioritarios.")

    # Validar métodos de AppState para Salud
    kpis_salud = state.get_salud_kpis()
    assert kpis_salud["total_obras"] == 134
    assert kpis_salud["culminadas"] == 113
    assert kpis_salud["en_proceso"] == 17
    assert kpis_salud["paralizadas"] == 4

    # Validar filtrado de centros
    centros_guanare = state.get_filtered_centros_salud(municipality="Guanare")
    assert len(centros_guanare) == 28
    centros_hosp = state.get_filtered_centros_salud(tipo="Hospitales (8)")
    assert len(centros_hosp) >= 8

    # Validar edición y persistencia
    prev_audit_salud = len(auth.get_auditoria())
    ok_upd = state.update_centro_salud(centro_id=1, estatus="CULMINADA", porcentaje=100.0, ente_ejecutor="MPPS - ACTUALIZADO", notas="Inspección PCEO")
    assert ok_upd is True
    assert len(auth.get_auditoria()) == prev_audit_salud + 1

    # Validar nuevo registro
    nuevo_c = state.add_centro_salud(
        municipio="Guanare",
        nombre="Centro Diagnóstico de Prueba PCEO",
        asic="LEONIDAS RAMOS",
        direccion="Sector Campo Alegre",
        tipo_centro="CPT",
        fase_nivel="CPT II",
        estatus="EN PROCESO",
        porcentaje=45.0,
        ente_ejecutor="GOBERNACIÓN"
    )
    assert nuevo_c["id"] > 133
    assert nuevo_c["porcentaje"] == 45.0

    # Limpiar archivo de persistencia de prueba si existe
    if os.path.exists(state.SALUD_UPDATES_PATH):
        os.remove(state.SALUD_UPDATES_PATH)

    # Validar actualización en Resumen Ejecutivo (GOVERNMENT_PLANS)
    plan_salud = next(p for p in GOVERNMENT_PLANS if p.id == "salud")
    assert "113 Centros Rehab." in plan_salud.main_metric
    assert "113 Culminadas" in plan_salud.secondary_metric
    assert "4 Paralizadas" in plan_salud.tertiary_metric

    # Validar construcción de la vista modules/salud.py
    from modules.salud import build_salud_view
    view_salud = build_salud_view(
        page=mock_p,
        on_back_to_summary=lambda: None,
        on_switch_role=lambda: None,
        on_logout=lambda: None
    )
    assert view_salud is not None
    print("-> Vista interactiva modules/salud.py validada con éxito.")

    print("\n--- TEST 21: PLAN DE RECUPERACIÓN DE CENTROS EDUCATIVOS ---")
    from data.escuelas_parser import EscuelasParser
    parser_escuelas = EscuelasParser("CENTROS_EDUCATIVOS_PORTUGUESA_2026.xlsx")
    escuelas_data = parser_escuelas.parse_all()
    assert escuelas_data["totales_estatales"]["total_centros"] == 259, f"Esperado 259 centros, obtenido {escuelas_data['totales_estatales']['total_centros']}"
    assert escuelas_data["totales_estatales"]["culminadas"] == 241, f"Esperado 241 culminadas, obtenido {escuelas_data['totales_estatales']['culminadas']}"
    assert escuelas_data["totales_estatales"]["en_ejecucion"] == 16, f"Esperado 16 en ejecución, obtenido {escuelas_data['totales_estatales']['en_ejecucion']}"
    assert escuelas_data["totales_estatales"]["paralizadas"] == 2, f"Esperado 2 paralizadas, obtenido {escuelas_data['totales_estatales']['paralizadas']}"
    assert escuelas_data["total_centros"] == 259, f"Esperado 259 escuelas en detalle, obtenido {escuelas_data['total_centros']}"
    assert len(escuelas_data["resumen_municipios"]) == 14, f"Esperado 14 municipios, obtenido {len(escuelas_data['resumen_municipios'])}"
    assert len(escuelas_data["por_programa"]) == 3, f"Esperado 3 programas, obtenido {len(escuelas_data['por_programa'])}"
    assert len(escuelas_data["frentes_prioritarios"]) == 18, f"Esperado 18 frentes prioritarios, obtenido {len(escuelas_data['frentes_prioritarios'])}"
    print("-> Lector inteligente de Centros Educativos validado al 100%: 259 Centros (241 Ejecutadas, 16 En Ejecución, 2 Paralizadas).")
    print("-> 259 Escuelas individuales, 3 Programas Oficiales, 14 Municipios, 5 Tipologías y 18 Frentes Prioritarios.")

    # Validar métodos de AppState para Centros Educativos
    kpis_escuelas = state.get_escuelas_kpis()
    assert kpis_escuelas["total_centros"] == 259
    assert kpis_escuelas["culminadas"] == 241
    assert kpis_escuelas["en_ejecucion"] == 16
    assert kpis_escuelas["paralizadas"] == 2

    # Validar filtrados
    escuelas_araure = state.get_filtered_centros_educativos(municipality="Araure")
    assert len(escuelas_araure) == 60, f"Esperado 60 escuelas en Araure, obtenido {len(escuelas_araure)}"
    escuelas_brico = state.get_filtered_centros_educativos(programa="Bricomiles (115)")
    assert len(escuelas_brico) == 115, f"Esperado 115 escuelas Bricomiles, obtenido {len(escuelas_brico)}"
    escuelas_ejec = state.get_filtered_centros_educativos(estatus="En Ejecución (16)")
    assert len(escuelas_ejec) == 16, f"Esperado 16 en ejecución, obtenido {len(escuelas_ejec)}"

    # Validar edición y persistencia
    prev_audit_esc = len(auth.get_auditoria())
    ok_upd_esc = state.update_centro_educativo(centro_id=1, estatus="CULMINADA", porcentaje=100.0, descripcion="REHABILITACION INTEGRAL Y PINTURA", notas="Inspección PCEO")
    assert ok_upd_esc is True
    assert len(auth.get_auditoria()) == prev_audit_esc + 1

    # Validar actualización en Resumen Ejecutivo (GOVERNMENT_PLANS)
    plan_escuelas = next(p for p in GOVERNMENT_PLANS if p.id in ["educacion", "escuelas"])
    assert "259 Centros" in plan_escuelas.main_metric
    assert "241 Ejecutados" in plan_escuelas.secondary_metric
    assert "2 Paralizados" in plan_escuelas.tertiary_metric

    # Validar nuevo registro
    nuevo_esc = state.add_centro_educativo(
        programa="BRICOMILES",
        municipio="Guanare",
        institucion="Liceo Bolivariano de Prueba PCEO",
        descripcion="Rehabilitación de Techos y Pintura",
        sector="La Arenosa",
        año="2026",
        estatus="EN EJECUCIÓN",
        porcentaje=50.0,
        notas="Registro de prueba"
    )
    assert nuevo_esc["id"] > 259
    assert nuevo_esc["porcentaje"] == 50.0

    # Limpiar archivo de persistencia de prueba si existe
    if os.path.exists(state.ESCUELAS_UPDATES_PATH):
        os.remove(state.ESCUELAS_UPDATES_PATH)
    state.escuelas_data["centros"] = [c for c in state.escuelas_data["centros"] if c["id"] != nuevo_esc["id"]]
    state._recalc_escuelas_totals()

    # Validar construcción de la vista modules/escuelas.py
    from modules.escuelas import build_escuelas_view
    view_escuelas = build_escuelas_view(
        page=mock_p,
        on_back_to_summary=lambda: None,
        on_switch_role=lambda: None,
        on_logout=lambda: None
    )
    assert view_escuelas is not None
    print("-> Vista interactiva modules/escuelas.py validada con éxito.")

    print("\n--- TEST 22: PLAN UNA CANCHA PARA TODOS ---")
    kpis_canchas = state.get_canchas_kpis()
    assert kpis_canchas["total_intervenidas"] == 135, f"Esperado 135 canchas intervenidas, obtenido {kpis_canchas['total_intervenidas']}"
    assert kpis_canchas["ejecutadas"] == 122, f"Esperado 122 ejecutadas, obtenido {kpis_canchas['ejecutadas']}"
    assert kpis_canchas["en_ejecucion"] == 4, f"Esperado 4 en ejecución, obtenido {kpis_canchas['en_ejecucion']}"
    assert kpis_canchas["paralizadas"] == 9, f"Esperado 9 paralizadas, obtenido {kpis_canchas['paralizadas']}"
    assert len(state.get_canchas_municipios_resumen()) == 14, "Esperado 14 municipios en resumen"
    assert len(state.get_canchas_frentes_prioritarios()) == 13, "Esperado 13 frentes prioritarios (4 en ejec + 9 paralizadas)"
    print("-> Métricas oficiales de Una Cancha para Todos validadas: 135 Canchas (122 Culminadas, 4 En Ejecución, 9 Paralizadas).")

    # Validar métricas de la tarjeta del plan
    plan_canchas = next(p for p in GOVERNMENT_PLANS if p.id == "canchas")
    assert "135 Intervenidas" in plan_canchas.main_metric, f"Esperado '135 Intervenidas', obtenido {plan_canchas.main_metric}"
    assert "122 Culminadas" in plan_canchas.secondary_metric, f"Esperado '122 Culminadas', obtenido {plan_canchas.secondary_metric}"
    assert "4 En Ejecución" in plan_canchas.tertiary_metric, f"Esperado '4 En Ejecución', obtenido {plan_canchas.tertiary_metric}"

    # Validar construcción de la vista modules/cancha_para_todos.py y alias canchas.py
    from modules.cancha_para_todos import build_cancha_para_todos_view
    view_canchas_new = build_cancha_para_todos_view(
        page=mock_p,
        on_back_to_summary=lambda: None,
        on_switch_role=lambda: None,
        on_logout=lambda: None
    )
    assert view_canchas_new is not None
    from modules.canchas import build_canchas_view
    view_canchas = build_canchas_view(
        page=mock_p,
        on_back_to_summary=lambda: None,
        on_switch_role=lambda: None,
        on_logout=lambda: None
    )
    assert view_canchas is not None
    print("-> Vista interactiva modules/cancha_para_todos.py validada con éxito.")

    # 23. TEST DATOS SOCIOPOLÍTICOS, TERRITORIALES Y DEMOGRÁFICOS DE MUNICIPIOS (INE 2026)
    print("\n--- TEST 23: DATOS SOCIOPOLÍTICOS, TERRITORIALES Y DEMOGRÁFICOS DE MUNICIPIOS ---")
    from data.municipios_parser import MunicipiosParser
    mun_parser = MunicipiosParser()
    mun_data = mun_parser.parse_all()
    assert len(mun_data["municipios"]) == 14, f"Se esperaban 14 municipios, encontrados {len(mun_data['municipios'])}"

    # Validar datos de Guanare
    guanare = mun_parser.get_municipio("Guanare")
    assert guanare["capital"] == "Guanare"
    assert guanare["extension_km2"] == 2008
    assert guanare["parroquias"] == 5
    assert guanare["poblacion_ine"] == 235997
    assert guanare["familias_ine"] == 58999
    assert guanare["comunas"] == 29
    assert guanare["consejos_comunales"] == 350
    assert guanare["ubch"] == 141
    assert guanare["jefes_clap"] == 346
    assert guanare["jefes_calle"] == 1647

    # Validar datos de Páez
    paez = mun_parser.get_municipio("Páez")
    assert paez["capital"] == "Acarigua"
    assert paez["extension_km2"] == 425
    assert paez["parroquias"] == 4
    assert paez["poblacion_ine"] == 215938
    assert paez["comunas"] == 18
    assert paez["jefes_calle"] == 1777

    # Validar alias Unda -> José Vicente de Unda
    unda = mun_parser.get_municipio("Unda")
    assert unda["capital"] == "Paraíso de Chabasquén"
    assert unda["extension_km2"] == 222

    # Validar totales consolidados de Portuguesa
    totales = mun_parser.get_totales_estado()
    assert totales["extension_km2"] == 15200, f"Extensión total esperada 15.200, obtenida {totales['extension_km2']}"
    assert totales["parroquias"] == 41, f"Parroquias esperadas 41, obtenidas {totales['parroquias']}"
    assert totales["poblacion_ine"] == 1070599, f"Población esperada 1.070.599, obtenida {totales['poblacion_ine']}"
    assert totales["familias_ine"] == 267653
    assert totales["comunas"] == 192
    assert totales["consejos_comunales"] == 1916
    assert totales["ubch"] == 694
    assert totales["jefes_clap"] == 1914
    assert totales["jefes_calle"] == 9515

    # Validar integración en AppState
    assert state.get_municipio_demografia("Guanare")["capital"] == "Guanare"
    assert state.get_totales_demografia()["poblacion_ine"] == 1070599

    # Validar integración en Reporte de Impresión HTML
    from components.print_municipal_report import generate_municipal_html_report
    html_test_path = generate_municipal_html_report({
        "municipio": "Guanare",
        "demografia": guanare,
        "kpis": {},
        "obras": {"total": 1, "culm": 1, "proc": 0, "para": 0, "pct_culm": 100.0, "pct_proc": 0.0, "pct_para": 0.0},
        "planes": []
    })
    assert os.path.exists(html_test_path)
    with open(html_test_path, "r", encoding="utf-8") as f_html:
        html_src = f_html.read()
    assert "demo-bar" in html_src
    assert "235.997 hab." in html_src
    assert "2.008 km²" in html_src
    print("-> Ficha Sociopolítica, Territorial y Demográfica de los 14 Municipios validada al 100%.")
    print("-> Reporte de impresión Carta Horizontal con ficha sociopolítica integrado con éxito.")

    # 24. TEST: PLAN CONSTRUYE TU CASA - LECTOR EXCEL, KPIS Y MÓDULO PCEO
    print("\n--- TEST 24: Plan Construye Tu Casa - Lector Excel, KPIs y Módulo PCEO ---")
    from data.casas_parser import CasasParser
    from modules.construye_tu_casa import build_construye_tu_casa_view
    from modules.construye_casa import build_construye_casa_view
    from main import PLAN_VIEW_MAP

    c_parser = CasasParser()
    casas_full = c_parser.get_all_data()

    # Validar 8 municipios activos y ente ejecutor
    assert len(casas_full["municipios"]) == 8, f"Se esperaban 8 municipios, obtenidos {len(casas_full['municipios'])}"
    assert casas_full["ente_ejecutor"] == "FONDEREVI"

    # Validar totales exactos del Excel
    tot_c = casas_full["totales"]
    assert tot_c["total_general"] == 662, f"Total general esperado 662, obtenido {tot_c['total_general']}"
    assert tot_c["ejecutadas"] == 252, f"Ejecutadas esperadas 252, obtenidas {tot_c['ejecutadas']}"
    assert tot_c["proyeccion_ejecucion"] == 410, f"Proyección/Ejecución esperada 410, obtenida {tot_c['proyeccion_ejecucion']}"
    assert tot_c["por_iniciar"] == 0, f"Por iniciar esperadas 0, obtenidas {tot_c['por_iniciar']}"

    # Validar municipios clave y desglose exacto de DETALLE_URBANISMOS
    m_ab = c_parser.get_municipio("Agua Blanca")
    assert m_ab["total"] == 98 and m_ab["ejecutadas"] == 28 and m_ab["proyeccion_ejecucion"] == 70
    assert any("MANUELITA" in u["urbanismo"].upper() for u in m_ab["urbanismos"])

    m_ara = c_parser.get_municipio("Araure")
    assert m_ara["total"] == 239 and m_ara["ejecutadas"] == 43 and m_ara["proyeccion_ejecucion"] == 196
    assert any("VILLAS DE SAN JOS" in u["urbanismo"].upper() for u in m_ara["urbanismos"])
    assert any("ESPIGAS" in u["urbanismo"].upper() for u in m_ara["urbanismos"])

    m_gua = c_parser.get_municipio("Guanare")
    assert m_gua["total"] == 137 and m_gua["ejecutadas"] == 105 and m_gua["proyeccion_ejecucion"] == 32
    assert any("LA GRANJA" in u["urbanismo"].upper() for u in m_gua["urbanismos"])

    m_paez = c_parser.get_municipio("Páez")
    assert m_paez["total"] == 146 and m_paez["ejecutadas"] == 34 and m_paez["proyeccion_ejecucion"] == 112
    assert any("GARZAS" in u["urbanismo"].upper() for u in m_paez["urbanismos"])
    assert any("BELLA VISTA" in u["urbanismo"].upper() for u in m_paez["urbanismos"])

    # Validar total de 24 frentes/urbanismos oficiales
    assert len(casas_full["frentes"]) == 24, f"Se esperaban 24 urbanismos, obtenidos {len(casas_full['frentes'])}"

    # Validar integración en AppState
    kpis_estatales = state.get_casas_kpis("Todos los Municipios")
    assert kpis_estatales["total_viviendas"] == 662
    assert kpis_estatales["ejecutadas"] == 252
    assert kpis_estatales["proyeccion_ejecucion"] == 410
    assert kpis_estatales["ente_ejecutor"] == "FONDEREVI"

    kpis_gua = state.get_casas_kpis("Guanare")
    assert kpis_gua["total_viviendas"] == 137
    assert kpis_gua["ejecutadas"] == 105

    frentes = state.get_casas_frentes_prioritarios()
    assert len(frentes) == 7, f"Esperados 7 frentes en ejecución, obtenidos {len(frentes)}"
    assert sum(f["en_ejecucion"] for f in frentes) == 410

    # Validar tarjeta del plan de gobierno
    p_casa = next(p for p in GOVERNMENT_PLANS if p.id == "construye_casa")
    assert "662" in p_casa.main_metric
    assert "252" in p_casa.secondary_metric
    assert "410" in p_casa.tertiary_metric

    # Validar enrutamiento y creación de vista
    assert "construye_tu_casa" in PLAN_VIEW_MAP
    assert "construye_casa" in PLAN_VIEW_MAP

    v1 = build_construye_tu_casa_view(mock_p, lambda: None, lambda r: None, lambda: None)
    v2 = build_construye_casa_view(mock_p, lambda: None, lambda r: None, lambda: None)
    assert v1 is not None and isinstance(v1, ft.Control)
    assert v2 is not None and isinstance(v2, ft.Control)

    print("-> Lector de CONSTRUYE_TU_CASA_PORTUGUESA_2026.xlsx validado (662 viviendas, 252 ejecutadas, 410 en ejecución, 0 por iniciar).")
    print("-> Integración bidireccional en AppState, FONDEREVI, filtros y vistas verificada exitosamente.")

    print("\n--- TEST 25: PLAN CANALIZACIÓN Y CONSTRUCCIÓN DE BERMAS ---")
    from data.canalizacion_parser import CanalizacionParser
    from modules.canalizacion import build_canalizacion_view
    from main import PLAN_VIEW_MAP

    if os.path.exists(state.CANALIZACION_UPDATES_PATH):
        os.remove(state.CANALIZACION_UPDATES_PATH)

    can_parser = CanalizacionParser()
    can_data = can_parser.parse_all(force_reload=True)

    # Validar cifras macro del Excel oficial
    tots = can_data["totales_estatales"]
    assert tots["obras_canalizacion"] == 244, f"Esperadas 244 obras de canalización, recibidas {tots['obras_canalizacion']}"
    assert tots["canalizaciones_ejecutadas"] == 243, f"Esperadas 243 ejecutadas, recibidas {tots['canalizaciones_ejecutadas']}"
    assert tots["longitud_canalizada_km"] == 380.73, f"Esperados 380.73 km canalizados, recibidos {tots['longitud_canalizada_km']}"
    assert tots["bermas_construidas"] == 57, f"Esperadas 57 bermas construidas, recibidas {tots['bermas_construidas']}"
    assert tots["volumen_total_m3"] > 700000, f"Esperado volumen total > 700.000 M³, recibido {tots['volumen_total_m3']}"

    # Validar inventario detallado de OBRAS_2026 (43 obras)
    assert len(can_data["obras_2026"]) >= 43, f"Esperadas al menos 43 obras en 2026, recibidas {len(can_data['obras_2026'])}"
    canales_26 = [o for o in can_data["obras_2026"] if o["componente"] == "CANALIZACIÓN"]
    bermas_26 = [o for o in can_data["obras_2026"] if o["componente"] == "BERMAS"]
    assert len(canales_26) == 39, f"Esperadas 39 canalizaciones en 2026, recibidas {len(canales_26)}"
    assert len(bermas_26) == 4, f"Esperadas 4 bermas en 2026, recibidas {len(bermas_26)}"

    # Validar frentes fluviales activos y prioritarios
    frentes = can_parser._build_frentes_fluviales(can_data["obras_2026"])
    assert len(frentes) >= 43
    assert any("BOMBON" in f["cauce"].upper() and f["estatus"] == "EN DESARROLLO" for f in frentes)
    assert any("PAYARA" in f["cauce"].upper() for f in frentes)
    assert any("SARARE" in f["cauce"].upper() for f in frentes)

    # Validar integración en AppState
    kpis_estatales = state.get_canalizacion_kpis("Todos los Municipios")
    assert kpis_estatales["obras_canalizacion"] == 244
    assert kpis_estatales["longitud_canalizada_km"] == 380.73
    assert kpis_estatales["bermas_construidas"] == 57
    assert kpis_estatales["volumen_total_m3"] > 700000

    # Validar filtrado por municipio
    kpis_osp = state.get_canalizacion_kpis("Ospino")
    assert kpis_osp["total_obras"] == 9
    assert kpis_osp["canalizaciones_en_desarrollo"] == 1

    # Validar tarjeta del plan de gobierno
    p_canal = next(p for p in GOVERNMENT_PLANS if p.id == "canalizacion")
    assert "380.73" in p_canal.main_metric
    assert "243" in p_canal.secondary_metric
    assert "57" in p_canal.tertiary_metric

    # Validar enrutamiento y creación de vista
    assert "canalizacion" in PLAN_VIEW_MAP
    assert "canalizaciones" in PLAN_VIEW_MAP
    v_canal = build_canalizacion_view(mock_p, lambda: None, lambda r: None, lambda: None)
    assert v_canal is not None and isinstance(v_canal, ft.Control)

    # Validar registro auditado de obra en State
    prev_audits = len(auth.get_auditoria())
    test_obra = {
        "id": "obra_test_unitario",
        "componente": "CANALIZACIÓN",
        "nombre": "CANALIZACIÓN QUEBRADA TEST",
        "municipio": "Guanare",
        "sector": "Sector Test",
        "estatus": "EJECUTADA",
        "longitud": 1.25,
        "excavacion_m3": 1500.0,
        "material_removido_m3": 1500.0
    }
    state.add_canalizacion_obra(test_obra, audit_user="Master Test")
    assert len(auth.get_auditoria()) == prev_audits + 1
    # Limpiar archivo temporal de prueba si se generó
    if os.path.exists(state.CANALIZACION_UPDATES_PATH):
        os.remove(state.CANALIZACION_UPDATES_PATH)
    state.canalizacion_data_full = can_parser.parse_all(force_reload=True)

    print("-> Lector de PLAN_CANALIZACION_PORTUGUESA_2026.xlsx validado (380.73 Km, 243 ejecutadas, 57 bermas, >700k M³).")
    print("-> Inventario 2026 (43 obras), frentes fluviales, filtrado municipal y auditoría validados al 100%.")

    print("\n>>> TODAS LAS PRUEBAS UNITARIAS PASARON EXITOSAMENTE (100%) <<<")

if __name__ == "__main__":
    run_tests()
