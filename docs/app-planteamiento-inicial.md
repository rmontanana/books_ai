# Aplicación para consulta mediante modelo generativo local sobre información contenida en libros

Quiero diseñar e implementar una aplicación para poder consultar a un modelo LLM en local sobre la información contenida en los libros que se pueden encontrar en la carpeta books
Estos libros tratan sobre la literatura de Tolkien y por otro lado tenemos la literatura de George R. R. Martin
Necesito por tanto seleccionar un modelo sobre el que pueda hacer fine tuning con la información contenida en esos libros
La plataforma sobre la que voy a desarrollar y ejecutar la aplicación es una strix halo de amd con 128 GB de memoria unificada
Necesitaré hacer todo el proceso de fine tuning del modelo de forma repetible, es decir quiero poder seleccionar el modelo de partida y hacer el proceso de fine tuning con cualquier modelo que elija y también en un momento dado volver a hacerlo con otro modelo
Necesitaré también un backend para lanzar el modelo y un frontend para poder interrogarlo