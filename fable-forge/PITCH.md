# PITCH — fable-forge

## Nicho

Contenido infantil personalizado: cuentos/fábulas a medida del niño, su edad y lo que la
familia quiere transmitirle.

## Problema

Los padres quieren contenido que (a) sea apropiado para la edad exacta de su hijo, (b)
transmita valores que a *esa* familia le importan hoy ("hoy le costó compartir"), y (c) no
se agote — los libros se releen hasta el hartazgo. Hoy eso se resuelve con libros genéricos
(no personalizan la lección ni el momento), libros personalizados impresos tipo Wonderbly
(caros, one-shot, personalizan el nombre pero no la historia), o improvisación de los
padres a la hora de dormir (calidad despareja, cansancio).

## Cliente

Padres/madres de niños de 3 a 12 años, y como segundo segmento docentes de inicial/primaria
(fábulas para trabajar valores en el aula). Referencia de disposición a pagar: los libros
personalizados impresos rondan USD 30–40 one-shot; las apps de cuentos infantiles cobran
USD 5–10/mes de suscripción.

## Por qué ahora

Un LLM de primera línea genera fábulas *originales* con estructura narrativa correcta,
calibradas por edad y tono, en segundos y a costo marginal. Eso era imposible de escalar
con escritores humanos: la personalización real (moraleja del día + personajes recurrentes
que el niño conoce) solo cierra económicamente con generación automática. La continuidad de
serie (elenco persistente) es el diferencial defendible: convierte contenido descartable en
un mundo propio del niño — y es lo que una suscripción necesita para retener.

## MVP

Lo que implementa este módulo: CLI que genera fábulas (moraleja + audiencia + tono),
variantes de formato (corta, verso, guion narrado, prompts de ilustración) y series con
personajes recurrentes persistidas en archivos planos. Backend exclusivo: `claude-fable-5`.

El MVP de *demanda* (siguiente paso) sería envolver esto en algo mostrable a padres reales:
una fábula de muestra personalizada gratis → suscripción por la serie de su hijo.

## Monetización

- Suscripción familiar (~USD 5–8/mes): N fábulas/mes de la serie del niño + variantes.
- Add-ons one-shot: libro ilustrado imprimible de la serie (los prompts de ilustración ya
  salen del módulo), audio narrado.
- B2B2C: licenciar a jardines/escuelas o apps de crianza existentes.

## Señales de validación

- Positivas: padres que piden la *segunda* fábula de una serie (retención, no curiosidad);
  disposición a pagar por el libro impreso de la serie; docentes que lo usan más de una vez.
- Negativas: la personalización no importa (un libro genérico bueno alcanza); los padres no
  confían en contenido generado para sus hijos; el costo de adquisición supera lo que una
  suscripción chica banca.

## Estado

`prototipado` — el generador funciona end-to-end por CLI; no hubo todavía contacto con
usuarios reales ni prueba de demanda.

## Aprendizajes

- (2026-07) La calidad depende casi por completo del system prompt; el hallazgo clave fue
  separar reglas innegociables (estructura, moraleja ganada) de las calibrables (edad,
  tono) y prohibir explícitamente el recuento de fábulas clásicas.
- (2026-07) Las series sin base de datos funcionan: un bloque JSON de metadata al final de
  cada fábula, acumulado en un archivo por serie, alcanza para mantener continuidad de
  personajes.
