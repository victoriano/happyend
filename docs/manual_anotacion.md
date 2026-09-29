# Manual de anotación de finales y optimismo

**Versión 1.0 (congelada el 2026-09-29 tras el piloto; válida para la muestra principal).** Las versiones y cambios se registran al final del documento y en `docs/registro_decisiones.md`. La versión que se congele tras el piloto es la única válida para la muestra principal.

## 0. Qué se anota y con qué información

Cada unidad es **una sinopsis argumental en inglés** (sección *Plot* de Wikipedia) con el título y los años sustituidos por `[TÍTULO]` y `[AÑO]`. La persona o sistema que anota **no ve** título, año, década, popularidad, votos ni puntuación. Si reconoce la película, debe anotar **lo que dice la sinopsis**, no lo que recuerda de la película, y marcar `reconocida = true`.

Principios generales:

1. **Se anota el texto, no la película.** Si la sinopsis no describe el final, el final es `NO_CLASIFICABLE`, aunque la persona conozca la película.
2. **Las dimensiones son independientes.** Una película puede tener final trágico y visión esperanzadora (el protagonista muere pero su sacrificio salva a otros y el cierre mira al futuro), o final feliz y visión cínica (el protagonista gana gracias a un engaño en un mundo presentado como corrupto e inmutable). No hay que forzar coherencia entre dimensiones.
3. **Se evalúa el cierre tal como la narración lo presenta**: desde la perspectiva de los protagonistas y del encuadre moral del relato, no según las preferencias de quien anota.
4. **Ante la duda entre dos categorías adyacentes**, aplicar la regla específica de la sección correspondiente; si no la hay, elegir la más próxima al centro (`AGRIDULCE` o `AMBIGUO` antes que los extremos) y bajar `confianza` a 1.

Protagonista = el personaje o grupo cuyo objetivo organiza la trama. En historias corales, los 2-4 personajes con más peso en la sinopsis.

---

## 1. Resultado del argumento (`final`)

| Código | Definición operativa |
|---|---|
| `FELIZ` | El conflicto central se resuelve de forma favorable para los protagonistas y el cierre se presenta como satisfactorio. Puede haber pérdidas, pero secundarias o compensadas y no dominan el final. |
| `AGRIDULCE` | El cierre combina **una ganancia y una pérdida importantes a la vez**, ambas subrayadas por la narración: se logra el objetivo pero muere un personaje central querido; la pareja se separa pero ambos han crecido; se sobrevive a un precio alto que el texto enfatiza. |
| `AMBIGUO` | La propia obra deja **deliberadamente abierto** el resultado o su valoración: no se sabe si el protagonista sobrevive, si lo vivido fue real, o el texto presenta el desenlace como moralmente indeterminado. |
| `TRAGICO` | El desenlace es predominantemente negativo para los protagonistas: muerte, derrota, fracaso del objetivo central, pérdida irreparable o triunfo del antagonista, **sin compensación sustantiva** en el cierre. |
| `NO_CLASIFICABLE` | La sinopsis no llega al final, lo omite o es tan escueta que no permite decidir. |

**Reglas para casos difíciles**

* *AMBIGUO frente a NO_CLASIFICABLE*: `AMBIGUO` describe la película (el texto dice que el final queda abierto); `NO_CLASIFICABLE` describe la sinopsis (no informa).
* *Terror*: si la superviviente derrota a la amenaza y el cierre es de alivio → `FELIZ` aunque hayan muerto secundarios. Si la sinopsis subraya las muertes de personajes centrales o el trauma → `AGRIDULCE`. Si el mal regresa en la última escena: `AMBIGUO` si el destino de los protagonistas queda abierto; `TRAGICO` si les alcanza.
* *Protagonista antiheroico o criminal*: se valora el resultado **para el protagonista** según el encuadre del relato. Una historia de ascenso y caída que termina con su muerte o ruina es `TRAGICO` aunque el castigo se presente como justo (eso se recoge en `justicia_narrativa`).
* *Sacrificio*: si el protagonista muere para lograr el objetivo y el cierre celebra lo conseguido → `AGRIDULCE`. Solo `FELIZ` si la muerte es secundaria para la narración (p. ej., mentor que muere a mitad de la película).
* *Romance sin pareja final*: si los dos terminan mejor pero separados y la narración lo presenta como correcto → `AGRIDULCE`; si terminan juntos → `FELIZ`; si la ruptura es dolorosa y sin crecimiento → `TRAGICO`.
* *Epílogos*: si hay un salto temporal final, cuenta el estado que muestra el epílogo.
* *Giros finales*: cuenta la situación tras el último giro.
* *[v1.0] Escenas poscréditos, avances de secuela y «el mal regresa» en un epílogo*: se ignoran para `final` y `tono_cierre` **si no cambian el destino de los protagonistas** (p. ej., el villano sigue vivo en otro lugar). Si amenazan directamente a los protagonistas → `AMBIGUO`.
* *[v1.0] Finales alternativos*: si la sinopsis describe varios finales (versión de estreno y alternativos), se anota el que presenta como final de la versión estrenada; si no lo indica, el primero descrito.
* *[v1.0] Dos protagonistas de peso similar y uno muere*: si el otro logra el objetivo → `AGRIDULCE`; `TRAGICO` solo si el superviviente también fracasa o el cierre es de pérdida sin compensación.
* *[v1.0] Muerte de aliados secundarios* (compañeros, mentores) sin que el cierre la subraye: no rebaja el final (`FELIZ` si lo demás es favorable). Si el cierre se centra en el duelo → `AGRIDULCE`.
* *[v1.0] Historias sin conflicto central* (crónicas vitales, retratos): se compara el estado final del protagonista con el inicial. Claramente mejor → `FELIZ`; mezcla de ganancias y pérdidas → `AGRIDULCE`; peor → `TRAGICO`. `objetivo` = `NO_CLARO`.
* *[v1.0] Sinopsis confusa que sí describe la escena final*: `describe_final = true`; `AMBIGUO` solo si la obra deja el desenlace abierto, no porque la sinopsis esté mal escrita. Si falta el desenlace → `NO_CLASIFICABLE` y `describe_final = false`.

**Ejemplos ilustrativos** (descritos en abstracto; no son etiquetas de la muestra):

* Un grupo derrota a una invasión, el héroe regresa con su familia → `FELIZ`.
* El capitán hunde el barco enemigo pero muere su mejor amigo, y el epílogo es un funeral → `AGRIDULCE`.
* La protagonista despierta sin que quede claro si todo fue un sueño; el texto lo deja abierto → `AMBIGUO`.
* El protagonista es condenado injustamente y muere en prisión → `TRAGICO`.

---

## 2. Resultado para los protagonistas

| Campo | Códigos | Regla |
|---|---|---|
| `supervivencia` | `SOBREVIVE`, `MUERE`, `MIXTO`, `NO_CLARO` | `MIXTO` solo con varios protagonistas de los que unos mueren y otros no; la muerte de aliados secundarios no cuenta. [v1.0] Transformación irreversible (poseído, convertido en monstruo) = `MUERE`; encarcelado = `SOBREVIVE`. |
| `objetivo` | `LOGRADO`, `PARCIAL`, `NO_LOGRADO`, `NO_CLARO` | Objetivo central tal como lo plantea la trama. Si el protagonista cambia de objetivo, cuenta el objetivo final. [v1.0] Sin objetivo central identificable → `NO_CLARO`. |
| `relaciones` | `FORTALECIDAS`, `MIXTAS`, `ROTAS`, `NO_APLICA`, `NO_CLARO` | Estado de los vínculos principales (pareja, familia, amistad) al cierre respecto al inicio. |
| `justicia_narrativa` | `SI`, `PARCIAL`, `NO`, `NO_APLICA`, `NO_CLARO` | `SI`: quien causa daño sufre consecuencias y quien obra bien no es castigado. `NO`: el daño queda impune o los inocentes pagan. |

---

## 3. Tono emocional del cierre (`tono_cierre`)

Emoción dominante de la **última parte de la sinopsis** (aprox. el último párrafo o las últimas escenas descritas).

| Código | Definición | Valencia |
|---|---|---|
| `ESPERANZA` | Mirada hacia adelante: nuevos comienzos, promesa, posibilidad. | positiva |
| `ALIVIO` | Peligro superado, vuelta a la normalidad; énfasis en que lo malo terminó. | positiva |
| `CONEXION` | Reencuentro, reconciliación, comunidad, amor; énfasis en los vínculos. | positiva |
| `RESIGNACION` | Aceptación de una pérdida o de un orden que no cambia; calma melancólica. | negativa |
| `DESESPERANZA` | Desolación, amenaza persistente, pérdida sin consuelo. | negativa |
| `NO_CLARO` | La sinopsis no permite identificar el tono del cierre. | — |

**[v1.0] Procedimiento de decisión** (el piloto mostró poco acuerdo en esta dimensión):

1. Identifica la última escena que afecta a la historia principal de los protagonistas (se ignoran avances de secuela y poscréditos, como en la sección 1).
2. Decide primero la **valencia**: ¿el cierre invita a sentir algo positivo o negativo? Si no se puede decidir → `NO_CLARO`.
3. Si es positiva: `CONEXION` si la escena se centra en una relación (reencuentro, beso, familia reunida, reconciliación); si no, `ESPERANZA` si mira explícitamente al futuro (planes, nuevo comienzo, viaje); si no, `ALIVIO` (amenaza superada, vuelta a la normalidad).
4. Si es negativa: `DESESPERANZA` si hay amenaza persistente, muerte o pérdida sin consuelo, o vacío; `RESIGNACION` si hay aceptación serena de una pérdida o de un orden que no cambia.

El análisis principal usa la **valencia** (positiva/negativa); la subcategoría es secundaria.

---

## 4. Visión general de la vida

Cuatro ítems en escala de −2 a +2 (o `null` si el texto no permite juzgarlo). Se valora **la película entera tal como la resume la sinopsis**, no solo el final.

| Ítem | −2 | 0 | +2 |
|---|---|---|---|
| `agencia` | Los personajes son impotentes ante el destino, el sistema o el azar; sus decisiones no cambian nada. | Mixto o neutro. | Las decisiones y el esfuerzo de los personajes determinan el resultado. |
| `cambio` | Las personas y el mundo no mejoran, o empeoran; los ciclos se repiten. | Mixto o neutro. | Las personas pueden cambiar a mejor y el mundo puede mejorar. |
| `vinculos` | Las relaciones son fuente de traición, soledad o daño. | Mixto o neutro. | Las relaciones son fuente de sentido, apoyo o salvación. |
| `futuro` | El cierre proyecta un futuro sombrío o amenazante. | Neutro o no proyecta futuro. | El cierre proyecta un futuro prometedor. |

`vision_vida` = media de los ítems no nulos, exigiendo al menos 3 de 4 (se calcula en el análisis, no se anota).

---

## 5. Arco emocional

No se anota a partir de sinopsis. Requiere guion o subtítulos con procedencia y permisos adecuados; en la versión actual **no se ha podido obtener ningún corpus así con licencia verificable** (ver registro de decisiones D-009). El campo queda fuera de la anotación.

---

## 6. Campos de control

* `describe_final` (`true`/`false`): ¿la sinopsis describe el desenlace?
* `reconocida` (`true`/`false`): ¿se reconoció la película pese al cegado?
* `confianza`: 1 (baja), 2 (media), 3 (alta) sobre `final`.
* `nota`: justificación breve en español, **parafraseada**, máximo 30 palabras. No copiar frases de la sinopsis.

## 7. Formato de salida

Una línea JSON por película:

```json
{"id": "F1A2B3C4D", "final": "AGRIDULCE", "supervivencia": "SOBREVIVE", "objetivo": "LOGRADO",
 "relaciones": "ROTAS", "justicia_narrativa": "SI", "tono_cierre": "RESIGNACION",
 "agencia": 1, "cambio": 0, "vinculos": -1, "futuro": 0,
 "describe_final": true, "reconocida": false, "confianza": 2,
 "nota": "Logra el objetivo pero pierde a su pareja; cierre melancólico."}
```

## 8. Adjudicación

* Dos anotaciones independientes por película.
* Para variables categóricas, si coinciden se acepta el valor. Si no, una tercera anotación (adjudicador) ve la sinopsis y las dos etiquetas con sus notas, sin saber qué anotador es cuál, y elige una de las dos o, justificándolo, una tercera.
* Para los ítems de −2 a +2 se usa la media de los dos anotadores; si difieren en 3 o más puntos, decide el adjudicador.

## Historial de versiones

* 0.9 (2026-09-29): borrador inicial para el piloto.
* 1.0 (2026-09-29): congelada tras el piloto de 50 películas. Cambios (marcados [v1.0]): reglas para poscréditos y avances de secuela, finales alternativos, dos protagonistas, muerte de aliados, historias sin conflicto central, sinopsis confusas, transformación irreversible en `supervivencia`, `objetivo` sin meta central y procedimiento de decisión para `tono_cierre` (kappa del piloto = 0,49). No se cambió ninguna definición de categoría de `final`.

---

# Módulo B (v2): protagonistas, contexto y ánimo

**Versión 2.0-borrador.** Se añade en la versión 2 del estudio. Las secciones 1 a 8 anteriores (versión 1.0) **no cambian**. El módulo B se anota para todas las películas; para las 994 del estudio v1 se anota solo este módulo.

Las sinopsis pueden estar en inglés o en español; se anotan igual. Como los años están enmascarados, la época se deduce de pistas del texto (guerras, tecnología, acontecimientos). Si no hay pistas, `NO_CLARO`.

## B1. Protagonista (quien organiza la trama; si es coral, el grupo)

| Campo | Códigos | Regla |
|---|---|---|
| `genero_protagonista` | `HOMBRE`, `MUJER`, `MIXTO`, `NO_HUMANO`, `NO_CLARO` | `MIXTO` si el protagonismo es compartido entre hombres y mujeres; `NO_HUMANO` para animales, robots o criaturas sin género humano claro. |
| `edad_protagonista` | `NINO` (<13), `ADOLESCENTE` (13-17), `JOVEN` (18-29), `ADULTO` (30-49), `MADURO` (50-64), `MAYOR` (65+), `MIXTO`, `NO_CLARO` | Edad aparente al empezar la historia. Si la sinopsis no la da, dedúcela del contexto (estudia en el instituto → `ADOLESCENTE`; tiene hijos adolescentes → `ADULTO`). |
| `momento_vital` | `INFANCIA`, `ADOLESCENCIA`, `JUVENTUD`, `CRIANZA`, `MADUREZ`, `CRISIS_VITAL`, `VEJEZ`, `NO_CLARO` | `JUVENTUD`: estudios, primer trabajo, independizarse, primeras relaciones serias. `CRIANZA`: formar familia o criar hijos pequeños. `MADUREZ`: vida adulta asentada (carrera, familia estable). `CRISIS_VITAL`: una ruptura o pérdida que obliga a redefinir la vida adulta (divorcio, duelo, despido, enfermedad). `VEJEZ`: jubilación, final de la vida. |
| `estado_civil` | `SOLTERO`, `EN_PAREJA`, `CASADO`, `SEPARADO_DIVORCIADO`, `VIUDO`, `NO_CLARO` | Situación al **inicio** de la película. |
| `clase_social` | `BAJA_MARGINAL`, `TRABAJADORA`, `MEDIA`, `ALTA_ELITE`, `MIXTA`, `NO_CLARO` | Por ocupación, vivienda y recursos. Policías, soldados, profesores → normalmente `TRABAJADORA` o `MEDIA` según el texto; empresarios ricos, aristócratas, estrellas → `ALTA_ELITE`. `MIXTA` si la historia gira sobre protagonistas de clases distintas (p. ej., un romance entre clases). |

## B2. Relaciones y contexto

| Campo | Códigos | Regla |
|---|---|---|
| `relaciones_centrales` | lista de 1 a 3 entre `AMISTAD`, `ROMANCE`, `MATRIMONIO`, `DIVORCIO_SEPARACION`, `PADRES_HIJOS`, `HERMANOS`, `FAMILIA_EXTENSA`, `MENTOR_DISCIPULO`, `EQUIPO_COMPANEROS`, `RIVALIDAD`, `COMUNIDAD`; o `["NINGUNA"]` | Solo las relaciones que la trama desarrolla de verdad, ordenadas por importancia. `ROMANCE` = relación amorosa que se forma o se disputa; `MATRIMONIO` = pareja ya casada cuya relación es un tema. |
| `especulativa` | `NO`, `CIENCIA_FICCION`, `FANTASIA`, `SOBRENATURAL`, `SUPERHEROES` | Elemento especulativo principal. `SOBRENATURAL`: fantasmas, demonios, maldiciones en un mundo por lo demás real. `SUPERHEROES`: personajes con superpoderes en clave de cómic. |
| `epoca_trama` | `ANTES_1500`, `DE_1500_A_1899`, `DE_1900_A_1945`, `DE_1946_A_1979`, `DE_1980_EN_ADELANTE`, `FUTURO`, `MUNDO_FICTICIO`, `VARIAS`, `NO_CLARO` | Época principal de la acción. Una historia actual sin marcas de época (móviles, internet, ciudad moderna) es `DE_1980_EN_ADELANTE`. `MUNDO_FICTICIO`: mundos inventados sin correspondencia histórica (Tierra Media, galaxias lejanas…). |
| `paises_trama` | lista de países en español (`"Estados Unidos"`, `"España"`, `"Francia"`…) o `["Espacio"]`, `["Mundo ficticio"]`, `["No claro"]` | Países donde transcurre la acción principal, máximo 4, por orden de importancia. |
| `humor` | `NINGUNO`, `ALGO`, `CENTRAL` | Peso del humor en la película según la sinopsis. |

## B3. Ánimo (más allá del final)

Dos escalas de −2 a +2 (o `null` si no se puede juzgar), **independientes del tipo de final**:

| Ítem | −2 | 0 | +2 |
|---|---|---|---|
| `tono_general` | La película es sombría de principio a fin: violencia, desolación, crueldad dominan. | Mezcla de luz y oscuridad. | Luminosa, cálida o festiva en su mayor parte. |
| `optimismo_personajes` | Los protagonistas son cínicos, derrotistas, desesperados o amargados. | Mixto o neutro. | Los protagonistas son vitalistas, esperanzados, confían en la vida y en los demás, aunque sufran. |

**Ejemplo guía** (descrito en abstracto): un romance a bordo de un barco que se hunde, en el que la pareja vive con intensidad, se anima a romper convenciones y ella recuerda la experiencia como liberadora, tiene `final` = `TRAGICO` o `AGRIDULCE`, pero `optimismo_personajes` = `+2` y `tono_general` probablemente `0` o `+1`. Un thriller en el que un detective cansado y cínico persigue a un asesino en una ciudad podrida tiene `optimismo_personajes` = `−2` aunque atrape al asesino.

## B4. Formato de salida

Anotación completa (películas nuevas): una línea JSON con **todos** los campos de la sección 7 **más** los del módulo B. Solo módulo B (películas del estudio v1): `id` + campos del módulo B + `reconocida` + `confianza_b` (1-3, confianza global del módulo B).

```json
{"id":"F1A2B3C4D", "genero_protagonista":"HOMBRE", "edad_protagonista":"ADULTO", "momento_vital":"CRISIS_VITAL",
 "estado_civil":"SEPARADO_DIVORCIADO", "clase_social":"TRABAJADORA", "relaciones_centrales":["PADRES_HIJOS","AMISTAD"],
 "especulativa":"NO", "epoca_trama":"DE_1980_EN_ADELANTE", "paises_trama":["Estados Unidos"], "humor":"ALGO",
 "tono_general":0, "optimismo_personajes":1, "confianza_b":2}
```

## B5. Adjudicación del módulo B

Igual que en la sección 8: los campos de elección única en desacuerdo y los ítems con 3 o más puntos de diferencia pasan al adjudicador. En las listas (`relaciones_centrales`, `paises_trama`) no se adjudica: el análisis usa las marcadas por ambos anotadores y, como sensibilidad, las marcadas por al menos uno.
