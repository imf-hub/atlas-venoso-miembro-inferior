# Anatomía venosa del miembro inferior

Modelo interactivo 3D de la anatomía venosa del miembro inferior del Instituto Mexicano de Flebología (IMF): modelo 3D, ficha por estructura, simulador de ecografía en modo B, evaluación y ruta de aprendizaje.

Sitio en producción: https://anatomia.flebologiamexico.com (GitHub Pages, rama `main`).

## Actualización 2026.10.29-uniones2 · Uniones continuas

El modelo utiliza 143 mallas basadas en Z-Anatomy y complementos del IMF exportadas en cuatro GLB por capa, con 30 fichas seleccionables. Se conservan las 27 fichas originales, las capas, el simulador ecográfico, los ocho módulos de aprendizaje y la evaluación. Los cortes ecográficos se obtienen de las mismas mallas que se ven en 3D. El botón **Cayado** acerca a la unión safenofemoral.

Las siete estructuras complementarias del IMF conservan sus fichas y ahora tienen 15 inserciones con una pared continua: unión booleana, eliminación de paredes internas y suavizado local sin alterar el resto del trayecto. Las normales se comparten entre etiquetas anatómicas para evitar costuras de iluminación. La ecografía enlaza los contornos de los vasos fusionados antes de dibujar el lumen. Las superficies receptoras adaptadas se identifican en sus fichas.

La safena anterior se inserta en un tramo cerrado de la safena mayor y evita un cruce no deseado con la vena femoral. La obturatriz entra lateralmente en un tramo cerrado de la ilíaca interna. Son ajustes del esquema complementario, no una validación clínica ni geometría nativa de Z-Anatomy. Los extremos libres del recorte original se conservan. No se añaden válvulas. El proyecto mantiene su condición de fase beta.

`npm test` comprueba las 30 fichas, los nueve cortes ecográficos de referencia, las 15 conexiones mediante bordes y normales compartidos, contornos ecográficos cerrados en cada unión y los módulos de aprendizaje. `assets/z-anatomy/fusion-report.json` registra las inserciones y la auditoría geométrica. Manifold es una dependencia de preparación, no se carga en el navegador.

Procedencia y licencias: `assets/z-anatomy/metadata.json` y `assets/z-anatomy/CREDITOS.txt`. Z-Anatomy, CC BY-SA 4.0; BodyParts3D, © DBCLS, CC BY-SA 2.1 Japón; adaptaciones y complementos 3D del IMF bajo CC BY-SA 4.0. Three.js se sirve localmente con su licencia MIT.

Para reproducir los modelos: instalar las dependencias con `npm ci`, descargar los cuatro FBX de la carpeta oficial indicada en los créditos y definir `Z_ANATOMY_SOURCE_DIR` con esa carpeta. Ejecutar `npm run prepare:z`, `python tools/integrate-z.py`, `python tools/generar-paginas.py` y `npm test`. Los identificadores Git de los FBX se comprueban antes de exportar. `tools/atlas-base.txt` conserva la versión de partida del atlas para que la integración sea reproducible.

Los FBX completos, capturas, comparaciones de revisión y archivos temporales locales no forman parte del despliegue.

## Archivos

| Archivo | Para qué sirve |
|---|---|
| `index.html` | Interfaz, fichas y lógica de la herramienta. Los modelos 3D se cargan por capas desde assets/z-anatomy/. No hay build para servir la web. |
| `anatomia-venosa-miembros-inferiores/index.html` | Guía de anatomía y nomenclatura: historia, tabla bilingüe de 79 entradas, siglas del consenso 2023, anatomía regional y 30 fichas. El texto se sirve en HTML; JavaScript mejora la búsqueda y navegación. Es la página pensada para buscadores; enlaza al modelo 3D y al IMF. Se genera con `tools/generar-paginas.py`. |
| `venas/<vena>/index.html` | Una página estática por vena (30), con su propia URL, para buscadores. Generadas, no editar a mano. |
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
- Aprender es una vista de la aplicación (`#aprender`). La bibliografía se encuentra únicamente al final de la guía (`/anatomia-venosa-miembros-inferiores/#referencias`); las citas enlazan directamente a cada referencia. Los antiguos enlaces `/#referencias` y `/#ref-N` redirigen a la guía.

## Regenerar las páginas para buscadores

Cada vez que cambies una ficha o una referencia en `index.html`:

```bash
python tools/generar-paginas.py
```

Actualiza la guía, las 30 páginas de vena, `sitemap.xml` y la lista de venas del `<noscript>` de la portada. Después haz commit y push de los archivos generados.

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
