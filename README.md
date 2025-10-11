# 🎓 Production-Ready Selenium Framework with Pytest

[![CI/CD Pipeline](https://github.com/daniellarry12/python-selenium-model-framework/actions/workflows/tests.yml/badge.svg)](https://github.com/daniellarry12/python-selenium-model-framework/actions/workflows/tests.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Selenium](https://img.shields.io/badge/selenium-4.0+-green.svg)](https://www.selenium.dev/)
[![Pytest](https://img.shields.io/badge/pytest-8.0+-orange.svg)](https://docs.pytest.org/)

> **🎯 Misión:** Framework de referencia que demuestra **estándares de la industria** y **mejores prácticas** para automatización de pruebas web. Diseñado como **guía educativa** y **base productiva** para equipos de QA.

---

## 📚 Tabla de Contenidos

- [¿Qué hace especial a este framework?](#-qué-hace-especial-a-este-framework)
- [Quick Start](#-quick-start-5-minutos)
- [Arquitectura](#-arquitectura-del-framework)
- [Ejecución de Tests](#-ejecución-de-tests)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Mejores Prácticas](#-mejores-prácticas-implementadas)

---

## 🌟 ¿Qué hace especial a este framework?

### ✅ **Arquitectura Limpia y Simplificada**
- ✨ **Page Object Model** - Separación UI/lógica de tests
- 🏭 **Factory Pattern** - Drivers con configuración productiva
- 📦 **Builder Pattern** - Opciones de navegador modulares
- 🎯 **Lifecycle Manager** - Gestión simplificada del driver
- ⚡ **Explicit Waits** - Cero `time.sleep()`

### 🎓 **Código Educativo**
- 📖 Docstrings completos en español
- 🧪 Tests demostrativos con patrones avanzados
- 🔬 Parametrización y markers
- 🛠️ Multi-ambiente (dev/staging/prod)
- 📊 CI/CD completo con GitHub Actions

### 🚀 **Production-Ready**
- ✅ Multi-browser (Chrome, Firefox, Edge)
- ✅ Headless mode para CI/CD
- ✅ Docker support (AMD64 + ARM64)
- ✅ Secrets management
- ✅ Parallel execution ready

---

## 🚀 Quick Start (5 minutos)

### **Opción A: Docker (Recomendado) 🐳**

```bash
# 1. Clonar
git clone https://github.com/daniellarry12/python-selenium-model-framework.git
cd python-selenium-model-framework

# 2. Ejecutar
docker-compose up

# ✅ Tests corren automáticamente
```

**Ventajas:**
- ✅ Zero setup - No instalar Python ni dependencias
- ✅ 100% consistente - Mismo ambiente everywhere
- ✅ Soporta ARM (M1/M2) y AMD64

---

### **Opción B: Instalación Local**

```bash
# 1. Clonar
git clone https://github.com/daniellarry12/python-selenium-model-framework.git
cd python-selenium-model-framework

# 2. Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar smoke tests
pytest -m smoke --browser=chrome
```

---

## 🏗️ Arquitectura del Framework

### **Diagrama de Componentes**

```
┌─────────────────────────────────────────────────────────┐
│                    TESTS (test_*.py)                    │
│                    ↓ usa Page Objects                   │
├─────────────────────────────────────────────────────────┤
│                  PAGES (Page Object Model)              │
│   LoginPage → BasePage ← MyAccountPage                  │
│                    ↓ hereda 54 métodos                  │
├─────────────────────────────────────────────────────────┤
│                PYTEST INTEGRATION (conftest.py)         │
│   CLI Options | Fixtures | Parametrization             │
│                    ↓ usa DriverManager                  │
├─────────────────────────────────────────────────────────┤
│              DRIVER LIFECYCLE (DriverManager)           │
│   Combina: Factory + Config + Navegación               │
│                    ↓ usa                                │
├─────────────────────────────────────────────────────────┤
│             BROWSER CREATION (BrowserFactory)           │
│   Chrome | Firefox | Edge                              │
│                    ↓ usa Builders                       │
├─────────────────────────────────────────────────────────┤
│          BROWSER OPTIONS (Options Builders)             │
│   ChromeOptionsBuilder | FirefoxOptionsBuilder          │
│                    ↓ retorna                            │
├─────────────────────────────────────────────────────────┤
│                  SELENIUM WEBDRIVER                     │
└─────────────────────────────────────────────────────────┘
```

---

### **1️⃣ Page Object Model**

```python
# ❌ Anti-pattern: Todo en el test
def test_login():
    driver.find_element(By.ID, "email").send_keys("user@test.com")
    driver.find_element(By.ID, "password").send_keys("pass123")
    driver.find_element(By.XPATH, "//button").click()

# ✅ Pattern: Page Objects
def test_login():
    login_page = LoginPage(driver)
    login_page.set_email("user@test.com")
    login_page.set_password("pass123")
    my_account_page = login_page.click_login_button()
    assert my_account_page.get_title() == "My Account"
```

**Beneficios:**
- 🔄 Reutilización de código
- 🛠️ Cambios de UI en un solo lugar
- 📖 Tests legibles y declarativos

---

### **2️⃣ Factory + Builder Pattern**

```python
# BrowserFactory - Centraliza creación
driver = BrowserFactory.create('chrome', headless=True)

# Usa Builders especializados internamente:
BrowserFactory.create()
    ├── ChromeOptionsBuilder.build()    # --no-sandbox, --disable-dev-shm
    ├── FirefoxOptionsBuilder.build()   # -private, preferences
    └── EdgeOptionsBuilder.build()      # InPrivate, optimizaciones
```

**Características:**
- 🎯 Opciones productivas pre-configuradas
- 🚫 Previene crashes en CI/CD
- 🔒 Modo incógnito habilitado
- 📏 Ventanas de tamaño consistente

---

### **3️⃣ Lifecycle Manager (DriverManager)**

```python
from drivers.driver_manager import DriverManager
from config.environment_manager import get_config

# Todo en un paso
config = get_config('dev')
manager = DriverManager('chrome', config, headless=True)

# Driver listo inmediatamente
driver = manager.driver  # Ya configurado + navegado a base_url

# Cleanup
manager.quit()
```

**Qué hace DriverManager:**
1. Crea driver via `BrowserFactory`
2. Aplica timeouts (implicit_wait, page_load_timeout)
3. Navega a base_url
4. Maximiza ventana
5. Todo en `__init__` - API simple

**API:**
- `__init__(browser, config, headless)` - Crea y configura
- `driver` - Propiedad pública con WebDriver
- `quit()` - Cleanup seguro

---

### **4️⃣ Environment Management**

```python
from config.environment_manager import get_config

# Carga config por ambiente
config = get_config('staging')

# Config inmutable (frozen dataclass)
print(config.base_url)           # De .env (STAGING_BASE_URL)
print(config.implicit_wait)      # De base_config.py
print(config.page_load_timeout)  # De base_config.py
```

**Fuentes de configuración:**
- `.env` → URLs, credenciales por ambiente
- `config/base_config.py` → Timeouts, configuración global

---

### **Flujo de Ejecución Completo**

```
1. pytest --env=dev --browser=chrome --headless

2. conftest.py
   ├── pytest_addoption() → parsea CLI flags
   ├── config fixture → get_config('dev')
   └── initialize_driver fixture
       ├── DriverManager('chrome', config, headless=True)
       │   ├── BrowserFactory.create('chrome', headless=True)
       │   │   └── ChromeOptionsBuilder.build(headless=True)
       │   │       └── webdriver.Chrome(options)
       │   ├── driver.implicitly_wait(10)
       │   ├── driver.set_page_load_timeout(30)
       │   ├── driver.get(config.base_url)
       │   └── driver.maximize_window()
       └── request.cls.driver = manager.driver

3. Test ejecuta
   ├── self.driver disponible
   ├── LoginPage(self.driver)
   └── Explicit waits via BasePage

4. Teardown
   └── manager.quit()
```

---

## 🧪 Ejecución de Tests

### **Comandos Esenciales**

```bash
# Smoke tests (críticos, ~30s)
pytest -m smoke

# Suite completo
pytest --browser=chrome -v

# Multi-browser
pytest --browser=all        # Chrome + Firefox + Edge

# Multi-environment
pytest --env=dev            # Local
pytest --env=staging --headless
pytest --env=prod --headless -m smoke

# Reportes
pytest --html=reports/report.html --self-contained-html

# Parallel (requiere pytest-xdist)
pytest -n auto

# Debug
pytest --pdb               # Debugger interactivo
pytest -vv --tb=long       # Traceback completo
```

### **Markers**

```python
@pytest.mark.smoke          # Tests críticos
@pytest.mark.regression     # Suite completo
@pytest.mark.slow          # Tests lentos

# Ejecutar
pytest -m smoke
pytest -m "smoke or regression"
pytest -m "not slow"
```

### **Parametrización**

```python
@pytest.mark.parametrize("email,password,expected", [
    ("", "", "Warning"),
    ("invalid@test.com", "wrong", "Warning"),
])
def test_login_validations(email, password, expected):
    login_page.login(email, password)
    assert expected in login_page.get_warning_message()
```

---

## 📁 Estructura del Proyecto

```
Pytest_Framework/
├── 📄 conftest.py                   # Fixtures globales de pytest
├── 📄 pytest.ini                    # Configuración pytest
├── 📄 requirements.txt              # Dependencias
├── 📄 .env                          # Variables locales (gitignore)
│
├── 📂 config/                       # Gestión de ambientes
│   ├── base_config.py               # Config global (timeouts)
│   └── environment_manager.py       # Carga configs por ambiente
│
├── 📂 drivers/                      # Creación y gestión de drivers
│   ├── browser_factory.py           # Factory pattern
│   ├── driver_manager.py            # Lifecycle manager (simplificado)
│   └── browser_options/
│       ├── chrome_options.py        # ChromeOptionsBuilder
│       ├── firefox_options.py       # FirefoxOptionsBuilder
│       └── edge_options.py          # EdgeOptionsBuilder
│
├── 📂 pages/                        # Page Object Models
│   ├── base_page.py                 # BasePage con 54 métodos
│   ├── login_page.py
│   ├── my_account_page.py
│   ├── change_password_page.py
│   └── components/
│       └── right_menu_component.py
│
├── 📂 tests/                        # Test suites
│   ├── base_test.py                 # Base class para tests
│   ├── test_login.py                # Login tests (smoke)
│   └── test_change_password.py
│
├── 📂 utilities/
│   └── test_data.py                 # Datos de prueba
│
├── 📂 docs/                         # Documentación
│   ├── DRIVER_FLOW_GUIDE.md         # Flujo completo del driver
│   └── DECORATORS_GUIDE.md          # Guía de decoradores
│
├── 📂 .github/workflows/
│   └── tests.yml                    # CI/CD pipeline
│
└── 📂 reports/
    └── report.html                  # Reportes HTML
```

### **Componentes Clave**

#### **conftest.py** - Integración con Pytest

```python
# 1. CLI Options
pytest_addoption()  # --env, --browser, --headless

# 2. Config fixture
@pytest.fixture(scope="session")
def config(request):
    return get_config(env_name)

# 3. Driver fixture
@pytest.fixture
def initialize_driver(config, browser_name):
    manager = DriverManager(browser_name, config, headless)
    yield manager.driver
    manager.quit()
```

#### **BrowserFactory** - Factory Pattern

```python
class BrowserFactory:
    @staticmethod
    def create(browser: str, headless: bool) -> WebDriver:
        if browser == "chrome":
            return BrowserFactory._create_chrome(headless)
        elif browser == "firefox":
            return BrowserFactory._create_firefox(headless)
        else:
            return BrowserFactory._create_edge(headless)
```

#### **DriverManager** - Lifecycle Simplificado

```python
class DriverManager:
    def __init__(self, browser, config, headless=False):
        # Crear driver
        self.driver = BrowserFactory.create(browser, headless)

        # Configurar timeouts
        self.driver.implicitly_wait(config.implicit_wait)
        self.driver.set_page_load_timeout(config.page_load_timeout)

        # Navegar y maximizar
        self.driver.get(config.base_url)
        self.driver.maximize_window()

    def quit(self):
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"Warning: {e}")
            finally:
                self.driver = None
```

---

## 🔥 CI/CD Pipeline

### **Pipeline Multi-Etapa**

```
┌─────────────────────────────────────────┐
│  STAGE 1: Smoke Tests (Fast - 30s)     │
│  ────────────────────────────────────   │
│  ✅ Pass → Continue                     │
│  ❌ Fail → Stop pipeline               │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  STAGE 2: Full Suite (2-3 min)         │
│  ────────────────────────────────────   │
│  • All tests                            │
│  • HTML reports (30 días retention)    │
│  • GitHub Summary                       │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  STAGE 3: Manual Testing (On-Demand)   │
│  ────────────────────────────────────   │
│  • Browser: chrome|firefox|all          │
│  • Environment: dev|staging|prod        │
│  • Test type: smoke|regression|all      │
└─────────────────────────────────────────┘
```

### **Features**

| Feature | Beneficio |
|---------|-----------|
| **Multi-stage** | Fast feedback (30s vs 3min) |
| **Smart caching** | Build 2x más rápido |
| **Artifacts** | HTML reports históricos |
| **Secrets** | Credenciales seguras |
| **Fail-fast** | Ahorra runner minutes |

### **Secrets Management**

```yaml
# GitHub → Settings → Secrets
DEV_BASE_URL=https://...
DEV_TEST_EMAIL=user@test.com
DEV_TEST_PASSWORD=pass123

# Uso en workflow
- name: Create .env
  run: |
    echo "DEV_BASE_URL=${{ secrets.DEV_BASE_URL }}" >> .env
```

---

## ✨ Mejores Prácticas Implementadas

### **1. No Hard-Coded Sleeps**

```python
# ❌ MAL
driver.find_element(By.ID, "button").click()
time.sleep(3)  # Frágil y lento

# ✅ BIEN
WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "button"))
).click()

# ✅ MEJOR (via BasePage)
self.wait_until_clickable(self.LOGIN_BUTTON).click()
```

### **2. Explicit Waits**

```python
# BasePage tiene 10+ explicit waits:
wait_until_visible()
wait_until_clickable()
wait_until_invisible()
wait_for_url_contains()
wait_for_title_contains()
```

### **3. Assertions Descriptivas**

```python
# ❌ MAL
assert driver.title == "My Account"

# ✅ BIEN
actual = driver.title
expected = "My Account"
assert actual == expected, (
    f"Expected '{expected}' but got '{actual}'. "
    f"URL: {driver.current_url}"
)
```

### **4. Locators Robustos**

```python
# Jerarquía de robustez (mejor → peor)
(By.ID, "username")                          # ✅ Mejor
(By.NAME, "email")                           # ✅ Bueno
(By.CSS_SELECTOR, "[data-testid='login']")  # ✅ Bueno
(By.XPATH, "//input[@placeholder='Email']") # ⚠️ OK
(By.XPATH, "/html/body/div[2]/form/...")    # ❌ Frágil
```

### **5. Test Independence**

```python
# ✅ Tests independientes
pytest --random-order  # Detecta dependencias

# ✅ Cleanup automático
@pytest.fixture(autouse=True)
def clean_cookies():
    yield
    driver.delete_all_cookies()
```

---

## 🌍 Ambientes

### **Configuración por Ambiente**

| Feature | Dev | Staging | Prod |
|---------|-----|---------|------|
| **Implicit Wait** | 10s | 15s | 20s |
| **Page Load** | 30s | 60s | 90s |
| **Headless** | ❌ No | ✅ Sí | ✅ Sí |
| **Uso** | Local dev | Pre-release | Monitoring |

### **Archivo .env**

```bash
TEST_ENV=dev
DEV_BASE_URL=https://example.com
DEV_TEST_EMAIL=user@test.com
DEV_TEST_PASSWORD=pass123

STAGING_BASE_URL=https://staging.example.com
STAGING_TEST_EMAIL=staging@test.com
STAGING_TEST_PASSWORD=staging123
```

---

## 📊 Estado del Proyecto

### ✅ Implementado
- [x] Page Object Model completo
- [x] Multi-browser (Chrome/Firefox/Edge)
- [x] Multi-environment (dev/staging/prod)
- [x] CI/CD Pipeline multi-etapa
- [x] Docker support (ARM64 + AMD64)
- [x] Explicit Waits (cero sleep)
- [x] Lifecycle Manager simplificado

### 🔮 Roadmap
- [ ] Allure Reports
- [ ] Visual Regression Testing
- [ ] API Testing integration
- [ ] Selenium Grid

---

## 🤝 Contribuir

```bash
# 1. Fork y clonar
git clone https://github.com/TU_USER/python-selenium-model-framework.git

# 2. Crear rama
git checkout -b feature/nueva-funcionalidad

# 3. Hacer cambios
# - Sigue patrones existentes
# - Agrega docstrings
# - Sin time.sleep()

# 4. Tests
pytest -m smoke

# 5. Commit
git commit -m "feat: Add nueva funcionalidad"

# 6. PR
git push origin feature/nueva-funcionalidad
```

### **Checklist**
- [ ] Tests pasan (`pytest -v`)
- [ ] Smoke pasa (`pytest -m smoke`)
- [ ] Docstrings completos
- [ ] Sin `time.sleep()`
- [ ] `.env` no commiteado

---

## 📚 Recursos

### Documentación
- [Selenium Docs](https://www.selenium.dev/documentation/)
- [Pytest Docs](https://docs.pytest.org/en/stable/)
- [GitHub Actions](https://docs.github.com/en/actions)

### Patrones
- [Page Object Model](https://martinfowler.com/bliki/PageObject.html)
- [Selenium Best Practices](https://www.selenium.dev/documentation/test_practices/)

---

## 👥 Autores

- **Daniel Aguilar** - [@daniellarry12](https://github.com/daniellarry12)
- **Claude (Anthropic)** - AI Pair Programming Assistant

---

## 📞 Soporte

- 🐛 [GitHub Issues](https://github.com/daniellarry12/python-selenium-model-framework/issues)
- 💬 [Discussions](https://github.com/daniellarry12/python-selenium-model-framework/discussions)

---

<div align="center">

**⭐ Si este proyecto te ayudó, dale una estrella ⭐**

**🚀 Happy Testing! 🚀**

</div>
