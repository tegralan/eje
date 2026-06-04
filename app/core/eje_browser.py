"""
Módulo de automatización de navegador para EJE CLOUD.
Maneja la sesión de Chrome y las interacciones con la plataforma.
"""
import asyncio
import logging
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright

from app.core.config import settings

logger = logging.getLogger(__name__)


class EjeCloudBrowser:
    def __init__(self):
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._authenticated = False

    async def start(self):
        """Inicia el navegador Playwright."""
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=settings.browser_headless,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        self._context = await self._browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="es-AR",
        )
        self._page = await self._context.new_page()
        self._page.set_default_timeout(settings.browser_timeout)
        logger.info("Navegador iniciado correctamente")

    async def stop(self):
        """Cierra el navegador."""
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._authenticated = False
        logger.info("Navegador cerrado")

    async def login(self, usuario: str = None, password: str = None) -> bool:
        """Autentica en EJE CLOUD."""
        if not self._page:
            await self.start()

        user = usuario or settings.eje_cloud_user
        pwd = password or settings.eje_cloud_password

        try:
            await self._page.goto(settings.eje_cloud_url, wait_until="networkidle")

            # Espera el formulario de login
            await self._page.wait_for_selector("input[type='text'], input[name='usuario'], input[id*='user']", timeout=10000)

            # Completa usuario
            user_input = await self._page.query_selector(
                "input[type='text'], input[name='usuario'], input[id*='user'], input[placeholder*='usuario']"
            )
            if user_input:
                await user_input.fill(user)

            # Completa contraseña
            pass_input = await self._page.query_selector("input[type='password']")
            if pass_input:
                await pass_input.fill(pwd)

            # Hace click en ingresar
            submit = await self._page.query_selector(
                "button[type='submit'], input[type='submit'], button:has-text('Ingresar'), button:has-text('Iniciar')"
            )
            if submit:
                await submit.click()
                await self._page.wait_for_load_state("networkidle")

            self._authenticated = True
            logger.info(f"Autenticación exitosa para usuario: {user}")
            return True

        except Exception as e:
            logger.error(f"Error al autenticar: {e}")
            return False

    async def navigate_to(self, url_path: str) -> str:
        """Navega a una sección de EJE CLOUD."""
        if not self._page:
            raise RuntimeError("Navegador no iniciado")

        full_url = f"{settings.eje_cloud_url.rstrip('/')}/{url_path.lstrip('/')}"
        await self._page.goto(full_url, wait_until="networkidle")
        return await self.get_page_content()

    async def get_page_content(self) -> str:
        """Extrae el contenido de texto de la página actual."""
        if not self._page:
            raise RuntimeError("Navegador no iniciado")

        # Extrae texto limpio
        content = await self._page.evaluate("""() => {
            const elements = document.querySelectorAll('table, .data-grid, .grid, [class*="table"], [class*="grid"], main, #content, #main-content, .content');
            if (elements.length > 0) {
                return Array.from(elements).map(el => el.innerText).join('\\n\\n');
            }
            return document.body.innerText;
        }""")
        return content or ""

    async def get_page_html(self) -> str:
        """Obtiene el HTML de la página actual."""
        if not self._page:
            raise RuntimeError("Navegador no iniciado")
        return await self._page.content()

    async def search_in_page(self, campo: str, valor: str) -> str:
        """Busca un valor en un campo de búsqueda."""
        if not self._page:
            raise RuntimeError("Navegador no iniciado")

        try:
            selector = f"input[placeholder*='{campo}'], input[name*='{campo}'], input[id*='{campo}']"
            input_el = await self._page.query_selector(selector)
            if input_el:
                await input_el.fill(valor)
                await self._page.keyboard.press("Enter")
                await self._page.wait_for_load_state("networkidle")
                return await self.get_page_content()
            return f"No se encontró el campo de búsqueda: {campo}"
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            return f"Error al buscar: {str(e)}"

    async def click_element(self, texto: str) -> str:
        """Hace click en un elemento por su texto."""
        if not self._page:
            raise RuntimeError("Navegador no iniciado")

        try:
            await self._page.click(f"text={texto}", timeout=5000)
            await self._page.wait_for_load_state("networkidle")
            return await self.get_page_content()
        except Exception as e:
            logger.error(f"Error al hacer click en '{texto}': {e}")
            return f"Error al hacer click: {str(e)}"

    async def take_screenshot(self, path: str = "/tmp/eje_screenshot.png") -> str:
        """Captura una imagen de la página actual."""
        if not self._page:
            raise RuntimeError("Navegador no iniciado")
        await self._page.screenshot(path=path, full_page=True)
        return path

    async def extract_table_data(self) -> list:
        """Extrae datos de tablas en la página actual."""
        if not self._page:
            raise RuntimeError("Navegador no iniciado")

        data = await self._page.evaluate("""() => {
            const tables = document.querySelectorAll('table');
            const result = [];
            tables.forEach(table => {
                const headers = Array.from(table.querySelectorAll('th')).map(th => th.innerText.trim());
                const rows = Array.from(table.querySelectorAll('tbody tr')).map(tr => {
                    const cells = Array.from(tr.querySelectorAll('td')).map(td => td.innerText.trim());
                    if (headers.length > 0) {
                        const obj = {};
                        headers.forEach((h, i) => { obj[h] = cells[i] || ''; });
                        return obj;
                    }
                    return cells;
                });
                if (rows.length > 0) result.push({ headers, rows });
            });
            return result;
        }""")
        return data or []

    async def fill_form(self, campos: dict) -> str:
        """Completa un formulario con los datos proporcionados."""
        if not self._page:
            raise RuntimeError("Navegador no iniciado")

        resultados = []
        for campo, valor in campos.items():
            try:
                selector = f"input[name='{campo}'], input[id='{campo}'], textarea[name='{campo}'], select[name='{campo}']"
                el = await self._page.query_selector(selector)
                if el:
                    tag = await el.evaluate("el => el.tagName.toLowerCase()")
                    if tag == "select":
                        await el.select_option(label=str(valor))
                    else:
                        await el.fill(str(valor))
                    resultados.append(f"✓ {campo}: completado")
                else:
                    resultados.append(f"✗ {campo}: campo no encontrado")
            except Exception as e:
                resultados.append(f"✗ {campo}: error - {str(e)}")

        return "\n".join(resultados)

    @property
    def is_authenticated(self) -> bool:
        return self._authenticated

    @property
    def current_url(self) -> str:
        if self._page:
            return self._page.url
        return ""


# Instancia global del navegador
_browser_instance: Optional[EjeCloudBrowser] = None


async def get_browser() -> EjeCloudBrowser:
    """Obtiene la instancia global del navegador, iniciándola si es necesario."""
    global _browser_instance
    if _browser_instance is None:
        _browser_instance = EjeCloudBrowser()
        await _browser_instance.start()
    return _browser_instance


async def shutdown_browser():
    """Cierra el navegador global."""
    global _browser_instance
    if _browser_instance:
        await _browser_instance.stop()
        _browser_instance = None
