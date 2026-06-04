"""
Servicio de generación de documentos oficiales del Consejo de la Magistratura de la CABA.
Genera informes, notas, resoluciones, dictámenes y memos en formato HTML.
"""
import logging
from datetime import datetime
from jinja2 import Environment
import os

logger = logging.getLogger(__name__)

# Colores institucionales del Consejo de la Magistratura de la CABA
CM_DARK = "#1A1A3E"      # Azul oscuro institucional
CM_BLUE = "#2C3E7A"      # Azul principal
CM_GOLD = "#C9A84C"      # Dorado institucional

HEADER_PARTIAL = """
<div class="cm-header">
    <div class="cm-logo-area">
        <div class="cm-escudo">
            <div class="escudo-inner">CM</div>
        </div>
        <div class="cm-titles">
            <div class="cm-title-main">CONSEJO DE LA MAGISTRATURA</div>
            <div class="cm-title-sub">CIUDAD AUTÓNOMA DE BUENOS AIRES</div>
            <div class="cm-system">EJE CLOUD — Sistema de Gestión Judicial</div>
        </div>
    </div>
    <div class="cm-header-date">Buenos Aires, {{ fecha }}</div>
</div>
"""

DOCUMENT_TEMPLATES = {
    "informe": """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; color: #222; }
        .cm-header { border-bottom: 3px solid #C9A84C; padding-bottom: 14px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: flex-end; }
        .cm-logo-area { display: flex; align-items: center; gap: 14px; }
        .cm-escudo { width: 54px; height: 54px; background: #1A1A3E; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 2px solid #C9A84C; }
        .escudo-inner { color: #C9A84C; font-weight: 800; font-size: 15px; }
        .cm-title-main { font-size: 13px; font-weight: 800; color: #1A1A3E; letter-spacing: 0.5px; }
        .cm-title-sub { font-size: 11px; font-weight: 600; color: #2C3E7A; }
        .cm-system { font-size: 10px; color: #888; margin-top: 2px; }
        .cm-header-date { font-size: 12px; color: #555; text-align: right; }
        .badge { display: inline-block; background: #1A1A3E; color: white; padding: 3px 12px; border-radius: 3px; font-size: 11px; letter-spacing: 1px; }
        h1 { color: #1A1A3E; font-size: 17px; text-align: center; margin: 18px 0 14px 0; text-transform: uppercase; }
        .meta { background: #f8f8f0; padding: 12px 16px; border-left: 4px solid #C9A84C; margin: 14px 0 20px 0; }
        .meta p { margin: 4px 0; font-size: 13px; }
        .contenido { line-height: 1.75; font-size: 13px; text-align: justify; }
        .firma { margin-top: 55px; text-align: right; font-size: 12px; }
        .footer { margin-top: 40px; border-top: 1px solid #ddd; padding-top: 10px; font-size: 10px; color: #999; text-align: center; }
    </style>
</head>
<body>
    """ + HEADER_PARTIAL + """
    <span class="badge">INFORME</span>
    <h1>{{ asunto }}</h1>

    <div class="meta">
        <p><strong>Para:</strong> {{ destinatario }}</p>
        <p><strong>Asunto:</strong> {{ asunto }}</p>
        <p><strong>Fecha:</strong> {{ fecha }}</p>
        {% if numero_expediente %}<p><strong>Expte. N°:</strong> {{ numero_expediente }}</p>{% endif %}
    </div>

    <div class="contenido">
        {{ contenido | replace('\\n', '<br>') }}
    </div>

    <div class="firma">
        <p>________________________</p>
        <p>Firma y Sello</p>
        <p>Consejo de la Magistratura — CABA</p>
    </div>

    <div class="footer">
        Documento generado por EJE CLOUD IA — Consejo de la Magistratura de la CABA — {{ fecha }}
    </div>
</body>
</html>
""",

    "nota": """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; color: #222; }
        .cm-header { border-bottom: 3px solid #C9A84C; padding-bottom: 14px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: flex-end; }
        .cm-logo-area { display: flex; align-items: center; gap: 14px; }
        .cm-escudo { width: 54px; height: 54px; background: #1A1A3E; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 2px solid #C9A84C; }
        .escudo-inner { color: #C9A84C; font-weight: 800; font-size: 15px; }
        .cm-title-main { font-size: 13px; font-weight: 800; color: #1A1A3E; letter-spacing: 0.5px; }
        .cm-title-sub { font-size: 11px; font-weight: 600; color: #2C3E7A; }
        .cm-system { font-size: 10px; color: #888; margin-top: 2px; }
        .cm-header-date { font-size: 12px; color: #555; text-align: right; }
        .nota-num { text-align: right; font-size: 12px; color: #555; margin-bottom: 16px; }
        .destinatario { font-size: 13px; margin-bottom: 14px; }
        .ref { font-weight: 700; color: #1A1A3E; font-size: 13px; margin-bottom: 16px; }
        .cuerpo { line-height: 1.8; font-size: 13px; text-align: justify; border-top: 1px solid #eee; padding-top: 14px; }
        .saludo { margin-top: 28px; font-size: 13px; }
        .firma { margin-top: 55px; font-size: 12px; }
        .footer { margin-top: 40px; border-top: 1px solid #ddd; padding-top: 10px; font-size: 10px; color: #999; text-align: center; }
    </style>
</head>
<body>
    """ + HEADER_PARTIAL + """
    <div class="nota-num">Nota N°: ____/{{ anio }}</div>

    <div class="destinatario">
        <strong>Al/A la Señor/a:</strong><br>
        {{ destinatario }}
    </div>

    <div class="ref">REF.: {{ asunto }}</div>

    <div class="cuerpo">
        <p>Me dirijo a usted a efectos de comunicarle lo siguiente:</p>
        <p>{{ contenido | replace('\\n', '<br>') }}</p>
    </div>

    <div class="saludo">
        <p>Sin otro particular, saludo a usted muy atentamente.</p>
    </div>

    <div class="firma">
        <p>________________________</p>
        <p>Firma y Sello</p>
        <p>Consejo de la Magistratura — CABA</p>
    </div>

    <div class="footer">
        Documento generado por EJE CLOUD IA — Consejo de la Magistratura de la CABA
    </div>
</body>
</html>
""",

    "memo": """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; color: #222; }
        .cm-header { border-bottom: 3px solid #C9A84C; padding-bottom: 14px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: flex-end; }
        .cm-logo-area { display: flex; align-items: center; gap: 14px; }
        .cm-escudo { width: 54px; height: 54px; background: #1A1A3E; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 2px solid #C9A84C; }
        .escudo-inner { color: #C9A84C; font-weight: 800; font-size: 15px; }
        .cm-title-main { font-size: 13px; font-weight: 800; color: #1A1A3E; letter-spacing: 0.5px; }
        .cm-title-sub { font-size: 11px; font-weight: 600; color: #2C3E7A; }
        .cm-system { font-size: 10px; color: #888; margin-top: 2px; }
        .cm-header-date { font-size: 12px; color: #555; text-align: right; }
        .memo-title { background: #1A1A3E; color: white; padding: 10px 16px; margin-bottom: 20px; letter-spacing: 2px; font-size: 13px; font-weight: 700; }
        table.meta { width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 13px; }
        table.meta td { padding: 7px 10px; border-bottom: 1px solid #eee; }
        table.meta td:first-child { font-weight: 700; color: #1A1A3E; width: 90px; }
        .cuerpo { line-height: 1.75; font-size: 13px; padding: 14px 16px; background: #fafaf5; border-left: 3px solid #C9A84C; }
        .footer { margin-top: 40px; font-size: 10px; color: #999; text-align: center; border-top: 1px solid #eee; padding-top: 10px; }
    </style>
</head>
<body>
    """ + HEADER_PARTIAL + """
    <div class="memo-title">MEMORANDO INTERNO</div>

    <table class="meta">
        <tr><td>PARA:</td><td>{{ destinatario }}</td></tr>
        <tr><td>ASUNTO:</td><td>{{ asunto }}</td></tr>
        <tr><td>FECHA:</td><td>{{ fecha }}</td></tr>
    </table>

    <div class="cuerpo">
        {{ contenido | replace('\\n', '<br>') }}
    </div>

    <div class="footer">
        Memorando generado por EJE CLOUD IA — Consejo de la Magistratura de la CABA — {{ fecha }}
    </div>
</body>
</html>
""",

    "resolucion": """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: 'Times New Roman', serif; margin: 50px; color: #000; }
        .cm-header { border-bottom: 3px solid #C9A84C; padding-bottom: 14px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: flex-end; }
        .cm-logo-area { display: flex; align-items: center; gap: 14px; }
        .cm-escudo { width: 54px; height: 54px; background: #1A1A3E; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 2px solid #C9A84C; }
        .escudo-inner { color: #C9A84C; font-weight: 800; font-size: 15px; }
        .cm-title-main { font-size: 13px; font-weight: 800; color: #1A1A3E; letter-spacing: 0.5px; }
        .cm-title-sub { font-size: 11px; font-weight: 600; color: #2C3E7A; }
        .cm-system { font-size: 10px; color: #888; margin-top: 2px; }
        .cm-header-date { font-size: 12px; color: #555; text-align: right; }
        .res-title { text-align: center; margin-bottom: 22px; }
        .res-title h1 { font-size: 15px; letter-spacing: 3px; margin-bottom: 4px; }
        .res-numero { font-size: 22px; font-weight: bold; margin: 10px 0 4px 0; }
        .bloque { margin: 18px 0; font-size: 13px; }
        .bloque-titulo { text-transform: uppercase; font-weight: bold; letter-spacing: 1px; }
        .articulo { margin: 12px 0; line-height: 1.8; text-align: justify; }
        .articulo strong { display: block; }
        .firma-section { margin-top: 65px; text-align: center; font-size: 12px; }
        .firma-linea { border-top: 1px solid #000; padding-top: 5px; width: 250px; margin: 0 auto; }
        .footer { margin-top: 40px; font-size: 10px; color: #666; text-align: center; border-top: 1px solid #ddd; padding-top: 10px; }
    </style>
</head>
<body>
    """ + HEADER_PARTIAL + """
    <div class="res-title">
        <h1>CONSEJO DE LA MAGISTRATURA</h1>
        <div style="font-size:11px;color:#555;">Ciudad Autónoma de Buenos Aires</div>
        <div class="res-numero">RESOLUCIÓN CM N°: ____/{{ anio }}</div>
    </div>

    <div class="bloque">
        <span class="bloque-titulo">VISTO:</span>
        <p>{{ asunto }}, y</p>
    </div>

    <div class="bloque">
        <span class="bloque-titulo">CONSIDERANDO:</span>
        <p>{{ contenido | replace('\\n', '<br>') }}</p>
    </div>

    <div class="bloque">
        <p style="text-align:center;font-weight:bold;letter-spacing:2px;">EL CONSEJO DE LA MAGISTRATURA RESUELVE</p>

        <div class="articulo">
            <strong>ARTÍCULO 1°.-</strong>
            {{ asunto }}.
        </div>

        <div class="articulo">
            <strong>ARTÍCULO 2°.-</strong>
            Regístrese. Publíquese en el Boletín Oficial de la Ciudad de Buenos Aires. Comuníquese a {{ destinatario }}. Oportunamente, archívese.
        </div>
    </div>

    <div class="firma-section">
        <div style="height:60px;"></div>
        <div class="firma-linea">
            Presidente del Consejo de la Magistratura<br>
            Ciudad Autónoma de Buenos Aires
        </div>
    </div>

    <div class="footer">
        Documento generado por EJE CLOUD IA — Consejo de la Magistratura de la CABA
    </div>
</body>
</html>
""",

    "dictamen": """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: 'Times New Roman', serif; margin: 45px; color: #000; }
        .cm-header { border-bottom: 3px solid #C9A84C; padding-bottom: 14px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: flex-end; }
        .cm-logo-area { display: flex; align-items: center; gap: 14px; }
        .cm-escudo { width: 54px; height: 54px; background: #1A1A3E; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 2px solid #C9A84C; }
        .escudo-inner { color: #C9A84C; font-weight: 800; font-size: 15px; }
        .cm-title-main { font-size: 13px; font-weight: 800; color: #1A1A3E; }
        .cm-title-sub { font-size: 11px; font-weight: 600; color: #2C3E7A; }
        .cm-system { font-size: 10px; color: #888; margin-top: 2px; }
        .cm-header-date { font-size: 12px; color: #555; text-align: right; }
        .badge-dict { display: inline-block; border: 2px solid #1A1A3E; padding: 3px 14px; font-size: 12px; font-weight: bold; letter-spacing: 2px; margin-bottom: 16px; }
        h1 { font-size: 15px; text-align: center; margin: 10px 0 20px; text-transform: uppercase; }
        .bloque { margin: 16px 0; font-size: 13px; line-height: 1.75; }
        .bloque-titulo { font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }
        .opinion { margin-top: 24px; padding: 14px 18px; border: 1px solid #1A1A3E; background: #f9f9f5; font-size: 13px; line-height: 1.75; }
        .firma { margin-top: 55px; font-size: 12px; }
        .footer { margin-top: 40px; font-size: 10px; color: #999; text-align: center; border-top: 1px solid #ddd; padding-top: 10px; }
    </style>
</head>
<body>
    """ + HEADER_PARTIAL + """
    <div class="badge-dict">DICTAMEN</div>
    <h1>{{ asunto }}</h1>

    <div class="bloque">
        <span class="bloque-titulo">Expediente N°:</span> {{ numero_expediente or '____' }}
    </div>

    <div class="bloque">
        <span class="bloque-titulo">Objeto:</span>
        <p>{{ asunto }}</p>
    </div>

    <div class="bloque">
        <span class="bloque-titulo">Antecedentes y Análisis:</span>
        <p>{{ contenido | replace('\\n', '<br>') }}</p>
    </div>

    <div class="opinion">
        <strong>OPINIÓN:</strong> En virtud de lo expuesto, esta asesoría entiende que corresponde proceder conforme lo indicado precedentemente, dejando a criterio del Consejo de la Magistratura de la CABA la adopción de las medidas pertinentes.
    </div>

    <div class="firma">
        <p>________________________</p>
        <p>Firma y Sello</p>
        <p>Asesoría / Área Competente<br>Consejo de la Magistratura — CABA</p>
    </div>

    <div class="footer">
        Documento generado por EJE CLOUD IA — Consejo de la Magistratura de la CABA — {{ fecha }}
    </div>
</body>
</html>
""",
}


class DocumentService:
    async def generate(
        self,
        tipo: str,
        asunto: str,
        contenido: str,
        destinatario: str = "",
        datos_adicionales: dict = None,
    ) -> str:
        """Genera un documento HTML usando la plantilla del Consejo de la Magistratura."""
        template_str = DOCUMENT_TEMPLATES.get(tipo, DOCUMENT_TEMPLATES["informe"])

        env = Environment(autoescape=False)
        template = env.from_string(template_str)

        MESES = {
            "January": "enero", "February": "febrero", "March": "marzo",
            "April": "abril", "May": "mayo", "June": "junio",
            "July": "julio", "August": "agosto", "September": "septiembre",
            "October": "octubre", "November": "noviembre", "December": "diciembre",
        }
        now = datetime.now()
        fecha_str = now.strftime("%d de %B de %Y")
        for en, es in MESES.items():
            fecha_str = fecha_str.replace(en, es)

        context = {
            "asunto": asunto,
            "contenido": contenido,
            "destinatario": destinatario or "A quien corresponda",
            "fecha": fecha_str,
            "anio": now.year,
            "numero_expediente": "",
        }

        if datos_adicionales:
            context.update(datos_adicionales)

        return template.render(**context)
