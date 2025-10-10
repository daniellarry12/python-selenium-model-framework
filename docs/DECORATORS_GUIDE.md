# 📚 GUÍA COMPLETA DE DECORATORS EN EL FRAMEWORK

Esta guía explica **TODOS** los decorators utilizados en el framework de testing, con conceptos de OOP y ejemplos prácticos del código.

---

## 📖 ÍNDICE

1. [Decorators de Python Estándar (OOP)](#1-decorators-de-python-estándar-oop)
   - [@property](#11-property---encapsulamiento-oop)
   - [@staticmethod](#12-staticmethod---métodos-de-utilidad-sin-estado)
   - [@classmethod](#13-classmethod---métodos-que-acceden-a-la-clase)
2. [Decorators de Pytest](#2-decorators-de-pytest)
   - [@pytest.fixture](#21-pytestfixture---inyección-de-dependencias)
   - [@pytest.mark.usefixtures](#22-pytestmarkusefixtures---aplicar-fixtures-sin-recibirlos)
   - [@pytest.mark.<nombre>](#23-pytestmarknombre---tags-para-organizar-tests)
   - [@pytest.mark.parametrize](#24-pytestmarkparametrize---tests-data-driven)
3. [Decorators de Python Avanzados](#3-decorators-de-python-avanzados)
   - [@dataclass](#31-dataclass---generación-automática-de-métodos)
   - [@lru_cache](#32-lru_cache---memoización-caché)
4. [Conceptos Fundamentales](#4-conceptos-fundamentales)
5. [Resumen de Decorators en el Framework](#5-resumen-de-decorators-en-el-framework)

---

## 🎯 1. DECORATORS DE PYTHON ESTÁNDAR (OOP)

### 1.1 `@property` - Encapsulamiento (OOP)

**Concepto OOP**: **Encapsulamiento** - Controla el acceso a atributos privados mediante métodos públicos.

**Qué hace**: Convierte un método en un atributo de solo lectura (getter).

**Ejemplo en el framework** (`drivers/driver_manager.py:168`):

```python
class DriverManager:
    def __init__(self):
        self._driver = None  # Atributo privado (convención: _ prefix)

    @property
    def driver(self) -> WebDriver:
        """
        Convierte self._driver en una propiedad de solo lectura.
        Permite acceder al driver como atributo en vez de método.
        """
        if self._driver is None:
            raise RuntimeError("Driver not started. Call start() first.")
        return self._driver

# USO:
manager = DriverManager()
manager.start()

# ✅ Acceso como atributo (gracias a @property)
driver = manager.driver

# ❌ Sin @property, tendrías que hacer:
# driver = manager.driver()  # Llamada a método
```

**Ventajas**:
- ✅ **Encapsulación**: Ocultas `_driver` (privado) y expones `driver` (público)
- ✅ **Validación**: Puedes validar antes de devolver el valor
- ✅ **Sintaxis limpia**: `manager.driver` en vez de `manager.get_driver()`
- ✅ **Protección**: No pueden modificar directamente `_driver` desde fuera

**Conceptos OOP relacionados**:
- **Encapsulamiento**: Ocultar detalles internos
- **Information Hiding**: Exponer solo lo necesario
- **Getter/Setter**: Métodos para acceder/modificar atributos

---

### 1.2 `@staticmethod` - Métodos de utilidad sin estado

**Concepto OOP**: **Métodos estáticos** - No dependen del estado de la instancia ni de la clase.

**Qué hace**: Define un método que NO accede a `self` ni a `cls`.

**Ejemplo en el framework** (`drivers/browser_factory.py:71`):

```python
class BrowserFactory:
    """Factory para crear WebDriver instances"""

    @staticmethod
    def create(browser: str, headless: bool = False) -> WebDriver:
        """
        Crea un driver sin necesitar instancia de BrowserFactory.
        No usa 'self' porque no depende del estado de la clase.
        """
        if browser == "chrome":
            return BrowserFactory._create_chrome(headless)
        elif browser == "firefox":
            return BrowserFactory._create_firefox(headless)
        elif browser == "edge":
            return BrowserFactory._create_edge(headless)

    @staticmethod
    def _create_chrome(headless: bool) -> WebDriver:
        """Método privado estático (convención: _ prefix)"""
        options = ChromeOptionsBuilder.build(headless=headless)
        return webdriver.Chrome(options=options)

# USO - NO necesitas crear instancia:
driver = BrowserFactory.create("chrome", headless=True)

# ❌ Sin @staticmethod, tendrías que hacer:
# factory = BrowserFactory()  # Crear instancia innecesaria
# driver = factory.create("chrome", headless=True)
```

**Ventajas**:
- ✅ **Factory Pattern**: Métodos de creación que no dependen del estado
- ✅ **Organización**: Agrupa utilidades relacionadas en una clase
- ✅ **No requiere instancia**: `BrowserFactory.create()` directamente
- ✅ **Claridad**: Indica que el método no usa estado interno

**Conceptos OOP relacionados**:
- **Factory Pattern**: Creación de objetos sin exponer lógica
- **Utility Methods**: Funciones helper agrupadas por responsabilidad
- **Stateless**: No depende de estado mutable

**Otros ejemplos en el framework**:
```python
# drivers/browser_options/chrome_options.py:20
@staticmethod
def build(headless: bool = False) -> ChromeOptions:
    """Build Chrome options without needing instance"""
    options = ChromeOptions()
    # ... configuración
    return options

# drivers/browser_options/firefox_options.py:34
@staticmethod
def build(headless: bool = False) -> FirefoxOptions:
    """Build Firefox options without needing instance"""
    options = FirefoxOptions()
    # ... configuración
    return options
```

---

### 1.3 `@classmethod` - Métodos que acceden a la clase

**Concepto OOP**: **Métodos de clase** - Reciben la clase (`cls`) en vez de la instancia (`self`).

**Qué hace**: Permite acceder a atributos de clase y crear instancias alternativas.

**Ejemplo en el framework** (`drivers/browser_factory.py:46`):

```python
class Browser(Enum):
    """Enum de browsers soportados"""
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"

    @classmethod
    def values(cls) -> list:
        """
        Accede a TODOS los valores del Enum.

        Args:
            cls: Browser (la clase, no una instancia)

        Returns:
            Lista de valores: ['chrome', 'firefox', 'edge']
        """
        return [browser.value for browser in cls]

# USO:
browsers = Browser.values()  # ['chrome', 'firefox', 'edge']

# cls = Browser (la clase)
# browser in cls = browser in Browser
```

**Diferencia con @staticmethod**:
```python
class Example:
    class_var = "I'm a class variable"

    @staticmethod
    def static_method():
        # ❌ No puede acceder a class_var
        # print(class_var)  # Error!
        pass

    @classmethod
    def class_method(cls):
        # ✅ Puede acceder a class_var
        print(cls.class_var)  # Funciona!
```

**Ventajas**:
- ✅ **Constructores alternativos**: `cls()` para crear instancias
- ✅ **Acceso a atributos de clase**: `cls.SUPPORTED_BROWSERS`
- ✅ **Factory methods**: Crear objetos de formas diferentes
- ✅ **Herencia**: Funciona correctamente con subclases

**Ejemplo de constructor alternativo**:
```python
class EnvironmentConfig:
    def __init__(self, base_url: str, timeout: int):
        self.base_url = base_url
        self.timeout = timeout

    @classmethod
    def from_env(cls, env_name: str):
        """Constructor alternativo desde nombre de entorno"""
        if env_name == "dev":
            return cls("https://dev.example.com", timeout=10)
        elif env_name == "prod":
            return cls("https://prod.example.com", timeout=30)

# USO:
config = EnvironmentConfig.from_env("dev")
```

---

## 🧪 2. DECORATORS DE PYTEST

### 2.1 `@pytest.fixture` - Inyección de dependencias

**Concepto OOP**: **Dependency Injection** - Provee objetos configurados a los tests.

**Qué hace**: Define funciones que proveen datos/objetos a los tests automáticamente.

**Ejemplo en el framework** (`conftest.py:61, 77, 120`):

```python
@pytest.fixture(scope="session")
def config(request) -> EnvironmentConfig:
    """
    Fixture de configuración - Se ejecuta 1 vez por sesión.

    Pytest inyecta automáticamente 'request' (objeto especial de pytest).
    Retorna la configuración que luego se inyecta a los tests.
    """
    env_name = request.config.getoption("--env")
    return get_config(env_name)


@pytest.fixture(scope="session")
def base_url(config: EnvironmentConfig) -> str:
    """
    Fixture que DEPENDE de otro fixture (config).
    Pytest resuelve la cadena de dependencias automáticamente.
    """
    return config.base_url


@pytest.fixture
def initialize_driver(request, config, base_url, browser_name):
    """
    Fixture de driver - Se ejecuta 1 vez por test (scope por defecto).

    Usa 'yield' para separar setup/teardown:
    - Antes de yield: Setup (crear driver)
    - Después de yield: Teardown (cerrar driver)
    """
    manager = DriverManager(browser=browser_name, config=config)
    driver = manager.start()

    # Inyecta driver a la clase de test
    request.cls.driver = driver

    yield driver  # ← El test se ejecuta aquí

    # Teardown (siempre se ejecuta, incluso si el test falla)
    manager.stop()


# USO en tests:
def test_login(config, base_url):
    """
    Pytest inyecta automáticamente config y base_url.
    No necesitas crear estos objetos manualmente.
    """
    assert config.environment == "dev"
    assert "https://" in base_url
```

**Scopes disponibles**:

| Scope | Cuándo se ejecuta | Ejemplo |
|-------|-------------------|---------|
| `function` (default) | 1 vez por test | Driver, página temporal |
| `class` | 1 vez por clase de test | Setup compartido en clase |
| `module` | 1 vez por archivo | Base de datos temporal |
| `session` | 1 vez para toda la sesión | Config, API tokens |

**Ventajas**:
- ✅ **Dependency Injection**: Pytest maneja las dependencias
- ✅ **Reutilización**: Mismo fixture en múltiples tests
- ✅ **Cleanup automático**: `yield` garantiza teardown
- ✅ **Scopes optimizados**: Evita crear objetos innecesariamente

**Fixture con parámetros**:
```python
@pytest.fixture(params=["chrome", "firefox"])
def browser(request):
    """
    Ejecuta el test 2 veces (una por cada parámetro).
    request.param contiene el valor actual.
    """
    return BrowserFactory.create(request.param)

def test_homepage(browser):
    """Se ejecuta 2 veces: test_homepage[chrome], test_homepage[firefox]"""
    browser.get("https://example.com")
```

---

### 2.2 `@pytest.mark.usefixtures` - Aplicar fixtures sin recibirlos

**Concepto**: Aplica un fixture a una clase/test sin recibir el valor de retorno.

**Qué hace**: Ejecuta el fixture pero NO lo pasa como argumento al test.

**Ejemplo en el framework** (`tests/base_test.py:5`):

```python
@pytest.mark.usefixtures("initialize_driver")
class BaseTest:
    """
    Aplica initialize_driver a TODOS los tests de esta clase.

    El fixture asigna self.driver automáticamente (via request.cls.driver),
    por lo que no necesitamos recibirlo como parámetro.
    """
    driver: WebDriver = None  # Type hint para IDE


@pytest.mark.smoke
class TestLogin(BaseTest):
    """Hereda @pytest.mark.usefixtures de BaseTest"""

    def test_valid_credentials(self):
        """
        self.driver ya está disponible (gracias a usefixtures).
        No necesitamos: def test_valid_credentials(self, initialize_driver)
        """
        login_page = LoginPage(self.driver)
        login_page.set_email_address("test@example.com")
        # ...

    def test_invalid_credentials(self):
        """También tiene self.driver disponible"""
        login_page = LoginPage(self.driver)
        # ...
```

**Comparación - CON vs SIN usefixtures**:

```python
# ❌ SIN usefixtures - Repetitivo
class TestLogin:
    def test_1(self, initialize_driver):
        login_page = LoginPage(initialize_driver)

    def test_2(self, initialize_driver):
        login_page = LoginPage(initialize_driver)

    def test_3(self, initialize_driver):
        login_page = LoginPage(initialize_driver)


# ✅ CON usefixtures - DRY (Don't Repeat Yourself)
@pytest.mark.usefixtures("initialize_driver")
class TestLogin:
    def test_1(self):
        login_page = LoginPage(self.driver)

    def test_2(self):
        login_page = LoginPage(self.driver)

    def test_3(self):
        login_page = LoginPage(self.driver)
```

**Ventajas**:
- ✅ **DRY**: No repites el fixture en cada test
- ✅ **Herencia**: Los tests heredan el setup
- ✅ **Limpieza**: No contaminas la firma de los tests
- ✅ **Múltiples fixtures**: `@pytest.mark.usefixtures("fix1", "fix2", "fix3")`

**Cuándo usar cada enfoque**:
```python
# Usa @pytest.mark.usefixtures cuando:
# - El fixture hace side effects (asigna self.driver)
# - No necesitas el valor de retorno
# - Quieres aplicarlo a toda una clase

# Usa parámetros cuando:
# - Necesitas el valor de retorno del fixture
# - El fixture es solo para 1-2 tests
def test_example(config):  # ← Recibes el valor
    assert config.environment == "dev"
```

---

### 2.3 `@pytest.mark.<nombre>` - Tags para organizar tests

**Concepto**: Etiqueta tests para ejecutarlos selectivamente.

**Qué hace**: Marca tests con etiquetas personalizadas para filtrar ejecución.

**Ejemplo en el framework** (`tests/test_login.py:26`):

```python
@pytest.mark.smoke  # ← Tag para tests críticos
class TestLogin(BaseTest):
    """
    Marca TODA la clase con el tag 'smoke'.
    Todos los tests dentro heredan este tag.
    """

    def test_valid_credentials(self):
        # Este test tiene tag: smoke
        pass

    def test_invalid_credentials(self):
        # Este test tiene tag: smoke
        pass


@pytest.mark.regression  # ← Tag para suite completo
class TestChangePassword(BaseTest):
    """Marca toda la clase con 'regression'"""

    @pytest.mark.slow  # ← Tag adicional solo para este test
    def test_change_password_flow(self):
        # Este test tiene tags: regression, slow
        pass
```

**USO en terminal**:

```bash
# Ejecutar solo tests smoke (críticos)
pytest -m smoke

# Ejecutar solo tests regression
pytest -m regression

# Ejecutar smoke O regression (OR lógico)
pytest -m "smoke or regression"

# Ejecutar smoke PERO NO slow (AND NOT)
pytest -m "smoke and not slow"

# Ejecutar TODOS excepto slow
pytest -m "not slow"
```

**Marks comunes en testing**:

| Mark | Propósito | Ejemplo |
|------|-----------|---------|
| `@pytest.mark.smoke` | Tests críticos (login, checkout) | Suite de 10 min |
| `@pytest.mark.regression` | Suite completo | Suite de 2 horas |
| `@pytest.mark.slow` | Tests lentos (>30s) | Integración E2E |
| `@pytest.mark.skip` | Temporalmente deshabilitado | Bug conocido |
| `@pytest.mark.xfail` | Se espera que falle | Feature no implementada |

**Configuración de marks personalizados** (`pytest.ini`):

```ini
[pytest]
markers =
    smoke: Critical tests that must pass (login, checkout)
    regression: Full test suite
    slow: Tests that take >30 seconds
    integration: Integration tests requiring external services
    unit: Fast unit tests
```

**Ventajas**:
- ✅ **Ejecución selectiva**: Solo tests necesarios en CI/CD
- ✅ **Organización**: Clasifica tests por tipo/prioridad
- ✅ **Velocidad**: `pytest -m smoke` ejecuta solo lo crítico
- ✅ **Integración CI/CD**: Diferentes pipelines por tag

**Ejemplo de estrategia CI/CD**:
```yaml
# .github/workflows/tests.yml
jobs:
  smoke-tests:
    runs-on: ubuntu-latest
    steps:
      - run: pytest -m smoke  # 5 min - en cada commit

  regression-tests:
    runs-on: ubuntu-latest
    steps:
      - run: pytest -m regression  # 2 horas - solo en PRs
```

---

### 2.4 `@pytest.mark.parametrize` - Tests data-driven

**Concepto**: Ejecuta el mismo test con múltiples conjuntos de datos.

**Qué hace**: Genera múltiples variantes del test, una por cada conjunto de parámetros.

**Ejemplo en el framework** (`tests/test_login.py:106`):

```python
@pytest.mark.parametrize("email,password,expected_error", [
    # Caso 1: Credenciales vacías
    ("", "", "Warning"),

    # Caso 2: Email inválido
    ("invalidemail", "password", "Warning"),

    # Caso 3: Email válido, password incorrecta
    (TestData.email, "wrongpassword", "Warning"),
])
def test_login_validation_scenarios(self, email, password, expected_error):
    """
    Este test se ejecuta 3 veces (una por cada tupla).

    Pytest desempaqueta cada tupla en los parámetros:
    - 1ra ejecución: email="", password="", expected_error="Warning"
    - 2da ejecución: email="invalidemail", password="password", ...
    - 3ra ejecución: email=TestData.email, password="wrongpassword", ...
    """
    # Arrange
    login_page = LoginPage(self.driver)

    # Act
    login_page.log_into_application(email, password)

    # Assert
    assert login_page.is_warning_message_displayed(timeout=5)
    actual_message = login_page.get_warning_message()
    assert expected_error in actual_message


# RESULTADO en pytest:
# test_login_validation_scenarios[--Warning]                       PASSED
# test_login_validation_scenarios[invalidemail-password-Warning]    PASSED
# test_login_validation_scenarios[email-wrongpassword-Warning]      PASSED
```

**Parametrización múltiple** (producto cartesiano):

```python
@pytest.mark.parametrize("base", [1, 2, 3])
@pytest.mark.parametrize("exponent", [4, 5, 6])
def test_power(base, exponent):
    """
    Se ejecuta 9 veces (3 bases × 3 exponentes):
    - test_power[1-4], test_power[1-5], test_power[1-6]
    - test_power[2-4], test_power[2-5], test_power[2-6]
    - test_power[3-4], test_power[3-5], test_power[3-6]
    """
    assert base ** exponent > 0
```

**Parametrización con IDs personalizados**:

```python
@pytest.mark.parametrize("email,password,expected_error", [
    ("", "", "Warning"),
    ("invalidemail", "password", "Warning"),
], ids=["empty_credentials", "invalid_email_format"])
def test_login(email, password, expected_error):
    pass

# RESULTADO:
# test_login[empty_credentials]      PASSED
# test_login[invalid_email_format]   PASSED
```

**Parametrización con objetos complejos**:

```python
@pytest.mark.parametrize("user", [
    {"email": "admin@test.com", "role": "admin"},
    {"email": "user@test.com", "role": "user"},
    {"email": "guest@test.com", "role": "guest"},
])
def test_user_permissions(user):
    """Cada user es un diccionario"""
    login_as(user["email"])
    assert has_role(user["role"])
```

**Ventajas**:
- ✅ **DRY**: No repites lógica para cada caso
- ✅ **Cobertura**: Múltiples escenarios con 1 función
- ✅ **Mantenimiento**: Agregar casos = agregar tuplas
- ✅ **Reporte claro**: Cada caso se reporta individualmente
- ✅ **Paralelización**: `pytest-xdist` ejecuta en paralelo

**Ejemplo real del framework**:
```python
# FirstPartTutorial/DemoPytest/test_parameters_1.py:8
@pytest.mark.parametrize("num1, num2, expected_total", [
    (5, 5, 10),
    (3, 7, 10),
    (2, 8, 10),
])
def test_addition(num1, num2, expected_total):
    assert num1 + num2 == expected_total
```

---

## 🔧 3. DECORATORS DE PYTHON AVANZADOS

### 3.1 `@dataclass` - Generación automática de métodos

**Concepto OOP**: **Value Object** - Clase inmutable para datos.

**Qué hace**: Genera automáticamente `__init__`, `__repr__`, `__eq__`, y más.

**Ejemplo en el framework** (`config/environment_manager.py:21`):

```python
from dataclasses import dataclass

@dataclass(frozen=True)  # frozen=True → inmutable
class EnvironmentConfig:
    """
    @dataclass genera automáticamente:
    - __init__(self, environment, base_url, ...)
    - __repr__(self)  → "EnvironmentConfig(environment='dev', ...)"
    - __eq__(self, other)  → Comparación de atributos
    - __hash__(self)  → Solo si frozen=True
    """
    environment: str
    base_url: str
    test_email: str
    test_password: str
    implicit_wait: int
    page_load_timeout: int


# ========================================
# SIN @dataclass tendrías que escribir:
# ========================================
class EnvironmentConfig:
    def __init__(self, environment, base_url, test_email, test_password,
                 implicit_wait, page_load_timeout):
        self.environment = environment
        self.base_url = base_url
        self.test_email = test_email
        self.test_password = test_password
        self.implicit_wait = implicit_wait
        self.page_load_timeout = page_load_timeout

    def __repr__(self):
        return (
            f"EnvironmentConfig(environment={self.environment!r}, "
            f"base_url={self.base_url!r}, test_email={self.test_email!r}, "
            f"test_password={self.test_password!r}, "
            f"implicit_wait={self.implicit_wait!r}, "
            f"page_load_timeout={self.page_load_timeout!r})"
        )

    def __eq__(self, other):
        if not isinstance(other, EnvironmentConfig):
            return NotImplemented
        return (
            self.environment == other.environment and
            self.base_url == other.base_url and
            # ... comparar todos los atributos
        )

    # ... __hash__, etc.


# ========================================
# CON @dataclass (mucho más simple):
# ========================================
@dataclass(frozen=True)
class EnvironmentConfig:
    environment: str
    base_url: str
    test_email: str
    test_password: str
    implicit_wait: int
    page_load_timeout: int


# USO:
config = EnvironmentConfig(
    environment="dev",
    base_url="https://dev.example.com",
    test_email="test@example.com",
    test_password="pass123",
    implicit_wait=10,
    page_load_timeout=30
)

# __repr__ automático
print(config)
# Output: EnvironmentConfig(environment='dev', base_url='https://dev.example.com', ...)

# __eq__ automático
config2 = EnvironmentConfig(
    environment="dev",
    base_url="https://dev.example.com",
    test_email="test@example.com",
    test_password="pass123",
    implicit_wait=10,
    page_load_timeout=30
)
assert config == config2  # ✅ True (compara todos los atributos)

# frozen=True → inmutable
config.environment = "prod"  # ❌ FrozenInstanceError!
```

**Parámetros importantes de @dataclass**:

| Parámetro | Descripción | Ejemplo |
|-----------|-------------|---------|
| `frozen=True` | Inmutable (no se puede modificar) | `@dataclass(frozen=True)` |
| `order=True` | Genera `__lt__`, `__le__`, `__gt__`, `__ge__` | Para ordenar objetos |
| `eq=True` | Genera `__eq__` (default: True) | Comparación de igualdad |
| `init=True` | Genera `__init__` (default: True) | Constructor automático |
| `repr=True` | Genera `__repr__` (default: True) | Representación string |

**Valores por defecto**:

```python
@dataclass
class User:
    name: str
    age: int = 0  # ← Valor por defecto
    active: bool = True  # ← Valor por defecto

user1 = User("Alice")  # age=0, active=True
user2 = User("Bob", age=30)  # active=True
user3 = User("Charlie", age=25, active=False)
```

**Ventajas**:
- ✅ **Menos boilerplate**: 50+ líneas → 6 líneas
- ✅ **Type hints**: Documentación automática
- ✅ **Inmutabilidad**: `frozen=True` previene modificaciones
- ✅ **Debugging**: `__repr__` útil para logs

**Conceptos OOP relacionados**:
- **Value Object**: Objeto definido por sus valores, no identidad
- **Immutability**: Objetos que no cambian después de crear
- **Data Transfer Object (DTO)**: Objeto para transportar datos

---

### 3.2 `@lru_cache` - Memoización (caché)

**Concepto**: **Memoization** - Guarda resultados de llamadas anteriores para evitar recalcularlos.

**Qué hace**: Cachea el resultado de una función basándose en sus argumentos.

**Ejemplo en el framework** (`config/environment_manager.py:35`):

```python
from functools import lru_cache

@lru_cache(maxsize=3)  # ← Caché para máximo 3 resultados
def get_config(env_name: str | None = None) -> EnvironmentConfig:
    """
    Si llamas get_config('dev') 2 veces:
    - 1ra vez: Carga .env, parsea variables, crea config
    - 2da vez: Retorna el MISMO objeto (del caché) ← MUY RÁPIDO

    El caché usa los argumentos como key:
    - get_config('dev') → key: ('dev',)
    - get_config('staging') → key: ('staging',)
    """
    print(f"🔄 Loading config for {env_name}...")  # Solo imprime la 1ra vez

    # Operaciones costosas (solo se ejecutan la 1ra vez)
    load_dotenv()  # Leer archivo .env
    env_name = (env_name or os.getenv('TEST_ENV', 'dev')).lower()

    # Cargar variables de entorno
    base_url = os.getenv(f"{env_name.upper()}_BASE_URL")
    test_email = os.getenv(f"{env_name.upper()}_TEST_EMAIL")
    # ...

    # Crear y retornar config
    return EnvironmentConfig(
        environment=env_name,
        base_url=base_url,
        # ...
    )


# USO:
config1 = get_config('dev')
# Output: 🔄 Loading config for dev...

config2 = get_config('dev')
# Output: (nada) ← Retorna del caché, no recarga

config3 = get_config('staging')
# Output: 🔄 Loading config for staging...

# Verifica que son el MISMO objeto en memoria
assert config1 is config2  # ✅ True (mismo objeto)
assert config1 is not config3  # ✅ True (diferente objeto)
```

**Cómo funciona internamente**:

```python
# Sin @lru_cache, cada llamada ejecuta toda la función:
def get_config(env_name):
    # Se ejecuta SIEMPRE
    load_dotenv()
    # ...
    return config


# Con @lru_cache, usa un diccionario interno:
_cache = {}

def get_config(env_name):
    # Verifica si está en caché
    if env_name in _cache:
        return _cache[env_name]  # ← Retorna del caché

    # Si no está, ejecuta y guarda
    load_dotenv()
    config = EnvironmentConfig(...)
    _cache[env_name] = config
    return config
```

**Parámetros de @lru_cache**:

| Parámetro | Descripción | Ejemplo |
|-----------|-------------|---------|
| `maxsize=N` | Máximo N resultados en caché | `@lru_cache(maxsize=128)` |
| `maxsize=None` | Caché ilimitado (cuidado!) | `@lru_cache(maxsize=None)` |
| `typed=True` | `f(3)` y `f(3.0)` son keys diferentes | `@lru_cache(typed=True)` |

**Estadísticas del caché**:

```python
@lru_cache(maxsize=3)
def get_config(env_name):
    # ...
    pass

get_config('dev')
get_config('dev')
get_config('staging')

# Ver estadísticas
print(get_config.cache_info())
# CacheInfo(hits=1, misses=2, maxsize=3, currsize=2)
# hits=1: 1 vez retornó del caché (2da llamada a 'dev')
# misses=2: 2 veces no estaba en caché ('dev' y 'staging')
# currsize=2: 2 objetos en caché actualmente

# Limpiar caché manualmente
get_config.cache_clear()
```

**Ventajas**:
- ✅ **Performance**: Evita operaciones costosas repetidas
- ✅ **Consistencia**: Mismo objeto en toda la sesión
- ✅ **Memoria limitada**: `maxsize` evita caché infinito
- ✅ **Thread-safe**: Seguro en entornos multi-hilo

**Cuándo NO usar @lru_cache**:

```python
# ❌ NO usar si la función tiene side effects
@lru_cache
def send_email(to, subject):
    # Problema: Solo envía el email la 1ra vez
    smtp.send(to, subject)

# ❌ NO usar si los argumentos son mutables
@lru_cache
def process_list(items: list):
    # Problema: list no es hashable
    return sum(items)

# ✅ Solución: Convierte a inmutable
@lru_cache
def process_list(items: tuple):  # ← tuple es hashable
    return sum(items)
```

**Conceptos relacionados**:
- **Memoization**: Guardar resultados de funciones puras
- **Pure Functions**: Funciones sin side effects
- **LRU (Least Recently Used)**: Elimina el ítem menos usado cuando se llena

---

## 🎓 4. CONCEPTOS FUNDAMENTALES

### ¿Qué es un decorator?

Un decorator es una **función que modifica el comportamiento de otra función/método/clase**.

**Sintaxis básica**:
```python
@decorator
def funcion():
    pass

# Es equivalente a:
funcion = decorator(funcion)
```

### Anatomía de un decorator simple:

```python
def log_execution(func):
    """Decorator que loggea cuándo se ejecuta una función"""

    def wrapper(*args, **kwargs):
        """Función wrapper que envuelve la original"""
        print(f"🚀 Ejecutando {func.__name__}")

        # Ejecuta la función original
        result = func(*args, **kwargs)

        print(f"✅ {func.__name__} terminó")
        return result

    return wrapper


@log_execution
def suma(a, b):
    return a + b


# USO:
resultado = suma(2, 3)

# Output:
# 🚀 Ejecutando suma
# ✅ suma terminó
# resultado = 5
```

### Decorator con argumentos:

```python
def retry(max_attempts=3):
    """Decorator que reintenta la función si falla"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    print(f"⚠️ Intento {attempt + 1} falló: {e}")
        return wrapper
    return decorator


@retry(max_attempts=5)
def fetch_data(url):
    # Código que puede fallar
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
```

### Decorator de clase:

```python
def singleton(cls):
    """Decorator que convierte una clase en Singleton"""
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class DatabaseConnection:
    def __init__(self, host):
        self.host = host
        print(f"Conectando a {host}...")


# USO:
db1 = DatabaseConnection("localhost")  # Conectando a localhost...
db2 = DatabaseConnection("localhost")  # (no imprime nada)
assert db1 is db2  # ✅ Mismo objeto
```

---

## 📊 5. RESUMEN DE DECORATORS EN EL FRAMEWORK

### Tabla de referencia rápida:

| Decorator | Ubicación | Propósito | Concepto OOP |
|-----------|-----------|-----------|--------------|
| `@property` | `driver_manager.py:168` | Getter de solo lectura | Encapsulamiento |
| `@staticmethod` | `browser_factory.py:71, 117, 161, 198` | Métodos sin estado | Factory Pattern |
| `@classmethod` | `browser_factory.py:46` | Métodos de clase | Métodos de clase |
| `@dataclass` | `environment_manager.py:21` | Generación automática | Value Object |
| `@lru_cache` | `environment_manager.py:35` | Memoización | Caché/Performance |
| `@pytest.fixture` | `conftest.py:61, 77, 120` | Inyección de dependencias | DI Pattern |
| `@pytest.mark.usefixtures` | `base_test.py:5` | Aplicar fixtures sin recibir | Setup/Teardown |
| `@pytest.mark.smoke` | `test_login.py:26` | Tag para tests críticos | Test Organization |
| `@pytest.mark.parametrize` | `test_login.py:106` | Tests data-driven | Test Parametrization |

### Ubicaciones completas en el código:

```python
# PYTHON ESTÁNDAR (OOP)
drivers/driver_manager.py:168          → @property
drivers/browser_factory.py:46          → @classmethod
drivers/browser_factory.py:71          → @staticmethod
drivers/browser_factory.py:117         → @staticmethod
drivers/browser_factory.py:161         → @staticmethod
drivers/browser_factory.py:198         → @staticmethod
drivers/browser_options/chrome_options.py:20   → @staticmethod
drivers/browser_options/firefox_options.py:34  → @staticmethod
drivers/browser_options/edge_options.py:24     → @staticmethod

# PYTHON AVANZADO
config/environment_manager.py:21       → @dataclass(frozen=True)
config/environment_manager.py:35       → @lru_cache(maxsize=3)

# PYTEST
conftest.py:61                         → @pytest.fixture(scope="session")
conftest.py:77                         → @pytest.fixture(scope="session")
conftest.py:120                        → @pytest.fixture
tests/base_test.py:5                   → @pytest.mark.usefixtures("initialize_driver")
tests/test_login.py:26                 → @pytest.mark.smoke
tests/test_login.py:106                → @pytest.mark.parametrize
tests/test_change_password.py:26       → @pytest.mark.regression
```

---

## 🚀 EJERCICIOS PRÁCTICOS

### 1. Crea tu propio decorator de timing:

```python
import time
from functools import wraps

def timing(func):
    """Mide cuánto tarda una función"""
    @wraps(func)  # ← Preserva metadata de func
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"⏱️ {func.__name__} tardó {end - start:.2f}s")
        return result
    return wrapper


@timing
def test_login(self):
    # ... código del test
    pass

# Output: ⏱️ test_login tardó 3.45s
```

### 2. Combina múltiples decorators:

```python
@pytest.mark.smoke
@pytest.mark.parametrize("browser", ["chrome", "firefox"])
@timing
def test_multi_browser(browser):
    driver = BrowserFactory.create(browser)
    # ...
```

### 3. Decorator para retry con exponential backoff:

```python
def retry_with_backoff(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    wait_time = delay * (2 ** attempt)
                    print(f"⚠️ Intento {attempt + 1} falló. Esperando {wait_time}s...")
                    time.sleep(wait_time)
        return wrapper
    return decorator
```

---

## 📚 RECURSOS ADICIONALES

### Documentación oficial:
- [Python Decorators](https://docs.python.org/3/glossary.html#term-decorator)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Pytest Markers](https://docs.pytest.org/en/stable/mark.html)
- [Python dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [functools.lru_cache](https://docs.python.org/3/library/functools.html#functools.lru_cache)

### Patrones de diseño relacionados:
- **Decorator Pattern**: Añadir responsabilidades dinámicamente
- **Factory Pattern**: Creación de objetos (BrowserFactory)
- **Dependency Injection**: Proveer dependencias (pytest fixtures)
- **Value Object**: Objetos inmutables (EnvironmentConfig)
- **Singleton**: Una sola instancia (@singleton decorator)

---

## ✅ CHECKLIST DE APRENDIZAJE

- [ ] Entiendo qué es un decorator y cómo funciona
- [ ] Puedo explicar la diferencia entre `@staticmethod` y `@classmethod`
- [ ] Sé cuándo usar `@property` para encapsulamiento
- [ ] Entiendo cómo `@pytest.fixture` implementa DI
- [ ] Puedo usar `@pytest.mark.parametrize` para tests data-driven
- [ ] Sé cómo organizar tests con `@pytest.mark.<tag>`
- [ ] Entiendo los beneficios de `@dataclass`
- [ ] Comprendo cuándo usar `@lru_cache` para performance
- [ ] Puedo crear mis propios decorators personalizados
- [ ] Sé combinar múltiples decorators correctamente

---

**¡Dominar decorators te hace un mejor desarrollador Python y tester!** 🎉
