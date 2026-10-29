# Atlas venoso del miembro inferior

Atlas interactivo 3D de anatomía venosa del miembro inferior del Instituto Mexicano de Flebología (IMF): modelo 3D, ficha por estructura, simulador de ecografía en modo B, evaluación, tutor y ruta de aprendizaje.

Sitio en producción: https://anatomia.flebologiamexico.com (GitHub Pages, rama `main`).

## Archivos

| Archivo | Para qué sirve |
|---|---|
| `index.html` | Todo el atlas en un solo archivo (HTML, CSS, JS y datos del modelo). No hay build. |
| `anatomia-venosa-miembros-inferiores/index.html` | Guía estática en HTML (sin JavaScript) con el texto de las 27 venas y las referencias. Es la página pensada para buscadores; enlaza al atlas y al IMF. Se genera con `tools/generar-paginas.py`. |
| `venas/<vena>/index.html` | Una página estática por vena (27), con su propia URL, para buscadores. Generadas, no editar a mano. |
| `tools/generar-paginas.py` | Genera la guía, las páginas de vena y `sitemap.xml` a partir de los datos de `index.html` (requiere Python 3 y Node). |
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

## Regenerar las páginas para buscadores

Cada vez que cambies una ficha o una referencia en `index.html`:

```bash
python tools/generar-paginas.py
```

Actualiza la guía, las 27 páginas de vena, `sitemap.xml` y la lista de venas del `<noscript>` de la portada. Después haz commit y push de los archivos generados.

## Enlaces del IMF

- Sitio del IMF: https://flebo.mx/
- Oferta educativa (Aprende flebología en el IMF): https://flebo.mx/oferta-educativa/
- Boletín de noticias flebológicas: https://boletin.flebologiamexico.com/

Aparecen en la barra lateral y el pie de página del atlas, en la guía, en el resultado de la evaluación y en los datos estructurados (JSON-LD).

## Enlace directo a una vena

`https://anatomia.flebologiamexico.com/#v-vsm` abre el atlas con esa vena seleccionada (usa el id de la vena: vsm, vfc, etc.).

## Notas

- El chat del tutor con IA solo funciona dentro de Claude (usa una función de ese entorno). En el sitio público se muestra la ruta de aprendizaje y un aviso.
- Huesos y músculos: BodyParts3D, © DBCLS, CC BY-SA 2.1 Japón. Mantener la atribución.


