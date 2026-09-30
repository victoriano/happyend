# Módulo C (borrador 0.1, en piloto): ¿es una película *feel good*?

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

## C3. Escala `feel_good` (−2 a +2)

| Valor | Significado | Ejemplo de patrón |
|---|---|---|
| **+2** | Claramente *feel good* | Todos los vínculos importantes quedan en paz y amor; el cierre irradia esperanza. |
| **+1** | Mayormente *feel good*, con sombras | Hay pérdidas o dolor, pero el balance final es de armonía y esperanza. |
| **0** | Ambivalente | Luces y sombras equilibradas, o cierre deliberadamente ambiguo. |
| **−1** | Mayormente no *feel good* | Algo de consuelo, pero predominan la soledad, la pérdida o la inquietud. |
| **−2** | Claramente no *feel good* | Desesperanza, cinismo, vínculos destruidos o el mal triunfa. |
| `null` | No clasificable | La sinopsis no permite juzgar el cierre. |

## C4. Campos de salida (una línea JSON por película)

* `id`
* `feel_good`: entero de −2 a 2, o `null`.
* `feel_good_por_que`: explicación en español de 40 a 70 palabras, parafraseada (sin copiar frases de la sinopsis), que diga qué vínculos quedan en paz o rotos, cómo queda el mundo y si hay esperanza. Puede contener spoilers.
* `confianza_c`: 1 (baja), 2 (media) o 3 (alta).
