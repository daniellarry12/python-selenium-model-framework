# 🎓 Production-Ready Selenium Framework with Pytest

[![CI/CD Pipeline](https://github.com/daniellarry12/python-selenium-model-framework/actions/workflows/tests.yml/badge.svg)](https://github.com/daniellarry12/python-selenium-model-framework/actions/workflows/tests.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Selenium](https://img.shields.io/badge/selenium-4.0+-green.svg)](https://www.selenium.dev/)
[![Pytest](https://img.shields.io/badge/pytest-8.0+-orange.svg)](https://docs.pytest.org/)

> **🎯 Misión:** Ser un framework de referencia que demuestre **estándares de la industria** y **mejores prácticas** para automatización de pruebas web. Diseñado para servir como **guía educativa** y **base productiva** para equipos de QA.

---

## 📚 Tabla de Contenidos

- [¿Qué hace especial a este framework?](#-qué-hace-especial-a-este-framework)
- [Quick Start (5 minutos)](#-quick-start-5-minutos)
- [Arquitectura y Patrones de Diseño](#-arquitectura-y-patrones-de-diseño)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Ejecución de Tests](#-ejecución-de-tests)
- [Ambientes Multi-Environment](#-ambientes-multi-environment)
- [Mejores Prácticas Implementadas](#-mejores-prácticas-implementadas)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Contribuir](#-contribuir)

---

## 🌟 ¿Qué hace especial a este framework?

### ✅ **Estándares de Producción**
- ✨ **Page Object Model (POM)** - Separación clara entre tests y UI
- 🏭 **Factory Pattern** - Creación centralizada de drivers con configuraciones óptimas
- 🔄 **Dependency Injection** - Via fixtures de Pytest
- 📦 **Single Responsibility** - Cada componente hace una sola cosa bien
- 🎯 **Explicit Waits** - Cero `time.sleep()`, solo waits inteligentes

### 🎓 **Valor Educativo**
- 📖 Código auto-documentado con docstrings completos
- 🧪 Tests que demuestran diferentes patrones
- 🔬 Ejemplos de parametrización y markers
- 🛠️ Configuración multi-ambiente lista para usar
- 📊 CI/CD completo con GitHub Actions

### 🚀 **Listo para Producción**
- ✅ Multi-browser (Chrome, Firefox, Edge)
- ✅ Multi-environment (dev, staging, prod)
- ✅ Headless mode para CI/CD
- ✅ Reportes HTML con pytest-html
- ✅ Secrets management con GitHub
- ✅ Parallel execution ready (pytest-xdist)

---

## 🚀 Quick Start (5 minutos)

### 1. **Clonar el repositorio**
```bash
git clone https://github.com/daniellarry12/python-selenium-model-framework.git
cd python-selenium-model-framework
```

### 2. **Instalar dependencias**
```bash
# Usando pip
pip install -r requirements.txt

# O usando un virtual environment (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. **Configurar ambiente local**
```bash
# El .env ya está configurado con valores de ejemplo
# Para usar tus propias credenciales, edita .env
nano .env  # o usa tu editor favorito
```

### 4. **Ejecutar tu primer test**
```bash
# Smoke tests (rápidos, críticos)
pytest -m smoke --browser=chrome

# Suite completa
pytest --browser=chrome -v

# Con reporte HTML
pytest --browser=chrome --html=reports/report.html --self-contained-html
```

### 5. **Ver resultados**
- Consola: Logs detallados en tiempo real
- Reporte HTML: Abre `reports/report.html` en tu navegador
- CI/CD: Ve a [GitHub Actions](https://github.com/daniellarry12/python-selenium-model-framework/actions)

---

## 🏗️ Arquitectura y Patrones de Diseño

### 🎨 **Patrones Implementados**

#### 1️⃣ **Page Object Model (POM)**
```python
# ❌ Enfoque Tradicional (No escalable)
def test_login():
    driver.find_element(By.ID, "email").send_keys("user@example.com")
    driver.find_element(By.ID, "password").send_keys("pass123")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

# ✅ Enfoque POM (Escalable, mantenible)
def test_login():
    login_page = LoginPage(driver)
    login_page.set_email("user@example.com")
    login_page.set_password("pass123")
    my_account_page = login_page.click_login_button()
    assert my_account_page.get_title() == "My Account"
```

**Beneficios:**
- 🔄 **Reutilización:** Métodos compartidos entre tests
- 🛠️ **Mantenibilidad:** Cambios de UI en un solo lugar
- 📖 **Legibilidad:** Tests expresan intención de negocio
- 🧪 **Testabilidad:** Lógica de página aislada

#### 2️⃣ **Factory Pattern (BrowserFactory)**
```python
# Creación centralizada de drivers con configuraciones productivas
driver = BrowserFactory.create_driver('chrome', headless=True)
# ✅ Incluye: no-sandbox, disable-dev-shm, window-size, y 15+ optimizaciones
```

**Ventajas:**
- 🎯 Configuraciones CI/CD-ready (Docker, GitHub Actions)
- 🚫 Evita crashes en ambientes con memoria limitada
- 📏 Viewports consistentes para screenshots
- 🔇 Logs limpios (suprime ruido de ChromeDriver)

#### 3️⃣ **Dependency Injection (via Pytest Fixtures)**
```python
@pytest.fixture
def initialize_driver(config, base_url, browser_name):
    driver = BrowserFactory.create_driver(browser_name, headless)
    driver.get(base_url)
    yield driver
    driver.quit()

# Test recibe dependencias automáticamente
@pytest.mark.usefixtures("initialize_driver")
class TestLogin:
    def test_valid_credentials(self):
        # self.driver está disponible automáticamente
        login_page = LoginPage(self.driver)
```

**Beneficios:**
- 🧹 Cleanup automático (yield + quit)
- 🔄 Configuración reutilizable
- 🎛️ Control granular de scope (function, class, session)

### 📐 **Flujo de Ejecución**

```
1. pytest CLI
   ├── --env=staging --browser=chrome --headless
   │
2. conftest.py (pytest_addoption)
   ├── Lee flags de CLI
   │
3. EnvironmentManager.get_config()
   ├── Carga config/environments/staging.py
   ├── Lee variables .env (STAGING_BASE_URL, etc.)
   ├── Retorna EnvironmentConfig (inmutable)
   │
4. BrowserFactory.create_driver()
   ├── Aplica 20+ opciones productivas
   ├── Configura headless, no-sandbox, window-size
   │
5. initialize_driver fixture
   ├── Aplica timeouts (implicit_wait, page_load)
   ├── Navega a base_url
   ├── Inyecta driver al test
   │
6. Test ejecuta
   ├── Usa Page Objects
   ├── Explicit waits (wait_until_clickable, etc.)
   │
7. Teardown automático
   ├── driver.quit()
   ├── Reportes generados
```

---

## 🔥 CI/CD Pipeline

### 🎯 **Arquitectura del Pipeline**

Nuestro CI/CD implementa un **flujo multi-etapa** optimizado para velocidad y confiabilidad:

```
┌─────────────────────────────────────────────────────────┐
│  STAGE 1: SMOKE TESTS (Fast Feedback - 30s)            │
│  ────────────────────────────────────────────────       │
│  ├── Trigger: push/PR a main/develop                    │
│  ├── Browser: Chrome only                               │
│  ├── Tests: pytest -m smoke (tests críticos)            │
│  └── ✅ Pass → Continúa | ❌ Fail → Stop pipeline       │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│  STAGE 2: FULL TEST SUITE (Comprehensive - 2-3min)     │
│  ────────────────────────────────────────────────       │
│  ├── Depends on: smoke-tests                            │
│  ├── Browser: Chrome (matrix ready para multi-browser)  │
│  ├── Tests: pytest tests/ (suite completo)              │
│  ├── Reports: HTML artifacts (30 días retention)        │
│  └── Summary: GitHub Step Summary con métricas          │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│  STAGE 3: MANUAL TESTING (On-Demand)                    │
│  ────────────────────────────────────────────────       │
│  ├── Trigger: Manual (workflow_dispatch)                │
│  ├── Options:                                            │
│  │   • Browser: chrome|firefox|all                      │
│  │   • Environment: dev|staging|prod                    │
│  │   • Test type: smoke|regression|all                  │
│  └── Use case: Pre-release validation                   │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│  STAGE 4: NOTIFICATIONS (Always Run)                    │
│  ────────────────────────────────────────────────       │
│  ├── Status: Runs even if previous stages fail          │
│  ├── Output: GitHub Summary                             │
│  └── Future: Slack/Email notifications                  │
└─────────────────────────────────────────────────────────┘
```

### 🔐 **Secrets Management**

El framework usa **GitHub Secrets** para manejar credenciales de forma segura:

**¿Por qué Secrets?**
- 🔒 **Seguridad:** Credenciales encriptadas, nunca en código
- 🚫 **Sin historial:** No quedan en git history
- 🎭 **Enmascaradas:** Aparecen como `***` en logs
- 🔄 **Rotación fácil:** Cambiar sin tocar código

**Configuración (GitHub → Settings → Secrets):**
```bash
# Secrets requeridos
DEV_BASE_URL=https://ecommerce-playground.lambdatest.io/...
DEV_TEST_EMAIL=pytesttutorial@gmail.com
DEV_TEST_PASSWORD=Jahlove1912$

# Opcionales (staging/prod)
STAGING_BASE_URL=...
STAGING_TEST_EMAIL=...
STAGING_TEST_PASSWORD=...
```

**Uso en Workflow:**
```yaml
- name: 🔧 Create .env file
  run: |
    echo "TEST_ENV=dev" > .env
    echo "DEV_BASE_URL=${{ secrets.DEV_BASE_URL }}" >> .env
    echo "TEST_EMAIL=${{ secrets.DEV_TEST_EMAIL }}" >> .env
    # ✅ Secrets inyectados en runtime, nunca expuestos
```

### 📊 **Features del CI/CD**

| Feature | Descripción | Beneficio |
|---------|-------------|-----------|
| **Multi-stage** | Smoke → Full → Manual | ⚡ Fast feedback (30s vs 3min) |
| **Smart caching** | Cache de pip dependencies | 🚀 Build 2x más rápido |
| **Artifacts** | HTML reports (30 días) | 📊 Debugging histórico |
| **GitHub Summaries** | Métricas en cada run | 📈 Visibilidad instantánea |
| **Fail-fast** | Para pipeline si smoke falla | 💰 Ahorra runners minutes |
| **Matrix ready** | Multi-browser/OS (commented) | 🌐 Cross-browser cuando necesites |

### 🎮 **Ejecutar Manualmente**

1. Ve a [GitHub Actions](https://github.com/daniellarry12/python-selenium-model-framework/actions)
2. Click en **"Automated Tests CI/CD"**
3. Click en **"Run workflow"** (botón derecho)
4. Selecciona opciones:
   - **Browser:** chrome | firefox | all
   - **Environment:** dev | staging | prod
   - **Test type:** smoke | regression | all
5. Click **"Run workflow"** ✅

---

## 🧪 Ejecución de Tests

### 📋 **Comandos Esenciales**

```bash
# 🚀 Quick Runs
pytest -m smoke                              # Solo tests críticos (30s)
pytest -m regression                         # Suite completo (2-3min)
pytest tests/test_login.py -v               # Test específico

# 🌐 Multi-Browser
pytest --browser=chrome                      # Chrome (default)
pytest --browser=firefox                     # Firefox
pytest --browser=all                         # Todos los browsers (paralelo)

# 🎯 Multi-Environment
pytest --env=dev                             # Local development
pytest --env=staging --headless              # Pre-producción
pytest --env=prod --headless -m smoke        # Producción (solo smoke)

# 📊 Reportes
pytest --html=reports/report.html --self-contained-html
pytest --alluredir=allure-results            # Allure (si instalado)

# 🚀 Parallel Execution (requiere pytest-xdist)
pytest -n 4                                  # 4 workers paralelos
pytest -n auto                               # Auto-detect CPUs

# 🔍 Debug Mode
pytest -v --tb=short                         # Traceback corto
pytest -vv --tb=long                         # Traceback completo
pytest --pdb                                 # Debugger interactivo
```

### 🏷️ **Markers (Categorías de Tests)**

```python
# Definir markers
@pytest.mark.smoke          # Tests críticos (login, checkout)
@pytest.mark.regression     # Suite completo
@pytest.mark.slow          # Tests lentos (>30s)
@pytest.mark.skip          # Temporalmente deshabilitado

# Ejecutar por marker
pytest -m smoke                              # Solo smoke
pytest -m "smoke or regression"              # Múltiples markers
pytest -m "not slow"                         # Excluir tests lentos
```

### 🎨 **Parametrización (Data-Driven Tests)**

```python
# Ejemplo de test parametrizado
@pytest.mark.parametrize("email,password,expected_error", [
    ("", "", "Warning"),                     # Campos vacíos
    ("invalid", "pass", "Warning"),          # Email inválido
    ("user@test.com", "wrong", "Warning"),   # Password incorrecto
])
def test_login_validations(email, password, expected_error):
    login_page.login(email, password)
    assert login_page.get_error() == expected_error

# Ejecutar: pytest -v (genera 3 tests)
# test_login_validations[--Warning]
# test_login_validations[invalid-pass-Warning]
# test_login_validations[user@test.com-wrong-Warning]
```

---

## 🌍 Ambientes Multi-Environment

### 🎛️ **Configuración por Ambiente**

| Característica | Dev | Staging | Prod |
|----------------|-----|---------|------|
| **Implicit Wait** | 10s | 15s | 20s |
| **Page Load Timeout** | 30s | 60s | 90s |
| **Log Level** | DEBUG | INFO | WARNING |
| **Headless Default** | ❌ No | ✅ Sí | ✅ Sí |
| **Uso Típico** | Local development | Pre-release testing | Smoke monitoring |
| **Velocidad** | ⚡ Rápido | 🚀 Medio | 🐢 Lento (safe) |

### 📝 **Archivo `.env` (Local)**

```bash
# ============================================
# DEVELOPMENT (Local Testing)
# ============================================
TEST_ENV=dev
DEV_BASE_URL=https://ecommerce-playground.lambdatest.io/index.php?route=account/login
DEV_TEST_EMAIL=pytesttutorial@gmail.com
DEV_TEST_PASSWORD=Jahlove1912$

# ============================================
# STAGING (Pre-Production)
# ============================================
STAGING_BASE_URL=https://staging.example.com
STAGING_TEST_EMAIL=staging@example.com
STAGING_TEST_PASSWORD=StagingPass123!

# ============================================
# PRODUCTION (Read-Only Monitoring)
# ============================================
PROD_BASE_URL=https://prod.example.com
PROD_TEST_EMAIL=monitor@example.com
PROD_TEST_PASSWORD=ProdPass123!
```

### 🔄 **Cambiar de Ambiente**

```bash
# Opción 1: Flag CLI (recomendado)
pytest --env=staging --browser=chrome --headless

# Opción 2: Variable de ambiente
export TEST_ENV=staging
pytest

# Opción 3: Editar .env
nano .env  # Cambiar TEST_ENV=staging
pytest
```

### 🎯 **Mejores Prácticas por Ambiente**

#### **Development (dev)**
```bash
# ✅ Browser visible para debugging
pytest --env=dev --browser=chrome

# ✅ Verbose output para ver qué pasa
pytest --env=dev -vv --tb=long

# ✅ Test específico en loop
pytest tests/test_login.py --env=dev --count=5
```

#### **Staging (staging)**
```bash
# ✅ Headless para velocidad
pytest --env=staging --headless

# ✅ Multi-browser antes de release
pytest --env=staging --browser=all --headless

# ✅ Reporte HTML para compartir
pytest --env=staging --html=staging-report.html
```

#### **Production (prod)**
```bash
# ✅ SOLO smoke tests (no destructivos)
pytest --env=prod --headless -m smoke

# ❌ NUNCA tests que modifiquen datos
# ❌ NUNCA sin --headless (sobrecarga)
```

---

## ✨ Mejores Prácticas Implementadas

### 1️⃣ **No Hard-Coded Sleeps**
```python
# ❌ MAL: Espera fija (lento, frágil)
driver.find_element(By.ID, "button").click()
time.sleep(3)  # ¿Por qué 3s? ¿Y si carga en 1s? ¿O 5s?

# ✅ BIEN: Explicit Wait (rápido, confiable)
element = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "button"))
)
element.click()

# ✅ MEJOR: Método reutilizable (BasePage)
self.wait_until_clickable(*self.login_button).click()
```

### 2️⃣ **Explicit Waits sobre Implicit Waits**
```python
# ⚠️ Implicit Wait (global, no granular)
driver.implicitly_wait(10)  # Aplica a TODOS los find_element

# ✅ Explicit Waits (solo cuando necesitas)
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "result"))
)

# ✅ Nuestro BasePage tiene 10+ explicit waits:
# wait_until_visible, wait_until_clickable, wait_until_invisible,
# wait_for_url_contains, wait_for_title_contains, etc.
```

### 3️⃣ **Assertions Descriptivas**
```python
# ❌ MAL: Assertion críptica
assert driver.title == "My Account"

# ✅ BIEN: Mensaje de error útil
actual_title = driver.title
expected_title = "My Account"
assert actual_title == expected_title, (
    f"Expected title '{expected_title}' but got '{actual_title}'. "
    f"Current URL: {driver.current_url}"
)
```

### 4️⃣ **Locators Robustos**
```python
# Jerarquía de robustez (mejor a peor)
(By.ID, "username")                    # ✅ Mejor: Único, rápido
(By.NAME, "email")                     # ✅ Bueno: Semántico
(By.CSS_SELECTOR, "[data-testid='login']")  # ✅ Bueno: Atributo test
(By.XPATH, "//input[@placeholder='Email']") # ⚠️ OK: Puede cambiar
(By.XPATH, "/html/body/div[2]/form/input[1]")  # ❌ Frágil: Rompe fácil
```

### 5️⃣ **Test Independence (No State Compartido)**
```python
# ✅ Cada test limpia su propio estado
@pytest.fixture(autouse=True)
def setup_teardown(self):
    # Setup
    self.driver.delete_all_cookies()
    yield
    # Teardown
    self.driver.delete_all_cookies()

# ✅ Tests pueden correr en cualquier orden
pytest --random-order  # Detecta dependencias ocultas
```

### 6️⃣ **Production-Ready Driver Config**
```python
# ✅ BrowserFactory incluye 20+ opciones críticas:
options.add_argument("--no-sandbox")           # Docker/CI
options.add_argument("--disable-dev-shm-usage") # Evita crashes
options.add_argument("--window-size=1920,1080") # Screenshots consistentes
options.add_argument("--headless=new")          # Headless moderno
options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Logs limpios
```

---

## 📁 Estructura del Proyecto

```
Pytest_Framework/
│
├── 📄 .env                          # ⚠️ Variables locales (GIT IGNORE)
├── 📄 .env.example                  # ✅ Template de configuración
├── 📄 .gitignore                    # Excluye .env, __pycache__, etc.
├── 📄 conftest.py                   # 🔧 Config global de pytest
├── 📄 pytest.ini                    # ⚙️ Settings de pytest
├── 📄 requirements.txt              # 📦 Dependencias
├── 📄 README.md                     # 📖 Esta documentación
│
├── 📂 .github/workflows/
│   └── tests.yml                    # 🚀 CI/CD Pipeline completo
│
├── 📂 config/                       # 🎛️ Gestión de ambientes
│   ├── __init__.py
│   ├── environment_manager.py       # Carga configs por ambiente
│   └── environments/
│       ├── dev.py                   # Timeouts dev
│       ├── staging.py               # Timeouts staging
│       └── prod.py                  # Timeouts prod
│
├── 📂 pages/                        # 📄 Page Object Models
│   ├── base_page.py                 # 🏗️ Métodos compartidos (54 métodos)
│   │   ├── find(), wait_until_visible()
│   │   ├── click(), type(), select()
│   │   ├── wait_for_url_contains()
│   │   └── is_displayed(), get_text()
│   │
│   ├── login_page.py                # 🔐 LoginPage POM
│   ├── my_account_page.py           # 👤 MyAccountPage POM
│   ├── change_password_page.py      # 🔑 ChangePasswordPage POM
│   └── components/
│       └── right_menu_component.py  # 🧩 Componente reutilizable
│
├── 📂 tests/                        # 🧪 Test Suites
│   ├── base_test.py                 # Base class para tests
│   ├── test_login.py                # Tests de login
│   │   ├── test_valid_credentials (smoke)
│   │   ├── test_invalid_credentials
│   │   └── test_login_validation_scenarios (parametrizado)
│   │
│   └── test_change_password.py      # Tests de cambio de password
│
├── 📂 utilities/                    # 🛠️ Utilidades
│   └── test_data.py                 # Datos de prueba (lee de .env)
│
├── 📂 FirstPartTutorial/            # 📚 Material educativo legacy
│   └── DemoPytest/                  # (Excluido del CI/CD)
│
└── 📂 reports/                      # 📊 Reportes generados
    └── report.html                  # HTML report (pytest-html)
```

### 🔍 **Componentes Clave**

#### **conftest.py** - El Corazón del Framework
```python
# 1. CLI Options
pytest_addoption()  # Define --env, --browser, --headless

# 2. Config Loading
@pytest.fixture(scope="session")
def config(request):
    return get_config(env_name)  # Carga config/environments/{env}.py

# 3. Browser Parametrization
pytest_generate_tests()  # --browser=all → genera tests por browser

# 4. Driver Initialization
@pytest.fixture
def initialize_driver(config, base_url, browser_name):
    driver = BrowserFactory.create_driver(browser_name, headless)
    # Aplica timeouts, navega a base_url
    yield driver
    driver.quit()  # Cleanup garantizado
```

#### **BrowserFactory** - Configuración Productiva
```python
class BrowserFactory:
    @staticmethod
    def create_driver(browser: str, headless: bool) -> WebDriver:
        if browser == "chrome":
            return BrowserFactory._create_chrome(headless)
        # + Firefox, Edge

    @staticmethod
    def _create_chrome(headless: bool):
        options = ChromeOptions()
        # 20+ opciones CI/CD-ready:
        # --no-sandbox, --disable-dev-shm-usage,
        # --window-size, --headless=new, etc.
        return webdriver.Chrome(options=options)
```

#### **BasePage** - 54 Métodos Productivos
```python
class BasePage:
    # Categoría 1: Element Finding (5 métodos)
    find(), find_all(), wait_until_visible(), etc.

    # Categoría 2: Interactions (8 métodos)
    click(), type(), clear_and_type(), select_by_text(), etc.

    # Categoría 3: Waits (12 métodos)
    wait_until_clickable(), wait_for_url_contains(),
    wait_until_invisible(), etc.

    # Categoría 4: Assertions (6 métodos)
    is_displayed(), is_enabled(), get_text(), etc.

    # Categoría 5: Navigation (4 métodos)
    get_current_url(), get_title(), refresh(), etc.

    # Categoría 6: Advanced (10+ métodos)
    scroll_to_element(), take_screenshot(),
    execute_script(), switch_to_frame(), etc.
```

---

## 🤝 Contribuir

### 🔄 **Flujo de Contribución**

```bash
# 1. Fork el repo y clona
git clone https://github.com/TU_USERNAME/python-selenium-model-framework.git

# 2. Crea una rama desde develop
git checkout -b feature/nueva-funcionalidad

# 3. Haz tus cambios
# - Sigue los patrones existentes
# - Agrega docstrings
# - Usa type hints cuando sea posible

# 4. Ejecuta tests localmente
pytest --env=dev -v
pytest -m smoke  # Al menos smoke debe pasar

# 5. Commit con mensaje descriptivo
git commit -m "feat: Add login with social media"
# Prefijos: feat|fix|docs|style|refactor|test|chore

# 6. Push y crea Pull Request
git push origin feature/nueva-funcionalidad
# PR hacia develop (NO main directamente)
```

### 📏 **Estándares de Código**

#### **Tests**
```python
# ✅ BIEN: Nombre descriptivo, AAA pattern, assertions claras
@pytest.mark.smoke
def test_valid_login_redirects_to_my_account(self):
    """Test that valid credentials redirect to My Account page."""
    # Arrange
    login_page = LoginPage(self.driver)

    # Act
    login_page.login(TestData.email, TestData.password)

    # Assert
    assert self.driver.title == "My Account"
    assert "account/account" in self.driver.current_url
```

#### **Page Objects**
```python
# ✅ BIEN: Locators como constantes, métodos descriptivos
class LoginPage(BasePage):
    # Locators (constantes de clase)
    EMAIL_FIELD = (By.ID, "input-email")
    PASSWORD_FIELD = (By.ID, "input-password")
    LOGIN_BUTTON = (By.XPATH, "//input[@value='Login']")

    def set_email(self, email: str) -> None:
        """Enter email address in login form."""
        self.type(self.EMAIL_FIELD, email)

    def click_login_button(self) -> 'MyAccountPage':
        """Click login button and return My Account page."""
        self.click(self.LOGIN_BUTTON)
        return MyAccountPage(self.driver)
```

### 🎯 **Checklist antes de PR**

- [ ] Tests pasan localmente (`pytest -v`)
- [ ] Smoke tests pasan (`pytest -m smoke`)
- [ ] Código tiene docstrings
- [ ] Sin `time.sleep()` en código nuevo
- [ ] Page Objects para nueva UI
- [ ] `.env` no está en commit
- [ ] Sin credenciales hardcodeadas

---

## 📚 Recursos Adicionales

### 🔗 **Documentación Oficial**
- [Selenium Docs](https://www.selenium.dev/documentation/)
- [Pytest Docs](https://docs.pytest.org/en/stable/)
- [GitHub Actions](https://docs.github.com/en/actions)

### 📖 **Patrones y Mejores Prácticas**
- [Page Object Model (Martin Fowler)](https://martinfowler.com/bliki/PageObject.html)
- [Selenium Best Practices](https://www.selenium.dev/documentation/test_practices/)
- [Pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)

### 🎓 **Learning Path Recomendado**

1. **Básicos** (1-2 semanas)
   - Python fundamentals
   - Selenium WebDriver basics
   - Pytest introducción

2. **Intermedio** (2-3 semanas)
   - Page Object Model
   - Explicit Waits
   - Pytest fixtures y markers

3. **Avanzado** (3-4 semanas)
   - Factory Pattern
   - Multi-environment configs
   - CI/CD con GitHub Actions
   - Parallel execution

4. **Experto** (Continuo)
   - Visual regression testing
   - API test integration
   - Performance testing
   - Accessibility testing

---

## 🐛 Troubleshooting

### ❓ **Errores Comunes**

#### 1. `ModuleNotFoundError: No module named 'selenium'`
```bash
# Solución: Instalar dependencias
pip install -r requirements.txt
```

#### 2. `WebDriverException: Message: 'chromedriver' executable needs to be in PATH`
```bash
# Solución: El framework usa selenium 4.x con driver manager automático
# Si falla, instala manualmente:
# macOS
brew install chromedriver

# Ubuntu
sudo apt-get install chromium-chromedriver

# Windows
# Descarga de https://chromedriver.chromium.org/
```

#### 3. `ValueError: DEV_BASE_URL not found in .env file`
```bash
# Solución: Verifica que .env existe y tiene las variables
cp .env.example .env  # Si no existe
nano .env  # Verifica que DEV_BASE_URL está definido
```

#### 4. Tests fallan en CI/CD pero pasan localmente
```bash
# Causas comunes:
# 1. Secrets no configurados en GitHub
#    → Settings → Secrets → Agregar DEV_BASE_URL, etc.
#
# 2. Timing issues (CI es más lento)
#    → Aumenta timeouts en config/environments/
#
# 3. Headless mode diferencias
#    → Prueba localmente con --headless
```

#### 5. `SessionNotCreatedException: session not created: This version of ChromeDriver only supports Chrome version 120`
```bash
# Solución: Actualizar Chrome o ChromeDriver
# Selenium 4.x maneja versiones automáticamente, pero si falla:
pip install --upgrade selenium
```

### 🔍 **Debug Tips**

```bash
# 1. Ver logs detallados
pytest -vv --tb=long

# 2. Pausar en error (debugger)
pytest --pdb

# 3. Ejecutar sin headless (ver qué pasa)
pytest --env=dev  # dev es headed por defecto

# 4. Screenshot en failure (agregar a conftest.py)
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    if outcome.get_result().failed:
        driver.save_screenshot(f"failure_{item.name}.png")
```

---

## 📊 Estado del Proyecto

### ✅ **Implementado**
- [x] Page Object Model con 54 métodos en BasePage
- [x] Multi-environment (dev/staging/prod)
- [x] Multi-browser (Chrome/Firefox/Edge)
- [x] CI/CD Pipeline multi-etapa
- [x] GitHub Secrets integration
- [x] HTML Reports con pytest-html
- [x] Smoke y Regression markers
- [x] Parametrized tests
- [x] Factory Pattern para drivers
- [x] Explicit Waits (cero time.sleep)

### 🚧 **En Progreso**
- [ ] Allure Reports integration
- [ ] Visual Regression Testing
- [ ] API Testing integration
- [ ] Performance metrics

### 🔮 **Roadmap Futuro**
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] Cross-browser cloud (BrowserStack/Sauce Labs)
- [ ] AI-powered self-healing locators
- [ ] Accessibility testing (axe-core)

---

## 📝 Licencia

Este proyecto es de código abierto y está disponible bajo la [MIT License](LICENSE).

---

## 👥 Autores

- **Daniel Aguilar** - *Framework Architecture & CI/CD* - [@daniellarry12](https://github.com/daniellarry12)
- **Claude (Anthropic)** - *AI Pair Programming Assistant*

---

## 🙏 Agradecimientos

- Comunidad de Selenium por las mejores prácticas
- Equipo de Pytest por un framework excelente
- LambdaTest por el sitio de prueba (ecommerce-playground)
- Todos los contribuidores del proyecto

---

## 📞 Contacto y Soporte

- 🐛 **Issues:** [GitHub Issues](https://github.com/daniellarry12/python-selenium-model-framework/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/daniellarry12/python-selenium-model-framework/discussions)
- 📧 **Email:** [Crear issue para contacto]

---

<div align="center">

**⭐ Si este proyecto te ayudó, dale una estrella en GitHub ⭐**

**🚀 Happy Testing! 🚀**

</div>