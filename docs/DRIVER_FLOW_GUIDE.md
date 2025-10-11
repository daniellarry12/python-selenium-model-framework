# 🚗 Guía Completa del Flujo del WebDriver

**Autor:** Framework Pytest - Selenium
**Última actualización:** Octubre 2024
**Objetivo:** Entender el flujo completo desde la creación del driver hasta su uso en tests

---

## 📋 Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Flujo Completo Paso a Paso](#flujo-completo-paso-a-paso)
4. [Componentes Principales](#componentes-principales)
5. [Código en Detalle](#código-en-detalle)
6. [FAQ - Preguntas Frecuentes](#faq---preguntas-frecuentes)
7. [Ejemplos Prácticos](#ejemplos-prácticos)

---

## 🎯 Visión General

El framework utiliza un **patrón de capas** para gestionar WebDriver:

```
┌─────────────────────────────────────────────────────────────┐
│                    CAPAS DEL FRAMEWORK                      │
├─────────────────────────────────────────────────────────────┤
│  1. TESTS (test_login.py)                                   │
│     └─ Usa: self.driver                                     │
├─────────────────────────────────────────────────────────────┤
│  2. PYTEST INTEGRATION (conftest.py)                        │
│     └─ Fixtures, CLI options, parametrización               │
├─────────────────────────────────────────────────────────────┤
│  3. DRIVER MANAGEMENT (drivers/driver_manager.py)           │
│     └─ Configuración, timeouts, navegación                  │
├─────────────────────────────────────────────────────────────┤
│  4. BROWSER CREATION (drivers/browser_factory.py)           │
│     └─ Creación de Chrome, Firefox, Edge                    │
├─────────────────────────────────────────────────────────────┤
│  5. SELENIUM WEBDRIVER                                      │
│     └─ selenium.webdriver.chrome/firefox/edge               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Arquitectura del Sistema

### Separación de Responsabilidades

| Componente | Archivo | Responsabilidad | ¿Por qué existe? |
|------------|---------|-----------------|------------------|
| **BrowserFactory** | `drivers/browser_factory.py` | Crear drivers crudos (Chrome, Firefox, Edge) | Factory Pattern - Centraliza la creación |
| **DriverManager** | `drivers/driver_manager.py` | Configurar driver (timeouts, navegación, cleanup) | Simplifica la gestión del ciclo de vida |
| **conftest.py** | `conftest.py` | Integración con pytest (fixtures, CLI, parametrización) | Pytest-specific - No puede estar en DriverManager |
| **BaseTest** | `tests/base_test.py` | Clase base con fixture `initialize_driver` | DRY - Evita repetir `@pytest.mark.usefixtures` en cada test |

### Diagrama de Dependencias

```
┌──────────────────────────────────────────────────────────────┐
│                    DEPENDENCIAS                              │
└──────────────────────────────────────────────────────────────┘

test_login.py
    │
    ├─ Hereda: BaseTest
    │           │
    │           └─ Usa fixture: initialize_driver (de conftest.py)
    │
    └─ Usa: LoginPage(self.driver)


conftest.py
    │
    ├─ Importa: DriverManager
    │            │
    │            ├─ Importa: BrowserFactory
    │            │            │
    │            │            └─ Importa: selenium.webdriver
    │            │
    │            └─ Importa: EnvironmentConfig
    │
    └─ Define: Fixtures (initialize_driver, config, base_url)
```

---

## 🔄 Flujo Completo Paso a Paso

### Comando Inicial

```bash
pytest tests/test_login.py --browser=chrome --env=dev --headless
```

### Paso 1: Pytest Detecta el Test

```python
# tests/test_login.py:26
@pytest.mark.smoke
class TestLogin(BaseTest):  # ← Hereda de BaseTest
    def test_valid_credentials(self):
        ...
```

### Paso 2: Herencia de BaseTest

```python
# tests/base_test.py:5-7
@pytest.mark.usefixtures("initialize_driver")  # ← Activa el fixture
class BaseTest:
    driver: WebDriver  # ← Declaración de tipo (inyectado después)
```

**¿Qué hace `@pytest.mark.usefixtures`?**
- Le dice a pytest: "Antes de ejecutar cualquier test de esta clase, ejecuta el fixture `initialize_driver`"
- Es como un `@BeforeClass` en JUnit/TestNG

### Paso 3: Pytest Ejecuta el Fixture

```python
# conftest.py:120-181
@pytest.fixture
def initialize_driver(
    request,
    config: EnvironmentConfig,      # ← Inyectado por pytest
    base_url: str,                  # ← Inyectado por pytest
    browser_name: str               # ← De parametrización
) -> Generator[WebDriver, None, None]:
    """
    Este fixture se ejecuta ANTES de cada test.
    """
    headless = request.config.getoption("--headless")

    # ========================================
    # PUNTO CLAVE 1: Crear DriverManager
    # ========================================
    manager = DriverManager(
        browser=browser_name,    # "chrome"
        config=config,           # EnvironmentConfig(base_url="...", timeouts=...)
        headless=headless        # True/False
    )

    # ========================================
    # PUNTO CLAVE 2: Driver ya está listo
    # ========================================
    driver = manager.driver  # ← Driver creado y configurado en __init__

    # ========================================
    # PUNTO CLAVE 3: Inyección a la clase
    # ========================================
    request.cls.driver = driver  # ← Inyecta driver a self.driver

    # Logs para debugging
    print(f"\n{'='*70}")
    print(f"🌍 Environment: {config.environment.upper()}")
    print(f"🌐 Browser: {browser_name.upper()} {'(Headless)' if headless else ''}")
    print(f"🔗 Base URL: {base_url}")
    print(f"⏱️  Timeouts: {config.implicit_wait}s implicit | {config.page_load_timeout}s page load")
    print(f"{'='*70}")

    # ========================================
    # El test se ejecuta aquí (yield)
    # ========================================
    yield driver

    # ========================================
    # TEARDOWN: Después del test
    # ========================================
    print(f"\n{'='*70}")
    print(f"🧹 [Teardown] Closing {browser_name} driver...")
    print(f"{'='*70}")
    manager.quit()  # ← Limpieza (driver.quit())
```

### Paso 4: ¿Qué Hace `DriverManager.__init__()`?

**Ubicación:** `drivers/driver_manager.py:25-56`

```python
def __init__(self, browser: str, config: EnvironmentConfig, headless: bool = False, **browser_options):
    """
    ESTE ES EL CONSTRUCTOR QUE CREA Y CONFIGURA TODO.
    """

    # ====================================================================
    # PASO 4.1: Crear driver via BrowserFactory
    # ====================================================================
    self.driver = BrowserFactory.create(
        browser=browser,      # "chrome"
        headless=headless,    # True/False
        **browser_options     # Opciones adicionales
    )
    # Resultado: self.driver = <selenium.webdriver.Chrome instance>

    # ====================================================================
    # PASO 4.2: Aplicar timeouts del ambiente
    # ====================================================================
    # Implicit wait: tiempo de espera para encontrar elementos
    self.driver.implicitly_wait(config.implicit_wait)  # 10 segundos

    # Page load timeout: tiempo máximo para cargar una página
    self.driver.set_page_load_timeout(config.page_load_timeout)  # 30 segundos

    # ====================================================================
    # PASO 4.3: Navegar a la URL base
    # ====================================================================
    self.driver.get(config.base_url)  # https://tutorialsninja.com/demo

    # ====================================================================
    # PASO 4.4: Maximizar ventana (consistencia)
    # ====================================================================
    self.driver.maximize_window()
```

### Paso 5: ¿Qué Hace `BrowserFactory.create()`?

**Ubicación:** `drivers/browser_factory.py:30-60` (aprox)

```python
@staticmethod
def create(browser: str, headless: bool = False, **options) -> WebDriver:
    """
    Factory Method Pattern:
    - Centraliza la lógica de creación
    - Oculta detalles de implementación
    """
    browser = browser.lower()

    if browser == "chrome":
        # Crear opciones de Chrome
        chrome_options = ChromeOptions()
        if headless:
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Crear servicio (maneja el chromedriver)
        service = ChromeService()

        # ¡CREAR EL DRIVER!
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    elif browser == "firefox":
        # Similar para Firefox...
        pass

    elif browser == "edge":
        # Similar para Edge...
        pass

    else:
        raise ValueError(f"Browser '{browser}' not supported")
```

### Paso 6: Test Usa `self.driver`

```python
# tests/test_login.py:34-52
def test_valid_credentials(self):
    """
    En este punto, self.driver YA EXISTE (fue inyectado en Paso 3)
    """
    # ✅ self.driver está disponible (WebDriver configurado)
    login_page = LoginPage(self.driver)

    # Usar Page Object
    login_page.set_email_address(TestData.email)
    login_page.set_password(TestData.password)
    my_account_page = login_page.click_login_button()

    # Assertions
    assert my_account_page.get_title() == "My Account"
```

### Paso 7: Teardown (Limpieza)

```python
# conftest.py:168-172
yield driver  # ← El test se ejecuta aquí

# Después del test (éxito o fallo):
manager.quit()  # ← Llama a driver.quit()
```

**¿Qué hace `manager.quit()`?**

**Ubicación:** `drivers/driver_manager.py:58-70`

```python
def quit(self) -> None:
    """
    Limpieza segura del driver.
    """
    if hasattr(self, 'driver') and self.driver:
        try:
            self.driver.quit()  # ← Cierra el navegador
        except Exception as e:
            # Log pero no falla el test
            print(f"Warning: Error during driver cleanup: {e}")
        finally:
            self.driver = None
```

---

## 🧩 Componentes Principales

### 1. DriverManager (`drivers/driver_manager.py`)

**Responsabilidades:**
- Crear y configurar el WebDriver inmediatamente
- Configurar timeouts y navegación
- Proveer cleanup seguro

**API Pública:**

```python
class DriverManager:
    def __init__(self, browser: str, config: EnvironmentConfig, headless: bool = False):
        """Crea y configura el driver inmediatamente"""
        # self.driver está listo para usar

    def quit(self) -> None:
        """Cierra el driver de forma segura"""
```

**Ejemplo de Uso Standalone (sin pytest):**

```python
from drivers.driver_manager import DriverManager
from config.environment_manager import get_config

# Uso simple
config = get_config('dev')
manager = DriverManager('chrome', config, headless=True)
driver = manager.driver  # Ya está listo
try:
    driver.get("https://example.com")
    # ... hacer algo ...
finally:
    manager.quit()
```

### 2. BrowserFactory (`drivers/browser_factory.py`)

**Patrón:** Factory Method Pattern

**Responsabilidades:**
- Crear drivers específicos (Chrome, Firefox, Edge)
- Aplicar opciones específicas del navegador
- Ocultar detalles de implementación de Selenium

**API Pública:**

```python
class BrowserFactory:
    @staticmethod
    def create(browser: str, headless: bool = False, **options) -> WebDriver:
        """
        Factory method para crear WebDriver.

        Args:
            browser: 'chrome', 'firefox', 'edge'
            headless: Modo sin interfaz gráfica
            **options: Opciones adicionales (prefs, binary_location, etc.)

        Returns:
            WebDriver configurado (sin timeouts ni navegación)
        """
```

### 3. conftest.py (Pytest Integration)

**Patrón:** Dependency Injection (via Pytest)

**Responsabilidades:**
- Definir fixtures de pytest
- Parsear CLI options (`--browser`, `--env`, `--headless`)
- Parametrizar tests para múltiples navegadores
- Integrar DriverManager con pytest

**Fixtures Principales:**

```python
@pytest.fixture(scope="session")
def config(request) -> EnvironmentConfig:
    """Carga configuración del ambiente (dev/staging/prod)"""

@pytest.fixture(scope="session")
def base_url(config: EnvironmentConfig) -> str:
    """Retorna URL base del config"""

@pytest.fixture
def initialize_driver(request, config, base_url, browser_name) -> WebDriver:
    """Crea, configura y retorna driver; limpieza automática"""
```

**CLI Options:**

```python
def pytest_addoption(parser):
    """
    Agrega opciones de línea de comandos:
    - --browser: chrome, firefox, edge, all
    - --env: dev, staging, prod
    - --headless: modo sin UI
    """
```

### 4. BaseTest (`tests/base_test.py`)

**Patrón:** Template Method Pattern

**Responsabilidad:**
- Proveer clase base para todos los tests
- Evitar repetir `@pytest.mark.usefixtures` en cada clase

```python
@pytest.mark.usefixtures("initialize_driver")
class BaseTest:
    driver: WebDriver  # Type hint (inyectado por fixture)
```

**Uso en Tests:**

```python
class TestLogin(BaseTest):  # ← Hereda fixture automáticamente
    def test_something(self):
        self.driver.get("...")  # ✅ driver disponible
```

---

## 💻 Código en Detalle

### Ejemplo Completo de Ejecución

```python
# ============================================================================
# COMANDO
# ============================================================================
pytest tests/test_login.py::TestLogin::test_valid_credentials --browser=chrome --env=dev

# ============================================================================
# PASO 1: pytest_addoption (conftest.py:29-54)
# ============================================================================
# Parsea: --browser=chrome --env=dev
# Resultado:
#   request.config.getoption("--browser") → "chrome"
#   request.config.getoption("--env") → "dev"

# ============================================================================
# PASO 2: pytest_generate_tests (conftest.py:94-113)
# ============================================================================
# Parametriza test con browser_name="chrome"

# ============================================================================
# PASO 3: Fixture 'config' (conftest.py:61-74)
# ============================================================================
env_name = "dev"  # De --env
config = get_config(env_name)
# Resultado:
#   config.environment = "dev"
#   config.base_url = "https://tutorialsninja.com/demo"
#   config.implicit_wait = 10
#   config.page_load_timeout = 30

# ============================================================================
# PASO 4: Fixture 'initialize_driver' (conftest.py:120-181)
# ============================================================================
browser_name = "chrome"  # De parametrización
headless = False         # No se pasó --headless

# 4.1: Crear DriverManager
manager = DriverManager(
    browser="chrome",
    config=config,
    headless=False
)

# 4.2: Driver ya está creado y configurado
driver = manager.driver  # Ya listo (creado en __init__)

# 4.3: Inyectar a clase
request.cls.driver = driver
# Ahora: TestLogin.driver = <selenium.webdriver.Chrome>

# ============================================================================
# PASO 5: DriverManager.__init__() (driver_manager.py:25-56)
# ============================================================================

# 5.1: Crear driver
self.driver = BrowserFactory.create(
    browser="chrome",
    headless=False
)
# ← ¡VER PASO 6!

# 5.2: Configurar timeouts
self.driver.implicitly_wait(10)  # config.implicit_wait
self.driver.set_page_load_timeout(30)  # config.page_load_timeout

# 5.3: Navegar a base URL
self.driver.get("https://tutorialsninja.com/demo")  # config.base_url

# 5.4: Maximizar ventana
self.driver.maximize_window()

# ============================================================================
# PASO 6: BrowserFactory.create() (browser_factory.py)
# ============================================================================

# 6.1: Crear opciones
chrome_options = ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 6.2: Crear servicio
service = ChromeService()

# 6.3: Crear driver RAW
driver = webdriver.Chrome(service=service, options=chrome_options)
# Resultado: <selenium.webdriver.Chrome (session="abc123")>

# 6.4: Retornar
return driver

# ============================================================================
# PASO 7: Test se ejecuta (test_login.py:34-66)
# ============================================================================
def test_valid_credentials(self):
    # self.driver = <selenium.webdriver.Chrome> (inyectado en Paso 4.3)

    login_page = LoginPage(self.driver)
    login_page.set_email_address("daniel@gmail.com")
    login_page.set_password("daniel12345")
    my_account_page = login_page.click_login_button()

    # Assertions
    assert my_account_page.get_title() == "My Account"
    assert "account/account" in my_account_page.get_current_url()

# ============================================================================
# PASO 8: Teardown (conftest.py:177-181)
# ============================================================================
# Fixture hace yield, test termina, ahora ejecuta cleanup

manager.quit()

# ============================================================================
# PASO 9: manager.quit() (driver_manager.py:58-70)
# ============================================================================
if hasattr(self, 'driver') and self.driver:
    try:
        self.driver.quit()  # Cierra navegador
    except Exception as e:
        print(f"Warning: Error during cleanup: {e}")
    finally:
        self.driver = None

# ============================================================================
# FIN
# ============================================================================
```

---

## ❓ FAQ - Preguntas Frecuentes

### ❓ ¿Por qué existe DriverManager si ya hay fixture en conftest?

**Respuesta:** Separación de responsabilidades (Single Responsibility Principle)

| Sin DriverManager | Con DriverManager |
|-------------------|-------------------|
| `conftest.py` tendría 100+ líneas mezclando pytest con lógica de driver | `conftest.py` tiene solo 15 líneas para el fixture |
| No reutilizable fuera de pytest | DriverManager es reutilizable en scripts standalone |
| Difícil de testear | Fácil de testear (unit tests para DriverManager) |
| Viola SRP | Cada clase tiene una responsabilidad |

**Ejemplo sin DriverManager:**

```python
# ❌ TODO EN CONFTEST.PY (anti-pattern)
@pytest.fixture
def initialize_driver(config, browser_name, headless):
    # 50 líneas creando driver
    if browser_name == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless")
        service = ChromeService()
        driver = webdriver.Chrome(service=service, options=options)
    elif browser_name == "firefox":
        # ... más código duplicado ...

    # 30 líneas configurando timeouts
    driver.implicitly_wait(config.implicit_wait)
    driver.set_page_load_timeout(config.page_load_timeout)
    driver.get(config.base_url)
    driver.maximize_window()

    yield driver

    # 10 líneas de cleanup
    try:
        driver.quit()
    except:
        pass
```

**Con DriverManager:**

```python
# ✅ LIMPIO Y MANTENIBLE
@pytest.fixture
def initialize_driver(config, browser_name, headless):
    manager = DriverManager(browser_name, config, headless)
    request.cls.driver = manager.driver
    yield manager.driver
    manager.quit()
```

---

### ❓ ¿Dónde exactamente se crea la instancia del driver?

**Respuesta:** En `BrowserFactory.create()` línea ~50 (aprox)

```python
# drivers/browser_factory.py
driver = webdriver.Chrome(service=service, options=chrome_options)
```

**Traza de llamadas:**

```
conftest.py:initialize_driver()
    └─ manager.start()                     [driver_manager.py:84]
        └─ BrowserFactory.create()         [browser_factory.py:30]
            └─ webdriver.Chrome()          [selenium/webdriver/chrome/webdriver.py]
                └─ ChromeDriver.exe        [OS process]
```

---

### ❓ ¿Cómo llega `driver` a `self.driver` en los tests?

**Respuesta:** Inyección via `request.cls.driver`

```python
# conftest.py:164
request.cls.driver = driver

# Explicación:
# - request: objeto pytest que contiene metadata del test
# - request.cls: la clase del test (ej: TestLogin)
# - request.cls.driver = driver: asigna driver como atributo de clase

# Equivalente a:
TestLogin.driver = driver

# Por eso funciona:
class TestLogin(BaseTest):
    def test_something(self):
        self.driver.get("...")  # ✅ Funciona
```

---

### ❓ ¿Puedo usar DriverManager sin pytest?

**Respuesta:** ¡Sí! Es completamente independiente.

```python
# script_standalone.py
from drivers.driver_manager import DriverManager
from config.environment_manager import get_config

# Cargar config
config = get_config('prod')

# Uso simple
manager = DriverManager('firefox', config, headless=True)
driver = manager.driver
try:
    driver.get("https://example.com")
    title = driver.title
    print(f"Title: {title}")
finally:
    manager.quit()
```

---

### ❓ ¿Qué pasa si no heredo de BaseTest?

**Respuesta:** Debes usar el fixture manualmente.

```python
# Opción 1: Heredar de BaseTest (recomendado)
class TestLogin(BaseTest):
    def test_something(self):
        self.driver.get("...")  # ✅ Funciona

# Opción 2: Usar fixture manualmente
class TestStandalone:  # No hereda de BaseTest
    def test_something(self, initialize_driver):
        # initialize_driver es el driver (fixture retorna WebDriver)
        initialize_driver.get("...")  # ✅ Funciona

# Opción 3: Marcar clase manualmente
@pytest.mark.usefixtures("initialize_driver")
class TestManual:
    driver: WebDriver

    def test_something(self):
        self.driver.get("...")  # ✅ Funciona
```

---

### ❓ ¿Por qué `yield` en el fixture?

**Respuesta:** Permite separar setup y teardown.

```python
@pytest.fixture
def initialize_driver(...):
    # ========== SETUP (antes del test) ==========
    manager = DriverManager(...)
    driver = manager.start()
    request.cls.driver = driver

    # ========== TEST SE EJECUTA AQUÍ ==========
    yield driver  # ← Pausa aquí, ejecuta test, luego continúa

    # ========== TEARDOWN (después del test) ==========
    manager.quit()
    # Se ejecuta INCLUSO si el test falla
```

**Alternativa sin yield (antiguo):**

```python
# ❌ ANTIGUO (pytest < 3.0)
@pytest.fixture
def driver_old(request):
    driver = webdriver.Chrome()

    def teardown():
        driver.quit()

    request.addfinalizer(teardown)
    return driver
```

---

### ❓ ¿Qué es `scope="session"` en fixture config?

**Respuesta:** Define cuántas veces se ejecuta el fixture.

| Scope | Ejecución | Ejemplo |
|-------|-----------|---------|
| `function` (default) | Una vez por test | Driver nuevo para cada test |
| `class` | Una vez por clase | Driver compartido en TestLogin |
| `module` | Una vez por archivo | Driver compartido en test_login.py |
| `session` | Una vez por sesión pytest | Config cargado solo una vez |

```python
# conftest.py:61
@pytest.fixture(scope="session")  # ← Se ejecuta 1 vez para toda la sesión
def config(request) -> EnvironmentConfig:
    env_name = request.config.getoption("--env")
    return get_config(env_name)  # Carga config solo 1 vez

# ¿Por qué?
# - Cargar config es costoso (leer .env, validar, etc.)
# - Config no cambia durante la ejecución
# - Mejora performance
```

---

### ❓ ¿Qué es `browser_name` en initialize_driver?

**Respuesta:** Viene de la parametrización dinámica.

```python
# conftest.py:94-113
def pytest_generate_tests(metafunc):
    """
    Hook de pytest que se ejecuta ANTES de colectar tests.
    Genera variantes del test para diferentes navegadores.
    """
    if "initialize_driver" in metafunc.fixturenames:
        browser_option = metafunc.config.getoption("--browser").lower()

        if browser_option == "all":
            browsers = ["chrome", "firefox", "edge"]
        else:
            browsers = [browser_option]

        # Parametriza browser_name
        metafunc.parametrize("browser_name", browsers, indirect=False)

# Resultado:
# pytest --browser=chrome
#   → browser_name = "chrome"
#   → 1 test execution

# pytest --browser=all
#   → browser_name = ["chrome", "firefox", "edge"]
#   → 3 test executions (uno por navegador)
```

**Ejemplo de salida:**

```bash
$ pytest tests/test_login.py::TestLogin::test_valid_credentials --browser=all -v

tests/test_login.py::TestLogin::test_valid_credentials[chrome] PASSED
tests/test_login.py::TestLogin::test_valid_credentials[firefox] PASSED
tests/test_login.py::TestLogin::test_valid_credentials[edge] PASSED
```

---

## 🔧 Ejemplos Prácticos

### Ejemplo 1: Ejecutar Test Simple

```bash
# Test en Chrome (default)
pytest tests/test_login.py::TestLogin::test_valid_credentials

# Test en Firefox
pytest tests/test_login.py::TestLogin::test_valid_credentials --browser=firefox

# Test en modo headless
pytest tests/test_login.py --browser=chrome --headless

# Test en staging
pytest tests/test_login.py --env=staging
```

### Ejemplo 2: Ejecutar en Todos los Navegadores

```bash
# Ejecuta el mismo test en Chrome, Firefox y Edge
pytest tests/test_login.py::TestLogin::test_valid_credentials --browser=all

# Output:
# test_valid_credentials[chrome] PASSED
# test_valid_credentials[firefox] PASSED
# test_valid_credentials[edge] PASSED
```

### Ejemplo 3: Debugging con Print Statements

```python
# tests/test_debug.py
class TestDebug(BaseTest):
    def test_check_driver(self):
        # Ver qué driver se creó
        print(f"\nDriver type: {type(self.driver)}")
        print(f"Driver session: {self.driver.session_id}")
        print(f"Current URL: {self.driver.current_url}")

        # Ver capabilities
        caps = self.driver.capabilities
        print(f"Browser: {caps['browserName']}")
        print(f"Version: {caps['browserVersion']}")
```

### Ejemplo 4: Usar DriverManager en Script

```python
# scripts/scrape_data.py
"""
Script standalone para scraping sin pytest.
"""
from drivers.driver_manager import DriverManager
from config.environment_manager import get_config

def main():
    config = get_config('prod')

    manager = DriverManager('chrome', config, headless=True)
    driver = manager.driver
    try:
        driver.get("https://example.com")

        # Scraping logic
        elements = driver.find_elements(By.CSS_SELECTOR, ".item")
        for elem in elements:
            print(elem.text)
    finally:
        manager.quit()

if __name__ == "__main__":
    main()
```

### Ejemplo 5: Override de Configuración

```python
# tests/test_custom_config.py
class TestCustomTimeout(BaseTest):
    def test_with_longer_timeout(self):
        # Override timeout para este test específico
        self.driver.implicitly_wait(30)  # Override config (default: 10s)

        # Buscar elemento que tarda en cargar
        slow_element = self.driver.find_element(By.ID, "slow-loading")
        assert slow_element.is_displayed()
```

---

## 📊 Diagramas de Secuencia

### Diagrama 1: Flujo Completo

```
Usuario              Pytest           conftest.py         DriverManager      BrowserFactory    Selenium
  │                    │                    │                    │                  │              │
  │ pytest test_login  │                    │                    │                  │              │
  │───────────────────>│                    │                    │                  │              │
  │                    │                    │                    │                  │              │
  │                    │ Detecta BaseTest   │                    │                  │              │
  │                    │ @usefixtures()     │                    │                  │              │
  │                    │─────────────────>  │                    │                  │              │
  │                    │                    │                    │                  │              │
  │                    │                    │ new DriverManager  │                  │              │
  │                    │                    │───────────────────>│                  │              │
  │                    │                    │                    │                  │              │
  │                    │                    │ manager.start()    │                  │              │
  │                    │                    │───────────────────>│                  │              │
  │                    │                    │                    │                  │              │
  │                    │                    │                    │ create("chrome") │              │
  │                    │                    │                    │─────────────────>│              │
  │                    │                    │                    │                  │              │
  │                    │                    │                    │                  │ new Chrome() │
  │                    │                    │                    │                  │─────────────>│
  │                    │                    │                    │                  │              │
  │                    │                    │                    │                  │    driver    │
  │                    │                    │                    │                  │<─────────────│
  │                    │                    │                    │      driver      │              │
  │                    │                    │                    │<─────────────────│              │
  │                    │                    │                    │                  │              │
  │                    │                    │                    │ configure driver │              │
  │                    │                    │                    │ (timeouts, nav)  │              │
  │                    │                    │                    │                  │              │
  │                    │                    │       driver       │                  │              │
  │                    │                    │<───────────────────│                  │              │
  │                    │                    │                    │                  │              │
  │                    │                    │ request.cls.driver = driver           │              │
  │                    │                    │ (inyección)        │                  │              │
  │                    │                    │                    │                  │              │
  │                    │    yield driver    │                    │                  │              │
  │                    │<───────────────────│                    │                  │              │
  │                    │                    │                    │                  │              │
  │                    │ ejecuta test       │                    │                  │              │
  │                    │ test usa self.driver                    │                  │              │
  │                    │                    │                    │                  │              │
  │                    │ test termina       │                    │                  │              │
  │                    │                    │                    │                  │              │
  │                    │                    │ manager.quit()     │                  │              │
  │                    │                    │───────────────────>│                  │              │
  │                    │                    │                    │                  │              │
  │                    │                    │                    │ driver.quit()    │              │
  │                    │                    │                    │─────────────────────────────────>│
  │                    │                    │                    │                  │              │
  │<───────────────────┴────────────────────┴────────────────────┴──────────────────┴──────────────│
  │ Test completo                          │                    │                  │              │
```

### Diagrama 2: Herencia y Fixtures

```
┌─────────────────────────────────────────────────────────────────────┐
│                    HERENCIA DE FIXTURES                             │
└─────────────────────────────────────────────────────────────────────┘

BaseTest (tests/base_test.py)
├─ @pytest.mark.usefixtures("initialize_driver")
├─ driver: WebDriver  (type hint)
│
├──> TestLogin(BaseTest)  (hereda fixture)
│    ├─ test_valid_credentials(self)
│    │   └─ self.driver ✅ (inyectado por fixture)
│    │
│    └─ test_invalid_credentials(self)
│        └─ self.driver ✅ (inyectado por fixture)
│
├──> TestChangePassword(BaseTest)  (hereda fixture)
│    └─ test_change_password(self)
│        └─ self.driver ✅ (inyectado por fixture)
│
└──> TestRegistration(BaseTest)  (hereda fixture)
     └─ test_register_user(self)
         └─ self.driver ✅ (inyectado por fixture)


conftest.py
├─ @pytest.fixture: initialize_driver
│   └─ Ejecutado automáticamente por @pytest.mark.usefixtures
│
├─ @pytest.fixture: config
│   └─ Inyectado a initialize_driver
│
└─ @pytest.fixture: base_url
    └─ Inyectado a initialize_driver
```

---

## 🎓 Conclusiones

### Ventajas de esta Arquitectura

✅ **Separación de Responsabilidades**
- Cada componente tiene un propósito claro
- Fácil de mantener y extender

✅ **Reutilización**
- DriverManager funciona sin pytest
- BrowserFactory reutilizable en otros contextos

✅ **Testabilidad**
- Componentes independientes = fáciles de testear
- Mocks fáciles de crear

✅ **Escalabilidad**
- Agregar nuevo navegador: solo modificar BrowserFactory
- Agregar nuevo ambiente: solo modificar config/

✅ **Legibilidad**
- Flujo claro y predecible
- Documentación inline

### Flujo Resumido

```
pytest comando
    ↓
Detecta BaseTest
    ↓
Ejecuta fixture initialize_driver
    ↓
Crea DriverManager
    ↓
manager.start() → BrowserFactory.create() → webdriver.Chrome()
    ↓
Configura driver (timeouts, navegación)
    ↓
Inyecta a self.driver
    ↓
Test usa self.driver
    ↓
Teardown: manager.quit() → driver.quit()
```

---

## 📚 Referencias

- **Pytest Fixtures:** https://docs.pytest.org/en/stable/fixture.html
- **Selenium WebDriver:** https://www.selenium.dev/documentation/webdriver/
- **Design Patterns:** https://refactoring.guru/design-patterns

---

**¿Preguntas?** Revisa la sección [FAQ](#faq---preguntas-frecuentes) o consulta el código fuente con los comentarios inline.