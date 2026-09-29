# Resumen ejecutivo: ¿eran más optimistas las películas de los noventa?

*Primera versión, exploratoria. Cifras generadas automáticamente a partir de `reports/tables/`. Informe completo en `reports/informe.md`.*

## Qué se ha hecho

Se compararon **994 largometrajes de ficción estadounidenses** (1980-2024) en dos marcos: un **marco popular** (150 películas por cohorte entre las 50 más votadas en IMDb de cada año) y un **marco amplio** (50 por cohorte, estratificado por popularidad). Se clasificaron el final, el resultado para los protagonistas, el tono del cierre y la visión de la vida a partir de las sinopsis de Wikipedia, con el título y los años ocultos. Anotaron **dos modelos de lenguaje de forma independiente**, un tercero adjudicó los desacuerdos y el acuerdo entre ambos fue alto (kappa 0,84 en el final).

## Antes de leer las conclusiones

* **No hay validación humana.** Las etiquetas son de modelos; el material para validarlas con personas está preparado, pero no se ha usado.
* **El cegado es imperfecto:** los modelos reconocieron la mayoría de las películas (90 % y 86 %).
* **La popularidad son votos actuales de IMDb**, retrospectivos y sujetos a sesgo de supervivencia.
* **La muestra solo detecta diferencias grandes** (unos 13,8 pp en el marco popular). La cohorte 2020-2024 abarca cinco años.

## Lo que los datos sostienen

* En el cine popular, los finales felices fueron **algo más frecuentes en los noventa (66,0 %) que en 2010-2024 (57,7 %)**: −8,3 pp, IC 95 % [−17,9 pp; +1,2 pp]. Es una diferencia moderada **y estadísticamente incierta**.
* **No hay más finales trágicos** en el cine popular reciente (−1,1 pp [−6,3 pp; +3,7 pp]), ni un tono de cierre menos positivo (−1,6 pp), ni una visión de la vida menos optimista (+0,06 en una escala de −2 a +2).
* Los finales **ambiguos** son algo más comunes que en los noventa (+5,1 pp [+1,2 pp; +9,0 pp]), porque los noventa tuvieron muy pocos; los ochenta y los dos mil tienen niveles parecidos a los actuales.

## Lo que los datos sugieren, sin confirmarlo

* Los noventa parecen **un pico** de finales felices, no el final de una época dorada: los ochenta quedan a una distancia parecida (−9,3 pp frente a los noventa).
* En el **cine de acción** la caída es mayor, del 73,7 % (1980-1999) al 60,2 % (2010-2024), en línea con lo que publicó Stephen Follows.
* En el **cine menos visible** (marco amplio) hay indicios de menos finales felices (−16,7 pp) y una visión más sombría en 2010-2019, pero con muestras pequeñas y problemas de cobertura.

## Lo que los datos no permiten afirmar

* Que el cine de los noventa fuera **claramente** más optimista: al ponderar por votos la diferencia desaparece (+1,9 pp), y solo 1 de las 11 variantes de sensibilidad excluye el cero.
* Que existiera una **prohibición** de hacer películas no optimistas: los estrenos no pueden probarlo.
* Que **el público eche de menos** ese optimismo: no se ha hecho ninguna encuesta ni experimento. Está diseñada, con unos 167 participantes para detectar una preferencia de 5 puntos.
* Nada sobre **causas**.

## Veredicto provisional

La afirmación queda **matizada**. Hay una ligera ventaja de los noventa en finales felices, pero es incierta y no se traslada a más tragedia, a un tono más oscuro ni a una visión de la vida más pesimista en el cine popular actual. La parte de que «se echa de menos» **sigue sin probar**.
