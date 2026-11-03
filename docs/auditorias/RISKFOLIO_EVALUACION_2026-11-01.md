# Riskfolio-Lib: evaluación técnica offline y límites del adaptador

Autor Codex, 2026-11-01. Reutiliza borrador de ChatGPT de la rama
feat/kronnos-riskfolio-20261101 (commits 0675390 y 256231a), conservando
autoría mediante cherry-pick. No se atribuye ese código original a Codex.
Estado: librería real probada localmente; 12 pruebas PASS en 13,77 s, pip check sin conflictos. CI y revisión final pendientes; no es entrega financiera aprobada.

Dependencias resueltas: 93 paquetes fijados en research/requirements-riskfolio.txt. Instalación local aislada completada; no se instalaron en el Python global.

## Cambio necesario frente al borrador

El máximo original 40 % por activo no respetaba el marco de riesgo vigente
(25 % por posición). Se fija 25 % como máximo no relajable por argumento;
el marco docs/riesgo/MARCO_DE_RIESGO.md permanece intacto. No se incorpora
el límite 40 % de tools/kronnos_finance_offline.py como autoridad.

## Alcance de la evaluación

Riskfolio-Lib 7.4.0, entorno virtual aislado, matrices sintéticas deterministas.
Se usa realmente Portfolio.assets_stats para covarianza histórica. No se
optimiza una estrategia, no se leen mercados, holdouts ni KT-002, no se
envían órdenes y no se llama a credenciales financieras.

La entrada debe ser una matriz diaria previamente alineada y validada por
el llamador; el adaptador no certifica fechas o fuente. Ventana de riesgo
60 días, anualización365 para cripto; 2–8 activos, pesos no negativos,
exposición bruta<=100 %, por posición<=25 %, agrupación conservadora de
correlaciones>0,70 con peso combinado<=25 %, correlación media<=0,50,
N efectivo por autovalores>=2 para múltiples posiciones, vol anual<=10 %.
Se permite efectivo sin invertir; no se fuerza suma de pesos1.

Pruebas negativas cubren concentración, bruto, cortos, series constantes,
historia insuficiente, datos no finitos, forma, volatilidad y grupos
correlacionados. Son pruebas de software, no resultados financieros.

## Qué falta para el marco completo

No se verifican stops, riesgo por operación, volumen y liquidez, pérdidas
diarias/semanales/mensuales, costos ni apagado por drawdown. No se afirma
que pasar covarianza y exposición autorice una simulación con posiciones.
El reporte mantiene full_risk_framework_verified=False y
promotion_permitted=False. El adaptador no invoca optimizadores ni altera
límites. Para usar posiciones hace falta implementación y revisión adicional.

## Utilidad y costo de mantenimiento

Utilidad demostrable buscada: covarianza de la librería real y controles
conservadores reproducibles bajo el marco existente. No se demuestra mejora
de predicciones, rentabilidad o asignación. La fórmula histórica de
covarianza también existe en NumPy/Pandas: no se afirma ventaja única de
Riskfolio para este cálculo. No añadirlo a producción por el solo hecho
de estar instalado. Mantener evaluación aislada hasta demostrar necesidad
de funciones de riesgo adicionales.

Costo: dependencias de optimización, estadística, gráficos y notebooks
amplían descarga, espacio e importación; registrar versiones resueltas y
pip check. No mezclar ese entorno con loggers ni tareas existentes.

## Reproducción

```powershell
python -m venv .local/riskfolio-env
.local/riskfolio-env/Scripts/python.exe -m pip install -r research/requirements-riskfolio.txt
.local/riskfolio-env/Scripts/python.exe -m pip check
.local/riskfolio-env/Scripts/python.exe -m unittest discover -s tests -p test_kronnos_riskfolio.py -v
```

Fuente primaria de API y alcance:
https://riskfolio-lib.readthedocs.io/en/latest/index.html

La acreditación F4.4 exige pruebas reales de librería, CI, revisión y
aceptación de la evaluación por el dueño. No se marca ese hito por crear
este documento o instalar una dependencia. No es auditoría global del
proyecto ni acta de entrega final.
