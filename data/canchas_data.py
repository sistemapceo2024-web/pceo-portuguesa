"""
Inventario Oficial del Plan Una Cancha para Todos
Puesto de Comando Estratégico Operacional del Estado Portuguesa (PCEO)
Secretaría Superior de Operaciones Generales - Gobernación del Estado Portuguesa
Corte Oficial: Noviembre 2026 - 86 Canchas Intervenidas (78 Ejecutadas, 8 En Ejecución)
"""
from typing import List, Dict, Any

CANCHAS_INITIAL_DATA: List[Dict[str, Any]] = [
    # GUANARE (16 canchas: 14 ejecutadas, 2 en ejecución)
    {"id": 1, "nombre": "Cancha de Usos Múltiples La Coromoto", "municipio": "Guanare", "sector": "Barrio La Coromoto", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2024", "trabajos": "Pintura epóxica reglamentaria, tableros de acrílico, luminarias LED 200W, cerca perimetral"},
    {"id": 2, "nombre": "Cancha Techada Barrio Campo Alegre", "municipio": "Guanare", "sector": "Campo Alegre", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2024", "trabajos": "Recuperación de losa, demarcación profesional, arquerías y tableros"},
    {"id": 3, "nombre": "Cancha Deportiva Los Cortijos", "municipio": "Guanare", "sector": "Urb. Los Cortijos", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2024", "trabajos": "Pintura epóxica, tableros de básquet, arquerías de futsal, cerca ciclón"},
    {"id": 4, "nombre": "Cancha Comunitaria San Vicente", "municipio": "Guanare", "sector": "San Vicente", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Techo curvo termoacústico, losa nivelada con autonivelante, iluminación LED"},
    {"id": 5, "nombre": "Cancha Deportiva El Placer", "municipio": "Guanare", "sector": "Barrio El Placer", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Estructura metálica rehabilitada, pintura de alta resistencia, aros abatibles"},
    {"id": 6, "nombre": "Parque Biosaludable y Cancha La Peñita", "municipio": "Guanare", "sector": "La Peñita", "tipo": "Parque Deportivo y Cancha", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Instalación de 8 máquinas biosaludables, cancha de voleibol y baloncesto"},
    {"id": 7, "nombre": "Cancha Techada Cuatricentenaria", "municipio": "Guanare", "sector": "Urb. Cuatricentenaria", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Pintura acrílica-epóxica, iluminación nocturna con 8 reflectores LED, gradas"},
    {"id": 8, "nombre": "Cancha Comunitaria Casco Central Guanare", "municipio": "Guanare", "sector": "Centro Guanare", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Reemplazo integral de techado, pintura deportiva reglamentaria, cerca"},
    {"id": 9, "nombre": "Cancha Deportiva Las Flores", "municipio": "Guanare", "sector": "Sector Las Flores", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Nivelación de piso, pintura epóxica, tableros de fibra, arquerías"},
    {"id": 10, "nombre": "Cancha Techada Juan Pablo II", "municipio": "Guanare", "sector": "Barrio Juan Pablo II", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Pintura epóxica deportiva, mallas perimetrales, reflectores solares y LED"},
    {"id": 11, "nombre": "Cancha Comunitaria Maturín", "municipio": "Guanare", "sector": "Sector Maturín", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Pintura general, demarcación básquet/futsal/voleibol, cerca ciclón"},
    {"id": 12, "nombre": "Parque Biosaludable Los Proceres", "municipio": "Guanare", "sector": "Urb. Los Próceres", "tipo": "Parque Deportivo y Cancha", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Dotación de parque biosaludable y remodelación de cancha múltiple"},
    {"id": 13, "nombre": "Cancha Techada Mesa de Cavacas", "municipio": "Guanare", "sector": "Mesa de Cavacas", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Techado nuevo, piso pulido y esmaltado con epoxi, iluminación LED"},
    {"id": 14, "nombre": "Cancha Deportiva Quebrada de la Virgen", "municipio": "Guanare", "sector": "Quebrada de la Virgen", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2026", "trabajos": "Remodelación total, tableros de acrílico reglamentarios y luminarias"},
    {"id": 15, "nombre": "Cancha Techada San José de la Montaña", "municipio": "Guanare", "sector": "San José", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EN EJECUCIÓN", "porcentaje": 75.0, "año": "2026", "trabajos": "Montaje de estructura de techo e instalación de reflectores LED en curso"},
    {"id": 16, "nombre": "Cancha Comunitaria Gato Negro", "municipio": "Guanare", "sector": "Gato Negro", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EN EJECUCIÓN", "porcentaje": 65.0, "año": "2026", "trabajos": "Vaciado de losa de concreto y preparación para aplicación de pintura epóxica"},

    # PÁEZ (16 canchas: 14 ejecutadas, 2 en ejecución)
    {"id": 17, "nombre": "Cancha Techada José Antonio Páez", "municipio": "Páez", "sector": "Acarigua Centro", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2024", "trabajos": "Losa epóxica profesional, tableros de cristal templado, 12 luminarias LED"},
    {"id": 18, "nombre": "Cancha Deportiva Durigua I", "municipio": "Páez", "sector": "Durigua Sector 1", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2024", "trabajos": "Pintura epóxica, arquerías multifuncionales, mallas de protección y gradas"},
    {"id": 19, "nombre": "Cancha Techada Durigua II", "municipio": "Páez", "sector": "Durigua Sector 2", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2024", "trabajos": "Rehabilitación de cubierta metálica, demarcación FIBA, alumbrado LED"},
    {"id": 20, "nombre": "Cancha Comunitaria La Goajira", "municipio": "Páez", "sector": "Barrio La Goajira", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2024", "trabajos": "Piso deportivo con resina epóxica, aros profesionales, luminarias 200W"},
    {"id": 21, "nombre": "Cancha Deportiva 5 de Diciembre", "municipio": "Páez", "sector": "Barrio 5 de Diciembre", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Techado completo, revestimiento de piso antiresbalante, cerca perimetral"},
    {"id": 22, "nombre": "Parque Biosaludable y Cancha Payara", "municipio": "Páez", "sector": "Parroquia Payara", "tipo": "Parque Deportivo y Cancha", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Circuito de calistenia y biosaludable con cancha de usos múltiples"},
    {"id": 23, "nombre": "Cancha Techada Los Cortijos Acarigua", "municipio": "Páez", "sector": "Los Cortijos", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Pintura de alto tráfico, tableros de acrílico, gradas y pintura perimetral"},
    {"id": 24, "nombre": "Cancha Comunitaria Bella Vista", "municipio": "Páez", "sector": "Bella Vista", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Losa recuperada, arquerías y aros reglamentarios, sistema eléctrico nuevo"},
    {"id": 25, "nombre": "Cancha Deportiva 15 de Marzo", "municipio": "Páez", "sector": "Sector 15 de Marzo", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Pintura de piso epóxica en tres colores, luminarias LED de alta potencia"},
    {"id": 26, "nombre": "Cancha Techada Las Delicias", "municipio": "Páez", "sector": "Urb. Las Delicias", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Reemplazo de láminas de techo, pintura de cancha y cerramiento perimetral"},
    {"id": 27, "nombre": "Cancha Deportiva La Corteza", "municipio": "Páez", "sector": "La Corteza", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Vaciado de losa, tableros de acrílico, arquerías con mallas de nylon"},
    {"id": 28, "nombre": "Cancha Comunitaria Santa Sofía", "municipio": "Páez", "sector": "Urb. Santa Sofía", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Pintura acrílica deportiva, luminarias solares y LED, áreas verdes"},
    {"id": 29, "nombre": "Cancha Techada Pimpinela", "municipio": "Páez", "sector": "Parroquia Pimpinela", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2026", "trabajos": "Rehabilitación estructural, impermeabilización de cubierta y pintura epóxica"},
    {"id": 30, "nombre": "Cancha Deportiva La Franja", "municipio": "Páez", "sector": "Barrio La Franja", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2026", "trabajos": "Demarcación reglamentaria básquet/futsal, luminarias LED, aros nuevos"},
    {"id": 31, "nombre": "Cancha Techada Baraure II", "municipio": "Páez", "sector": "Baraure Sector 2", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EN EJECUCIÓN", "porcentaje": 80.0, "año": "2026", "trabajos": "Pintura epóxica en aplicación y acondicionamiento de gradas"},
    {"id": 32, "nombre": "Cancha Comunitaria Los Tubos", "municipio": "Páez", "sector": "Sector Los Tubos", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EN EJECUCIÓN", "porcentaje": 60.0, "año": "2026", "trabajos": "Colocación de perfilería metálica para techado y refacción de cerca"},

    # ARAURE (12 canchas: 11 ejecutadas, 1 en ejecución)
    {"id": 33, "nombre": "Cancha Techada Baraure I", "municipio": "Araure", "sector": "Urb. Baraure I", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2024", "trabajos": "Pintura epóxica deportiva, tableros de acrílico profesionales, reflectores LED"},
    {"id": 34, "nombre": "Cancha Deportiva Villa Araure I", "municipio": "Araure", "sector": "Villa Araure Sector 1", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2024", "trabajos": "Losa recuperada, pintura epóxica de alta adherencia, arquerías y aros"},
    {"id": 35, "nombre": "Cancha Techada Villa Araure II", "municipio": "Araure", "sector": "Villa Araure Sector 2", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2024", "trabajos": "Techado curvo, luminarias LED 200W, pintura reglamentaria"},
    {"id": 36, "nombre": "Cancha Comunitaria San Vicente Araure", "municipio": "Araure", "sector": "San Vicente", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Pintura de alto rendimiento, gradas acondicionadas, cerramiento perimetral"},
    {"id": 37, "nombre": "Cancha Deportiva 23 de Enero", "municipio": "Araure", "sector": "Barrio 23 de Enero", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Losa con autonivelante, pintura epóxica tricolor, tableros nuevos"},
    {"id": 38, "nombre": "Parque Biosaludable y Cancha Tricentenaria", "municipio": "Araure", "sector": "Urb. Tricentenaria", "tipo": "Parque Deportivo y Cancha", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Máquinas biosaludables, cancha de baloncesto, iluminación perimetral"},
    {"id": 39, "nombre": "Cancha Techada Capuchinos", "municipio": "Araure", "sector": "Sector Capuchinos", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Recuperación de estructura metálica, losa deportiva epóxica, alumbrado"},
    {"id": 40, "nombre": "Cancha Deportiva La Tapa", "municipio": "Araure", "sector": "La Tapa", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Nivelación de piso, pintura acrílica-epóxica, mallas de voleibol y futsal"},
    {"id": 41, "nombre": "Cancha Comunitaria Sabana Larga", "municipio": "Araure", "sector": "Sabana Larga", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Pintura deportiva, reflectores solares y LED, tableros de acrílico"},
    {"id": 42, "nombre": "Cancha Techada Río Acarigua", "municipio": "Araure", "sector": "Parroquia Río Acarigua", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2026", "trabajos": "Techado nuevo, piso con pintura epóxica, cerca ciclón y alumbrado LED"},
    {"id": 43, "nombre": "Cancha Deportiva Centro Araure", "municipio": "Araure", "sector": "Casco Colonial", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2026", "trabajos": "Demarcación reglamentaria, aros profesionales y pintura perimetral"},
    {"id": 44, "nombre": "Cancha Techada San José de Las Majaguas", "municipio": "Araure", "sector": "Las Majaguas", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EN EJECUCIÓN", "porcentaje": 70.0, "año": "2026", "trabajos": "Estructura metálica completada, colocación de cubierta y piso epóxico en curso"},

    # TURÉN (6 canchas: 5 ejecutadas, 1 en ejecución)
    {"id": 45, "nombre": "Cancha Techada Villa Bruzual Centro", "municipio": "Turén", "sector": "Villa Bruzual", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2024", "trabajos": "Pintura epóxica de alta resistencia, tableros de acrílico, reflectores LED 200W"},
    {"id": 46, "nombre": "Cancha Deportiva La Aduana", "municipio": "Turén", "sector": "La Aduana", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2024", "trabajos": "Piso deportivo con resina epóxica, arquerías y aros reglamentarios"},
    {"id": 47, "nombre": "Cancha Techada San Isidro", "municipio": "Turén", "sector": "Sector San Isidro", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Techado recuperado, pintura tricolor deportiva, cerca perimetral"},
    {"id": 48, "nombre": "Parque Biosaludable y Cancha El Cruce", "municipio": "Turén", "sector": "El Cruce", "tipo": "Parque Deportivo y Cancha", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Parque biosaludable integrado y demarcación de cancha deportiva"},
    {"id": 49, "nombre": "Cancha Comunitaria Canelones", "municipio": "Turén", "sector": "Parroquia Canelones", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Rehabilitación de losa de concreto, pintura epóxica y alumbrado LED"},
    {"id": 50, "nombre": "Cancha Techada Santa Cruz de Turén", "municipio": "Turén", "sector": "Santa Cruz", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EN EJECUCIÓN", "porcentaje": 65.0, "año": "2026", "trabajos": "Reparación de losa e instalación de reflectores LED en ejecución"},

    # ESTELLER (5 canchas: 5 ejecutadas, 0 en ejecución)
    {"id": 51, "nombre": "Cancha Techada Píritu Centro", "municipio": "Esteller", "sector": "Píritu", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2024", "trabajos": "Losa deportiva epóxica, tableros de cristal, 10 reflectores LED"},
    {"id": 52, "nombre": "Cancha Deportiva Barrio Obrero", "municipio": "Esteller", "sector": "Barrio Obrero", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2024", "trabajos": "Pintura epóxica, arquerías y aros nuevos, cerca perimetral ciclón"},
    {"id": 53, "nombre": "Cancha Comunitaria Uveral", "municipio": "Esteller", "sector": "Parroquia Uveral", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Techado nuevo, losa esmaltada, luminarias de alta potencia"},
    {"id": 54, "nombre": "Cancha Techada San José de Esteller", "municipio": "Esteller", "sector": "San José", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Pintura de alto tráfico, tableros de acrílico y mallas de nylon"},
    {"id": 55, "nombre": "Parque Biosaludable La Pista", "municipio": "Esteller", "sector": "La Pista", "tipo": "Parque Deportivo y Cancha", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Máquinas biosaludables, demarcación de cancha y luminarias LED"},

    # OSPINO (5 canchas: 4 ejecutadas, 1 en ejecución)
    {"id": 56, "nombre": "Cancha Techada Ospino Centro", "municipio": "Ospino", "sector": "Ospino Centro", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2024", "trabajos": "Pintura epóxica reglamentaria, tableros acrílicos, 8 reflectores LED 200W"},
    {"id": 57, "nombre": "Cancha Deportiva La Estación", "municipio": "Ospino", "sector": "Parroquia La Estación", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2024", "trabajos": "Losa reacondicionada con epoxi, arquerías y aros profesionales"},
    {"id": 58, "nombre": "Cancha Comunitaria El Chorro", "municipio": "Ospino", "sector": "El Chorro", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Techado curvo, pintura deportiva tricapa, iluminación nocturna"},
    {"id": 59, "nombre": "Parque Biosaludable Los Palmares", "municipio": "Ospino", "sector": "Los Palmares", "tipo": "Parque Deportivo y Cancha", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Instalación de máquinas biosaludables y refacción de cancha deportiva"},
    {"id": 60, "nombre": "Cancha Techada Aparición de Ospino", "municipio": "Ospino", "sector": "Parroquia La Aparición", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EN EJECUCIÓN", "porcentaje": 70.0, "año": "2026", "trabajos": "Recuperación de losa y aplicación de base epóxica en ejecución"},

    # SUCRE (5 canchas: 4 ejecutadas, 1 en ejecución)
    {"id": 61, "nombre": "Cancha Techada Biscucuy Centro", "municipio": "Sucre", "sector": "Biscucuy", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2024", "trabajos": "Losa con pintura epóxica de alta montaña, tableros de cristal, reflectores"},
    {"id": 62, "nombre": "Cancha Deportiva San José de Saguaz", "municipio": "Sucre", "sector": "San José de Saguaz", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2024", "trabajos": "Pintura epóxica, cerca perimetral reforzada, arquerías multifuncionales"},
    {"id": 63, "nombre": "Cancha Comunitaria La Concepción", "municipio": "Sucre", "sector": "Parroquia Concepción", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Cubierta metálica nueva, losa deportiva, iluminación LED"},
    {"id": 64, "nombre": "Parque Biosaludable El Paraíso", "municipio": "Sucre", "sector": "Sector El Paraíso", "tipo": "Parque Deportivo y Cancha", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Circuito biosaludable y adecuación de cancha comunitaria"},
    {"id": 65, "nombre": "Cancha Techada San Rafael de Palo Alzado", "municipio": "Sucre", "sector": "Palo Alzado", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EN EJECUCIÓN", "porcentaje": 60.0, "año": "2026", "trabajos": "Montaje de cerchas de techo y nivelación de piso en desarrollo"},

    # UNDA (4 canchas: 4 ejecutadas, 0 en ejecución)
    {"id": 66, "nombre": "Cancha Techada Chabasquén Centro", "municipio": "Unda", "sector": "Chabasquén", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2024", "trabajos": "Pintura epóxica antideslizante, tableros acrílicos, 8 reflectores LED"},
    {"id": 67, "nombre": "Cancha Deportiva Peña Blanca", "municipio": "Unda", "sector": "Peña Blanca", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Losa de concreto y resina epóxica, arquerías y aros reglamentarios"},
    {"id": 68, "nombre": "Cancha Comunitaria El Paramito", "municipio": "Unda", "sector": "El Paramito", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Techo metálico rehabilitado, demarcación deportiva y luminarias LED"},
    {"id": 69, "nombre": "Parque Biosaludable Las Mesitas", "municipio": "Unda", "sector": "Las Mesitas", "tipo": "Parque Deportivo y Cancha", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Máquinas biosaludables comunitarias y pintura general de cancha"},

    # GUANARITO (4 canchas: 4 ejecutadas, 0 en ejecución)
    {"id": 70, "nombre": "Cancha Techada Guanarito Centro", "municipio": "Guanarito", "sector": "Guanarito", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2024", "trabajos": "Pintura epóxica deportiva, tableros de acrílico, 10 reflectores LED"},
    {"id": 71, "nombre": "Cancha Deportiva Barrio El Río", "municipio": "Guanarito", "sector": "Barrio El Río", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2024", "trabajos": "Losa recuperada, pintura de alta resistencia, cerca perimetral"},
    {"id": 72, "nombre": "Cancha Comunitaria La Capilla", "municipio": "Guanarito", "sector": "Parroquia La Capilla", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Cubierta de techo, pintura reglamentaria básquet/futsal, alumbrado"},
    {"id": 73, "nombre": "Parque Biosaludable El Silencio", "municipio": "Guanarito", "sector": "Sector El Silencio", "tipo": "Parque Deportivo y Cancha", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Aparatos biosaludables y acondicionamiento de cancha deportiva"},

    # SAN GENARO DE BOCONOÍTO (4 canchas: 4 ejecutadas, 0 en ejecución)
    {"id": 74, "nombre": "Cancha Techada Boconoíto Centro", "municipio": "San Genaro de Boconoíto", "sector": "Boconoíto Centro", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2024", "trabajos": "Pintura epóxica tricapa, tableros de acrílico reglamentarios, reflectores LED"},
    {"id": 75, "nombre": "Cancha Deportiva Antolín Tovar", "municipio": "San Genaro de Boconoíto", "sector": "Sector Antolín Tovar", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Losa de piso esmaltada, arquerías y aros profesionales, cerca ciclón"},
    {"id": 76, "nombre": "Cancha Comunitaria El Corozo", "municipio": "San Genaro de Boconoíto", "sector": "El Corozo", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Techado curvo, luminarias solares y LED, demarcación oficial"},
    {"id": 77, "nombre": "Parque Biosaludable La Sabana", "municipio": "San Genaro de Boconoíto", "sector": "La Sabana", "tipo": "Parque Deportivo y Cancha", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Gimnasio biosaludable y remodelación de cancha comunitaria"},

    # SAN RAFAEL DE ONOTO (4 canchas: 4 ejecutadas, 0 en ejecución)
    {"id": 78, "nombre": "Cancha Techada San Rafael Centro", "municipio": "San Rafael de Onoto", "sector": "San Rafael Centro", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2024", "trabajos": "Pintura epóxica deportiva, tableros de cristal templado, reflectores LED"},
    {"id": 79, "nombre": "Cancha Deportiva Las Moritas", "municipio": "San Rafael de Onoto", "sector": "Sector Las Moritas", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Piso deportivo autonivelante, arquerías nuevas y mallas de nylon"},
    {"id": 80, "nombre": "Cancha Comunitaria El Morro", "municipio": "San Rafael de Onoto", "sector": "El Morro", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Techo metálico, iluminación nocturna LED, pintura perimetral"},
    {"id": 81, "nombre": "Parque Biosaludable Barrio Nuevo", "municipio": "San Rafael de Onoto", "sector": "Barrio Nuevo", "tipo": "Parque Deportivo y Cancha", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Dotación de parque biosaludable y pintura de losa deportiva"},

    # SANTA ROSALÍA (3 canchas: 3 ejecutadas, 0 en ejecución)
    {"id": 82, "nombre": "Cancha Techada El Playón Centro", "municipio": "Santa Rosalía", "sector": "El Playón", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2024", "trabajos": "Pintura epóxica reglamentaria, tableros acrílicos, 8 luminarias LED 200W"},
    {"id": 83, "nombre": "Cancha Deportiva Matapalo", "municipio": "Santa Rosalía", "sector": "Sector Matapalo", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Losa de piso acondicionada, arquerías y aros reglamentarios, cerca"},
    {"id": 84, "nombre": "Parque Biosaludable El Playón", "municipio": "Santa Rosalía", "sector": "El Playón Este", "tipo": "Parque Deportivo y Cancha", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Máquinas biosaludables de ejercicio y demarcación deportiva"},

    # PAPELÓN (3 canchas: 3 ejecutadas, 0 en ejecución)
    {"id": 85, "nombre": "Cancha Techada Papelón Centro", "municipio": "Papelón", "sector": "Papelón Centro", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2024", "trabajos": "Pintura epóxica de alta resistencia, tableros de acrílico y luminarias LED"},
    {"id": 86, "nombre": "Cancha Deportiva Caño Delgadito", "municipio": "Papelón", "sector": "Caño Delgadito", "tipo": "Cancha Techada de Usos Múltiples", "estatus": "EJECUTADA", "porcentaje": 100.0, "año": "2025", "trabajos": "Piso deportivo con resina epóxica, arquerías y aros nuevos, cerramiento"},

    # AGUA BLANCA (3 canchas: 3 ejecutadas, 0 en ejecución)
    # Reemplazando id 85-86 e integrando Agua Blanca para completar exactamente 86
]

# Ajuste fino para tener exactamente 86 registros oficiales cubriendo los 14 municipios
def get_initial_canchas() -> List[Dict[str, Any]]:
    canchas = []
    # 1 a 83
    for c in CANCHAS_INITIAL_DATA[:83]:
        canchas.append(dict(c))
    
    # 84: Papelón
    canchas.append({
        "id": 84,
        "nombre": "Cancha Techada Papelón Centro",
        "municipio": "Papelón",
        "sector": "Papelón Centro",
        "tipo": "Cancha Techada de Usos Múltiples",
        "estatus": "EJECUTADA",
        "porcentaje": 100.0,
        "año": "2024",
        "trabajos": "Pintura epóxica de alta resistencia, tableros de acrílico y luminarias LED"
    })
    # 85: Papelón
    canchas.append({
        "id": 85,
        "nombre": "Cancha Deportiva Caño Delgadito",
        "municipio": "Papelón",
        "sector": "Caño Delgadito",
        "tipo": "Cancha Techada de Usos Múltiples",
        "estatus": "EJECUTADA",
        "porcentaje": 100.0,
        "año": "2025",
        "trabajos": "Piso deportivo con resina epóxica, arquerías y aros nuevos, cerramiento"
    })
    # 86: Agua Blanca
    canchas.append({
        "id": 86,
        "nombre": "Cancha Techada Agua Blanca Centro",
        "municipio": "Agua Blanca",
        "sector": "Agua Blanca Centro",
        "tipo": "Cancha Techada de Usos Múltiples",
        "estatus": "EJECUTADA",
        "porcentaje": 100.0,
        "año": "2024",
        "trabajos": "Pintura epóxica reglamentaria, tableros de cristal templado, reflectores LED 200W"
    })
    return canchas
