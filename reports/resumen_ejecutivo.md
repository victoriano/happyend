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

## Veredicto provisional

La afirmación queda **matizada**. Hay una ligera ventaja de los noventa en finales felices, pero es incierta y no se traslada a más tragedia, a un tono más oscuro ni a una visión de la vida más pesimista en el cine popular actual. La parte de que «se echa de menos» **sigue sin probar**.
