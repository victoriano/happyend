# Manual de anotación de finales y optimismo

**Versión 0.9 (borrador para piloto).** Las versiones y cambios se registran al final del documento y en `docs/registro_decisiones.md`. La versión que se congele tras el piloto es la única válida para la muestra principal.

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

**Ejemplos ilustrativos** (descritos en abstracto; no son etiquetas de la muestra):

* Un grupo derrota a una invasión, el héroe regresa con su familia → `FELIZ`.
* El capitán hunde el barco enemigo pero muere su mejor amigo, y el epílogo es un funeral → `AGRIDULCE`.
* La protagonista despierta sin que quede claro si todo fue un sueño; el texto lo deja abierto → `AMBIGUO`.
* El protagonista es condenado injustamente y muere en prisión → `TRAGICO`.

---

## 2. Resultado para los protagonistas

| Campo | Códigos | Regla |
|---|---|---|
| `supervivencia` | `SOBREVIVE`, `MUERE`, `MIXTO`, `NO_CLARO` | `MIXTO` solo con varios protagonistas de los que unos mueren y otros no. |
| `objetivo` | `LOGRADO`, `PARCIAL`, `NO_LOGRADO`, `NO_CLARO` | Objetivo central tal como lo plantea la trama. Si el protagonista cambia de objetivo, cuenta el objetivo final. |
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

Si concurren dos, elegir la que ocupa la **última frase o escena**. Esperanza frente a alivio: ¿mira hacia el futuro (esperanza) o hacia lo que se deja atrás (alivio)?

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
