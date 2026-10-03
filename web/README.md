# Web divulgativa: happyend.victoriano.me

Página estática (sin build): `index.html` + `data.json` (generado con `make web`). Solo contiene agregados y, para las 750 películas del marco popular, título de Wikipedia, año, cohorte, género principal y la etiqueta de final. No incluye datos de IMDb.

Vista local: `cd web && python3 -m http.server 8000`

Despliegue en Vercel desde esta carpeta: `npx vercel --prod` (proyecto `happyend`), después añadir el dominio `happyend.victoriano.me` al proyecto y, en Cloudflare, un registro CNAME `happyend` → `cname.vercel-dns.com` (solo DNS, sin proxy).

**Estado (2026-09-29):** publicada en https://happyend.victoriano.me (proyecto Vercel `happyend`, equipo victorianos-projects; CNAME `happyend` → `cname.vercel-dns.com` en Cloudflare, solo DNS). Ficheros desplegados verificados por SHA-1 contra esta carpeta.

**Datos descargables:** `datos/happyend.csv` y `datos/happyend.parquet` (una fila por título, etiquetas decodificadas de `films.json`; se regeneran con `make web` o `python -c "from finales import web; web.main_dataset()"`). Enlazados en el pie de la web.
