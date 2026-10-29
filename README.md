# Atlas venoso del miembro inferior

Atlas interactivo 3D de anatomía venosa del miembro inferior del Instituto Mexicano de Flebología (IMF): modelo 3D, ficha por estructura, simulador de ecografía en modo B, evaluación, tutor y ruta de aprendizaje.

Sitio en producción: https://anatomia.flebologiamexico.com (GitHub Pages, rama `main`).

## Archivos

| Archivo | Para qué sirve |
|---|---|
| `index.html` | Todo el atlas en un solo archivo (HTML, CSS, JS y datos del modelo). No hay build. |
| `CNAME` | Dominio personalizado de GitHub Pages. No borrar. |
| `favicon.ico`, `favicon-16x16.png`, `favicon-32x32.png` | Favicon: emblema rojo del IMF sobre fondo transparente. |
| `apple-touch-icon.png`, `icon-192.png`, `icon-512.png` | Sello completo para iOS, Android e instalación. |
| `site.webmanifest` | Nombre e íconos al agregar el sitio a la pantalla de inicio. |
| `og-image.png` | Imagen 1200×630 que se ve al compartir el enlace. |
| `robots.txt`, `sitemap.xml` | Indexación en buscadores. |
| `assets/logo-imf-sello.jpg` | Original del sello, para regenerar los íconos. |

## SEO

- Título, descripción, URL canónica, Open Graph, Twitter Card y datos estructurados (JSON-LD) están en el `<head>` de `index.html`.
- Si cambias el dominio, actualiza `index.html` (canonical, `og:url`, `og:image`, JSON-LD), `robots.txt`, `sitemap.xml` y `CNAME`.
- Las secciones Tutor y Referencias son vistas dentro de la misma página (`#tutor`, `#referencias`), no URL separadas.

## Notas

- El chat del tutor con IA solo funciona dentro de Claude (usa una función de ese entorno). En el sitio público se muestra la ruta de aprendizaje y un aviso.
- Huesos y músculos: BodyParts3D, © DBCLS, CC BY-SA 2.1 Japón. Mantener la atribución.
