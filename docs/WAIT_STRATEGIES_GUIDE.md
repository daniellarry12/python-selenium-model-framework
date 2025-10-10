# 📚 Guía Completa: Wait Strategies en Selenium (Profesional)

> **Autor:** Framework Team
> **Última actualización:** 2025
> **Framework:** Pytest + Selenium + Page Object Model
> **Nivel:** Intermedio-Avanzado

---

## 📑 Tabla de Contenidos

1. [Introducción](#introducción)
2. [El Problema del Flakiness](#el-problema-del-flakiness)
3. [Estados de un Elemento Web](#estados-de-un-elemento-web)
4. [Las 5 Wait Strategies Fundamentales](#las-5-wait-strategies-fundamentales)
5. [Comparativa y Decisiones](#comparativa-y-decisiones)
6. [Implementación en tu Framework](#implementación-en-tu-framework)
7. [Ejemplos Prácticos Completos](#ejemplos-prácticos-completos)
8. [Errores Comunes](#errores-comunes)
9. [Mejores Prácticas](#mejores-prácticas)

---

## 🎯 Introducción

Las **Wait Strategies** son patrones de espera que aseguran que los elementos web estén en el estado correcto antes de interactuar con ellos. Esto elimina el **flakiness** (tests que fallan aleatoriamente) causado por:

- ⏱️ Cargas asíncronas (AJAX, APIs)
- 🎨 Animaciones CSS
- ⚡ JavaScript dinámico
- 🌐 Latencia de red
- 🔄 Single Page Applications (SPAs)

---

## 🐛 El Problema del Flakiness

### Escenario SIN Wait Strategies

```python
# ❌ MAL - Sin wait strategy
driver.get("https://example.com/login")
email_field = driver.find_element(By.ID, "email")  # Puede fallar aquí
email_field.send_keys("test@test.com")
```

**¿Por qué falla?**

```
Timeline del navegador:
┌──────────────────────────────────────────────────────────┐
│  T=0ms:  driver.get() ejecutado                          │
│  T=100ms: HTML básico cargado                            │
│  T=150ms: ❌ find_element() ejecutado (DEMASIADO RÁPIDO)│
│  T=500ms: JavaScript carga el formulario                 │
│  T=600ms: Campo de email finalmente visible              │
└──────────────────────────────────────────────────────────┘

Error: NoSuchElementException
```

### Escenario CON Wait Strategy

```python
# ✅ BIEN - Con wait strategy
driver.get("https://example.com/login")
wait = WebDriverWait(driver, 10)
email_field = wait.until(EC.visibility_of_element_located((By.ID, "email")))
email_field.send_keys("test@test.com")
```

**¿Por qué funciona?**

```
Timeline del navegador:
┌──────────────────────────────────────────────────────────┐
│  T=0ms:  driver.get() ejecutado                          │
│  T=100ms: HTML básico cargado                            │
│  T=150ms: ✅ wait.until() inicia polling cada 500ms     │
│  T=500ms: JavaScript carga el formulario                 │
│  T=600ms: Campo de email visible ✅ wait.until() retorna│
│  T=601ms: send_keys() ejecutado exitosamente            │
└──────────────────────────────────────────────────────────┘

Success: Sin errores
```

---

## 🔄 Estados de un Elemento Web

Un elemento HTML pasa por diferentes estados durante su ciclo de vida:

```
┌─────────────────────────────────────────────────────────────────┐
│                    ESTADO 1: NO EXISTE                          │
│  ❌ El elemento NO está en el HTML (DOM)                        │
│  📝 Ejemplo: <div id="app"></div> (vacío)                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                  JavaScript agrega el elemento
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              ESTADO 2: EXISTE PERO OCULTO (PRESENT)             │
│  ✅ Está en el DOM                                              │
│  ❌ display: none / visibility: hidden / opacity: 0            │
│  📝 Ejemplo: <input id="email" style="display: none">          │
│                                                                  │
│  ➡️  USA: find() / presence_of_element_located()               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                  CSS cambia a display: block
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    ESTADO 3: VISIBLE                            │
│  ✅ Está en el DOM                                              │
│  ✅ Es visible (width > 0, height > 0)                         │
│  ✅ No tiene display: none                                     │
│  ❌ Puede estar disabled                                       │
│  📝 Ejemplo: <input id="email" style="display: block">         │
│                                                                  │
│  ➡️  USA: wait_until_visible() / visibility_of_element()       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                  Atributo disabled se quita
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                 ESTADO 4: CLICKABLE (INTERACTUABLE)             │
│  ✅ Está en el DOM                                              │
│  ✅ Es visible                                                  │
│  ✅ Está enabled (sin atributo disabled)                       │
│  ✅ No hay overlays cubriéndolo                                │
│  ✅ Puede recibir eventos de click                             │
│  📝 Ejemplo: <button id="submit">Login</button>                │
│                                                                  │
│  ➡️  USA: wait_until_clickable() / element_to_be_clickable()   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Las 5 Wait Strategies Fundamentales

### 1️⃣ PRESENCE WAIT (Esperar Existencia en DOM)

#### ¿Qué verifica?

```
┌────────────────────────────────┐
│  ✅ Elemento existe en el DOM  │
│  ❌ NO verifica visibilidad    │
│  ❌ NO verifica si está enabled│
└────────────────────────────────┘
```

#### Código de implementación

```python
# En BasePage.py
def find(self, *locator) -> WebElement:
    """Find element with PRESENCE wait."""
    return self.wait.until(
        EC.presence_of_element_located(locator)
    )
```

#### ¿Cuándo usarla?

| ✅ Usar cuando | ❌ NO usar cuando |
|----------------|-------------------|
| Leer atributos de campos hidden | Vas a hacer click en el elemento |
| Verificar que JavaScript agregó elemento | Vas a escribir en un campo |
| Hacer scroll a elementos fuera del viewport | Vas a leer texto visible |
| Verificar que elemento existe (aunque esté oculto) | Necesitas interactuar con el elemento |

#### Ejemplo Real #1: Campo Hidden con Token

```html
<!-- HTML -->
<form>
  <input type="hidden" id="csrf-token" value="abc123xyz" style="display: none;">
  <input type="email" id="email">
</form>
```

```python
# Page Object
class LoginPage(BasePage):
    csrf_token_field = (By.ID, "csrf-token")

    def get_csrf_token(self):
        # ✅ USA PRESENCE porque el campo está hidden
        element = self.find(self.csrf_token_field)
        return element.get_attribute("value")

        # ❌ NO usar wait_until_visible() porque NUNCA será visible

# Test
def test_csrf_token_present():
    login_page = LoginPage(driver)
    token = login_page.get_csrf_token()
    assert token == "abc123xyz"
    print(f"✅ Token encontrado: {token}")
```

#### Ejemplo Real #2: Scroll a Footer

```python
# En tu BasePage.py (línea 493-506)
def scroll_to_element(self, *locator) -> None:
    """Scroll element into view."""
    # ✅ USA PRESENCE (find) porque el elemento puede estar fuera de pantalla
    element = self.find(*locator)
    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

# Caso real en tu framework
class HomePage(BasePage):
    footer_privacy_link = (By.LINK_TEXT, "Privacy Policy")

    def click_privacy_policy(self):
        # Link existe pero está 3000px abajo (no visible inicialmente)
        self.scroll_to_element(self.footer_privacy_link)
        self.click(self.footer_privacy_link)
```

#### Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENCE WAIT FLOW                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │  find() es llamado      │
              └─────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │ WebDriverWait inicia    │
              │ Polling cada 500ms      │
              └─────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │ ¿Elemento en el DOM?    │
              └─────────────────────────┘
                    │               │
                   SÍ              NO
                    │               │
                    ▼               ▼
        ┌───────────────────┐  ┌──────────────────┐
        │ ✅ Retorna        │  │ ⏱️ Espera 500ms  │
        │    elemento       │  │    y reintenta   │
        └───────────────────┘  └──────────────────┘
                                        │
                                        ▼
                            ┌──────────────────────┐
                            │ ¿Timeout alcanzado?  │
                            └──────────────────────┘
                                    │         │
                                   SÍ        NO (volver arriba)
                                    │
                                    ▼
                        ┌──────────────────────────┐
                        │ ❌ TimeoutException      │
                        └──────────────────────────┘
```

---

### 2️⃣ VISIBILITY WAIT (Esperar Visibilidad)

#### ¿Qué verifica?

```
┌────────────────────────────────────────┐
│  ✅ Elemento existe en el DOM          │
│  ✅ Es visible (width > 0, height > 0) │
│  ✅ No tiene display: none             │
│  ✅ No tiene visibility: hidden        │
│  ✅ No tiene opacity: 0                │
│  ❌ NO verifica si está enabled        │
└────────────────────────────────────────┘
```

#### Código de implementación

```python
# En BasePage.py
def wait_until_visible(self, *locator, timeout: int = None) -> WebElement:
    """Wait for element to be visible."""
    wait = WebDriverWait(self.driver, timeout or self.timeout)
    return wait.until(
        EC.visibility_of_element_located(locator)
    )
```

#### ¿Cuándo usarla?

| ✅ Usar cuando | ❌ NO usar cuando |
|----------------|-------------------|
| Escribir en campos de texto | Solo necesitas leer atributos hidden |
| Leer texto visible de elementos | Vas a hacer click (usa clickable) |
| Verificar que modal/popup apareció | Elemento puede estar permanentemente oculto |
| Esperar que dropdown se expanda | Solo verificas existencia |

#### Ejemplo Real #1: Escribir en Campo de Email (TU CAMBIO RECIENTE)

```python
# En tu LoginPage.py
class LoginPage(BasePage):
    email_address_field = (By.ID, "input-email")
    password_field = (By.ID, "input-password")

    def set_email_address(self, email_address):
        # ✅ AHORA USA VISIBILITY (a través de clear_and_type)
        self.set(self.email_address_field, email_address)

    # En BasePage.py (línea 208-223)
    def clear_and_type(self, locator, value: str) -> None:
        # ✅ USA wait_until_visible() - TU CAMBIO
        element = self.wait_until_visible(*locator)
        element.clear()
        element.send_keys(value)
```

**Escenario real:**

```
Timeline de la página:
┌──────────────────────────────────────────────────────────┐
│  T=0ms:   driver.get("...login")                         │
│  T=200ms: HTML cargado con overlay "Loading..."         │
│           Campo email existe pero está oculto:           │
│           <input id="email" style="display: none">       │
│  T=500ms: ✅ wait_until_visible() está esperando...     │
│  T=1500ms: JavaScript quita overlay                      │
│  T=1600ms: Campo email ahora visible:                    │
│            <input id="email" style="display: block">     │
│  T=1601ms: ✅ wait_until_visible() retorna elemento     │
│  T=1602ms: send_keys("test@test.com") ejecutado         │
└──────────────────────────────────────────────────────────┘

Resultado: ✅ Test pasa sin errores
```

#### Ejemplo Real #2: Mensaje de Error Dinámico

```python
# En tu LoginPage.py (mejora sugerida)
class LoginPage(BasePage):
    warning_message = (By.CSS_SELECTOR, "#account-login .alert-danger")

    def get_warning_message(self):
        # ✅ DEBERÍA usar wait_until_visible()
        # Porque el mensaje aparece DESPUÉS del submit
        element = self.wait_until_visible(self.warning_message, timeout=10)
        return element.text.strip()

    # Actualmente usa find() (línea 32-33):
    # def get_warning_message(self):
    #     return self.get_text(self.warning_message)  # Usa find() internamente

# Test
def test_invalid_credentials(self):
    login_page = LoginPage(driver)
    login_page.set_email_address("invalid@test.com")
    login_page.set_password("wrongpassword")
    login_page.click_login_button()

    # ✅ Espera hasta que el mensaje sea visible
    warning = login_page.get_warning_message()
    assert "Warning: No match" in warning
```

**Escenario:**

```html
<!-- Antes del click en Login -->
<div id="account-login">
  <!-- Sin mensaje de error -->
</div>

<!-- Usuario hace click en "Login" -->
<!-- Backend valida credenciales (2 segundos) -->

<!-- Después de la validación -->
<div id="account-login">
  <div class="alert alert-danger">  <!-- ✅ Ahora visible -->
    Warning: No match for E-Mail Address and/or Password.
  </div>
</div>
```

#### Ejemplo Real #3: Modal de Confirmación

```python
# Ejemplo hipotético en tu framework
class CheckoutPage(BasePage):
    success_modal = (By.ID, "order-success-modal")
    order_number = (By.CLASS_NAME, "order-number")

    def verify_order_placed(self):
        # ✅ USA VISIBILITY porque el modal aparece con delay
        modal = self.wait_until_visible(self.success_modal, timeout=15)

        # Modal está visible, ahora lee el número de orden
        order_num = self.get_text(self.order_number)
        return order_num

# Test
def test_place_order():
    checkout_page = CheckoutPage(driver)
    checkout_page.click_place_order_button()

    # Espera que modal aparezca (puede tardar 5-10 segundos)
    order_number = checkout_page.verify_order_placed()
    assert order_number.startswith("ORD-")
    print(f"✅ Orden creada: {order_number}")
```

#### Diagrama Visual: PRESENCE vs VISIBILITY

```
┌────────────────────────────────────────────────────────────────┐
│                   PRESENCE vs VISIBILITY                        │
└────────────────────────────────────────────────────────────────┘

HTML en el DOM:
<input id="email" style="display: none;">

┌───────────────────────┐       ┌──────────────────────────┐
│   find() (PRESENCE)   │       │ wait_until_visible()     │
│                       │       │    (VISIBILITY)          │
└───────────────────────┘       └──────────────────────────┘
          │                                  │
          ▼                                  ▼
  ┌───────────────┐                 ┌──────────────────┐
  │ ¿Existe en    │                 │ ¿Existe Y        │
  │ el DOM?       │                 │  es visible?     │
  └───────────────┘                 └──────────────────┘
          │                                  │
          ▼                                  ▼
      ✅ SÍ                              ❌ NO
   (elemento oculto                   (display: none)
    pero existe)
          │                                  │
          ▼                                  ▼
  ┌───────────────┐                 ┌──────────────────┐
  │ Retorna       │                 │ Sigue esperando  │
  │ elemento      │                 │ hasta que sea    │
  │               │                 │ visible          │
  └───────────────┘                 └──────────────────┘
          │                                  │
          ▼                                  ▼
  send_keys()                         (espera)
  ❌ FALLA:                                  │
  ElementNotInteractableException            ▼
                               CSS cambia a display: block
                                              │
                                              ▼
                                      ✅ Retorna elemento
                                              │
                                              ▼
                                        send_keys()
                                        ✅ FUNCIONA
```

---

### 3️⃣ CLICKABILITY WAIT (Esperar Clickeabilidad)

#### ¿Qué verifica?

```
┌────────────────────────────────────────────────────┐
│  ✅ Elemento existe en el DOM                      │
│  ✅ Es visible                                     │
│  ✅ Está enabled (sin atributo disabled)          │
│  ✅ No hay overlays/modals cubriéndolo            │
│  ✅ Puede recibir eventos de click                │
└────────────────────────────────────────────────────┘
```

#### Código de implementación

```python
# En BasePage.py
def wait_until_clickable(self, *locator, timeout: int = None) -> WebElement:
    """Wait for element to be clickable."""
    wait = WebDriverWait(self.driver, timeout or self.timeout)
    return wait.until(
        EC.element_to_be_clickable(locator)
    )

def click(self, *locator) -> None:
    """Click element (waits for clickability)."""
    # ✅ TU FRAMEWORK YA USA CLICKABILITY - PERFECTO!
    element = self.wait_until_clickable(*locator)
    try:
        element.click()
    except Exception:
        # Fallback: JavaScript click
        self.driver.execute_script("arguments[0].click();", element)
```

#### ¿Cuándo usarla?

| ✅ Usar cuando | ❌ NO usar cuando |
|----------------|-------------------|
| Hacer click en botones | Solo necesitas leer texto |
| Hacer click en links | Solo verificas existencia |
| Seleccionar checkboxes/radios | Elemento nunca será clickeable |
| Hacer click en elementos de menú | Solo necesitas escribir en campo |

#### Ejemplo Real #1: Click en Botón de Login (TU FRAMEWORK)

```python
# En tu LoginPage.py (línea 22-24)
class LoginPage(BasePage):
    login_button = (By.XPATH, "//div[@id='content']//input[@value='Login']")

    def click_login_button(self):
        # ✅ Usa self.click() que internamente usa wait_until_clickable()
        self.click(self.login_button)
        return MyAccountPage(self.driver)

# En BasePage.py (línea 175-190)
def click(self, *locator) -> None:
    # ✅ CLICKABILITY WAIT aplicado automáticamente
    element = self.wait_until_clickable(*locator)
    element.click()
```

**Escenarios que maneja:**

```
┌──────────────────────────────────────────────────────────┐
│  ESCENARIO 1: Botón Disabled                             │
└──────────────────────────────────────────────────────────┘

HTML inicial:
<button id="submit" disabled>Login</button>

T=0ms:    click() llamado
T=100ms:  wait_until_clickable() verifica
          └─ Botón existe: ✅
          └─ Botón visible: ✅
          └─ Botón enabled: ❌ (disabled attribute)
          └─ Resultado: Sigue esperando...

T=2000ms: JavaScript quita el atributo disabled
          <button id="submit">Login</button>

T=2001ms: wait_until_clickable() verifica de nuevo
          └─ Botón existe: ✅
          └─ Botón visible: ✅
          └─ Botón enabled: ✅
          └─ Resultado: ✅ Retorna elemento

T=2002ms: element.click() ejecutado ✅

┌──────────────────────────────────────────────────────────┐
│  ESCENARIO 2: Overlay Cubriendo Botón                    │
└──────────────────────────────────────────────────────────┘

HTML:
<div class="loading-overlay" style="position: fixed;
     width: 100%; height: 100%; z-index: 9999;">
  Loading...
</div>
<button id="submit">Login</button>

T=0ms:    click() llamado
T=100ms:  wait_until_clickable() verifica
          └─ Botón existe: ✅
          └─ Botón visible: ✅
          └─ Overlay cubriendo: ❌
          └─ Resultado: Sigue esperando...

T=3000ms: JavaScript quita el overlay
          (loading-overlay removed from DOM)

T=3001ms: wait_until_clickable() verifica
          └─ Botón existe: ✅
          └─ Botón visible: ✅
          └─ Overlay cubriendo: ✅ (no overlay)
          └─ Resultado: ✅ Retorna elemento

T=3002ms: element.click() ejecutado ✅
```

#### Ejemplo Real #2: Checkbox de Términos y Condiciones

```python
# En tu BasePage.py (línea 259-271) - MEJORADO
class BasePage:
    def check_checkbox(self, *locator) -> None:
        """Check checkbox (if not already checked)."""
        # ✅ MEJORA: Debería usar wait_until_clickable()
        # Actualmente usa find() (solo presence)
        element = self.wait_until_clickable(*locator)
        if not element.is_selected():
            element.click()

# Ejemplo en tu framework
class RegisterPage(BasePage):
    terms_checkbox = (By.ID, "agree-terms")
    register_button = (By.CSS_SELECTOR, "input[value='Register']")

    def accept_terms_and_register(self):
        # ✅ Espera que checkbox sea clickeable
        self.check_checkbox(self.terms_checkbox)
        self.click(self.register_button)
```

**Escenario:**

```html
<!-- Checkbox disabled hasta llenar formulario -->
<input type="checkbox" id="agree-terms" disabled>
<label>I agree to the Terms & Conditions</label>

<!-- Usuario llena email y password -->

<!-- JavaScript habilita el checkbox -->
<input type="checkbox" id="agree-terms">  <!-- disabled removido -->
<label>I agree to the Terms & Conditions</label>
```

```
Timeline:
┌──────────────────────────────────────────────────────────┐
│  T=0ms:   Página carga con checkbox disabled             │
│  T=500ms: Usuario llena email                            │
│  T=1000ms: Usuario llena password                        │
│  T=1500ms: JavaScript detecta campos llenos              │
│  T=1600ms: Checkbox habilitado (disabled attribute gone) │
│  T=1601ms: check_checkbox() llamado                      │
│  T=1602ms: wait_until_clickable() verifica:              │
│            ✅ Existe, ✅ Visible, ✅ Enabled              │
│  T=1603ms: click() ejecutado exitosamente                │
└──────────────────────────────────────────────────────────┘
```

#### Diagrama: VISIBILITY vs CLICKABILITY

```
┌────────────────────────────────────────────────────────────────┐
│              VISIBILITY vs CLICKABILITY                         │
└────────────────────────────────────────────────────────────────┘

HTML:
<button id="submit" disabled style="display: block;">Login</button>

┌───────────────────────────┐       ┌──────────────────────────┐
│ wait_until_visible()      │       │ wait_until_clickable()   │
└───────────────────────────┘       └──────────────────────────┘
          │                                    │
          ▼                                    ▼
  ┌─────────────────┐                ┌──────────────────────┐
  │ ¿Existe Y       │                │ ¿Existe Y visible    │
  │  visible?       │                │  Y enabled Y sin     │
  │                 │                │  overlays?           │
  └─────────────────┘                └──────────────────────┘
          │                                    │
          ▼                                    ▼
      ✅ SÍ                                ❌ NO
   (botón visible                      (botón disabled)
    pero disabled)
          │                                    │
          ▼                                    ▼
  ┌─────────────────┐                ┌──────────────────────┐
  │ Retorna         │                │ Sigue esperando      │
  │ elemento        │                │ hasta que esté       │
  │                 │                │ enabled              │
  └─────────────────┘                └──────────────────────┘
          │                                    │
          ▼                                    ▼
     click()                            (espera)
     ❌ FALLA:                                 │
     ElementNotInteractableException           ▼
     (disabled button)              disabled attribute removido
                                                │
                                                ▼
                                        ✅ Retorna elemento
                                                │
                                                ▼
                                           click()
                                           ✅ FUNCIONA
```

---

### 4️⃣ INVISIBILITY WAIT (Esperar Invisibilidad)

#### ¿Qué verifica?

```
┌────────────────────────────────────────────────────┐
│  ✅ Elemento NO es visible (display: none, etc.)   │
│  ✅ O elemento fue removido del DOM                │
└────────────────────────────────────────────────────┘
```

#### Código de implementación

```python
# En BasePage.py
def wait_until_invisible(self, *locator, timeout: int = None) -> bool:
    """Wait for element to become invisible."""
    wait = WebDriverWait(self.driver, timeout or self.timeout)
    return wait.until(
        EC.invisibility_of_element_located(locator)
    )
```

#### ¿Cuándo usarla?

| ✅ Usar cuando | ❌ NO usar cuando |
|----------------|-------------------|
| Esperar que spinner de carga desaparezca | Necesitas que elemento aparezca |
| Esperar que overlay se cierre | Verificas existencia del elemento |
| Esperar que toast notification se oculte | Vas a interactuar con el elemento |
| Esperar que modal se cierre | Necesitas leer datos del elemento |

#### Ejemplo Real #1: Loading Spinner

```python
# Ejemplo en tu framework (si tuvieras spinners)
class BasePage:
    loading_spinner = (By.CLASS_NAME, "loading-spinner")

    def wait_for_page_ready(self):
        """Wait for loading spinner to disappear."""
        # ✅ USA INVISIBILITY para esperar que desaparezca
        try:
            self.wait_until_invisible(self.loading_spinner, timeout=30)
        except TimeoutException:
            print("⚠️ Warning: Spinner still visible after 30s")

# Caso de uso en test
class ProductPage(BasePage):
    add_to_cart_button = (By.ID, "add-to-cart")
    cart_count = (By.CLASS_NAME, "cart-count")

    def add_product_to_cart(self):
        self.click(self.add_to_cart_button)

        # ✅ Espera que spinner desaparezca antes de verificar
        self.wait_for_page_ready()

        # Ahora es seguro leer el contador
        count = self.get_text(self.cart_count)
        return count
```

**Escenario:**

```html
<!-- Antes del click -->
<button id="add-to-cart">Add to Cart</button>
<div class="cart-count">0</div>

<!-- Usuario hace click -->
<!-- Spinner aparece inmediatamente -->
<div class="loading-spinner" style="display: block;">
  <img src="spinner.gif">
</div>

<!-- Backend procesa (3 segundos) -->

<!-- Spinner desaparece -->
<div class="loading-spinner" style="display: none;">  <!-- ✅ Invisible -->
  <img src="spinner.gif">
</div>

<!-- Contador actualizado -->
<div class="cart-count">1</div>  <!-- ✅ Ahora podemos leerlo -->
```

```
Timeline:
┌──────────────────────────────────────────────────────────┐
│  T=0ms:   click(add_to_cart_button)                      │
│  T=100ms: Spinner aparece (display: block)               │
│  T=200ms: wait_until_invisible() inicia                  │
│  T=300ms: Verificación: ¿Spinner invisible? NO           │
│  T=800ms: Verificación: ¿Spinner invisible? NO           │
│  T=1300ms: Verificación: ¿Spinner invisible? NO          │
│  T=3000ms: Backend termina procesamiento                 │
│  T=3100ms: Spinner oculto (display: none)                │
│  T=3200ms: Verificación: ¿Spinner invisible? ✅ SÍ      │
│  T=3201ms: wait_until_invisible() retorna True           │
│  T=3202ms: get_text(cart_count) ejecutado               │
│  T=3203ms: Resultado: "1" ✅                             │
└──────────────────────────────────────────────────────────┘
```

#### Ejemplo Real #2: Modal de Procesamiento

```python
class CheckoutPage(BasePage):
    place_order_button = (By.ID, "place-order")
    processing_modal = (By.CLASS_NAME, "processing-modal")
    order_number = (By.ID, "order-number")

    def complete_purchase(self):
        # Paso 1: Click en botón
        self.click(self.place_order_button)

        # Paso 2: ✅ Espera que modal de procesamiento desaparezca
        self.wait_until_invisible(self.processing_modal, timeout=30)

        # Paso 3: Ahora modal ya no cubre el número de orden
        order_num = self.get_text(self.order_number)
        return order_num
```

**HTML Sequence:**

```html
<!-- 1. Antes del click -->
<button id="place-order">Place Order</button>

<!-- 2. Modal aparece -->
<div class="processing-modal" style="display: block; z-index: 9999;">
  Processing your payment...
</div>

<!-- 3. Modal desaparece después de 10 segundos -->
<div class="processing-modal" style="display: none;">  <!-- ✅ -->
  Processing your payment...
</div>

<!-- 4. Orden completada (visible ahora) -->
<div id="order-number">ORD-123456</div>
```

#### Ejemplo Real #3: Toast Notification

```python
class BasePage:
    toast_notification = (By.CLASS_NAME, "toast")

    def wait_for_toast_to_disappear(self):
        """Wait for temporary notification to fade out."""
        # ✅ Toast desaparece automáticamente después de 3 segundos
        self.wait_until_invisible(self.toast_notification, timeout=5)

# Uso en test
class CartPage(BasePage):
    remove_item_button = (By.CLASS_NAME, "remove-item")

    def remove_product(self):
        self.click(self.remove_item_button)

        # Toast aparece: "Item removed from cart"
        # ✅ Espera que desaparezca antes de continuar
        self.wait_for_toast_to_disappear()

        # Ahora puedes interactuar con la página sin interferencias
```

---

### 5️⃣ TEXT PRESENT WAIT (Esperar Texto Específico)

#### ¿Qué verifica?

```
┌────────────────────────────────────────────────────┐
│  ✅ Elemento es visible                            │
│  ✅ Elemento contiene el texto esperado            │
└────────────────────────────────────────────────────┘
```

#### Código de implementación

```python
from selenium.webdriver.support import expected_conditions as EC

# En tus tests o Page Objects
def wait_for_text(self, locator, expected_text, timeout=10):
    """Wait for specific text to appear in element."""
    wait = WebDriverWait(self.driver, timeout)
    wait.until(
        EC.text_to_be_present_in_element(locator, expected_text)
    )
    return self.driver.find_element(*locator)
```

#### ¿Cuándo usarla?

| ✅ Usar cuando | ❌ NO usar cuando |
|----------------|-------------------|
| Esperar mensaje de validación específico | Solo necesitas que elemento sea visible |
| Esperar que contador cambie | Texto puede estar presente desde el inicio |
| Esperar cambio de estado ("Processing" → "Done") | No importa el contenido del texto |
| Verificar resultado de búsqueda | Elemento siempre tiene el mismo texto |

#### Ejemplo Real #1: Mensaje de Validación Específico

```python
# En tu LoginPage.py (MEJORADO)
class LoginPage(BasePage):
    warning_message = (By.CSS_SELECTOR, "#account-login .alert-danger")

    def verify_invalid_credentials_message(self):
        """Wait for specific error message to appear."""
        wait = WebDriverWait(self.driver, 10)

        # ✅ Espera el texto específico, no solo que elemento sea visible
        wait.until(
            EC.text_to_be_present_in_element(
                self.warning_message,
                "No match for E-Mail Address"
            )
        )
        return self.get_text(self.warning_message)

# Test mejorado
def test_invalid_credentials():
    login_page = LoginPage(driver)
    login_page.set_email_address("wrong@test.com")
    login_page.set_password("wrongpassword")
    login_page.click_login_button()

    # ✅ Espera el mensaje ESPECÍFICO
    message = login_page.verify_invalid_credentials_message()
    assert "No match" in message
```

**¿Por qué usar TEXT PRESENT en vez de VISIBILITY?**

```
┌──────────────────────────────────────────────────────────┐
│  PROBLEMA: Elemento visible pero SIN texto aún           │
└──────────────────────────────────────────────────────────┘

T=0ms:    click_login_button()
T=100ms:  Backend valida credenciales
T=500ms:  Elemento de error aparece VACÍO:
          <div class="alert-danger"></div>  ✅ Visible pero vacío

          ❌ wait_until_visible() retornaría aquí
          ❌ get_text() retornaría "" (string vacío)
          ❌ Test fallaría: assert "" contains "No match"

T=1500ms: JavaScript inserta el texto:
          <div class="alert-danger">
            Warning: No match for E-Mail Address...
          </div>

          ✅ text_to_be_present_in_element() retorna aquí
          ✅ get_text() retorna el mensaje completo
          ✅ Test pasa
```

#### Ejemplo Real #2: Contador que Cambia

```python
class CartPage(BasePage):
    cart_count = (By.CLASS_NAME, "cart-count")
    add_to_cart_button = (By.ID, "add-to-cart")

    def add_product_and_verify_count(self, expected_count):
        """Add product and wait for cart count to update."""
        # Contador antes de agregar
        old_count = self.get_text(self.cart_count)  # "0"

        # Agregar producto
        self.click(self.add_to_cart_button)

        # ✅ Espera que el texto cambie al número esperado
        wait = WebDriverWait(self.driver, 10)
        wait.until(
            EC.text_to_be_present_in_element(
                self.cart_count,
                str(expected_count)
            )
        )

        # Ahora podemos leer el nuevo valor
        new_count = self.get_text(self.cart_count)
        return new_count

# Test
def test_add_to_cart():
    cart_page = CartPage(driver)

    # ✅ Espera que contador cambie de "0" a "1"
    new_count = cart_page.add_product_and_verify_count(expected_count=1)
    assert new_count == "1"
```

**Timeline:**

```
┌──────────────────────────────────────────────────────────┐
│  Estado inicial:                                          │
│  <span class="cart-count">0</span>                       │
└──────────────────────────────────────────────────────────┘
                    ↓
          click(add_to_cart_button)
                    ↓
┌──────────────────────────────────────────────────────────┐
│  T=100ms: AJAX request enviado al backend                │
│  <span class="cart-count">0</span>  ← Todavía "0"       │
│                                                           │
│  ❌ Sin text_present wait:                               │
│     get_text() retornaría "0" aquí (valor viejo)        │
└──────────────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────────────┐
│  T=2000ms: Backend responde                              │
│  <span class="cart-count">1</span>  ← ✅ Ahora "1"      │
│                                                           │
│  ✅ Con text_present wait:                               │
│     wait.until(text == "1") retorna aquí                │
└──────────────────────────────────────────────────────────┘
```

#### Ejemplo Real #3: Estado de Procesamiento

```python
class OrderStatusPage(BasePage):
    status_label = (By.ID, "order-status")

    def wait_for_order_completion(self):
        """Wait for order status to change from Processing to Completed."""
        # Estado inicial: "Processing..."

        # ✅ Espera hasta que el texto cambie a "Completed"
        wait = WebDriverWait(self.driver, 60)
        wait.until(
            EC.text_to_be_present_in_element(
                self.status_label,
                "Completed"
            )
        )

        return self.get_text(self.status_label)

# Test
def test_order_processing():
    status_page = OrderStatusPage(driver)
    status_page.place_order()

    # ✅ Espera hasta 60 segundos para que status cambie
    final_status = status_page.wait_for_order_completion()
    assert final_status == "Completed"
```

**Estados del elemento:**

```
┌──────────────────────────────────────────────────────────┐
│  T=0s:  <div id="order-status">Pending</div>            │
│         ❌ text_present("Completed") → sigue esperando  │
└──────────────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────────────┐
│  T=5s:  <div id="order-status">Processing</div>         │
│         ❌ text_present("Completed") → sigue esperando  │
└──────────────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────────────┐
│  T=30s: <div id="order-status">Shipping</div>           │
│         ❌ text_present("Completed") → sigue esperando  │
└──────────────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────────────┐
│  T=45s: <div id="order-status">Completed</div>          │
│         ✅ text_present("Completed") → retorna True     │
└──────────────────────────────────────────────────────────┘
```

---

## 📊 Comparativa y Decisiones

### Matriz de Decisión Rápida

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    ¿QUÉ WAIT STRATEGY USAR?                              │
└──────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────┬────────────────────────────────────┐
│         TU OBJETIVO                │    WAIT STRATEGY RECOMENDADA       │
├────────────────────────────────────┼────────────────────────────────────┤
│ Hacer CLICK en un elemento         │ ✅ wait_until_clickable()         │
│ Escribir en un CAMPO               │ ✅ wait_until_visible()           │
│ Leer TEXTO visible                 │ ✅ wait_until_visible()           │
│ Leer ATRIBUTO de campo hidden      │ ✅ find() (presence)              │
│ Hacer SCROLL a elemento            │ ✅ find() (presence)              │
│ SELECT en dropdown                 │ ✅ wait_until_visible()           │
│ CHECK/UNCHECK checkbox             │ ✅ wait_until_clickable()         │
│ HOVER sobre elemento               │ ✅ wait_until_visible()           │
│ Esperar que DESAPAREZCA spinner    │ ✅ wait_until_invisible()         │
│ Esperar TEXTO específico           │ ✅ text_to_be_present_in_element()│
│ Esperar cambio de ESTADO           │ ✅ text_to_be_present_in_element()│
│ Drag and Drop                      │ ✅ wait_until_visible() (ambos)   │
│ Verificar elemento EXISTE          │ ✅ find() (presence)              │
└────────────────────────────────────┴────────────────────────────────────┘
```

### Tabla Comparativa Detallada

| Wait Strategy | Verifica Existencia | Verifica Visible | Verifica Enabled | Verifica Sin Overlays | Uso % |
|---------------|:------------------:|:----------------:|:----------------:|:---------------------:|:-----:|
| **PRESENCE** | ✅ | ❌ | ❌ | ❌ | 3% |
| **VISIBILITY** | ✅ | ✅ | ❌ | ❌ | 80% |
| **CLICKABILITY** | ✅ | ✅ | ✅ | ✅ | 15% |
| **INVISIBILITY** | ✅ | ❌ (debe ser invisible) | - | - | 1% |
| **TEXT PRESENT** | ✅ | ✅ | ❌ | ❌ | 1% |

### Diagrama de Flujo: ¿Qué Wait Usar?

```
                    ┌─────────────────────────┐
                    │  ¿Qué necesitas hacer?  │
                    └─────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
      ┌─────────────┐  ┌──────────┐   ┌─────────────┐
      │ Interactuar │  │  Leer    │   │   Esperar   │
      │ con elemento│  │   info   │   │ que cambie  │
      └─────────────┘  └──────────┘   └─────────────┘
              │               │               │
              ▼               ▼               ▼
      ┌─────────────┐  ┌──────────┐   ┌─────────────┐
      │ ¿Qué tipo?  │  │ ¿Qué     │   │ ¿Qué debe   │
      │             │  │ lees?    │   │  cambiar?   │
      └─────────────┘  └──────────┘   └─────────────┘
              │               │               │
        ┌─────┴─────┐   ┌─────┴─────┐   ┌─────┴─────┐
        ▼           ▼   ▼           ▼   ▼           ▼
    ┌──────┐   ┌──────┐ ┌────┐  ┌────┐ ┌────┐  ┌────┐
    │Click │   │Type  │ │Text│  │Attr│ │Debe│  │Debe│
    │      │   │      │ │    │  │    │ │desa│  │apa │
    │      │   │      │ │    │  │    │ │pare│  │rece│
    │      │   │      │ │    │  │    │ │cer │  │r   │
    └──────┘   └──────┘ └────┘  └────┘ └────┘  └────┘
        │           │      │        │      │        │
        ▼           ▼      ▼        ▼      ▼        ▼
  ┌──────────┐ ┌────────┐ ┌───┐ ┌────┐ ┌───┐   ┌───┐
  │clickable │ │visible │ │vis│ │pres│ │inv│   │txt│
  └──────────┘ └────────┘ └───┘ └────┘ └───┘   └───┘
```

---

## 💻 Implementación en tu Framework

### Estado Actual de tu BasePage.py

#### ✅ Métodos que YA usan la wait strategy correcta:

```python
# 1. click() - PERFECTO ✅
def click(self, *locator) -> None:
    element = self.wait_until_clickable(*locator)  # ✅ Correcto
    element.click()

# 2. type() - MEJORADO RECIENTEMENTE ✅
def type(self, locator, value: str) -> None:
    element = self.wait_until_visible(*locator)  # ✅ Tu cambio
    element.send_keys(value)

# 3. clear_and_type() - MEJORADO RECIENTEMENTE ✅
def clear_and_type(self, locator, value: str) -> None:
    element = self.wait_until_visible(*locator)  # ✅ Tu cambio
    element.clear()
    element.send_keys(value)
```

#### ⚠️ Métodos que podrían mejorarse:

```python
# 1. get_text() - Usa find() (presence) ⚠️
def get_text(self, *locator) -> str:
    element = self.find(*locator)  # ⚠️ Debería usar wait_until_visible()
    return element.text.strip()

# MEJORA SUGERIDA:
def get_text(self, *locator) -> str:
    element = self.wait_until_visible(*locator)  # ✅
    return element.text.strip()

# 2. check_checkbox() - Usa find() (presence) ⚠️
def check_checkbox(self, *locator) -> None:
    element = self.find(*locator)  # ⚠️ Debería usar wait_until_clickable()
    if not element.is_selected():
        element.click()

# MEJORA SUGERIDA:
def check_checkbox(self, *locator) -> None:
    element = self.wait_until_clickable(*locator)  # ✅
    if not element.is_selected():
        element.click()

# 3. uncheck_checkbox() - Usa find() (presence) ⚠️
def uncheck_checkbox(self, *locator) -> None:
    element = self.find(*locator)  # ⚠️ Debería usar wait_until_clickable()
    if element.is_selected():
        element.click()

# MEJORA SUGERIDA:
def uncheck_checkbox(self, *locator) -> None:
    element = self.wait_until_clickable(*locator)  # ✅
    if element.is_selected():
        element.click()

# 4. select_dropdown_by_text() - Usa find() (presence) ⚠️
def select_dropdown_by_text(self, locator, text: str) -> None:
    element = self.find(*locator)  # ⚠️ Debería usar wait_until_visible()
    Select(element).select_by_visible_text(text)

# MEJORA SUGERIDA:
def select_dropdown_by_text(self, locator, text: str) -> None:
    element = self.wait_until_visible(*locator)  # ✅
    Select(element).select_by_visible_text(text)

# 5. hover() - Usa find() (presence) ⚠️
def hover(self, *locator) -> None:
    element = self.find(*locator)  # ⚠️ Debería usar wait_until_visible()
    ActionChains(self.driver).move_to_element(element).perform()

# MEJORA SUGERIDA:
def hover(self, *locator) -> None:
    element = self.wait_until_visible(*locator)  # ✅
    ActionChains(self.driver).move_to_element(element).perform()
```

#### ✅ Métodos que están CORRECTOS con find() (presence):

```python
# 1. get_attribute() - CORRECTO ✅
def get_attribute(self, locator, attribute: str) -> str:
    element = self.find(*locator)  # ✅ Correcto (puede ser hidden field)
    return element.get_attribute(attribute)

# 2. scroll_to_element() - CORRECTO ✅
def scroll_to_element(self, *locator) -> None:
    element = self.find(*locator)  # ✅ Correcto (puede estar fuera del viewport)
    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

# 3. is_enabled() - CORRECTO ✅
def is_enabled(self, *locator) -> bool:
    element = self.find(*locator)  # ✅ Correcto (puede verificar hidden)
    return element.is_enabled()

# 4. is_selected() - CORRECTO ✅
def is_selected(self, *locator) -> bool:
    element = self.find(*locator)  # ✅ Correcto (puede verificar hidden)
    return element.is_selected()
```

### Resumen de Mejoras Sugeridas

```
┌────────────────────────────────────────────────────────────────┐
│            MEJORAS PRIORITARIAS (5 métodos)                    │
└────────────────────────────────────────────────────────────────┘

🔥 Alta Prioridad (Más usados en tests):
  1. get_text() → Cambiar a wait_until_visible()
  2. check_checkbox() → Cambiar a wait_until_clickable()
  3. uncheck_checkbox() → Cambiar a wait_until_clickable()

🟡 Media Prioridad:
  4. select_dropdown_by_text() → Cambiar a wait_until_visible()
  5. select_dropdown_by_value() → Cambiar a wait_until_visible()

🟢 Baja Prioridad (Menos usados):
  6. hover() → Cambiar a wait_until_visible()
  7. double_click() → Cambiar a wait_until_clickable()
  8. right_click() → Cambiar a wait_until_clickable()
  9. drag_and_drop() → Cambiar ambos a wait_until_visible()
```

---

## 🎓 Ejemplos Prácticos Completos

### Ejemplo 1: Login Flow Completo

```python
# ========================================================================
# TEST: Login con credenciales válidas
# ========================================================================

def test_valid_login():
    """
    Demuestra uso correcto de wait strategies en flujo de login.
    """
    driver = webdriver.Chrome()
    driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=account/login")

    login_page = LoginPage(driver)

    # PASO 1: Escribir email
    # ✅ Usa wait_until_visible() (tu mejora reciente)
    login_page.set_email_address("test@test.com")

    # PASO 2: Escribir password
    # ✅ Usa wait_until_visible() (tu mejora reciente)
    login_page.set_password("password123")

    # PASO 3: Click en botón login
    # ✅ Usa wait_until_clickable() (ya estaba correcto)
    my_account_page = login_page.click_login_button()

    # PASO 4: Verificar redirección exitosa
    # ✅ Usa wait strategy de URL
    assert "/account/account" in driver.current_url

    driver.quit()
```

**Timeline del test:**

```
T=0ms:     driver.get() ejecutado
T=500ms:   Página carga con overlay "Loading..."
           └─ Email field existe pero display: none

T=1000ms:  set_email_address() llamado
           └─ wait_until_visible() inicia polling

T=1500ms:  JavaScript quita overlay
           └─ Email field ahora visible (display: block)
           └─ wait_until_visible() retorna elemento
           └─ send_keys("test@test.com") ejecutado ✅

T=2000ms:  set_password() llamado
           └─ Password field ya visible
           └─ send_keys("password123") ejecutado ✅

T=2500ms:  click_login_button() llamado
           └─ wait_until_clickable() verifica:
              • Botón existe: ✅
              • Botón visible: ✅
              • Botón enabled: ✅
              • Sin overlays: ✅
           └─ click() ejecutado ✅

T=3000ms:  Backend valida credenciales

T=4000ms:  Redirección a /account/account ✅

Test Result: ✅ PASSED
```

### Ejemplo 2: Login con Credenciales Inválidas

```python
# ========================================================================
# TEST: Login con credenciales inválidas (espera mensaje de error)
# ========================================================================

def test_invalid_login_with_wait_strategies():
    """
    Demuestra uso de wait strategies para manejar mensajes dinámicos.
    """
    driver = webdriver.Chrome()
    driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=account/login")

    login_page = LoginPage(driver)

    # PASO 1: Escribir credenciales inválidas
    login_page.set_email_address("invalid@test.com")
    login_page.set_password("wrongpassword")

    # PASO 2: Click en login
    login_page.click_login_button()

    # PASO 3: Esperar mensaje de error (MEJOR APPROACH)
    wait = WebDriverWait(driver, 10)

    # ✅ OPCIÓN 1: Esperar que elemento sea visible
    error_element = wait.until(
        EC.visibility_of_element_located(login_page.warning_message)
    )

    # ✅ OPCIÓN 2 (MEJOR): Esperar texto específico
    wait.until(
        EC.text_to_be_present_in_element(
            login_page.warning_message,
            "No match for E-Mail Address"
        )
    )

    # PASO 4: Verificar mensaje
    error_text = login_page.get_warning_message()
    assert "Warning" in error_text

    driver.quit()
```

**Timeline:**

```
T=0ms:     Credenciales inválidas escritas
T=500ms:   click_login_button() ejecutado
T=1000ms:  Backend valida credenciales
T=2000ms:  Backend responde: "Invalid"
T=2100ms:  JavaScript crea elemento de error:
           <div class="alert-danger"></div>  ← Vacío

           ❌ visibility_of_element_located() retornaría aquí
           ❌ get_text() retornaría "" (vacío)

T=2200ms:  JavaScript inserta texto:
           <div class="alert-danger">
             Warning: No match for E-Mail Address...
           </div>

           ✅ text_to_be_present_in_element() retorna aquí
           ✅ get_text() retorna mensaje completo

Test Result: ✅ PASSED
```

### Ejemplo 3: Add to Cart con Spinner

```python
# ========================================================================
# TEST: Agregar producto al carrito (con loading spinner)
# ========================================================================

class ProductPage(BasePage):
    add_to_cart_button = (By.ID, "add-to-cart")
    loading_spinner = (By.CLASS_NAME, "loading-spinner")
    cart_count = (By.CLASS_NAME, "cart-count")
    success_message = (By.CLASS_NAME, "alert-success")

    def add_product_to_cart(self):
        """Add product to cart with proper wait strategies."""

        # PASO 1: Click en "Add to Cart"
        # ✅ Usa wait_until_clickable()
        self.click(self.add_to_cart_button)

        # PASO 2: Esperar que spinner desaparezca
        # ✅ Usa wait_until_invisible()
        self.wait_until_invisible(self.loading_spinner, timeout=10)

        # PASO 3: Esperar mensaje de éxito con texto específico
        # ✅ Usa text_to_be_present_in_element()
        wait = WebDriverWait(self.driver, 10)
        wait.until(
            EC.text_to_be_present_in_element(
                self.success_message,
                "Success: You have added"
            )
        )

        # PASO 4: Verificar que contador aumentó
        # ✅ Usa wait_until_visible()
        new_count = self.get_text(self.cart_count)
        return new_count

# Test
def test_add_to_cart_with_wait_strategies():
    product_page = ProductPage(driver)

    # Contador inicial: "0"
    initial_count = product_page.get_text(product_page.cart_count)
    assert initial_count == "0"

    # Agregar producto (maneja todos los waits internamente)
    new_count = product_page.add_product_to_cart()

    # Verificar contador actualizado
    assert new_count == "1"
```

**Timeline completo:**

```
┌──────────────────────────────────────────────────────────┐
│  T=0ms:   get_text(cart_count)                           │
│           └─ wait_until_visible() espera                 │
│           └─ Retorna "0" ✅                              │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│  T=500ms: click(add_to_cart_button)                      │
│           └─ wait_until_clickable() verifica             │
│           └─ Botón clickeable ✅                         │
│           └─ click() ejecutado ✅                        │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│  T=600ms: Loading spinner aparece:                       │
│           <div class="loading-spinner"                   │
│                style="display: block;"></div>            │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│  T=700ms: wait_until_invisible(spinner) inicia           │
│           └─ Polling cada 500ms                          │
│           └─ Verifica: ¿Spinner invisible? NO            │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│  T=3000ms: Backend procesa "add to cart"                 │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│  T=3200ms: Spinner desaparece:                           │
│            <div class="loading-spinner"                  │
│                 style="display: none;"></div>            │
│            └─ wait_until_invisible() retorna True ✅     │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│  T=3300ms: Mensaje de éxito aparece VACÍO:               │
│            <div class="alert-success"></div>             │
│            └─ text_to_be_present() sigue esperando...   │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│  T=3500ms: JavaScript inserta texto en mensaje:          │
│            <div class="alert-success">                   │
│              Success: You have added...                  │
│            </div>                                        │
│            └─ text_to_be_present() retorna ✅           │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│  T=3600ms: get_text(cart_count)                          │
│            <span class="cart-count">1</span>             │
│            └─ Retorna "1" ✅                             │
└──────────────────────────────────────────────────────────┘

Test Result: ✅ PASSED (Sin flakiness)
```

---

## ⚠️ Errores Comunes

### Error #1: Usar find() para elementos interactuables

```python
# ❌ MAL
def click_button(self):
    button = self.find(self.submit_button)  # Solo verifica existence
    button.click()  # ❌ Puede fallar si está disabled u oculto

# ✅ BIEN
def click_button(self):
    button = self.wait_until_clickable(self.submit_button)
    button.click()  # ✅ Garantiza que es clickeable
```

**Error que previene:**
```
selenium.common.exceptions.ElementClickInterceptedException:
Message: element click intercepted: Element <button>...</button>
is not clickable at point (100, 200). Other element would receive the click
```

---

### Error #2: Leer texto sin esperar visibilidad

```python
# ❌ MAL
def get_error_message(self):
    element = self.find(self.error_message)  # Puede estar oculto
    return element.text  # ❌ Retorna string vacío si está display: none

# ✅ BIEN
def get_error_message(self):
    element = self.wait_until_visible(self.error_message)
    return element.text  # ✅ Garantiza que el texto es visible
```

---

### Error #3: No esperar que spinner desaparezca

```python
# ❌ MAL
def submit_form(self):
    self.click(self.submit_button)
    # ❌ Continúa inmediatamente, spinner puede cubrir siguiente elemento
    next_element = self.find(self.next_button)
    next_element.click()  # ❌ Puede fallar por spinner encima

# ✅ BIEN
def submit_form(self):
    self.click(self.submit_button)
    self.wait_until_invisible(self.loading_spinner)  # ✅ Espera
    self.click(self.next_button)  # ✅ Ahora es seguro
```

---

### Error #4: Verificar texto sin esperar el cambio

```python
# ❌ MAL
def verify_cart_updated(self):
    old_count = self.get_text(self.cart_count)  # "0"
    self.click(self.add_to_cart)
    time.sleep(2)  # ❌ Hard wait (malo)
    new_count = self.get_text(self.cart_count)  # Puede aún ser "0"
    assert new_count == "1"  # ❌ Flaky test

# ✅ BIEN
def verify_cart_updated(self):
    old_count = self.get_text(self.cart_count)
    self.click(self.add_to_cart)
    # ✅ Espera el texto específico
    wait = WebDriverWait(self.driver, 10)
    wait.until(
        EC.text_to_be_present_in_element(self.cart_count, "1")
    )
    new_count = self.get_text(self.cart_count)
    assert new_count == "1"  # ✅ Siempre pasa
```

---

### Error #5: Usar visibility para campos hidden

```python
# ❌ MAL
def get_csrf_token(self):
    # ❌ Campo está hidden (display: none)
    element = self.wait_until_visible(self.csrf_token_field)
    return element.get_attribute("value")  # ❌ Timeout!

# ✅ BIEN
def get_csrf_token(self):
    # ✅ Usa presence para campos hidden
    element = self.find(self.csrf_token_field)
    return element.get_attribute("value")  # ✅ Funciona
```

---

## ✨ Mejores Prácticas

### 1. Siempre usa explicit waits, nunca implicit

```python
# ❌ MAL - Implicit Wait
driver.implicitly_wait(10)
element = driver.find_element(By.ID, "email")

# ✅ BIEN - Explicit Wait
wait = WebDriverWait(driver, 10)
element = wait.until(EC.visibility_of_element_located((By.ID, "email")))
```

**¿Por qué?**
- Implicit waits aplican a TODOS los find_element()
- Son lentos y no específicos
- No verifican condiciones (solo existence)
- Explicit waits son más rápidos y precisos

---

### 2. Usa timeouts específicos según la acción

```python
# ✅ BIEN - Timeouts específicos
class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.short_timeout = 5   # Para elementos rápidos
        self.normal_timeout = 10  # Para la mayoría
        self.long_timeout = 30    # Para operaciones lentas

    def wait_for_spinner_to_disappear(self):
        # Spinner puede tardar más
        self.wait_until_invisible(self.spinner, timeout=self.long_timeout)

    def click_button(self):
        # Botones son rápidos
        self.wait_until_clickable(self.button, timeout=self.short_timeout)
```

---

### 3. Crea métodos helper para wait patterns comunes

```python
# ✅ BIEN - Helper methods
class BasePage:
    def wait_for_page_ready(self):
        """Wait for all loading indicators to disappear."""
        self.wait_until_invisible(self.loading_spinner, timeout=30)
        self.wait_until_invisible(self.loading_overlay, timeout=30)

    def wait_for_ajax_complete(self):
        """Wait for jQuery AJAX to complete."""
        wait = WebDriverWait(self.driver, 10)
        wait.until(lambda driver: driver.execute_script("return jQuery.active == 0"))

    def wait_for_text_change(self, locator, old_text, timeout=10):
        """Wait for element text to change from old value."""
        wait = WebDriverWait(self.driver, timeout)
        wait.until_not(
            EC.text_to_be_present_in_element(locator, old_text)
        )
```

---

### 4. Combina múltiples wait conditions

```python
# ✅ BIEN - Múltiples condiciones
from selenium.webdriver.support import expected_conditions as EC

def wait_for_modal_and_button(self):
    """Wait for modal to appear AND button to be clickable."""
    wait = WebDriverWait(self.driver, 10)

    # Espera ambas condiciones
    wait.until(
        EC.presence_of_element_located(self.modal)
    )
    wait.until(
        EC.element_to_be_clickable(self.modal_button)
    )
```

---

### 5. Maneja timeouts con mensajes descriptivos

```python
# ✅ BIEN - Mensajes descriptivos
def click_submit(self):
    try:
        element = self.wait_until_clickable(
            self.submit_button,
            timeout=10
        )
        element.click()
    except TimeoutException:
        raise TimeoutException(
            f"Submit button not clickable after 10s. "
            f"Current URL: {self.driver.current_url}. "
            f"Page title: {self.driver.title}"
        )
```

---

### 6. Usa custom expected conditions para casos complejos

```python
# ✅ BIEN - Custom Expected Condition
class element_has_css_class:
    """Wait for element to have specific CSS class."""
    def __init__(self, locator, css_class):
        self.locator = locator
        self.css_class = css_class

    def __call__(self, driver):
        element = driver.find_element(*self.locator)
        classes = element.get_attribute("class")
        if self.css_class in classes:
            return element
        return False

# Uso:
wait = WebDriverWait(driver, 10)
element = wait.until(
    element_has_css_class((By.ID, "button"), "active")
)
```

---

### 7. Documenta tus wait strategies

```python
# ✅ BIEN - Documentación clara
def set_email(self, email):
    """
    Set email address in login form.

    Wait Strategy: VISIBILITY
    - Waits for email field to be visible before typing
    - Handles scenarios where field is hidden during page load
    - Timeout: 10 seconds (default)

    Args:
        email: Email address to enter

    Raises:
        TimeoutException: If field not visible after 10s
    """
    self.clear_and_type(self.email_field, email)
```

---

## 📖 Resumen Final

### Las 5 Reglas de Oro

```
┌────────────────────────────────────────────────────────────┐
│              LAS 5 REGLAS DE ORO                           │
└────────────────────────────────────────────────────────────┘

1️⃣  ¿Vas a HACER CLICK?
    └─ wait_until_clickable()

2️⃣  ¿Vas a ESCRIBIR o LEER?
    └─ wait_until_visible()

3️⃣  ¿Solo necesitas que EXISTA?
    └─ find() / presence

4️⃣  ¿Necesitas que DESAPAREZCA?
    └─ wait_until_invisible()

5️⃣  ¿Necesitas un TEXTO ESPECÍFICO?
    └─ text_to_be_present_in_element()
```

### Cheat Sheet Rápido

| Acción | Método BasePage | Wait Strategy | Timeout Sugerido |
|--------|----------------|---------------|------------------|
| Click en botón | `click()` | Clickable | 10s |
| Escribir en campo | `clear_and_type()` | Visibility | 10s |
| Leer texto | `get_text()` | Visibility | 10s |
| Leer atributo hidden | `get_attribute()` | Presence | 10s |
| Checkbox | `check_checkbox()` | Clickable | 10s |
| Dropdown | `select_dropdown_by_text()` | Visibility | 10s |
| Esperar spinner | `wait_until_invisible()` | Invisibility | 30s |
| Scroll | `scroll_to_element()` | Presence | 10s |
| Hover | `hover()` | Visibility | 10s |

---

## 🎓 Conclusión

Las **Wait Strategies** son la diferencia entre:

```
❌ Tests flaky que fallan aleatoriamente (20% failure rate)
✅ Tests estables que siempre pasan (99.9% reliability)
```

**Tu framework ya está en buen camino:**
- ✅ `click()` usa `wait_until_clickable()` (perfecto)
- ✅ `type()` usa `wait_until_visible()` (tu mejora reciente)
- ✅ `clear_and_type()` usa `wait_until_visible()` (tu mejora reciente)

**Próximos pasos sugeridos:**
1. Mejorar `get_text()` → `wait_until_visible()`
2. Mejorar `check_checkbox()` → `wait_until_clickable()`
3. Mejorar `uncheck_checkbox()` → `wait_until_clickable()`

---

**Documento creado con ❤️ para entender Wait Strategies a nivel profesional**

*Última actualización: 2025*
