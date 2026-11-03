# Guardia: diagnóstico y auditoría acotada de seguridad

Fecha local: 2026-11-01. Autor: Codex. Revisión independiente pendiente.
Base: master b3e7abd. Alcance: lógica pura de salud, publicación segura y
lectura estática de permisos de cinco workflows. No certifica seguridad
global, estabilidad longitudinal ni ausencia de incidentes remotos.

## Hallazgos reproducibles y corrección propuesta

1. Fecha futura: `frescura` calculaba edad negativa y no reportaba problema;
   `saltar_duplicada` omitía medir incluso con publicación fechada en el futuro.
   Ahora se rechazan fechas futuras o sin zona; la salud falla y el dedupe no
   omite la medición. Fechas ilegibles generan NO VERIFICADO.
2. Paso obligatorio omitido: `verificar_salud` solo registraba `failure`;
   `publicar=skipped` o `kt002=cancelled` podían dejar un resultado sano si
   quedaban datos recientes remotos. Ahora todo resultado distinto de success
   falla, salvo spread/velas skipped: esas omisiones están previstas por dedupe
   y frescura. Los datos remotos siguen siendo obligatorios.
3. Entrada de corridas no confiable: estados desconocidos, conclusiones
   ausentes, fechas inválidas o corridas desordenadas no autorizan dispatch.
   Se devuelve alerta NO VERIFICADO sin relanzamiento ni cancelación.

Pruebas: `tests/test_guardia_entradas_invalidas.py` usa entradas sintéticas;
no llama a GitHub, MT5, modelos ni red. Ejecutar:

```powershell
python -m unittest discover -s tests -p test_guardia_salud.py -q
python -m unittest discover -s tests -p test_guardia_entradas_invalidas.py -v
python -m unittest discover -s tests -p test_publicar_mercado_seguro.py -q
```

## Permisos observados y necesidad

| Workflow | Permisos declarados | Uso / límite observado |
|---|---|---|
| guardia | contents/actions/issues write | Publica mercado, dispatch de KT-002 y avisos. Rama distinta de master inhibe dispatch y avisos productivos. El token no está limitado por ruta: riesgo residual |
| kt002 | contents/actions write | Publica sus propios registros y dispara guardia. Solo inspección: no modificado |
| guardia-publicacion-tests | contents read | Pruebas sin secretos ni escritura; se amplían casos de salud |
| orion-ci | contents read | Pruebas y compilación de consulta |
| orion-pages | contents read; pages/id-token write | Despliegue Pages; sin permiso contents write |

No se cambian permisos de producción. `cancel-in-progress: false` observado
en guardia y KT-002; no se canceló ni relanzó ninguna corrida. Permiso
actions write tiene capacidad mayor que dispatch: no equivale a mínimo
privilegio perfecto. Separar tokens/jobs exige diseño y revisión adicional.
No se afirma que los permisos efectivos de la organización o protecciones
de ramas hayan sido consultados.

## Integridad y límites del dictamen

KT-002, sus datos, preregistro y holdouts quedan fuera de la modificación.
La evidencia de inmutabilidad de este cambio es el diff contra la base;
no se abren reservas ni se publica hash de contenido protegido. No se
ejecuta guardia.yml: solo CI de pruebas sobre el PR.

El hito F1.2 se propone tras revisión y CI. F1.3 requiere completar la
auditoría del pipeline de KT-002; F1.4 permanece pendiente. ATLAS depende
de custodia externa histórica y validación real: un archivo o hash creado
hoy no demuestra procedencia previa. FreqAI/combinador necesitan protocolo
aprobado antes de resultados nuevos. Ninguno de esos hitos se acredita aquí.
