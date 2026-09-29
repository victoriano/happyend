# Instrucciones para anotadores, versión 2

Igual que `docs/instrucciones_anotador.md`, con dos diferencias:

1. **Modo completo** (lotes `v2piloto_*` y `v2_completa_*`): cada línea de salida lleva todos los campos de la sección 7 del manual **más** los del módulo B (sección B4). Las sinopsis pueden estar en inglés o en español.
2. **Modo solo módulo B** (lotes `v2_modb_*`): cada línea lleva `id`, los campos del módulo B, `reconocida` y `confianza_b`.

Lee el manual completo (`docs/manual_anotacion.md`), incluido el módulo B. Abre solo tu lote. No abras otros ficheros del repositorio ni busques información externa. Anota solo lo que dice el texto.

Validación (modo completo):
`python3 -c "from finales import annotation as an; from pathlib import Path; df,e=an.load_labels_b([Path('SALIDA')],'X',True); print(len(df), e)"`
Validación (solo módulo B): lo mismo con `False` en lugar de `True`.
