# 🎨 FRONTEND AGENT - Especificación Completa

**ID**: `frontend`  
**Versión**: 1.0  
**Prioridad**: Alta  
**Estado**: Habilitado  

---

## 📋 DESCRIPCIÓN GENERAL

El **Frontend Agent** es un agente especializado en validación, creación y modificación de código frontend. Su responsabilidad principal es asegurar que todos los archivos HTML, CSS, JavaScript y templates Jinja2 cumplan con las mejores prácticas de desarrollo web, accesibilidad, rendimiento, SEO y seguridad.

---

## 🎯 RESPONSABILIDADES PRINCIPALES

1. **Validación de HTML**: Estructura semántica, accesibilidad, SEO
2. **Validación de CSS**: Organización, performance, responsive design
3. **Validación de JavaScript**: Seguridad, performance, mejores prácticas
4. **Validación de Jinja2**: Sintaxis, herencia de templates, seguridad
5. **Accesibilidad (WCAG 2.1 AA)**: Contraste, navegación por teclado, ARIA
6. **Responsive Design**: Mobile-first, breakpoints, touch targets
7. **SEO**: Meta tags, structured data, semantic HTML
8. **Performance**: Optimización de assets, lazy loading, critical CSS
9. **Seguridad Frontend**: XSS prevention, CSRF, data sanitization
10. **PWA**: Manifest, service workers, offline support

---

## 📁 ARCHIVOS MONITOREADOS

### Patrones de Archivos

```json
{
  "patterns": [
    "app/frontend/**/*.html",
    "app/frontend/**/*.css",
    "app/frontend/**/*.js",
    "app/frontend/**/*.json"
  ]
}
```

### Archivos Específicos

- `app/frontend/templates/base.html` - Template base
- `app/frontend/templates/panel.html` - Panel principal
- `app/frontend/templates/login.html` - Página de login
- `app/frontend/templates/admin_panel.html` - Panel de administrador
- `app/frontend/templates/asesor_panel.html` - Panel de asesor
- `app/frontend/static/css/styles.css` - Estilos principales
- `app/frontend/static/css/animations.css` - Animaciones
- `app/frontend/static/js/language.js` - JavaScript principal
- `app/frontend/static/manifest.json` - Manifest PWA

### Directorios Monitoreados

- `app/frontend/` - Directorio raíz frontend
- `app/frontend/templates/` - Templates Jinja2
- `app/frontend/static/` - Archivos estáticos
- `app/frontend/static/css/` - Hojas de estilo
- `app/frontend/static/js/` - JavaScript

---

## 🔧 FUNCIONES PRINCIPALES

### 1. `validate_html()`

**Descripción**: Valida estructura HTML, semántica, accesibilidad y mejores prácticas

**Parámetros**:
- `check_accessibility` (bool): Verificar accesibilidad WCAG
- `check_seo` (bool): Verificar optimización SEO
- `check_semantic` (bool): Verificar HTML semántico
- `w3c_validation` (bool): Validación W3C (opcional)
- `strict_mode` (bool): Modo estricto

**Reglas de Validación**:

#### HTML Estructura
- ✅ HTML debe ser válido y seguir estándares HTML5
- ✅ Doctype HTML5 debe estar presente: `<!doctype html>`
- ✅ Atributo `lang` debe estar presente en `<html>`
- ✅ Charset UTF-8 debe estar presente: `<meta charset="utf-8">`
- ✅ Viewport meta tag debe estar presente para responsive

#### HTML Semántico
- ✅ Estructura semántica correcta (`<header>`, `<nav>`, `<main>`, `<section>`, `<footer>`)
- ✅ Headings deben seguir jerarquía lógica (h1 > h2 > h3)
- ✅ No usar `<div>` para elementos semánticos cuando existe alternativa

#### Accesibilidad
- ✅ Atributos `alt` en todas las imágenes
- ✅ Labels asociados a todos los inputs
- ✅ ARIA labels donde sea necesario
- ✅ Contraste de colores mínimo 4.5:1 para texto normal
- ✅ Elementos interactivos deben tener focus visible
- ✅ Navegación por teclado debe funcionar

#### SEO
- ✅ Meta tags para SEO deben estar presentes
- ✅ Title tag debe ser único y descriptivo
- ✅ Meta description debe estar presente (150-160 caracteres)
- ✅ Open Graph tags deben estar presentes
- ✅ Twitter Card tags deben estar presentes
- ✅ Schema.org structured data debe estar presente

#### Seguridad
- ✅ Links a recursos externos deben tener `rel="noopener noreferrer"`
- ✅ Formularios deben tener method y action apropiados
- ✅ CSRF tokens deben estar presentes en formularios

#### Mejores Prácticas
- ✅ IDs deben ser únicos en cada página
- ✅ No usar atributos inline (excepto critical CSS)
- ✅ No usar scripts inline (excepto configuraciones críticas)

**Output**:
```json
{
  "file": "app/frontend/templates/panel.html",
  "status": "valid|invalid|warning",
  "html_validation": {
    "valid": true,
    "errors": [],
    "warnings": []
  },
  "accessibility_issues": [
    {
      "type": "missing_alt",
      "element": "img",
      "line": 45,
      "recommendation": "Add alt='Description of image'"
    }
  ],
  "semantic_issues": [],
  "seo_issues": [],
  "security_issues": []
}
```

---

### 2. `validate_css()`

**Descripción**: Valida CSS, organización, performance y mejores prácticas

**Parámetros**:
- `check_browser_compatibility` (bool): Verificar compatibilidad con navegadores
- `check_performance` (bool): Verificar optimización de performance
- `check_responsive` (bool): Verificar diseño responsive
- `validate_variables` (bool): Validar variables CSS
- `check_animations` (bool): Verificar optimización de animaciones

**Reglas de Validación**:

#### CSS Válido
- ✅ CSS debe ser válido y seguir estándares
- ✅ No debe haber errores de sintaxis
- ✅ Propiedades deben estar escritas correctamente

#### Variables CSS
- ✅ Variables CSS deben estar definidas en `:root`
- ✅ Variables deben tener nombres descriptivos
- ✅ No usar valores mágicos, usar variables

#### Performance
- ✅ No usar `!important` innecesariamente
- ✅ Animaciones deben usar GPU acceleration (`transform`, `opacity`)
- ✅ Evitar selectores muy específicos (> 3 niveles)
- ✅ Evitar repaint/reflow innecesarios

#### Responsive Design
- ✅ Media queries deben estar presentes para responsive
- ✅ Mobile-first approach debe seguirse
- ✅ Breakpoints comunes deben estar cubiertos (320px, 768px, 1024px)

#### Mejores Prácticas
- ✅ Usar unidades relativas (`rem`, `em`, `%`) cuando sea posible
- ✅ Dark mode debe estar soportado
- ✅ Fallbacks para propiedades nuevas deben estar presentes

**Output**:
```json
{
  "file": "app/frontend/static/css/styles.css",
  "status": "valid|needs_optimization",
  "css_validation": {
    "valid": true,
    "errors": [],
    "warnings": []
  },
  "duplicates": [
    {
      "property": "color: #333",
      "occurrences": 5,
      "recommendation": "Create CSS variable: --text-primary"
    }
  ],
  "performance_issues": [],
  "responsive_issues": [],
  "variables_usage": {
    "defined": 15,
    "used": 12,
    "unused": 3
  }
}
```

---

### 3. `validate_javascript()`

**Descripción**: Valida JavaScript, seguridad, performance y mejores prácticas

**Parámetros**:
- `check_security` (bool): Verificar seguridad
- `check_performance` (bool): Verificar optimización de performance
- `check_async` (bool): Verificar uso correcto de async/await
- `strict_mode` (bool): Verificar uso de strict mode
- `check_memory_leaks` (bool): Verificar posibles memory leaks

**Reglas de Validación**:

#### Sintaxis
- ✅ JavaScript debe ser válido (ES6+)
- ✅ No debe haber errores de sintaxis
- ✅ Código debe seguir estándares ES6+

#### Variables y Scope
- ✅ Evitar variables globales innecesarias
- ✅ Usar `const`/`let` en lugar de `var`
- ✅ Variables deben tener nombres descriptivos

#### Manejo de Errores
- ✅ Funciones deben tener manejo de errores
- ✅ Try/catch debe usarse apropiadamente
- ✅ Errores deben loguearse apropiadamente

#### Seguridad
- ✅ No exponer información sensible en `console.log`
- ✅ Validar inputs del usuario antes de procesar
- ✅ No usar `eval()` o `innerHTML` con contenido no sanitizado
- ✅ Sanitizar datos antes de enviar al servidor

#### Performance
- ✅ Usar `async`/`await` para operaciones asíncronas
- ✅ Evitar DOM queries repetidos (cachear resultados)
- ✅ Event listeners deben ser removidos cuando no se usen
- ✅ Usar event delegation cuando sea apropiado

#### Mejores Prácticas
- ✅ Código debe ser legible y documentado
- ✅ Funciones deben ser pequeñas y enfocadas
- ✅ Comentarios JSDoc deben estar presentes en funciones públicas

**Output**:
```json
{
  "file": "app/frontend/static/js/language.js",
  "status": "valid|needs_improvement",
  "javascript_validation": {
    "valid": true,
    "errors": [],
    "warnings": []
  },
  "security_issues": [
    {
      "type": "console_log_sensitive",
      "line": 125,
      "recommendation": "Remove or sanitize console.log output"
    }
  ],
  "performance_issues": [
    {
      "type": "repeated_dom_query",
      "line": 45,
      "recommendation": "Cache DOM query result"
    }
  ],
  "best_practices_issues": []
}
```

---

### 4. `validate_jinja2()`

**Descripción**: Valida sintaxis Jinja2 y uso correcto de templates

**Parámetros**:
- `check_syntax` (bool): Verificar sintaxis Jinja2
- `check_variables` (bool): Verificar que variables estén definidas
- `check_inheritance` (bool): Verificar herencia de templates
- `check_security` (bool): Verificar seguridad en templates

**Reglas de Validación**:

#### Sintaxis
- ✅ Sintaxis Jinja2 debe ser válida
- ✅ No debe haber errores de sintaxis
- ✅ Bloques deben estar correctamente definidos

#### Variables
- ✅ Variables deben estar definidas antes de usar
- ✅ Variables deben tener nombres descriptivos
- ✅ No usar variables no definidas

#### Herencia
- ✅ Templates deben usar `base.html` cuando sea posible
- ✅ `extends` debe estar correctamente definido
- ✅ Bloques deben estar correctamente definidos

#### Filtros y Macros
- ✅ Usar filtros Jinja2 apropiados
- ✅ Macros deben usarse para código repetido
- ✅ i18n debe usarse para textos traducibles

#### Seguridad
- ✅ No exponer información sensible en templates
- ✅ Sanitizar datos antes de renderizar
- ✅ Escapar datos del usuario apropiadamente

#### Mejores Prácticas
- ✅ Evitar lógica compleja en templates
- ✅ No hacer queries a BD directamente desde templates
- ✅ No usar HTML hardcodeado, usar variables

**Output**:
```json
{
  "file": "app/frontend/templates/panel.html",
  "status": "valid|invalid",
  "jinja2_validation": {
    "valid": true,
    "errors": [],
    "warnings": []
  },
  "inheritance_issues": [],
  "variable_issues": [],
  "security_issues": [],
  "best_practices_issues": []
}
```

---

### 5. `check_accessibility()`

**Descripción**: Verifica accesibilidad (WCAG 2.1 AA)

**Parámetros**:
- `wcag_level` (string): Nivel WCAG ("A", "AA", "AAA")
- `check_keyboard_navigation` (bool): Verificar navegación por teclado
- `check_screen_reader` (bool): Verificar compatibilidad con screen readers
- `check_contrast` (bool): Verificar contraste de colores
- `check_aria` (bool): Verificar uso de ARIA

**Reglas de Validación**:

#### Contraste
- ✅ Contraste de colores mínimo 4.5:1 para texto normal
- ✅ Contraste de colores mínimo 3:1 para texto grande
- ✅ No depender solo del color para transmitir información

#### Navegación
- ✅ Navegación por teclado debe funcionar
- ✅ Elementos interactivos deben tener focus visible
- ✅ Tab order debe ser lógico

#### Screen Readers
- ✅ Imágenes deben tener alt text descriptivo
- ✅ Formularios deben tener labels asociados
- ✅ ARIA labels deben usarse apropiadamente
- ✅ Estructura de headings debe ser lógica

#### Otros
- ✅ Videos deben tener subtítulos o transcripción
- ✅ Formularios deben tener mensajes de error accesibles
- ✅ Contenido dinámico debe anunciarse apropiadamente

**Output**:
```json
{
  "file": "app/frontend/templates/panel.html",
  "accessibility_score": 85,
  "wcag_level": "AA",
  "issues": [
    {
      "type": "low_contrast",
      "element": ".text-muted",
      "line": 125,
      "current_contrast": "3.2:1",
      "required_contrast": "4.5:1",
      "recommendation": "Increase text color contrast"
    }
  ],
  "keyboard_navigation": {
    "works": true,
    "issues": []
  },
  "screen_reader": {
    "compatible": true,
    "issues": []
  }
}
```

---

### 6. `check_responsive()`

**Descripción**: Verifica diseño responsive y mobile-first

**Parámetros**:
- `check_breakpoints` (bool): Verificar breakpoints comunes
- `check_mobile` (bool): Verificar diseño móvil
- `check_tablet` (bool): Verificar diseño tablet
- `check_desktop` (bool): Verificar diseño desktop
- `check_touch_targets` (bool): Verificar tamaños de touch targets

**Reglas de Validación**:

#### Viewport
- ✅ Viewport meta tag debe estar presente
- ✅ Viewport debe tener configuración apropiada

#### Breakpoints
- ✅ Media queries deben cubrir breakpoints comunes
- ✅ Diseño debe funcionar en móvil (320px+)
- ✅ Diseño debe funcionar en tablet (768px+)
- ✅ Diseño debe funcionar en desktop (1024px+)

#### Mobile-First
- ✅ Diseño debe seguir mobile-first approach
- ✅ Contenido debe ser accesible en móvil
- ✅ Texto debe ser legible en móvil (mínimo 16px)
- ✅ Botones deben tener tamaño mínimo táctil (44x44px)

#### Responsive Elements
- ✅ Imágenes deben ser responsive (`max-width: 100%`)
- ✅ Tablas deben ser responsive o scrollables
- ✅ Menús móviles deben estar implementados
- ✅ No usar hover en móvil

**Output**:
```json
{
  "file": "app/frontend/templates/panel.html",
  "responsive_score": 90,
  "breakpoints": {
    "320px": "pass",
    "768px": "pass",
    "1024px": "pass"
  },
  "issues": [
    {
      "type": "small_touch_target",
      "element": ".btn-small",
      "line": 45,
      "size": "32x32px",
      "required": "44x44px",
      "recommendation": "Increase touch target size"
    }
  ],
  "mobile_issues": [],
  "tablet_issues": [],
  "desktop_issues": []
}
```

---

### 7. `check_seo()`

**Descripción**: Verifica optimización SEO

**Parámetros**:
- `check_meta_tags` (bool): Verificar meta tags
- `check_structured_data` (bool): Verificar structured data
- `check_sitemap` (bool): Verificar sitemap (opcional)
- `check_robots` (bool): Verificar robots.txt (opcional)

**Reglas de Validación**:

#### Meta Tags
- ✅ Title tag debe estar presente y ser único
- ✅ Meta description debe estar presente (150-160 caracteres)
- ✅ Meta keywords debe estar presente (opcional pero recomendado)

#### Open Graph
- ✅ Open Graph tags deben estar presentes
- ✅ OG title, description, image deben estar presentes

#### Twitter Card
- ✅ Twitter Card tags deben estar presentes
- ✅ Twitter Card title, description, image deben estar presentes

#### Structured Data
- ✅ Schema.org structured data debe estar presente
- ✅ Structured data debe ser válido

#### Otros
- ✅ Canonical URL debe estar presente
- ✅ Headings deben usar jerarquía correcta
- ✅ Alt text en imágenes debe ser descriptivo
- ✅ URLs deben ser amigables y descriptivas

**Output**:
```json
{
  "file": "app/frontend/templates/panel.html",
  "seo_score": 85,
  "meta_tags": {
    "title": "present",
    "description": "present",
    "keywords": "present"
  },
  "open_graph": {
    "present": true,
    "complete": true
  },
  "twitter_card": {
    "present": true,
    "complete": true
  },
  "structured_data": {
    "present": true,
    "valid": true
  },
  "issues": []
}
```

---

### 8. `check_performance()`

**Descripción**: Verifica optimización de performance frontend

**Parámetros**:
- `check_load_time` (bool): Verificar tiempo de carga (opcional)
- `check_render_blocking` (bool): Verificar render-blocking resources
- `check_image_optimization` (bool): Verificar optimización de imágenes
- `check_css_optimization` (bool): Verificar optimización de CSS
- `check_js_optimization` (bool): Verificar optimización de JavaScript

**Reglas de Validación**:

#### Assets
- ✅ Imágenes deben estar optimizadas
- ✅ CSS debe estar optimizado (minificado en producción)
- ✅ JavaScript debe estar optimizado (minificado en producción)

#### Critical Resources
- ✅ CSS crítico debe estar inline o en `<head>`
- ✅ JavaScript no crítico debe estar `defer` o `async`

#### Preconnect/DNS Prefetch
- ✅ Recursos externos deben usar `preconnect` o `dns-prefetch`

#### Lazy Loading
- ✅ Lazy loading debe usarse para imágenes
- ✅ Lazy loading debe usarse para contenido no crítico

#### Render Blocking
- ✅ Evitar render-blocking resources
- ✅ Cache headers deben estar configurados

#### Performance Best Practices
- ✅ Evitar múltiples reflows/repaints
- ✅ Usar CSS animations en lugar de JS cuando sea posible

**Output**:
```json
{
  "file": "app/frontend/templates/panel.html",
  "performance_score": 88,
  "file_sizes": {
    "css": "45KB",
    "js": "78KB",
    "html": "12KB"
  },
  "render_blocking": {
    "css": "none",
    "js": "none"
  },
  "optimization_issues": [
    {
      "type": "large_image",
      "file": "hero-image.jpg",
      "size": "2.5MB",
      "recommendation": "Optimize image (target: <500KB)"
    }
  ],
  "lazy_loading": {
    "images": "enabled",
    "content": "enabled"
  }
}
```

---

### 9. `check_security()`

**Descripción**: Verifica seguridad frontend

**Parámetros**:
- `check_xss` (bool): Verificar prevención XSS
- `check_csrf` (bool): Verificar protección CSRF
- `check_data_exposure` (bool): Verificar exposición de datos
- `check_external_links` (bool): Verificar links externos
- `strict_mode` (bool): Modo estricto

**Reglas de Validación**:

#### XSS Prevention
- ✅ No usar `eval()` o `innerHTML` con contenido no sanitizado
- ✅ Sanitizar inputs del usuario antes de renderizar
- ✅ Escapar datos del usuario apropiadamente

#### CSRF Protection
- ✅ CSRF tokens deben estar presentes en formularios
- ✅ Tokens deben ser válidos y verificados

#### Data Exposure
- ✅ No exponer información sensible en HTML/CSS/JS
- ✅ No almacenar tokens o secrets en localStorage sin encriptar
- ✅ No exponer información sensible en `console.log`

#### External Links
- ✅ Links externos deben tener `rel="noopener noreferrer"`
- ✅ Links externos deben ser validados

#### Content Security Policy
- ✅ Content Security Policy debe estar configurado
- ✅ CSP debe ser apropiado para la aplicación

#### Input Validation
- ✅ Inputs deben tener validación del lado del cliente
- ✅ Validar y sanitizar datos antes de enviar al servidor

**Output**:
```json
{
  "file": "app/frontend/templates/panel.html",
  "security_score": 92,
  "xss_prevention": {
    "status": "good",
    "issues": []
  },
  "csrf_protection": {
    "status": "good",
    "issues": []
  },
  "data_exposure": {
    "status": "good",
    "issues": []
  },
  "issues": []
}
```

---

### 10. `check_pwa()`

**Descripción**: Verifica configuración PWA (Progressive Web App)

**Parámetros**:
- `check_manifest` (bool): Verificar manifest.json
- `check_service_worker` (bool): Verificar service worker (opcional)
- `check_icons` (bool): Verificar iconos
- `check_offline` (bool): Verificar soporte offline (opcional)

**Reglas de Validación**:

#### Manifest
- ✅ manifest.json debe estar presente y ser válido
- ✅ Name y short_name deben estar presentes
- ✅ Start URL debe estar presente
- ✅ Display mode debe estar configurado
- ✅ Theme color debe estar configurado

#### Icons
- ✅ Iconos deben estar en múltiples tamaños
- ✅ Iconos deben estar en formato apropiado

#### Service Worker
- ✅ Service worker debe estar registrado (si aplica)
- ✅ Service worker debe estar configurado correctamente

#### Offline Support
- ✅ Soporte offline debe estar implementado (si aplica)

**Output**:
```json
{
  "file": "app/frontend/static/manifest.json",
  "pwa_score": 95,
  "manifest": {
    "present": true,
    "valid": true,
    "complete": true
  },
  "icons": {
    "present": true,
    "sizes": ["192x192", "512x512"],
    "complete": true
  },
  "service_worker": {
    "present": false,
    "recommendation": "Consider implementing service worker for offline support"
  },
  "issues": []
}
```

---

### 11. `suggest_improvements()`

**Descripción**: Sugiere mejoras basadas en mejores prácticas y patrones del proyecto

**Parámetros**:
- `check_patterns` (bool): Analizar patrones existentes
- `check_trends` (bool): Verificar tendencias actuales (opcional)
- `check_best_practices` (bool): Verificar mejores prácticas
- `provide_examples` (bool): Proporcionar ejemplos

**Output**:
```json
{
  "file": "app/frontend/templates/panel.html",
  "suggestions": [
    {
      "type": "ux_improvement",
      "priority": "medium",
      "title": "Add loading states",
      "description": "Add loading states for async operations to improve UX",
      "example": "<button class='btn' data-loading='Cargando...'>Enviar</button>"
    },
    {
      "type": "performance_improvement",
      "priority": "high",
      "title": "Lazy load images",
      "description": "Implement lazy loading for images below the fold",
      "example": "<img src='...' loading='lazy' alt='...'>"
    }
  ]
}
```

---

## ⚙️ CONFIGURACIÓN

### Parámetros de Configuración

```json
{
  "agent": "frontend",
  "enabled": true,
  "priority": "high",
  "config": {
    "validate_on_change": true,
    "strict_html": false,
    "strict_css": false,
    "strict_javascript": false,
    "accessibility_level": "AA",
    "seo_enabled": true,
    "performance_enabled": true,
    "security_enabled": true,
    "pwa_enabled": true
  }
}
```

---

## 📤 FORMATO DE FEEDBACK

```json
{
  "agent": "frontend",
  "trigger_id": "frontend-20250115-143022",
  "timestamp": "2025-01-15T14:30:22Z",
  "status": "completed",
  "file_analyzed": "app/frontend/templates/panel.html",
  "results": {
    "html_validation": "passed",
    "css_validation": "passed",
    "javascript_validation": "passed",
    "accessibility_score": 90,
    "responsive_score": 95,
    "seo_score": 85,
    "performance_score": 88,
    "security_score": 92,
    "pwa_score": 95
  },
  "errors": [],
  "warnings": [
    {
      "type": "missing_alt",
      "file": "app/frontend/templates/panel.html",
      "line": 45,
      "message": "Image missing alt attribute"
    }
  ],
  "suggestions": [
    {
      "type": "performance",
      "priority": "medium",
      "message": "Consider lazy loading images below the fold"
    }
  ]
}
```

---

## 🧪 TESTING Y PERFORMANCE

### Testing Automatizado

El Frontend Agent ejecuta tests automatizados según el schedule configurado:

- **Frecuencia**: Diaria
- **Hora**: 02:00 AM (America/Lima)
- **Tests incluidos**:
  - HTML validation
  - CSS validation
  - JavaScript validation
  - Accessibility check
  - Responsive check
  - SEO check
  - Security check

### Análisis de Performance

- **Frecuencia**: Semanal (Domingos)
- **Hora**: 03:00 AM (America/Lima)
- **Métricas analizadas**:
  - Tamaños de archivos (CSS, JS, HTML)
  - Tiempo de carga
  - Score de accesibilidad
  - Score de SEO
  - Optimizaciones sugeridas

### Reportes

Los reportes se generan en formato JSON y se almacenan en:
- `agentes/reports/frontend_agent_reports/`

---

## 📝 REGLAS ESPECÍFICAS POR TECNOLOGÍA

### HTML

**Prioridad**: Alta

**Requerido**:
- Doctype HTML5
- Atributo `lang`
- Charset UTF-8
- Viewport meta tag
- Title tag
- Estructura semántica

**Recomendado**:
- Meta description
- Favicon
- Open Graph tags
- Schema.org structured data
- ARIA labels

**Prohibido**:
- Inline styles (excepto critical CSS)
- Script tags inline (excepto configuraciones críticas)
- Tables para layout
- Deprecated HTML tags

### CSS

**Prioridad**: Alta

**Requerido**:
- CSS válido
- Variables CSS en `:root`
- Media queries para responsive
- Dark mode support

**Recomendado**:
- Organización por componentes
- Comentarios para secciones
- Mobile-first approach
- Performance optimizations

**Prohibido**:
- `!important` sin justificación
- Valores mágicos
- Selectores muy específicos
- Animaciones que causan repaint

### JavaScript

**Prioridad**: Alta

**Requerido**:
- JavaScript válido ES6+
- Manejo de errores
- Validación de inputs

**Recomendado**:
- `async`/`await` para operaciones asíncronas
- Código modular
- Comentarios JSDoc
- Event delegation

**Prohibido**:
- `var` (usar `const`/`let`)
- `eval()`
- `innerHTML` con contenido no sanitizado
- Variables globales innecesarias

### Jinja2

**Prioridad**: Media

**Requerido**:
- Sintaxis válida
- `extends base.html` cuando sea posible
- Variables definidas

**Recomendado**:
- Uso de filtros
- Macros para código repetido
- i18n para textos

**Prohibido**:
- Lógica compleja en templates
- Queries a BD directamente
- HTML hardcodeado

---

## 🔄 COMUNICACIÓN CON OTROS AGENTES

### Canales Redis

**Escucha**:
- `agent:frontend:trigger`
- `agent:frontend:validate`
- `agent:frontend:create`
- `agent:frontend:modify`

**Publica**:
- `agent:frontend:results`
- `agent:frontend:errors`
- `agent:frontend:warnings`
- `agent:frontend:suggestions`

### Comunicación Basada en Archivos

- **Input**: `agentes/communication/frontend_agent_input.json`
- **Output**: `agentes/communication/frontend_agent_output.json`
- **Errors**: `agentes/communication/frontend_agent_errors.json`

---

## ✅ RESUMEN DE CARACTERÍSTICAS DEL AGENTE FRONTEND

### Funcionalidades Principales
- ✅ Validación completa de HTML, CSS, JavaScript y Jinja2
- ✅ Verificación de accesibilidad WCAG 2.1 AA
- ✅ Verificación de diseño responsive y mobile-first
- ✅ Verificación de optimización SEO
- ✅ Verificación de performance frontend
- ✅ Verificación de seguridad frontend (XSS, CSRF)
- ✅ Verificación de configuración PWA
- ✅ Sugerencias de mejoras basadas en mejores prácticas

### Monitoreo
- ✅ Monitoreo automático de cambios en archivos frontend
- ✅ Activación automática al crear/modificar archivos
- ✅ Validación en tiempo real

### Testing y Performance
- ✅ Tests automatizados diarios
- ✅ Análisis de performance semanal
- ✅ Reportes detallados en formato JSON
- ✅ Sugerencias de optimización automáticas

### Integración
- ✅ Comunicación con otros agentes vía Redis
- ✅ Comunicación basada en archivos JSON
- ✅ Integración con sistema de agentes maestro

---

**Última actualización**: 2025-01-XX

