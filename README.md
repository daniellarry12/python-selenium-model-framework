# Pytest Framework - Configuración y Uso

## 📋 Instalación Inicial

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar variables de entorno:**
   - El archivo `.env` ya está creado con valores por defecto
   - Puedes editarlo para usar diferentes URLs/credenciales

## 🚀 Ejecución Local

### Ejecutar tests en un navegador específico:

```bash
# Solo Chrome (por defecto)
pytest

# Solo Firefox
pytest --browser=firefox

# Solo Edge
pytest --browser=edge

# Todos los navegadores
pytest --browser=all
```

### Opciones adicionales:

```bash
# Con verbose
pytest --browser=chrome -v

# Con reporte HTML
pytest --browser=firefox --html=report.html --self-contained-html

# Ejecutar un test específico
pytest tests/test_login.py --browser=chrome

# Ejecución paralela (si tienes pytest-xdist)
pytest --browser=chrome -n 4
```

## 🌍 Cambiar Ambiente (URL)

### Opción 1: Editar archivo `.env`
```bash
# Editar .env y cambiar BASE_URL
BASE_URL=https://staging.example.com
```

### Opción 2: Variable de entorno temporal
```bash
# Solo para esta ejecución
BASE_URL=https://staging.example.com pytest --browser=chrome
```

### Opción 3: Export en terminal
```bash
# Para todas las ejecuciones en esta sesión
export BASE_URL=https://staging.example.com
pytest --browser=chrome
```

## 🔧 GitHub Actions

### Configurar Secrets en GitHub:

1. Ve a: `Settings` → `Secrets and variables` → `Actions`
2. Crea estos secrets:
   - `BASE_URL`: URL del ambiente
   - `TEST_EMAIL`: Email de prueba
   - `TEST_PASSWORD`: Password de prueba

### El workflow se ejecuta automáticamente:
- En push a `main` o `develop`
- En pull requests
- Manualmente desde la pestaña "Actions"

### Ver resultados:
- Ve a la pestaña "Actions" en GitHub
- Selecciona el workflow run
- Revisa los logs de cada navegador/ambiente

## 📁 Estructura del Proyecto

```
Pytest_Framework/
├── .env                    # Variables locales (NO commitear)
├── .env.example            # Template de variables
├── conftest.py             # Configuración de pytest
├── requirements.txt        # Dependencias
├── utilities/
│   └── test_data.py       # Datos de prueba
├── tests/                  # Tests
└── .github/
    └── workflows/
        └── tests.yml       # CI/CD con GitHub Actions
```

## 🔍 Troubleshooting

### Error: "BASE_URL environment variable is not set"
- Verifica que el archivo `.env` existe
- Ejecuta: `pip install python-dotenv`

### Tests no corren en el navegador deseado
- Verifica que el navegador esté instalado
- Usa: `pytest --browser=chrome -v` para ver logs detallados

### Error en GitHub Actions
- Verifica que los Secrets estén configurados correctamente
- Revisa los logs en la pestaña "Actions"