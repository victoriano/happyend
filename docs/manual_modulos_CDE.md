# Manual de anotación, módulos C, D y E (versión 1.0, congelada): *feel good*, utopía y público

**Estado:** congelado el 2026-09-30 tras dos pilotos con las 10 películas más votadas (borradores 0.1 a 0.4, en `docs/borrador_feel_good.md`). No se modifica durante la anotación.

## C1. Pregunta central

¿La película, tomada en conjunto y sobre todo por cómo termina, nos deja con la idea de que **los personajes acaban en paz, armonía y amor** con sus familias, amigos, seres queridos, su comunidad, su país o el universo, y de que **hay esperanza en la humanidad**?

## C2. Reglas

1. **No es lo mismo que el final feliz.**
   - Una película con muertes o pérdidas puede ser *feel good* si deja reconciliación, amor y esperanza. Un sacrificio que salva a otros y tiene sentido es compatible con *feel good*.
   - Un final «feliz» para el protagonista puede no serlo si lo deja solo o corrompido, si el mal queda impune o si el mundo queda cínico.
2. **Se juzga la película entera, con más peso en el cierre**: el estado final de los vínculos y del mundo, y el tono con el que la narración lo presenta.
3. **Los vínculos cuentan tanto como los objetivos.** La pregunta no es si el protagonista gana, sino cómo quedan él y los suyos: reunidos, reconciliados y queridos, o aislados, rotos y traicionados.
4. **La esperanza puede ser colectiva**: la humanidad sobrevive o mejora, la comunidad se une, alguien hace el bien sin esperar nada.
5. **Se anota el texto, no la película.** Si la sinopsis no permite juzgar el cierre, `feel_good = null`.

### Señales a favor

Reconciliación. Familia, amistad o pareja restauradas o reforzadas. Comunidad unida. Bondad, lealtad o sacrificio con sentido. Crecimiento personal. Justicia o reparación. Mirada esperanzada al futuro. Humor cálido.

### Señales en contra

Aislamiento o soledad final. Traición. Vínculos rotos sin reparar. Mal impune. Cinismo o nihilismo. Destrucción sin sentido. Protagonista corrompido. Final abierto inquietante o amenazante. Mundo peor que al principio.

## C3. Nota `feel_good` (0 a 10, como una nota)

Pon una nota entera de 0 a 10. Usa estos anclajes y los números intermedios cuando la película quede entre dos:

| Nota | Significado | Patrón |
|---|---|---|
| **10** | Muy *feel good* | Todos los vínculos importantes quedan en paz y amor; el cierre irradia esperanza sin sombras relevantes. |
| **7-8** | Bastante *feel good* | Hay pérdidas o dolor, pero el balance final es de armonía, amor y esperanza. |
| **5** | A medias | Luces y sombras equilibradas, o cierre deliberadamente ambiguo. |
| **2-3** | Poco *feel good* | Algo de consuelo, pero predominan la soledad, la pérdida o la inquietud. |
| **0** | Nada *feel good* | Desesperanza, cinismo, vínculos destruidos o el mal triunfa. |
| `null` | No clasificable | La sinopsis no permite juzgar el cierre. |

Reglas añadidas en 0.2:
* **Sagas y partes**: se juzga la película tal como termina en sí misma, aunque la historia continúe. Un cierre abierto de saga cuenta como sombra (baja la nota), no como motivo para dejarla sin clasificar.
* **Pérdida con sentido**: un sacrificio o una pérdida asumidos con serenidad y amor, que dejan a los demás en paz y con esperanza, pueden llegar a 9-10. Una pérdida que deja dolor abierto o soledad baja la nota a 7-8 o menos.

## C4. Campos de salida (una línea JSON por película)

* `id`
* `feel_good`: entero de 0 a 10, o `null`.
* `feel_good_por_que`: explicación en español de 40 a 70 palabras, parafraseada (sin copiar frases de la sinopsis), que diga qué vínculos quedan en paz o rotos, cómo queda el mundo y si hay esperanza. Puede contener spoilers.
* `confianza_c`: 1 (baja), 2 (media) o 3 (alta).

## D. Utopía o distopía: ¿hacia dónde va la sociedad según la película? (añadido en 0.3)

### D1. Pregunta central

Más allá de los protagonistas, ¿qué imagen transmite la película sobre **la sociedad y hacia dónde va**? ¿Las instituciones, la comunidad y la gente en general tienden a mejorar, a cuidarse y a resolver sus problemas (utopía), o a degradarse, oprimir, corromperse o destruirse (distopía)?

Se anota **en todas las películas, sean o no de ciencia ficción**. Una comedia romántica en una ciudad amable transmite una sociedad funcional; un thriller sobre policías corruptos transmite una sociedad podrida, aunque pase en el presente.

### D2. Reglas

1. **No es lo mismo que el *feel good*.** Una historia íntima puede acabar muy bien para sus personajes en una sociedad cruel, y al revés: puede haber tragedia personal en una sociedad sana.
2. **Se mira la sociedad que muestra la película y su trayectoria al final:** instituciones (justicia, policía, gobierno, empresas, ciencia), comunidad, solidaridad entre desconocidos y la relación con la naturaleza o la tecnología. Si al final la sociedad mejora (se libera, se reforma, se une), la nota sube; si empeora o se revela podrida sin remedio, baja.
3. **Si la película apenas muestra la sociedad** (un drama de cámara, una historia en un lugar aislado), la nota es 5 salvo que haya indicios claros, y se indica en la explicación.

### D3. Nota `utopia` (0 a 10)

| Nota | Significado | Patrón |
|---|---|---|
| **10** | Utopía | La sociedad es justa, solidaria y va a mejor; las instituciones funcionan y protegen. |
| **7-8** | Sociedad sana con problemas | Hay injusticias o amenazas, pero la sociedad reacciona, se corrige o se une. |
| **5** | Neutral o no se muestra | Sociedad corriente, sin juicio claro, o la película apenas la muestra. |
| **2-3** | Sociedad enferma | Corrupción, desigualdad, violencia o deshumanización extendidas, con poca salida. |
| **0** | Distopía | La sociedad oprime, se destruye o ha colapsado, y va a peor. |
| `null` | No clasificable | La sinopsis no permite juzgarlo. |

### D4. Campos de salida

* `utopia`: entero de 0 a 10, o `null`.
* `utopia_por_que`: explicación en español de 25 a 50 palabras, parafraseada, sobre qué sociedad muestra la película y hacia dónde va.

## E. ¿Para qué público es? (añadido en 0.4)

`publico`: una de estas categorías, según a quién se dirige principalmente la película por su historia, tono y contenido (no por su clasificación por edades oficial, que no se ve):

* `INFANTIL`: pensada sobre todo para niños (hasta unos 12 años): protagonistas infantiles o animales, conflictos sencillos, sin violencia ni sexo explícitos.
* `FAMILIAR`: pensada para verse en familia, para niños y adultos a la vez (muchas películas de animación y de aventuras «para todos los públicos»).
* `JUVENIL`: dirigida sobre todo a adolescentes (comedias de instituto, sagas juveniles).
* `ADULTO`: dirigida a adultos (violencia, sexo, temas o tratamiento adultos), aunque la puedan ver adolescentes.

Se comprueba con los géneros de IMDb (*Family*, *Animation*) como control, sin sustituir la anotación.

## F. Salida (una línea JSON por película, en el mismo orden del lote)

Campos: `id`, `feel_good`, `feel_good_por_que`, `confianza_c`, `utopia`, `utopia_por_que`, `publico`.

Ejemplo:
`{"id": "G0123ABCD", "feel_good": 8, "feel_good_por_que": "…", "confianza_c": 3, "utopia": 6, "utopia_por_que": "…", "publico": "FAMILIAR"}`

Si la sinopsis es muy breve (por ejemplo, una sinopsis comercial que no cuenta el final), puedes dar `feel_good` y `utopia` si el texto permite juzgar el tono y la sociedad, con `confianza_c` = 1; si no, `null`. `publico` se da siempre.
