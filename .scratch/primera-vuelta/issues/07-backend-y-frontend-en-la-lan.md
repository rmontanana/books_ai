# 07 — Backend y frontend accesibles en la red local

**What to build:** Abrir el navegador del móvil, elegir Universo y Modo, escribir una
pregunta y leer la respuesta con sus Citas. Hasta ahora todo vivía en la línea de
comandos.

**Blocked by:** 04, 05.

**Status:** ready-for-agent

- [ ] El backend escucha en la red local y responde desde otro dispositivo, no sólo desde `localhost`
- [ ] El frontend lo sirve el propio backend; no hay un segundo proceso que arrancar
- [ ] Universo y Modo son dos selectores explícitos; ninguno se infiere de la pregunta
- [ ] Las Citas se muestran con **Volumen**, página y Pasaje literal — el nombre del Volumen ya lleva dentro el de la Obra («El Señor de los Anillos III: El retorno del rey»), así que no hacen falta los dos campos
- [ ] Sin autenticación, por decisión explícita de alcance
