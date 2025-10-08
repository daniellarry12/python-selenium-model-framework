# Pytest Framework - Multi-Environment Testing

Framework de pruebas automatizadas con Selenium y Pytest que soporta múltiples ambientes (dev, staging, prod).

## 📋 Instalación Inicial

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar variables de entorno:**
   ```bash
   cp .env.example .env
   # Edita .env con tus credenciales para cada ambiente
   ```

## 🌍 Ambientes Soportados

El framework soporta 3 ambientes:

- **dev** - Desarrollo local (headed por defecto, timeouts cortos)
- **staging** - Pre-producción (headless por defecto, timeouts medios)
- **prod** - Producción (headless, timeouts largos, solo smoke tests)

### Configuración de Ambientes

Cada ambiente requiere estas variables en `.env`:

```bash
# Development
DEV_BASE_URL=https://dev.example.com
DEV_TEST_EMAIL=dev-test@example.com
DEV_TEST_PASSWORD=password123

# Staging
STAGING_BASE_URL=https://staging.example.com
STAGING_TEST_EMAIL=staging-test@example.com
STAGING_TEST_PASSWORD=password123

# Production
PROD_BASE_URL=https://prod.example.com
PROD_TEST_EMAIL=prod-test@example.com
PROD_TEST_PASSWORD=password123
```

## 🚀 Ejecución Local

### Comandos Básicos

```bash
# Usar ambiente por defecto (dev)
pytest

# Especificar ambiente
pytest --env=dev
pytest --env=staging
pytest --env=prod

# Con navegador específico
pytest --env=staging --browser=firefox

# Modo headless
pytest --env=dev --headless

# Todos los navegadores
pytest --env=staging --browser=all
```

### Ejemplos Comunes

```bash
# Desarrollo local (con browser visible)
pytest --env=dev --browser=chrome

# Testing antes de merge (headless, más rápido)
pytest --env=staging --browser=chrome --headless

# Smoke test de producción
pytest --env=prod --headless -m smoke

# Test específico en staging
pytest tests/test_login.py --env=staging --headless -v
```

### Opciones Disponibles

| Opción | Valores | Default | Descripción |
|--------|---------|---------|-------------|
| `--env` | dev, staging, prod | dev (desde .env) | Ambiente a probar |
| `--browser` | chrome, firefox, edge, all | chrome | Navegador a usar |
| `--headless` | flag | False | Ejecutar sin UI |
| `-v` | flag | - | Verbose output |
| `-m` | marker | - | Ejecutar tests con marker específico |

## 🔧 CI/CD con GitHub Actions

### Workflows Disponibles

El proyecto incluye 3 workflows automáticos:

#### 1. Dev Environment Tests (`test-dev.yml`)
- **Trigger:** Push a `develop` o `feature/**`
- **Browsers:** Chrome
- **Modo:** Headless
- **Propósito:** Tests rápidos en desarrollo

#### 2. Staging Environment Tests (`test-staging.yml`)
- **Trigger:** Push/PR a `main`
- **Browsers:** Chrome + Firefox
- **Modo:** Headless
- **Propósito:** Tests completos pre-producción

#### 3. Production Smoke Tests (`test-prod.yml`)
- **Trigger:** Manual o cada 6 horas
- **Browsers:** Chrome
- **Modo:** Headless
- **Propósito:** Monitoreo de producción

### Configurar Secrets en GitHub

Ve a: `Settings` → `Secrets and variables` → `Actions`

Crea estos secrets por ambiente:

```
# Dev
DEV_BASE_URL
DEV_API_URL
DEV_TEST_EMAIL
DEV_TEST_PASSWORD

# Staging
STAGING_BASE_URL
STAGING_API_URL
STAGING_TEST_EMAIL
STAGING_TEST_PASSWORD

# Production
PROD_BASE_URL
PROD_API_URL
PROD_TEST_EMAIL
PROD_TEST_PASSWORD
```

### Ejecutar Workflows Manualmente

1. Ve a la pestaña **Actions**
2. Selecciona el workflow deseado
3. Click en **Run workflow**
4. Selecciona el branch y click **Run**

## 📁 Estructura del Proyecto

```
Pytest_Framework/
├── .env                        # Variables locales (NO commitear)
├── .env.example                # Template de configuración
├── conftest.py                 # Configuración de pytest
├── pytest.ini                  # Configuración de pytest
├── requirements.txt            # Dependencias
├── requirements-lock.txt       # Dependencias locked para CI/CD
├── config/                     # Configuración de ambientes
│   ├── __init__.py
│   ├── environment_manager.py  # Gestor de ambientes
│   └── environments/           # Configs por ambiente
│       ├── dev.py              # Timeouts y settings de dev
│       ├── staging.py          # Timeouts y settings de staging
│       └── prod.py             # Timeouts y settings de prod
├── pages/                      # Page Object Models
│   ├── base_page.py
│   ├── login_page.py
│   └── ...
├── tests/                      # Test suites
│   ├── test_login.py
│   └── ...
├── utilities/                  # Utilidades
│   └── test_data.py
└── .github/
    └── workflows/              # CI/CD workflows
        ├── test-dev.yml        # Tests de dev
        ├── test-staging.yml    # Tests de staging
        └── test-prod.yml       # Tests de producción
```

## 🎯 Arquitectura de Ambientes

### Flujo de Configuración

1. **CLI flags** (`--env=staging --headless`)
   ↓
2. **Environment Manager** carga config
   ↓
3. **Config file** (`config/environments/staging.py`) → Timeouts, log level
   ↓
4. **Variables .env** (`STAGING_BASE_URL`, etc.) → URLs, credenciales
   ↓
5. **Conftest.py** inicializa driver con toda la config

### Diferencias entre Ambientes

| Característica | Dev | Staging | Prod |
|----------------|-----|---------|------|
| Implicit Wait | 10s | 15s | 20s |
| Page Load Timeout | 30s | 60s | 90s |
| Log Level | DEBUG | INFO | WARNING |
| Headless Default | No | Sí | Sí |
| Uso | Desarrollo local | Pre-producción | Monitoring |

## 🔍 Troubleshooting

### Error: "Invalid environment: 'xyz'"
- Verifica que estés usando: `dev`, `staging`, o `prod`
- Revisa el valor de `TEST_ENV` en `.env`

### Error: "DEV_BASE_URL not found in .env"
- Asegúrate de haber copiado `.env.example` a `.env`
- Verifica que las variables tengan el prefijo correcto: `DEV_`, `STAGING_`, `PROD_`

### Tests fallan en CI/CD
- Verifica que todos los Secrets estén configurados en GitHub
- Revisa que los nombres de los secrets coincidan exactamente
- Checa los logs en la pestaña "Actions"

### Browser no se ve (headless no deseado)
- Remueve el flag `--headless`
- En local, dev usa headed por defecto

## 📚 Ejemplos de Uso

### Desarrollo Local
```bash
# Desarrollo normal (browser visible)
pytest --env=dev

# Testing rápido (headless)
pytest --env=dev --headless -v
```

### Pre-Deploy a Staging
```bash
# Suite completa en staging
pytest --env=staging --headless --browser=all

# Solo smoke tests
pytest --env=staging --headless -m smoke
```

### Monitoreo de Producción
```bash
# Smoke tests críticos
pytest --env=prod --headless -m "smoke or critical"

# Test específico no destructivo
pytest tests/test_login.py --env=prod --headless
```

## 🤝 Contribuir

1. Crea un branch desde `develop`: `git checkout -b feature/nueva-funcionalidad`
2. Haz tus cambios
3. Asegúrate de que los tests pasen: `pytest --env=dev`
4. Push y crea un PR hacia `develop`

## 📝 Notas

- **NUNCA** commitees el archivo `.env` (contiene credenciales)
- Los tests de producción deben ser **read-only** (no modificar datos)
- Usa markers de pytest (`@pytest.mark.smoke`) para categorizar tests