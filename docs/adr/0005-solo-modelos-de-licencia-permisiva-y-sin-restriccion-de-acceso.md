# Sólo modelos de licencia permisiva y sin restricción de acceso

Este repositorio es público y se publica con licencia MIT: el README invita a cualquiera a
aportar sus propios libros y ejecutarlo. Esa promesa se rompe si el modelo que hace falta
para ejecutarlo exige aceptar una licencia propietaria y esperar una aprobación manual.

Decidimos que todo modelo que el proyecto proponga por defecto —Modelo Base, generador o
de embeddings— tenga **licencia permisiva y acceso libre en el Hub**. En la práctica eso
deja dentro a Qwen, Gemma y Granite, todos Apache-2.0 y sin restricción, y deja fuera a
Llama, cuya licencia es propietaria y cuyo acceso requiere solicitud manual.

La restricción es del proyecto, no del usuario: quien quiera usar un modelo restringido en
su copia puede hacerlo, porque cambiar de Modelo Base es un parámetro. Lo que no hacemos es
proponerlo como camino por defecto.

## Consecuencias

- La elección concreta de modelo **no** lleva ADR propio: es barata de revertir por diseño
  —para eso están el pipeline repetible y el Conjunto de Evaluación— y no cumple el
  criterio. Lo que sí perdura es esta restricción, que acota el conjunto elegible.
- Cuando alguien proponga Llama dentro de seis meses, la respuesta está aquí y no hay que
  reconstruir el razonamiento.
