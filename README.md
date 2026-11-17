# Nadia Fitness Dance Studio — propuesta v4

La v4 reúne lo aprendido en las tres versiones anteriores ([v1](https://negimaru.github.io/nadia-fitness/) · [v2](https://negimaru.github.io/nadia-fitness-alt/) · [v3](https://negimaru.github.io/nadia-fitness-v3/)). Cada regla de diseño de [`DESIGN.md`](DESIGN.md) lleva al lado el motivo por el que existe.

## Qué toma de cada versión

| De | Qué |
|---|---|
| **v2** (la mejor valorada) | Dirección de «programa»: papel y tinta, secciones numeradas, listas con líneas y el panel «Hoy en el estudio» |
| **v1** | La energía de la marca: el rosa del logo en un bloque grande (el teléfono), la cursiva como acento, fotos en color y la tipografía condensada deportiva |
| **v3** | Páginas generadas de antemano con un script desde un solo archivo de datos: HTML estático completo sin JavaScript y sin necesidad de Chromium |
| **Feedback y auditorías** | Sin brillos ni etiquetas sobre los títulos, fotos en color, sin menores, interlíneas para las tildes, accesibilidad WCAG 2.2 AA, aviso de llamadas, horario imprimible, pestañas por día, 404 útil y «Volver» en los textos legales |

## Cómo se edita

Todo el contenido que se repite o cambia está en **`data/site.json`**: clases, horario, teléfono, WhatsApp, dirección, horario de llamadas, valoración, redes, curso, datos de la titular y fotos. Después de editarlo:

```
python3 tools/build.py
```

El script regenera todas las páginas, el sitemap, el manifest, la imagen para compartir el Horario y las imágenes de muestra de las clases (necesita Pillow). El HTML generado no se edita a mano.

```
data/site.json        Contenido (única fuente)
tools/build.py        Plantillas y generación
assets/css/site.css   Estilos (solo los tokens de DESIGN.md)
assets/js/site.js     Extras opcionales: tema, menú, filtros, pestañas, «Hoy», aviso de llamadas, formulario
```

**Fotos de clases:** sustituye `assets/img/clases/<id>.webp` por la foto real (horizontal, ~1200×750), pon `"placeholder": false` y un `photoAlt` en esa clase de `site.json`, y regenera.

## Comprobado

- **axe-core 4.10:** 0 infracciones en las 8 páginas, en escritorio y móvil, modo claro y oscuro.
- **Móvil:** sin scroll horizontal a 320 px y ningún elemento con foco tapado por las barras fijas (0 de 73).
- **Funcionamiento:** formulario y enlaces que abren otra pestaña revisados.
- **Sin JavaScript:** funciona completa.
- **Impresión:** el horario cabe en un folio A4.

Lleva `noindex` mientras sea una propuesta: hay que quitar esa línea en `tools/build.py` cuando sustituya a la web actual.
