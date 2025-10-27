## Pagina para restaurante "La media docena"

Primer entrega: pantallas generales (usuarios y admin comparten navegación) siguiendo los prototipos enviados.

## Estructura

- `index.html` – Inicio con hero y accesos a Menú y Contacto
- `menu.html` – Catálogo con filtros por categoría y botón “Agregar”
- `pedidos.html` – Carrito/Pedidos: sumar/restar, eliminar y total
- `acerca.html` – Acerca de nosotros
- `resenas.html` – Reseñas: formulario + listado (localStorage)
- `contacto.html` – Formulario de contacto (demo)
- `reservar.html` – Reservar una mesa (usuarios)
- `login.html` – Acceso con usuarios de prueba y control de rol
- `admin.html` – Panel de administración (solo admin)
- `admin-platillos.html` – Gestión de platillos con disponibilidad y alta
- `admin-pedidos.html` – Gestión de pedidos generados en checkout
- `assets/css/styles.css` – Estilos base con layout y componentes
- `assets/js/data.js` – Datos de ejemplo (categorías y productos)
- `assets/js/main.js` – Navegación lateral, cabecera y lógica compartida (carrito en localStorage)

Todo es HTML/CSS/JS estático, sin backend. El estado (carrito y reseñas) se guarda en `localStorage` del navegador.

## Cómo ejecutar localmente

Opción rápida: abrir `index.html` con el navegador.

Recomendado (para rutas relativas correctas y auto‑recarga): usa la extensión “Live Server” de VS Code y abre el proyecto, después “Open with Live Server”.

## Flujo básico

1. Ir a `Menú`, agregar productos al carrito.
2. Abrir `Carritos/pedidos` para ver, ajustar cantidades y total.
3. En `Reseñas` puedes enviar una reseña (se guarda localmente).
4. `Contacto` envía un mensaje de prueba (solo muestra un aviso y resetea el formulario).
5. `Reservar una mesa` guarda reservas de ejemplo en localStorage.

## Notas y próximos pasos

- El diseño intenta reflejar los colores y distribución de los prototipos (barra lateral naranja, encabezado ámbar, fondo gris).
- Imágenes de ejemplo se cargan desde Unsplash; podemos sustituirlas por imágenes propias.
- Próximas iteraciones sugeridas:
	- Autenticación simple (login/registro) para separar roles.
	- Pantallas de administración reales (CRUD de platillos) con persistencia.
	- Validaciones adicionales y accesibilidad.

## Credenciales de prueba

- Admin: `admin@lmd.com` / `admin123`
- Cliente: `cliente@lmd.com` / `123456`

Si no inicias sesión como admin, las páginas `admin*.html` redirigen a `login.html`.

---

Hecho para avanzar por commits pequeños: cada pantalla ya es navegable y funcional como prototipo.