# El Adaptador se conmuta sobre un Modelo Base intacto

Con dos modos sobre la misma aplicación, cabía servirlos con dos modelos separados, con
un único Modelo Afinado para ambos, o con un Modelo Base al que se le activa un Adaptador
sólo en Modo Personaje.

Elegimos lo tercero. La razón no es el ahorro de memoria — un Adaptador ocupa cientos de
MB — sino el aislamiento del riesgo: el Modo Consulta corre siempre sobre el Modelo Base
sin modificar, de forma que **ningún entrenamiento fallido puede degradar la herramienta**.
Es la traducción a arquitectura del principio de que la herramienta manda sobre el
experimento.

## Consecuencias

- El stack de servicio debe permitir activar y desactivar Adaptadores en caliente, lo que
  descarta empaquetar un modelo distinto por Adaptador.
- Probar N Modelos Afinados cuesta N Adaptadores, no N copias del modelo.
