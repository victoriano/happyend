# Scripts puntuales

- `rebatch_d017.py`: reorganización única de lotes tras corregir la extracción de sinopsis (registro D-017).
  Conserva las etiquetas de los lotes 01-10 cuyo texto no cambió, aparta las obsoletas en
  `annotation/labels/principal_obsoletas/` y reparte las películas pendientes en los lotes 11-20.
  Ya se ejecutó una vez; no hace falta volver a ejecutarlo para reproducir el análisis.
