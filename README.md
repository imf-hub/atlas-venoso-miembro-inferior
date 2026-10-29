# Anatomía venosa del miembro inferior

Modelo interactivo 3D de la anatomía venosa del miembro inferior del Instituto Mexicano de Flebología (IMF): modelo 3D, ficha por estructura, simulador de ecografía en modo B, evaluación y ruta de aprendizaje.

Sitio en producción: https://anatomia.flebologiamexico.com (GitHub Pages, rama `main`).

## Archivos

| Archivo | Para qué sirve |
|---|---|
| `index.html` | Toda la herramienta en un solo archivo (HTML, CSS, JS y datos del modelo). No hay build. |
| `anatomia-venosa-miembros-inferiores/index.html` | Guía de anatomía y nomenclatura: historia, tabla bilingüe de 79 entradas, siglas del consenso 2023, anatomía regional y 27 fichas. El texto se sirve en HTML; JavaScript mejora la búsqueda y navegación. Es la página pensada para buscadores; enlaza al modelo 3D y al IMF. Se genera con `tools/generar-paginas.py`. |
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
- Las secciones Aprender y Referencias son vistas dentro de la misma página (`#aprender`, `#referencias`), no URL separadas.

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

Aparecen en la barra lateral y el pie de página de la herramienta, en la guía, en el resultado de la evaluación y en los datos estructurados (JSON-LD).

## Enlace directo a una vena

`https://anatomia.flebologiamexico.com/#v-vsm` abre el modelo 3D con esa vena seleccionada (usa el id de la vena: vsm, vfc, etc.).

## Notas

- «Aprender» es una ruta de lectura de 8 módulos (datos en `ROUTE` dentro de `index.html`). No hay chat con IA ni se guarda el avance de nadie.
- Huesos y músculos: BodyParts3D, © DBCLS, CC BY-SA 2.1 Japón. Mantener la atribución.



## Nomenclatura bilingüe y guía ampliada

- `index.html` mantiene el catálogo único del modelo y las fichas: `n` (español), `en` (inglés), `alt` (otros términos e históricos), `ab` (sigla visible), `abSource` y `abNote` (fuente y alcance). No modificar los id del modelo al cambiar un nombre.
- La tabla VI de Bottini 2023 es la referencia de siglas superficiales y perforantes: GSV, SSV, AAGSV, PV, IV, etc. CEAP 2020 se identifica para otros ejes. Las siglas inglesas editoriales se rotulan como tales. AAGSV (2023) y ASV (2024) se explican con sus fuentes.
- `tools/guia-fuentes.json` conserva la síntesis anatómica, la tabla comparativa y 22 referencias verificadas del documento ampliado.
- `tools/guia_anatomica.py` compone la guía con HTML accesible, buscador progresivo, filtros, navegación y estilos adaptables.
- Ejecutar `python tools/generar-paginas.py` después de editar el catálogo, la guía o sus fuentes y publicar también los archivos generados.
- Se conservan las direcciones anteriores de las safenas; el arco plantar conserva su URL aunque el rótulo precisa su profundidad.

## Aprender y evaluación

- `tools/aprendizaje.json` mantiene los ocho módulos y el banco de preguntas de nomenclatura con explicación, referencias, sistemas relacionados y módulo de repaso.
- Las 17 equivalencias de la tabla VI se comparten con la guía desde `mapping2023` en `tools/guia-fuentes.json`.
- `tools/actualizar_aprendizaje.py` sincroniza estos datos en `index.html`; también se ejecuta al generar páginas.
- La evaluación ofrece rondas mixtas de reconocimiento y nomenclatura, o solo nomenclatura. Filtra por sistemas activos, explica respuestas correctas e incorrectas y enlaza a guía y módulos. El resultado es una práctica sin acreditación.
