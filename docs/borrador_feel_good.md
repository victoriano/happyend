# Módulo C (borrador 0.2, en piloto): ¿es una película *feel good*?

**Estado:** borrador para validar con el usuario sobre 10 películas. No está congelado: puede cambiar tras el piloto.

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
