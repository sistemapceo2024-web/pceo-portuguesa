"""
Generador de Reporte Ejecutivo Municipal para Impresión en Carta Horizontal (Landscape)
Puesto de Comando Estratégico Operacional del Estado Portuguesa (PCEO)
Gobernación del Estado Portuguesa
"""
import os
import base64
import webbrowser
from datetime import datetime
import flet as ft
from components.theme import (
    COLOR_NAVY_DARK,
    COLOR_ELECTRIC_BLUE,
    COLOR_SURFACE_WHITE,
    COLOR_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    COLOR_STATUS_GREEN,
    COLOR_STATUS_AMBER,
    COLOR_STATUS_RED
)
from data.municipios_parser import MunicipiosParser

def get_logo_base64() -> str:
    logo_path = os.path.join("assets", "logo_pceo.png")
    if os.path.exists(logo_path):
        try:
            with open(logo_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            return ""
    return ""

def get_linea_logos_base64() -> str:
    logo_path = os.path.join("assets", "linea_logos.png")
    if os.path.exists(logo_path):
        try:
            with open(logo_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            return ""
    return ""

def generate_municipal_html_report(data: dict) -> str:
    """Genera archivo HTML autónomo optimizado para impresión en Papel Carta Horizontal (279 x 215 mm)."""
    mun = data.get("municipio", "Guanare")
    fecha_corte = data.get("fecha", datetime.now().strftime("%d/%m/%Y"))
    logo_b64 = get_logo_base64()
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" alt="Escudo PCEO" style="height: 40px; object-fit: contain;">' if logo_b64 else ''
    linea_logos_b64 = get_linea_logos_base64()
    linea_logos_html = f'<img src="data:image/png;base64,{linea_logos_b64}" alt="Logos Institucionales" style="height: 24px; max-width: 230px; object-fit: contain;">' if linea_logos_b64 else ''

    kpis = data.get("kpis", {})
    obras = data.get("obras", {})
    planes = data.get("planes", [])
    demo = data.get("demografia") or MunicipiosParser().get_municipio(mun)

    # Construcción de filas de tabla en HTML equilibradas exactamente para 1 sola página Carta Horizontal
    table_rows_html = ""
    for idx, p in enumerate(planes, 1):
        bg = "#F8FAFC" if idx % 2 == 0 else "#FFFFFF"
        table_rows_html += f"""
        <tr style="background-color: {bg}; border-bottom: 1px solid #E2E8F0;">
            <td style="padding: 4px 8px; font-weight: bold; color: #0F172A; font-size: 10px;">{p.get('name')}</td>
            <td style="padding: 4px 8px; font-weight: 600; color: #0284C7; font-size: 10px;">{p.get('metric')}</td>
            <td style="padding: 4px 8px; color: #334155; font-size: 9px; line-height: 1.25;">{p.get('detail')}</td>
            <td style="padding: 4px 8px; text-align: center;">
                <span style="display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 8.5px; font-weight: bold; background-color: {p.get('bg', '#EFF6FF')}; color: {p.get('status_color', '#0284C7')}; border: 1px solid #CBD5E1;">
                    {p.get('status')}
                </span>
            </td>
        </tr>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Reporte Ejecutivo Municipal - {mun} - PCEO Portuguesa</title>
    <style>
        @page {{
            size: letter landscape;
            margin: 4mm 6mm;
        }}
        * {{
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}
        html, body {{
            margin: 0;
            padding: 0;
            background-color: #F1F5F9;
            color: #0F172A;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }}
        .no-print-bar {{
            background: #0A192F;
            color: #FFFFFF;
            padding: 8px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        }}
        .print-btn {{
            background: #0284C7;
            color: #FFFFFF;
            border: none;
            padding: 6px 16px;
            font-size: 12.5px;
            font-weight: bold;
            border-radius: 6px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: background 0.2s;
        }}
        .print-btn:hover {{
            background: #0369A1;
        }}
        .page-sheet {{
            width: 279.4mm;
            max-height: 206mm;
            margin: 10px auto;
            background: #FFFFFF;
            padding: 5mm 8mm;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
            border: 1px solid #CBD5E1;
            border-radius: 6px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            overflow: hidden;
            page-break-after: avoid;
            page-break-inside: avoid;
            break-inside: avoid;
        }}
        @media print {{
            @page {{
                size: letter landscape;
                margin: 4mm 6mm;
            }}
            html, body {{
                width: 100% !important;
                height: 100% !important;
                max-height: 100% !important;
                margin: 0 !important;
                padding: 0 !important;
                overflow: hidden !important;
                background: #FFFFFF !important;
            }}
            .no-print-bar {{
                display: none !important;
            }}
            .page-sheet {{
                width: 100% !important;
                height: 100% !important;
                max-height: 100% !important;
                margin: 0 !important;
                padding: 0 !important;
                box-shadow: none !important;
                border: none !important;
                display: flex !important;
                flex-direction: column !important;
                justify-content: space-between !important;
                page-break-after: avoid !important;
                page-break-before: avoid !important;
                page-break-inside: avoid !important;
                break-inside: avoid !important;
                break-after: avoid !important;
                overflow: hidden !important;
            }}
        }}
        .header-table {{
            width: 100%;
            border-collapse: collapse;
            border-bottom: 2px solid #0284C7;
            padding-bottom: 4px;
            margin-bottom: 5px;
        }}
        .header-title-box {{
            text-align: center;
        }}
        .header-inst {{
            font-size: 9.5px;
            font-weight: bold;
            color: #0284C7;
            letter-spacing: 0.8px;
            margin: 0;
        }}
        .header-main {{
            font-size: 14.5px;
            font-weight: bold;
            color: #0A192F;
            margin: 1px 0;
            letter-spacing: 0.2px;
        }}
        .header-sub {{
            font-size: 10px;
            color: #475569;
            margin: 0;
        }}
        .meta-badge {{
            background: #EFF6FF;
            border: 1px solid #BFDBFE;
            color: #1E40AF;
            padding: 3px 9px;
            border-radius: 4px;
            font-size: 10.5px;
            font-weight: bold;
            display: inline-block;
        }}
        .demo-bar {{
            background: #F8FAFC;
            border: 1px solid #CBD5E1;
            border-radius: 4px;
            padding: 4px 8px;
            margin-bottom: 5px;
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 3px 10px;
            font-size: 8.5px;
            line-height: 1.25;
        }}
        .demo-item {{
            color: #334155;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .demo-item strong {{
            color: #0A192F;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 5px;
            margin-bottom: 5px;
        }}
        .kpi-card {{
            border: 1px solid #CBD5E1;
            border-radius: 4px;
            padding: 4px 8px;
            background: #F8FAFC;
        }}
        .kpi-title {{
            font-size: 8.5px;
            font-weight: bold;
            color: #475569;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }}
        .kpi-val {{
            font-size: 13px;
            font-weight: bold;
            color: #0A192F;
            margin: 1px 0;
            line-height: 1.15;
        }}
        .kpi-sub {{
            font-size: 8px;
            color: #64748B;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .obras-bar-container {{
            background: #F8FAFC;
            border: 1px solid #CBD5E1;
            border-radius: 4px;
            padding: 4px 8px;
            margin-bottom: 5px;
        }}
        .progress-bar {{
            height: 7px;
            border-radius: 3px;
            display: flex;
            overflow: hidden;
            background: #E2E8F0;
            margin: 3px 0;
        }}
        .plans-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 9.5px;
            border: 1px solid #CBD5E1;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 5px;
        }}
        .plans-table th {{
            background-color: #0A192F;
            color: #FFFFFF;
            padding: 4px 8px;
            text-align: left;
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }}
        .footer {{
            border-top: 1.5px solid #CBD5E1;
            padding-top: 4px;
            margin-top: auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 9.5px;
            color: #475569;
            font-weight: 500;
        }}
    </style>
</head>
<body>
    <div class="no-print-bar">
        <div>
            <strong style="font-size: 13px;">Vista Preliminar de Impresión: Carta Horizontal (279.4 x 215.9 mm)</strong>
            <span style="margin-left: 10px; color: #94A3B8; font-size: 11.5px;">Municipio {mun} • Estado Portuguesa</span>
        </div>
        <button class="print-btn" onclick="window.print()">
            🖨️ Enviar a la Cola de Impresión / Guardar PDF
        </button>
    </div>

    <div class="page-sheet">
        <!-- Membrete Oficial -->
        <table class="header-table">
            <tr>
                <td style="width: 55px; vertical-align: middle;">
                    {logo_html}
                </td>
                <td class="header-title-box">
                    <p class="header-inst">REPÚBLICA BOLIVARIANA DE VENEZUELA • GOBERNACIÓN DEL ESTADO PORTUGUESA</p>
                    <h1 class="header-main">PUESTO DE COMANDO ESTRATÉGICO OPERACIONAL (PCEO)</h1>
                    <p class="header-sub">INFORME EJECUTIVO DE GESTIÓN MUNICIPAL CONSOLIDADO • CORTE OFICIAL</p>
                </td>
                <td style="width: 155px; text-align: right; vertical-align: middle;">
                    <div class="meta-badge">MUNICIPIO {mun.upper()}</div>
                    <div style="font-size: 9px; color: #64748B; margin-top: 2px;">Fecha: {fecha_corte}</div>
                </td>
            </tr>
        </table>

        <!-- Ficha Sociopolítica, Territorial y Demográfica Oficial (INE 2026) -->
        <div class="demo-bar">
            <div class="demo-item">🏛️ <strong>Capital:</strong> {demo.get('capital', mun)}</div>
            <div class="demo-item">📐 <strong>Extensión:</strong> {demo.get('extension_km2_fmt', '0')} km²</div>
            <div class="demo-item">🗺️ <strong>Parroquias:</strong> {demo.get('parroquias', '0')}</div>
            <div class="demo-item">👥 <strong>Población INE:</strong> {demo.get('poblacion_ine_fmt', '0')} hab.</div>
            <div class="demo-item">🏠 <strong>Familias:</strong> {demo.get('familias_ine_fmt', '0')}</div>
            <div class="demo-item">🏛️ <strong>Comunas:</strong> {demo.get('comunas_fmt', '0')}</div>
            <div class="demo-item">🤝 <strong>Consejos Com.:</strong> {demo.get('consejos_comunales_fmt', '0')}</div>
            <div class="demo-item">🚩 <strong>UBCH:</strong> {demo.get('ubch_fmt', '0')}</div>
            <div class="demo-item">📦 <strong>Jefes CLAP:</strong> {demo.get('jefes_clap_fmt', '0')}</div>
            <div class="demo-item">🚶 <strong>Jefes de Calle:</strong> {demo.get('jefes_calle_fmt', '0')}</div>
        </div>

        <!-- 8 Tarjetas de Totales Clave -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Pozos de Agua</div>
                <div class="kpi-val">{kpis.get('pozos_op', '0')} Op.</div>
                <div class="kpi-sub">{kpis.get('pozos_tot', '0')} Pozos ({kpis.get('pozos_pct', '0')}% Op)</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Asfalto Urbano</div>
                <div class="kpi-val">{kpis.get('asf_ton', '0')} Ton.</div>
                <div class="kpi-sub">{kpis.get('asf_fallas', '0')} Fallas atendidas</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Fiesta de la Luz</div>
                <div class="kpi-val">{kpis.get('luz_lum', '0')} Lum.</div>
                <div class="kpi-sub">{kpis.get('luz_tx', '0')} TX instalados</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Aguas Servidas</div>
                <div class="kpi-val">{kpis.get('aguas_m', '0')} m</div>
                <div class="kpi-sub">{kpis.get('hidro_m', '0')} m Hidrojet</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Puentes y Vialidad</div>
                <div class="kpi-val">{kpis.get('pue_culm', '0')} Culm.</div>
                <div class="kpi-sub">{kpis.get('pue_tot', '0')} Obras viales</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Espacios de Salud</div>
                <div class="kpi-val">{kpis.get('sal_culm', '0')} Rehab.</div>
                <div class="kpi-sub">{kpis.get('sal_tot', '0')} Centros ({kpis.get('sal_pct', '0')}%)</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Centros Educativos</div>
                <div class="kpi-val">{kpis.get('esc_culm', '0')} Escuelas</div>
                <div class="kpi-sub">{kpis.get('esc_tot', '0')} Planteles ({kpis.get('esc_pct', '0')}%)</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Canchas Deportivas</div>
                <div class="kpi-val">{kpis.get('can_culm', '0')} Canchas</div>
                <div class="kpi-sub">{kpis.get('can_tot', '0')} Intervenidas</div>
            </div>
        </div>

        <!-- Barra y Estatus de Proyectos Físicos -->
        <div class="obras-bar-container">
            <div style="display: flex; justify-content: space-between; font-size: 10px; font-weight: bold; margin-bottom: 2px;">
                <span>Estatus Consolidado de Proyectos ({obras.get('total', 0)} Frentes de Obra)</span>
                <span style="color: #16A34A;">{obras.get('pct_culm', '0')}% Eficiencia Municipal</span>
            </div>
            <div class="progress-bar">
                <div style="flex: {max(obras.get('culm', 1), 1)}; background-color: #16A34A;" title="Culminadas"></div>
                <div style="flex: {max(obras.get('proc', 0), 0)}; background-color: #D97706;" title="En Proceso"></div>
                <div style="flex: {max(obras.get('para', 0), 0)}; background-color: #DC2626;" title="Paralizadas"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 8.5px; margin-top: 2px;">
                <span style="color: #15803D; font-weight: bold;">● {obras.get('culm', 0)} Culminadas ({obras.get('pct_culm', '0')}%)</span>
                <span style="color: #B45309; font-weight: bold;">● {obras.get('proc', 0)} En Proceso ({obras.get('pct_proc', '0')}%)</span>
                <span style="color: #B91C1C; font-weight: bold;">● {obras.get('para', 0)} Paralizadas ({obras.get('pct_para', '0')}%)</span>
            </div>
        </div>

        <!-- Tabla Consolidada de Planes de Gobierno -->
        <table class="plans-table">
            <thead>
                <tr>
                    <th style="width: 22%;">Plan de Gobierno</th>
                    <th style="width: 28%;">Métrica Principal</th>
                    <th style="width: 38%;">Alcance y Detalle Operativo</th>
                    <th style="width: 12%; text-align: center;">Estatus</th>
                </tr>
            </thead>
            <tbody>
                {table_rows_html}
            </tbody>
        </table>

        <!-- Pie de Página Institucional -->
        <div class="footer">
            <span style="font-size: 11px; font-weight: bold; color: #0A192F;">PCEO</span>
            <span style="font-size: 10px; font-weight: 600; color: #475569; letter-spacing: 0.4px;">Portuguesa el Compromiso es Contigo</span>
            <div style="display: flex; align-items: center; justify-content: flex-end;">
                {linea_logos_html}
            </div>
        </div>
    </div>
    </style>
</head>
<body>
    <div class="no-print-bar">
        <div>
            <strong style="font-size: 14px;">Vista Preliminar de Impresión: Carta Horizontal (279.4 x 215.9 mm)</strong>
            <span style="margin-left: 10px; color: #94A3B8; font-size: 12px;">Municipio {mun} • Estado Portuguesa</span>
        </div>
        <button class="print-btn" onclick="window.print()">
            🖨️ Enviar a la Cola de Impresión / Guardar PDF
        </button>
    </div>

    <div class="page-sheet">
        <!-- Membrete Oficial -->
        <table class="header-table">
            <tr>
                <td style="width: 60px; vertical-align: middle;">
                    {logo_html}
                </td>
                <td class="header-title-box">
                    <p class="header-inst">REPÚBLICA BOLIVARIANA DE VENEZUELA • GOBERNACIÓN DEL ESTADO PORTUGUESA</p>
                    <h1 class="header-main">PUESTO DE COMANDO ESTRATÉGICO OPERACIONAL (PCEO)</h1>
                    <p class="header-sub">INFORME EJECUTIVO DE GESTIÓN MUNICIPAL CONSOLIDADO • CORTE OFICIAL</p>
                </td>
                <td style="width: 160px; text-align: right; vertical-align: middle;">
                    <div class="meta-badge">MUNICIPIO {mun.upper()}</div>
                    <div style="font-size: 9.5px; color: #64748B; margin-top: 3px;">Fecha: {fecha_corte}</div>
                </td>
            </tr>
        </table>

        <!-- Ficha Sociopolítica, Territorial y Demográfica Oficial (INE 2026) -->
        <div class="demo-bar">
            <div class="demo-item">🏛️ <strong>Capital:</strong> {demo.get('capital', mun)}</div>
            <div class="demo-item">📐 <strong>Extensión:</strong> {demo.get('extension_km2_fmt', '0')} km²</div>
            <div class="demo-item">🗺️ <strong>Parroquias:</strong> {demo.get('parroquias', '0')}</div>
            <div class="demo-item">👥 <strong>Población INE:</strong> {demo.get('poblacion_ine_fmt', '0')} hab.</div>
            <div class="demo-item">🏠 <strong>Familias:</strong> {demo.get('familias_ine_fmt', '0')}</div>
            <div class="demo-item">🏛️ <strong>Comunas:</strong> {demo.get('comunas_fmt', '0')}</div>
            <div class="demo-item">🤝 <strong>Consejos Com.:</strong> {demo.get('consejos_comunales_fmt', '0')}</div>
            <div class="demo-item">🚩 <strong>UBCH:</strong> {demo.get('ubch_fmt', '0')}</div>
            <div class="demo-item">📦 <strong>Jefes CLAP:</strong> {demo.get('jefes_clap_fmt', '0')}</div>
            <div class="demo-item">🚶 <strong>Jefes de Calle:</strong> {demo.get('jefes_calle_fmt', '0')}</div>
        </div>

        <!-- 8 Tarjetas de Totales Clave -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Pozos de Agua</div>
                <div class="kpi-val">{kpis.get('pozos_op', '0')} Op.</div>
                <div class="kpi-sub">{kpis.get('pozos_tot', '0')} Pozos ({kpis.get('pozos_pct', '0')}% Op)</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Asfalto Urbano</div>
                <div class="kpi-val">{kpis.get('asf_ton', '0')} Ton.</div>
                <div class="kpi-sub">{kpis.get('asf_fallas', '0')} Fallas atendidas</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Fiesta de la Luz</div>
                <div class="kpi-val">{kpis.get('luz_lum', '0')} Lum.</div>
                <div class="kpi-sub">{kpis.get('luz_tx', '0')} TX instalados</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Aguas Servidas</div>
                <div class="kpi-val">{kpis.get('aguas_m', '0')} m</div>
                <div class="kpi-sub">{kpis.get('hidro_m', '0')} m Hidrojet</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Puentes y Vialidad</div>
                <div class="kpi-val">{kpis.get('pue_culm', '0')} Culm.</div>
                <div class="kpi-sub">{kpis.get('pue_tot', '0')} Obras viales</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Espacios de Salud</div>
                <div class="kpi-val">{kpis.get('sal_culm', '0')} Rehab.</div>
                <div class="kpi-sub">{kpis.get('sal_tot', '0')} Centros ({kpis.get('sal_pct', '0')}%)</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Centros Educativos</div>
                <div class="kpi-val">{kpis.get('esc_culm', '0')} Escuelas</div>
                <div class="kpi-sub">{kpis.get('esc_tot', '0')} Planteles ({kpis.get('esc_pct', '0')}%)</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Canchas Deportivas</div>
                <div class="kpi-val">{kpis.get('can_culm', '0')} Canchas</div>
                <div class="kpi-sub">{kpis.get('can_tot', '0')} Intervenidas</div>
            </div>
        </div>

        <!-- Barra y Estatus de Proyectos Físicos -->
        <div class="obras-bar-container">
            <div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: bold; margin-bottom: 2px;">
                <span>Estatus Consolidado de Proyectos ({obras.get('total', 0)} Frentes de Obra)</span>
                <span style="color: #16A34A;">{obras.get('pct_culm', '0')}% Eficiencia Municipal</span>
            </div>
            <div class="progress-bar">
                <div style="flex: {max(obras.get('culm', 1), 1)}; background-color: #16A34A;" title="Culminadas"></div>
                <div style="flex: {max(obras.get('proc', 0), 0)}; background-color: #D97706;" title="En Proceso"></div>
                <div style="flex: {max(obras.get('para', 0), 0)}; background-color: #DC2626;" title="Paralizadas"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 9.5px; margin-top: 2px;">
                <span style="color: #15803D; font-weight: bold;">● {obras.get('culm', 0)} Culminadas ({obras.get('pct_culm', '0')}%)</span>
                <span style="color: #B45309; font-weight: bold;">● {obras.get('proc', 0)} En Proceso ({obras.get('pct_proc', '0')}%)</span>
                <span style="color: #B91C1C; font-weight: bold;">● {obras.get('para', 0)} Paralizadas ({obras.get('pct_para', '0')}%)</span>
            </div>
        </div>

        <!-- Tabla Consolidada de Planes de Gobierno -->
        <table class="plans-table">
            <thead>
                <tr>
                    <th style="width: 22%;">Plan de Gobierno</th>
                    <th style="width: 28%;">Métrica Principal</th>
                    <th style="width: 38%;">Alcance y Detalle Operativo</th>
                    <th style="width: 12%; text-align: center;">Estatus</th>
                </tr>
            </thead>
            <tbody>
                {table_rows_html}
            </tbody>
        </table>

        <!-- Pie de Página Institucional -->
        <div class="footer">
            <span style="font-size: 11px; font-weight: bold; color: #0A192F;">PCEO</span>
            <span style="font-size: 10.5px; font-weight: 600; color: #475569; letter-spacing: 0.4px;">Portuguesa el Compromiso es Contigo</span>
            <div style="display: flex; align-items: center; justify-content: flex-end;">
                {linea_logos_html}
            </div>
        </div>
    </div>

    <script>
        // Disparar diálogo de impresión automáticamente al abrir en navegador
        window.addEventListener('load', function() {{
            setTimeout(function() {{
                window.print();
            }}, 400);
        }});
    </script>
</body>
</html>"""

    # Guardar archivo en directorio exports y en assets/reports para acceso web directo
    os.makedirs("exports", exist_ok=True)
    os.makedirs(os.path.join("assets", "reports"), exist_ok=True)
    clean_mun = mun.lower().replace(" ", "_").replace("í", "i").replace("á", "a").replace("é", "e").replace("ó", "o")
    file_path = os.path.join("exports", f"reporte_ejecutivo_{clean_mun}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    web_file_path = os.path.join("assets", "reports", f"reporte_ejecutivo_{clean_mun}.html")
    with open(web_file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return os.path.abspath(file_path)

def open_print_preview_dialog(page: ft.Page, data: dict):
    """Abre el diálogo Flet de vista preliminar en formato Carta Horizontal y botón para enviar a cola de impresión."""
    mun = data.get("municipio", "Guanare")
    fecha_corte = data.get("fecha", datetime.now().strftime("%d/%m/%Y"))
    kpis = data.get("kpis", {})
    obras = data.get("obras", {})
    planes = data.get("planes", [])
    demo = data.get("demografia") or MunicipiosParser().get_municipio(mun)

    clean_mun = mun.lower().replace(" ", "_").replace("í", "i").replace("á", "a").replace("é", "e").replace("ó", "o")

    def show_feedback_snack(message: str, is_error: bool = False):
        snack = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.Icons.ERROR_ROUNDED if is_error else ft.Icons.CHECK_CIRCLE_ROUNDED, color="#FFFFFF", size=18),
                ft.Text(message, color="#FFFFFF", size=12, weight=ft.FontWeight.W_500)
            ], spacing=8),
            bgcolor=COLOR_STATUS_RED if is_error else COLOR_NAVY_DARK
        )
        if hasattr(page, "open"):
            page.open(snack)
        elif hasattr(page, "show_dialog"):
            page.show_dialog(snack)
        page.update()

    def do_print(e=None):
        try:
            html_path = generate_municipal_html_report(data)

            # Copia automática en la carpeta Descargas del usuario
            downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            if os.path.exists(downloads_dir):
                dl_target = os.path.join(downloads_dir, f"reporte_ejecutivo_{clean_mun}.html")
                try:
                    import shutil
                    shutil.copyfile(html_path, dl_target)
                except Exception:
                    pass

            # Invocación web con diálogo de impresión automática
            web_url = f"/reports/reporte_ejecutivo_{clean_mun}.html"
            opened = False
            if hasattr(page, "launch_url"):
                try:
                    page.launch_url(web_url, web_window_name="_blank")
                    opened = True
                except Exception:
                    pass

            if not opened:
                try:
                    os.startfile(html_path)
                    opened = True
                except Exception:
                    try:
                        webbrowser.open(f"file:///{html_path.replace(os.sep, '/')}")
                        opened = True
                    except Exception:
                        pass

            show_feedback_snack(f"Reporte enviado a impresión y guardado en Descargas / exports")

            if hasattr(page, "close"):
                page.close()
            elif hasattr(page, "pop_dialog"):
                page.pop_dialog()
            page.update()

        except Exception as err:
            show_feedback_snack(f"Error al enviar a la cola de impresión: {err}", is_error=True)

    def do_download(e=None):
        try:
            html_path = generate_municipal_html_report(data)
            downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            if os.path.exists(downloads_dir):
                dl_target = os.path.join(downloads_dir, f"reporte_ejecutivo_{clean_mun}.html")
                try:
                    import shutil
                    shutil.copyfile(html_path, dl_target)
                except Exception:
                    pass
            web_url = f"/reports/reporte_ejecutivo_{clean_mun}.html"
            if hasattr(page, "launch_url"):
                page.launch_url(web_url, web_window_name="_blank")
            show_feedback_snack(f"Reporte descargado y guardado en Descargas: reporte_ejecutivo_{clean_mun}.html")
        except Exception as err:
            show_feedback_snack(f"Error al descargar reporte: {err}", is_error=True)

    # Construir mini tarjetas para la vista modal en Flet con escala estándar y cómoda
    def mini_box(title, val, sub):
        return ft.Container(
            content=ft.Column(
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Text(title, size=9, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY),
                    ft.Text(val, size=14, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                    ft.Text(sub, size=8.5, color=COLOR_TEXT_MUTED, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)
                ]
            ),
            padding=ft.Padding.symmetric(horizontal=8, vertical=6),
            bgcolor="#F8FAFC",
            border_radius=6,
            border=ft.Border.all(1, COLOR_BORDER),
            expand=True
        )

    kpis_r1 = ft.Row(
        spacing=6,
        controls=[
            mini_box("POZOS DE AGUA", f"{kpis.get('pozos_op', '0')} Op.", f"{kpis.get('pozos_tot', '0')} Pozos"),
            mini_box("ASFALTO URBANO", f"{kpis.get('asf_ton', '0')} Ton.", f"{kpis.get('asf_fallas', '0')} Fallas"),
            mini_box("FIESTA DE LA LUZ", f"{kpis.get('luz_lum', '0')} Lum.", f"{kpis.get('luz_tx', '0')} TX"),
            mini_box("AGUAS SERVIDAS", f"{kpis.get('aguas_m', '0')} m", f"{kpis.get('hidro_m', '0')} m Hidrojet")
        ]
    )
    kpis_r2 = ft.Row(
        spacing=6,
        controls=[
            mini_box("PUENTES Y VIALIDAD", f"{kpis.get('pue_culm', '0')} Culm.", f"{kpis.get('pue_tot', '0')} Obras"),
            mini_box("ESPACIOS DE SALUD", f"{kpis.get('sal_culm', '0')} Rehab.", f"{kpis.get('sal_tot', '0')} Centros"),
            mini_box("CENTROS EDUCATIVOS", f"{kpis.get('esc_culm', '0')} Esc.", f"{kpis.get('esc_tot', '0')} Planteles"),
            mini_box("CANCHAS DEPORTIVAS", f"{kpis.get('can_culm', '0')} Culm.", f"{kpis.get('can_tot', '0')} Canchas")
        ]
    )

    # Filas de la tabla de planes para el modal con tipografía estándar
    plan_rows_controls = []
    for p in planes:
        plan_rows_controls.append(
            ft.Container(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(p.get("name"), size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK, width=180),
                        ft.Text(p.get("metric"), size=10.5, weight=ft.FontWeight.W_600, color=COLOR_ELECTRIC_BLUE, width=180),
                        ft.Text(p.get("detail"), size=10, color=COLOR_TEXT_SECONDARY, expand=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Container(
                            content=ft.Text(p.get("status"), size=9.5, weight=ft.FontWeight.BOLD, color=p.get("status_color")),
                            padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                            bgcolor="#F1F5F9",
                            border_radius=4,
                            border=ft.Border.all(1, COLOR_BORDER)
                        )
                    ]
                ),
                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                border=ft.Border(bottom=ft.BorderSide(1, "#F1F5F9"))
            )
        )

    demo_preview_box = ft.Container(
        content=ft.Column(
            spacing=3,
            controls=[
                ft.Row(
                    spacing=8,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(f"🏛️ Capital: {demo.get('capital', mun)}", size=9.5, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                        ft.Text(f"📐 Extensión: {demo.get('extension_km2_fmt', '0')} km²", size=9.5, weight=ft.FontWeight.W_600, color=COLOR_TEXT_SECONDARY),
                        ft.Text(f"🗺️ Parroquias: {demo.get('parroquias', '0')}", size=9.5, weight=ft.FontWeight.W_600, color=COLOR_TEXT_SECONDARY),
                        ft.Text(f"👥 Población: {demo.get('poblacion_ine_fmt', '0')} hab.", size=9.5, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_BLUE),
                        ft.Text(f"🏠 Familias: {demo.get('familias_ine_fmt', '0')}", size=9.5, weight=ft.FontWeight.W_600, color=COLOR_TEXT_SECONDARY),
                    ]
                ),
                ft.Row(
                    spacing=8,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(f"🏛️ Comunas: {demo.get('comunas_fmt', '0')}", size=9, color=COLOR_TEXT_MUTED),
                        ft.Text(f"🤝 Consejos Com.: {demo.get('consejos_comunales_fmt', '0')}", size=9, color=COLOR_TEXT_MUTED),
                        ft.Text(f"🚩 UBCH: {demo.get('ubch_fmt', '0')}", size=9, color=COLOR_TEXT_MUTED),
                        ft.Text(f"📦 Jefes CLAP: {demo.get('jefes_clap_fmt', '0')}", size=9, color=COLOR_TEXT_MUTED),
                        ft.Text(f"🚶 Jefes de Calle: {demo.get('jefes_calle_fmt', '0')}", size=9, color=COLOR_TEXT_MUTED),
                    ]
                )
            ]
        ),
        padding=ft.Padding.symmetric(horizontal=8, vertical=5),
        bgcolor="#F8FAFC",
        border_radius=6,
        border=ft.Border.all(1, COLOR_BORDER)
    )

    # Contenedor con aspecto de Hoja Carta Horizontal (Ancho profesional ~940px)
    sheet_container = ft.Container(
        content=ft.Column(
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            controls=[
                # Membrete
                ft.Container(
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Row(
                                spacing=10,
                                controls=[
                                    ft.Image(src="logo_pceo.png", width=40, height=40, fit=ft.BoxFit.CONTAIN) if os.path.exists("assets/logo_pceo.png") else ft.Icon(ft.Icons.SHIELD_ROUNDED, color=COLOR_ELECTRIC_BLUE, size=32),
                                    ft.Column(
                                        spacing=1,
                                        controls=[
                                            ft.Text("REPÚBLICA BOLIVARIANA DE VENEZUELA • GOBERNACIÓN DE PORTUGUESA", size=9, weight=ft.FontWeight.BOLD, color=COLOR_ELECTRIC_BLUE),
                                            ft.Text("PUESTO DE COMANDO ESTRATÉGICO OPERACIONAL (PCEO)", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                            ft.Text("INFORME EJECUTIVO DE GESTIÓN MUNICIPAL CONSOLIDADO", size=10, color=COLOR_TEXT_MUTED)
                                        ]
                                    )
                                ]
                            ),
                            ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                                spacing=2,
                                controls=[
                                    ft.Container(
                                        content=ft.Text(f"MUNICIPIO {mun.upper()}", size=11, weight=ft.FontWeight.BOLD, color="#1E40AF"),
                                        padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                                        bgcolor="#EFF6FF",
                                        border_radius=6,
                                        border=ft.Border.all(1, "#BFDBFE")
                                    ),
                                    ft.Text(f"Fecha: {fecha_corte}", size=9, color=COLOR_TEXT_MUTED)
                                ]
                            )
                        ]
                    ),
                    padding=ft.Padding.only(bottom=6),
                    border=ft.Border(bottom=ft.BorderSide(2, COLOR_ELECTRIC_BLUE))
                ),

                # Ficha Demográfica y Sociopolítica Oficial
                demo_preview_box,

                # Tarjetas
                kpis_r1,
                kpis_r2,

                # Barra Estatus
                ft.Container(
                    content=ft.Column(
                        spacing=3,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(f"Estatus Consolidado de Proyectos ({obras.get('total', 0)} Obras)", size=10.5, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                                    ft.Text(f"{obras.get('pct_culm', '0')}% Culminadas", size=10.5, weight=ft.FontWeight.BOLD, color="#16A34A")
                                ]
                            ),
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.Container(expand=max(obras.get("culm", 1), 1), bgcolor="#16A34A"),
                                        ft.Container(expand=max(obras.get("proc", 0), 0), bgcolor="#D97706"),
                                        ft.Container(expand=max(obras.get("para", 0), 0), bgcolor="#DC2626"),
                                    ],
                                    spacing=2
                                ),
                                height=8,
                                border_radius=4,
                                clip_behavior=ft.ClipBehavior.HARD_EDGE
                            )
                        ]
                    ),
                    padding=6,
                    bgcolor="#F8FAFC",
                    border_radius=6,
                    border=ft.Border.all(1, COLOR_BORDER)
                ),

                # Tabla de Planes
                ft.Container(
                    content=ft.Column(
                        spacing=0,
                        controls=[
                            ft.Container(
                                content=ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text("PLAN DE GOBIERNO", size=9.5, weight=ft.FontWeight.BOLD, color="#FFFFFF", width=180),
                                        ft.Text("MÉTRICA CLAVE", size=9.5, weight=ft.FontWeight.BOLD, color="#FFFFFF", width=180),
                                        ft.Text("DETALLE Y ALCANCE OPERATIVO", size=9.5, weight=ft.FontWeight.BOLD, color="#FFFFFF", expand=True),
                                        ft.Text("ESTATUS", size=9.5, weight=ft.FontWeight.BOLD, color="#FFFFFF", width=70, text_align=ft.TextAlign.CENTER)
                                    ]
                                ),
                                bgcolor=COLOR_NAVY_DARK,
                                padding=ft.Padding.symmetric(horizontal=8, vertical=5),
                                border_radius=ft.BorderRadius(top_left=6, top_right=6, bottom_left=0, bottom_right=0)
                            ),
                            *plan_rows_controls
                        ]
                    ),
                    border=ft.Border.all(1, COLOR_BORDER),
                    border_radius=6
                ),

                # Pie de Página Institucional
                ft.Container(
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text("PCEO", size=11, weight=ft.FontWeight.BOLD, color=COLOR_NAVY_DARK),
                            ft.Text("Portuguesa el Compromiso es Contigo", size=10.5, weight=ft.FontWeight.W_600, color=COLOR_TEXT_SECONDARY),
                            ft.Container(
                                content=ft.Image(
                                    src="linea_logos.png",
                                    height=24,
                                    fit=ft.BoxFit.CONTAIN
                                ) if os.path.exists("assets/linea_logos.png") else ft.Container(),
                                height=26,
                                alignment=ft.Alignment(1, 0)
                            )
                        ]
                    ),
                    padding=ft.Padding.only(top=6),
                    border=ft.Border(top=ft.BorderSide(1, COLOR_BORDER))
                )
            ]
        ),
        width=940,
        padding=12,
        bgcolor="#FFFFFF",
        border_radius=6,
        border=ft.Border.all(1, COLOR_BORDER)
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            spacing=8,
            controls=[
                ft.Icon(ft.Icons.PRINT_ROUNDED, color=COLOR_ELECTRIC_BLUE, size=18),
                ft.Text(f"Vista Preliminar de Impresión: Municipio {mun} (Carta Horizontal)", size=13.5, weight=ft.FontWeight.BOLD)
            ]
        ),
        content=ft.Container(
            content=ft.Column(
                controls=[sheet_container],
                scroll=ft.ScrollMode.ADAPTIVE
            ),
            width=960,
            height=540
        ),
        actions=[
            ft.TextButton(
                content=ft.Text("Cerrar", size=12),
                on_click=lambda e: (page.close() if hasattr(page, "close") else page.pop_dialog()) or page.update()
            ),
            ft.OutlinedButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.DOWNLOAD_ROUNDED, size=15, color=COLOR_ELECTRIC_BLUE),
                    ft.Text("Descargar Reporte HTML", size=12, weight=ft.FontWeight.W_600)
                ], tight=True),
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=6),
                    padding=ft.Padding.symmetric(horizontal=12, vertical=8)
                ),
                tooltip="Guardar copia del reporte en la carpeta Descargas",
                on_click=do_download
            ),
            ft.FilledButton(
                content=ft.Row(
                    spacing=6,
                    tight=True,
                    controls=[
                        ft.Icon(ft.Icons.PRINT_ROUNDED, size=15),
                        ft.Text("Enviar a Cola de Impresión / Guardar PDF", size=12, weight=ft.FontWeight.BOLD)
                    ]
                ),
                style=ft.ButtonStyle(
                    bgcolor=COLOR_ELECTRIC_BLUE,
                    color="#FFFFFF",
                    shape=ft.RoundedRectangleBorder(radius=6),
                    padding=ft.Padding.symmetric(horizontal=16, vertical=8)
                ),
                on_click=do_print
            )
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )

    if hasattr(page, "open"):
        page.open(dialog)
    elif hasattr(page, "show_dialog"):
        page.show_dialog(dialog)
