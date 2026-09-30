# Resumen ejecutivo: ¿eran más optimistas las películas de los noventa?

*Primera versión, exploratoria. Cifras generadas automáticamente a partir de `reports/tables/`. Informe completo en `reports/informe.md`.*

## Qué se ha hecho

Se compararon **994 largometrajes de ficción estadounidenses** (1980-2024) en dos marcos: un **marco popular** (150 películas por cohorte entre las 50 más votadas en IMDb de cada año) y un **marco amplio** (50 por cohorte, estratificado por popularidad). Se clasificaron el final, el resultado para los protagonistas, el tono del cierre y la visión de la vida a partir de las sinopsis de Wikipedia, con el título y los años ocultos. Anotaron **dos modelos de lenguaje de forma independiente**, un tercero adjudicó los desacuerdos y el acuerdo entre ambos fue alto (kappa 0,84 en el final).

## Antes de leer las conclusiones

* **No hay validación humana.** Las etiquetas son de modelos; el material para validarlas con personas está preparado, pero no se ha usado.
* **El cegado apenas funcionó en el cine popular:** al menos un modelo reconoció el 100 % de las películas populares, así que pudieron usar lo que sabían de ellas.
* **La popularidad son votos actuales de IMDb**, retrospectivos y sujetos a sesgo de supervivencia.
* **La muestra solo detecta diferencias grandes** (unos 13,8 pp en el marco popular). La cohorte 2020-2024 abarca cinco años.

## Lo que los datos sostienen

* **En el cine popular no se observa un giro grande hacia lo sombrío desde los noventa.** No aumentan los finales trágicos (−1,1 pp [−6,2 pp; +3,8 pp]), el tono de cierre positivo no baja (−1,6 pp) y la visión de la vida no empeora (+0,06 en una escala de −2 a +2). Los intervalos descartan cambios grandes, pero no moderados.
* Los finales **ambiguos** son algo más comunes que en los noventa (+5,1 pp [+1,3 pp; +8,9 pp]), porque los noventa tuvieron muy pocos; los ochenta y los dos mil tienen niveles parecidos a los actuales.

## Lo que los datos sugieren, sin confirmarlo

* En el cine popular, los finales felices fueron **algo más frecuentes en los noventa (66,0 %) que en 2010-2024 (57,7 %)**: −8,3 pp, IC 95 % [−17,7 pp; +1,2 pp]; ajustado por género y popularidad, −7,7 pp. El intervalo incluye el cero.
* Parte del cambio refleja la **composición por géneros**: en el cine popular, la acción pasa del 35 % al 49 % y la comedia, uno de los géneros con más finales felices, del 20 % al 11 %.

* Los noventa parecen **un pico** de finales felices, no el final de una época dorada: los ochenta quedan a una distancia parecida (−9,3 pp frente a los noventa).
* En el **cine de acción** la caída es mayor, del 73,7 % (1980-1999) al 60,2 % (2010-2024), en línea con lo que publicó Stephen Follows. La comedia cae incluso más (−20,0 pp), aunque con muestras pequeñas.
* En el **cine menos visible** (marco amplio) hay indicios de menos finales felices (−16,7 pp) y una visión más sombría en 2010-2019, pero con muestras pequeñas y problemas de cobertura.

## Lo que los datos no permiten afirmar

* Que el cine de los noventa fuera **claramente** más optimista: al ponderar por votos la diferencia se vuelve indeterminada (+1,9 pp [−15,8 pp; +17,7 pp]), y solo 1 de las 10 variantes de sensibilidad excluye el cero.
* Que existiera una **prohibición** de hacer películas no optimistas: los estrenos no pueden probarlo.
* Que **el público eche de menos** ese optimismo: no se ha hecho ninguna encuesta ni experimento. Está diseñada, con unos 167 participantes para detectar una preferencia de 5 puntos.
* Nada sobre **causas**.


## Resultado principal: las series se han vuelto mucho menos *feel good*

* **Series de EE. UU.:** la nota *feel good* media (0-10) pasa de 6,1 en los noventa a 3,8 en 2020-2025. Diferencia 2010-2025 frente a los noventa: −1,88 (IC 95 %: −2,16 a −1,59). Las series con 7 o más bajan del 44 % al 9 %.
* **Series de España:** de 5,9 a 3,9; diferencia −1,75 (IC 95 %: −2,28 a −1,18).
* **El cine apenas cambia:** las películas estadounidenses pasan de 6,3 a 6,1 en 2010-2025: diferencia −0,27 (IC 95 %: −0,57 a +0,03), con un intervalo que incluye el cero. En España el cine sube.
* **Robustez:** en EE. UU. la caída se mantiene con cada anotador (A −1,75, B −2,02), sin las series de solo premisa (−1,58) y ajustando por género y popularidad (−1,40).
* **Géneros:** con la mezcla de géneros de los noventa, la media reciente de EE. UU. sería 4,8: la composición explica el 31 % de la caída y el resto ocurre dentro de los géneros. En España la composición explica el 78 % y, ajustando por género, el intervalo incluye el cero.
* **Cautelas:** se juzga sobre todo la premisa (las series de solo premisa pasan del 15 % al 77 % en EE. UU.); solo vemos las series que siguen votándose hoy; no hay validación humana y los modelos reconocen las series. Los datos no dicen por qué ha ocurrido.

## Segunda parte: censo completo, cine español y ánimo de los personajes

Se anotaron **todas** las películas del marco popular estadounidense (**2.343**, las 50 más votadas de cada año) y las **1.340** españolas más votadas (30 por año). Además del final, se anotaron el protagonista (edad, momento vital, estado civil, clase social), las relaciones centrales, si la historia es especulativa, la época y los países de la trama, el humor, el **tono general** y el **optimismo de los personajes**. El acuerdo entre anotadores fue alto: final κ = 0,86; optimismo de los personajes α = 0,83.

Antes de las conclusiones, los límites de esta parte:

* Los modelos reconocieron el 98,5 % de las películas estadounidenses.
* Solo se adjudicó el final.
* El 58 % de las españolas no tiene final clasificable porque la Wikipedia en español a menudo no lo cuenta.
* Son muchas comparaciones por subgrupo.

* **EE. UU.:** los finales felices bajan del 67,3 % en los noventa al 61,3 % en 2010-2025 (−6,0 pp [−11,3 pp; −0,7 pp]), sobre todo por 2020-2025 (58,1 %). No hay más tragedias.
* **Optimismo de los personajes:** estable (+0,45 en los noventa, +0,53 en 2010-2019) salvo en 2020-2025 (+0,30). El tono general se oscurece algo (−0,23 puntos).
* **Final y ánimo son distintos:** el 40 % de los finales agridulces tiene personajes optimistas. *Titanic* es el ejemplo: final agridulce, optimismo +2.
* **Dónde cae el final feliz** (exploratorio): ciencia ficción, comedia, acción, protagonista femenina y personajes en crisis vital.
* **España va al revés:** más sombría en general, pero con más finales felices en 2010-2025 que en los noventa (+14,1 pp [+3,0 pp; +24,9 pp]). Es un resultado frágil.
* **IMDb:** a igualdad de año y género, los finales felices tienen una nota media −0,33 puntos distinta. Es una asociación y no mide nostalgia.

## Tercera parte: ¿es el cine de los noventa más *feel good*?

La medida principal pasa a ser una nota ***feel good*** de 0 a 10: si la película nos deja con la idea de que los personajes acaban en paz, armonía y amor con los suyos, y de que hay esperanza en la humanidad. Se añaden una nota de utopía o distopía de la sociedad (0 a 10) y el público al que se dirige. Doble anotación ciega de 3.138 películas y árbitro; acuerdo *feel good* α = 0,96.

Límites: juicio sobre un resumen, no sobre la película; sin validación humana; el 46 % de las españolas no tiene nota porque su sinopsis no cuenta el final.

* **EE. UU.:** los noventa son la década más *feel good* (6,3 de media), pero 2010-2019 está al mismo nivel (6,3). La caída llega en 2020-2025: media 5,7, −0,64 puntos (IC 95 %: −1,02 a −0,24). Todo 2010-2025 frente a los noventa: −0,27 (IC 95 %: −0,57 a +0,03).
* **Parte es composición:** menos comedia y menos cine familiar entre lo más visto. Sin películas infantiles y familiares, la diferencia queda en −0,15.
* **Feel good y final feliz** van juntos (correlación 0,67), pero no son lo mismo: el final feliz cae ya en 2010-2019.
* **Utopía:** el cine popular es más bien distópico (4,6 de media en EE. UU.) y empeora en 2020-2025 (−0,36).
* **España va al revés:** menos *feel good* (4,3 frente a 6,1), pero en aumento: +0,65 puntos entre los noventa y 2010-2025 (IC 95 %: +0,14 a +1,19).
* **IMDb:** cada punto de *feel good* se asocia con −0,038 puntos de nota media (mismo año y género).

## Veredicto provisional

La afirmación se sostiene **en las series, no en el cine**. Las series populares de los noventa, en EE. UU. y en España, son mucho más *feel good* que las de 2010-2025: la caída es grande y, en EE. UU., resiste a todas las comprobaciones. En España, casi toda se explica por el cambio de géneros. Cautela: se juzga sobre todo la premisa y solo vemos las series que siguen votándose hoy. En el cine la diferencia es pequeña: los noventa son la década más *feel good* y con más finales felices del cine popular estadounidense, pero el cambio claro se concentra en 2020-2025, con parte debida a la composición (menos comedia y menos cine familiar). No hay más tragedias, y en el cine español la tendencia es la contraria. Los datos no dicen por qué ha ocurrido, y la parte de que «se echa de menos» **sigue sin probar**.
