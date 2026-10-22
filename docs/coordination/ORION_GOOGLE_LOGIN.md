# ORION privado — solo iniciar sesión con Google

**Estado: gateway preparado, no desplegado.** El proyecto actual en GitHub Pages es público; no se puede hacerlo privado mediante una pantalla HTML. Nunca presentar un bloqueo visual en Pages como protección de datos.

## Qué consigue esta integración
- Gateway web propio con OAuth 2.0 / OpenID Connect de Google (biblioteca Authlib).
- Solo acepta cuentas de Google **con correo verificado** y presentes en `ORION_ALLOWED_GOOGLE_EMAILS`, gestionado en el servidor privado.
- Bloquea el HTML de ORION, el visor de Claude y el `data.json` de ORION antes de autenticar al usuario.
- Cookies de sesión firmadas, solo HTTPS, SameSite=lax y 4 horas de duración.
- Página privada `/cuentas` con enlaces oficiales a ChatGPT y Claude y cierre de sesión ORION.
- Sin almacenamiento ni captura de contraseñas Google, ChatGPT o Claude.

## Qué NO consigue
- Entrar con Google a ORION **no concede acceso automático** a las sesiones, chats, memoria, suscripciones o cuotas de ChatGPT y Claude.
- ChatGPT y Claude deben permitir `Continuar con Google` en sus **sitios oficiales** si ese es el método de ingreso de las cuentas. Los proveedores no comparten sus cookies ni tokens con ORION.
- No inicia automáticamente agentes ni permite intervenir en proyectos privados de los proveedores.
- **NO hace privado el GitHub Pages ya publicado** en `kronnos2006.github.io/xauusd-ema-atr-bot/`. Si el objetivo es que nadie lo vea, será necesario despublicar/migrar Pages cuando el dueño haya comprobado un despliegue privado alternativo. No despublicarlo sin confirmar que ambos visores funcionan en el nuevo alojamiento.

## Preparación que debe completar el propietario del proyecto
1. Elegir un backend HTTPS protegido (por ejemplo Render Web Service). El proveedor debe instalar dependencias de `gateway/requirements.txt` y ejecutar `uvicorn gateway.orion_google:app --host 0.0.0.0 --port $PORT --proxy-headers`. No publicar la dirección privada en Pages antes de configurar acceso.
2. Crear credenciales **Google OAuth de aplicación web** en Google Cloud Console; configurar la URL HTTPS de origen y la URL de redirección **exacta** `https://<dominio-del-backend>/auth/callback`.
3. Configurar **solo en las variables privadas del servidor**:
   - `GOOGLE_CLIENT_ID` = ID de cliente creado en Google.
   - `GOOGLE_CLIENT_SECRET` = secreto de Google. **Nunca en repositorio, issue ni ChatGPT**.
   - `ORION_SESSION_SECRET` = cadena larga aleatoria (mínimo 32 caracteres), secreta.
   - `ORION_BASE_URL` = `https://<dominio-del-backend>`.
   - `ORION_ALLOWED_GOOGLE_EMAILS` = correo(s) de Google autorizados, separados por comas; preferiblemente solo la cuenta del dueño.
4. Restringir el acceso administrativo del alojamiento y configurar límites de tráfico/registro seguro. Esta primera implementación no es un sistema completo de prevención de abuso; someter a revisión de seguridad antes de darle capacidad de escribir o activar APIs.
5. Verificar desde navegador privado o teléfono: visitante anónimo es redirigido a Google; cuenta incorrecta recibe 403; cuenta autorizada accede a `/`, `/visor/` y `/cuentas`.
6. Solo después de validar el backend privado: acordar y efectuar la migración/despublicación de la copia pública de ORION/visor, conservando respaldos y reversión.
7. Para conectar tareas de Claude/OpenAI usar **APIs oficiales con autorización y costos separados** en servidor, no sesiones ni cookies robadas del navegador.

## Restricciones de seguridad
No modificar KT-002/003, inferencia, datos, preregistros, holdouts, reglas científicas, auditorías independientes, capital real ni visor fuente de Claude. El gateway consulta archivos versionados del repositorio en el servidor. No tiene funciones de escritura.

## Pruebas
```
python -m pip install -r gateway/requirements.txt
python -m unittest discover -s tests -p 'test_orion_google.py' -v
```

No ejecutar el servidor si faltan las variables. El CI usa datos sintéticos y **nunca** solicita ni necesita credenciales reales.
