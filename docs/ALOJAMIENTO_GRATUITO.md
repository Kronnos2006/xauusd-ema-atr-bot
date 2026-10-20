# Donde guardar y ejecutar sin pagar

Verificado 2026-10-19 Costa Rica. Almacenamiento y computo son necesidades diferentes; la rama publicada conserva el codigo/evidencia pero no ejecuta Python.

## Guardar ahora: GitHub Free

GitHub Free admite repositorios privados y publicos. Usar el repositorio existente para codigo, protocolos e instantaneas pequeñas de los registros. Evitar pesos, entornos y caches: GitHub bloquea ficheros mayores de 100 MiB. Las predicciones reales de esta tarea pesan poco y se respaldan con manifiesto SHA256.

Fuentes: https://docs.github.com/en/get-started/learning-about-github/githubs-plans y https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github

## Candidato para correr con la PC apagada: Oracle Cloud Always Free

La documentacion vigente de Oracle indica una asignacion Ampere A1 ARM de 2 OCPU y 12 GB RAM para tenencias Always Free, equivalente a 1.500 horas OCPU/9.000 horas GB mensuales; hasta 200 GB de volumen total y cinco copias de volumen. Tambien incluye almacenamiento de objetos sujeto a limites. Comprobar siempre los limites y etiquetas gratis de la cuenta antes de crear recursos; no usar creditos de prueba como si fueran gratuidad permanente.

Limitaciones: puede no haber capacidad en la region; Oracle puede recuperar instancias ociosas. Este trabajo con inferencias esporadicas podria quedar sujeto a esa politica. No generar carga artificial para evitarla. La cuenta puede requerir verificacion de identidad/tarjeta; las condiciones concretas se comprueban al registrarse. No se ha creado cuenta ni aceptado cargos.

Fuente primaria de limites, disponibilidad y recuperacion: https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm

Verificacion de cuenta y tarjeta: https://www.oracle.com/cloud/free/faq/

Recomendacion condicionada: es una opcion candidata para probar la carga del proyecto sin pagar, no garantia de disponibilidad continua. Antes de migrar hay que adaptar las rutas Windows del servidor a Linux ARM, verificar ruedas PyTorch y compatibilidad/consumo de ambos modelos, preparar dependencias por arquitectura, almacenamiento durable, copia externa y acceso privado al panel. Este repositorio aun no esta desplegado ni probado en ARM. Los 12 GB publicados parecen un punto de partida razonable por la carga local observada, pero falta medirlo en esa maquina. No exponer directamente el servidor de desarrollo a Internet.

Para nuevas emisiones sin intervencion aun falta un planificador de aplicacion registrado y aprobado; hoy el monitor contrasta pendientes cada minuto, pero una nueva prediccion requiere boton. Ningun cambio de modelos, pesos o frecuencia queda autorizado por elegir alojamiento.

## Colab: solo pruebas interactivas

Colab gratuito tiene limites dinamicos, desconexiones por inactividad y tiempo maximo de runtime. No es una base fiable para un servicio continuo 24/6 ni para el unico registro de evidencia. Puede servir para probar compatibilidad/inferencia y guardar resultados externamente; no usar mecanismos para eludir sus limites.

Fuente: https://research.google.com/colaboratory/faq.html

## Decision recomendada

Guardar codigo/evidencia en GitHub ahora. Si se obtiene una instancia Oracle Always Free compatible, ensayar la migracion con los limites gratuitos y respaldo separado. Si no hay capacidad o la cuenta no cumple condiciones, no prometer una alternativa gratuita ininterrumpida. Mantener registro local y copias publicadas hasta elegir otro alojamiento. No se crea ningun recurso de pago ni tarea programada con esta documentacion.
