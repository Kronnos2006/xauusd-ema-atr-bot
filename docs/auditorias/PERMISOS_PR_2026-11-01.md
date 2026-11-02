# Auditoría acotada: permisos de trabajos de PR

Codex, 2026-11-01. Base master b70de39. El escaneo preliminar de48 workflows
incluía el CI de instalación propuesto; master contenía47. No es una
certificación de seguridad global ni consulta de permisos efectivos GitHub.

## Hallazgo

estado.yml y progreso.yml ejecutaban código del PR con permisos heredados
contents:write y token disponible al generador; omitir únicamente el paso
git push no reduce la capacidad del token. kt004.yml también concedía
contents:write al job de pruebas del PR. Esto es exceso de privilegio en
esas rutas, no prueba de explotación ni de escritura indebida observada.

## Cambio propuesto

- Estado/progreso: jobs de validación PR separados, permisos explícitos de
  lectura y checkout sin persistir credenciales. Los jobs de publicación
  solo son elegibles fuera de PR y desde refs/heads/master.
- KT004: el job pruebas conserva su condición solo PR pero recibe
  contents:read y checkout sin persistencia. No se cambian parámetros,
  dependencias, triggers, trabajos productivos ni datos del experimento.
- No se toca KT002. No se relanzan ni cancelan corridas. Concurrency sigue
  cancel-in-progress:false donde ya estaba establecido.

El código productivo conserva permisos de escritura necesarios para su
publicación. Las políticas de la organización, protecciones de rama,
permisos de colaboradores y secretos no se certifican por leer YAML.

## Verificación y alcance

tools/workflow_permissions.py analiza tres jobs conocidos y dos condiciones
de publicación exactas, con PyYAML BaseLoader. No pretende interpretar todas
las expresiones posibles ni probar acciones transitivas de terceros.
Salida PASS solo significa que esa política estática acotada coincide.
Mantiene full_permissions_audit_approved=False.

Cuatro pruebas con mutaciones: reintroducir write, heredar permisos,
persistir credenciales, quitar restricción master, configuración ausente o
malformada deben fallar. Los tests usan copias temporales, no editan el repo.

```powershell
python -m pip install PyYAML==6.0.3
python tools/workflow_permissions.py
python -m unittest discover -s tests -p test_workflow_permissions.py -v
```

Recomendación: ejecutar los comandos en un entorno de QA aislado. La PC
probó BaseLoader con PyYAML6.0.1; CI fija6.0.3. Para cerrar F1.4 falta revisión
de permisos efectivos y estabilidad, además de aprobación del dueño; este
PR aporta endurecimiento y evidencia parcial sin acreditar ese hito entero.
