"""
Servicio de generación de documentos oficiales del GCBA.
Genera informes, notas, resoluciones y memos en formato HTML/PDF.
"""
import logging
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

logger = logging.getLogger(__name__)

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "../../data/templates")

DOCUMENT_TEMPLATES = {
    "informe": """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; color: #333; }
        .header { border-bottom: 3px solid #003A70; padding-bottom: 15px; margin-bottom: 25px; }
        .gcba-logo { display: flex; align-items: center; gap: 15px; }
        .gcba-title { font-size: 11px; color: #666; line-height: 1.4; }
        h1 { color: #003A70; font-size: 18px; text-align: center; margin: 20px 0; }
        .meta { background: #f5f5f5; padding: 12px; border-left: 4px solid #003A70; margin: 15px 0; }
        .meta p { margin: 4px 0; font-size: 13px; }
        .contenido { line-height: 1.7; font-size: 13px; text-align: justify; }
        .firma { margin-top: 50px; text-align: right; font-size: 12px; }
        .footer { margin-top: 40px; border-top: 1px solid #ccc; padding-top: 10px; font-size: 10px; color: #999; text-align: center; }
        .badge { display: inline-block; background: #003A70; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="gcba-logo">
            <div style="width:50px;height:50px;background:#003A70;border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;font-size:14px;">BA</div>
            <div class="gcba-title">
                <strong>GOBIERNO DE LA CIUDAD AUTÓNOMA DE BUENOS AIRES</strong><br>
                EJE CLOUD — Sistema de Gestión Administrativa
            </div>
        </div>
    </div>

    <span class="badge">INFORME</span>
    <h1>{{ asunto | upper }}</h1>

    <div class="meta">
        <p><strong>Fecha:</strong> {{ fecha }}</p>
        <p><strong>Para:</strong> {{ destinatario }}</p>
        <p><strong>Asunto:</strong> {{ asunto }}</p>
        {% if numero_expediente %}
        <p><strong>N° Expediente:</strong> {{ numero_expediente }}</p>
        {% endif %}
    </div>

    <div class="contenido">
        {{ contenido | replace('\\n', '<br>') }}
    </div>

    <div class="firma">
        <p>________________________</p>
        <p>Firma</p>
        <p>Agente GCBA</p>
    </div>

    <div class="footer">
        Documento generado por EJE CLOUD IA — Gobierno de la Ciudad de Buenos Aires<br>
        {{ fecha }}
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
        body { font-family: Arial, sans-serif; margin: 40px; color: #333; }
        .header { border-bottom: 2px solid #F7C233; padding-bottom: 15px; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: flex-end; }
        .gcba-title { font-size: 11px; color: #666; }
        h1 { color: #003A70; font-size: 16px; margin: 20px 0 10px 0; }
        .destinatario { font-size: 13px; margin-bottom: 20px; }
        .destinatario strong { color: #003A70; }
        .cuerpo { line-height: 1.8; font-size: 13px; text-align: justify; border-top: 1px solid #eee; padding-top: 15px; }
        .saludo { margin-top: 30px; font-size: 13px; }
        .firma { margin-top: 50px; font-size: 12px; }
        .footer { margin-top: 40px; border-top: 1px solid #ccc; padding-top: 10px; font-size: 10px; color: #999; text-align: center; }
        .numero-nota { font-size: 12px; color: #666; text-align: right; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <div style="font-weight:bold;color:#003A70;font-size:14px;">GOBIERNO DE LA CIUDAD AUTÓNOMA DE BUENOS AIRES</div>
            <div class="gcba-title">EJE CLOUD — Sistema de Gestión</div>
        </div>
        <div class="numero-nota">Nota N°: ___/{{ anio }}<br>Buenos Aires, {{ fecha }}</div>
    </div>

    <div class="destinatario">
        <strong>Al/A la Señor/a:</strong><br>
        {{ destinatario }}
    </div>

    <div style="font-weight: bold; color: #003A70; margin-bottom: 15px;">
        REF.: {{ asunto }}
    </div>

    <div class="cuerpo">
        <p>Me dirijo a usted a efectos de informarle que:</p>
        <p>{{ contenido | replace('\\n', '<br>') }}</p>
    </div>

    <div class="saludo">
        <p>Sin otro particular, saludo a usted muy atentamente.</p>
    </div>

    <div class="firma">
        <p>________________________</p>
        <p>Firma y Sello</p>
        <p>Agente GCBA</p>
    </div>

    <div class="footer">
        Documento generado por EJE CLOUD IA — Gobierno de la Ciudad de Buenos Aires
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
        body { font-family: Arial, sans-serif; margin: 40px; color: #333; }
        .header { background: #003A70; color: white; padding: 15px 20px; margin-bottom: 25px; }
        .header h2 { margin: 0; font-size: 14px; letter-spacing: 2px; }
        .header p { margin: 3px 0; font-size: 11px; opacity: 0.8; }
        table.meta { width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 13px; }
        table.meta td { padding: 6px 10px; border-bottom: 1px solid #eee; }
        table.meta td:first-child { font-weight: bold; color: #003A70; width: 100px; }
        .cuerpo { line-height: 1.7; font-size: 13px; padding: 15px; background: #fafafa; border-left: 3px solid #F7C233; }
        .footer { margin-top: 40px; font-size: 10px; color: #999; text-align: center; border-top: 1px solid #eee; padding-top: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h2>MEMORANDO INTERNO</h2>
        <p>Gobierno de la Ciudad Autónoma de Buenos Aires — EJE CLOUD</p>
    </div>

    <table class="meta">
        <tr><td>PARA:</td><td>{{ destinatario }}</td></tr>
        <tr><td>ASUNTO:</td><td>{{ asunto }}</td></tr>
        <tr><td>FECHA:</td><td>{{ fecha }}</td></tr>
        <tr><td>PRIORIDAD:</td><td>Normal</td></tr>
    </table>

    <div class="cuerpo">
        {{ contenido | replace('\\n', '<br>') }}
    </div>

    <div class="footer">
        Memorando generado por EJE CLOUD IA — Gobierno de la Ciudad de Buenos Aires — {{ fecha }}
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
        .header { text-align: center; border-bottom: 3px double #000; padding-bottom: 20px; margin-bottom: 30px; }
        h1 { font-size: 16px; letter-spacing: 3px; margin: 5px 0; }
        h2 { font-size: 14px; margin: 5px 0; font-weight: normal; }
        .numero { font-size: 20px; font-weight: bold; margin: 15px 0 5px 0; }
        .visto { margin: 20px 0; font-size: 13px; }
        .visto strong { text-transform: uppercase; letter-spacing: 1px; }
        .considerando { margin: 20px 0; font-size: 13px; }
        .resuelve { margin: 20px 0; font-size: 13px; }
        .articulo { margin: 12px 0; text-align: justify; line-height: 1.8; }
        .articulo strong { display: block; }
        .firma-section { margin-top: 60px; display: flex; justify-content: space-around; text-align: center; font-size: 12px; }
        .firma-box { width: 200px; }
        .firma-box .linea { border-top: 1px solid #000; padding-top: 5px; }
        .footer { margin-top: 40px; font-size: 10px; color: #666; text-align: center; }
    </style>
</head>
<body>
    <div class="header">
        <h1>GOBIERNO DE LA CIUDAD AUTÓNOMA DE BUENOS AIRES</h1>
        <h2>EJE CLOUD — Sistema de Gestión Administrativa</h2>
        <div class="numero">RESOLUCIÓN N°: ____/{{ anio }}</div>
        <div style="font-size: 12px;">Buenos Aires, {{ fecha }}</div>
    </div>

    <div class="visto">
        <strong>VISTO:</strong>
        <p>{{ asunto }}, y</p>
    </div>

    <div class="considerando">
        <strong>CONSIDERANDO:</strong>
        <p>{{ contenido | replace('\\n', '<br>') }}</p>
    </div>

    <div class="resuelve">
        <strong>POR ELLO,</strong>
        <p style="text-align:center; font-weight: bold; letter-spacing: 2px;">EL/LA TITULAR RESUELVE</strong></p>

        <div class="articulo">
            <strong>ARTÍCULO 1°.-</strong>
            {{ asunto }}.
        </div>

        <div class="articulo">
            <strong>ARTÍCULO 2°.-</strong>
            Regístrese. Publíquese en el Boletín Oficial de la Ciudad de Buenos Aires. Comuníquese a {{ destinatario }}. Cumplido, archívese.
        </div>
    </div>

    <div class="firma-section">
        <div class="firma-box">
            <div style="height: 60px;"></div>
            <div class="linea">Firma<br>Titular del Organismo</div>
        </div>
    </div>

    <div class="footer">
        Documento generado por EJE CLOUD IA — Gobierno de la Ciudad de Buenos Aires
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
        """Genera un documento HTML usando la plantilla correspondiente."""
        template_str = DOCUMENT_TEMPLATES.get(tipo, DOCUMENT_TEMPLATES["informe"])

        env = Environment(autoescape=False)
        template = env.from_string(template_str)

        now = datetime.now()
        context = {
            "asunto": asunto,
            "contenido": contenido,
            "destinatario": destinatario or "A quien corresponda",
            "fecha": now.strftime("%d de %B de %Y").replace(
                "January", "enero").replace("February", "febrero").replace(
                "March", "marzo").replace("April", "abril").replace(
                "May", "mayo").replace("June", "junio").replace(
                "July", "julio").replace("August", "agosto").replace(
                "September", "septiembre").replace("October", "octubre").replace(
                "November", "noviembre").replace("December", "diciembre"),
            "anio": now.year,
            "numero_expediente": "",
        }

        if datos_adicionales:
            context.update(datos_adicionales)

        return template.render(**context)
