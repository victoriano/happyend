# Web divulgativa: happyend.victoriano.me

Página estática (sin build): `index.html` + `data.json` (generado con `make web`). Solo contiene agregados y, para las 750 películas del marco popular, título de Wikipedia, año, cohorte, género principal y la etiqueta de final. No incluye datos de IMDb.

Vista local: `cd web && python3 -m http.server 8000`

Despliegue en Vercel desde esta carpeta: `npx vercel --prod` (proyecto `happyend`), después añadir el dominio `happyend.victoriano.me` al proyecto y, en Cloudflare, un registro CNAME `happyend` → `cname.vercel-dns.com` (solo DNS, sin proxy).
