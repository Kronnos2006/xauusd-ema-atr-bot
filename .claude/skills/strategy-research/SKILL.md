---
name: strategy-research
description: >
  Workflow completo para investigar, codificar, backtestear y aprobar/descartar estrategias de trading
  para el EA de MT5 del proyecto Invenio (EURUSD M5, ICT/SMC, sesiones UTC).
  Usar siempre que el usuario mencione: nueva estrategia, probar estrategia, agregar al EA,
  investigar estrategia, descubrir si funciona, mejorar Venom/Judas/Bernd, backtestear idea,
  o pida comparar con las estrategias actuales. También usar cuando pregunte si una estrategia
  académica (trend following, momentum, mean reversion, etc.) aplica a su sistema.
---

# Skill: Investigación de Estrategias de Trading

## Contexto del proyecto

- **EA activo**: `0031.mq5` en MT5, timeframe M5, símbolo EURUSD
- **Estrategias aprobadas**: Venom (PF 1.54), Judas (PF 1.12), Bernd (PF 1.01)
- **Descartadas**: ORB, Doyle, Toto — documentadas en `estrategias_registro.md`
- **Registro maestro**: `outputs/estrategias_registro.md`
- **Riesgo por trade**: $1 | Max trades: 3 | Stop diario: $15
- **Período de backtest estándar**: Ene 1 – Ago 5, 2026 (7 meses, mismo para todas)

## Familia de estrategias que funciona

Las estrategias aprobadas son de tipo **sweep + reversal en kill zones**:
- Precio barre el H/L de una sesión previa → se entra en dirección contraria
- SL detrás del sweep | TP = 2R | ventanas de tiempo fijas (UTC)

Antes de proponer estrategias de distinta familia, recordar: ORB (breakout) y Doyle (EMA) fueron descartadas. La evidencia favorece sweeps de sesión.

---

## El workflow (seguir en orden)

### Paso 1 — Definir hipótesis falsable

```
Hipótesis: "[Nombre] generará PF > 1.0 en backtest 7 meses (Ene–Ago 2026) en EURUSD M5."
Regla de corte: Si PF < 1.0 O menos de 20 trades → DESCARTAR sin renegociar.
```
Mostrar al usuario y esperar confirmación antes de codificar.

### Paso 2 — Diseñar la lógica

Reglas objetivas:
- Ventana de tiempo (horas UTC)
- Condición de entrada (sweep de qué nivel)
- SL (dónde se invalida) / TP (múltiplo R, estándar 2R)
- Máx señales por día (estándar = 1)

### Paso 3 — Codificar en MQL5

Patrón de la estrategia en el EA:

```mql5
// ══ ESTRATEGIA N — [NOMBRE] ══════════════════════════════════════
bool g_sig_nueva = false;  // declarar en globales + resetear en DailyReset()

// En OnTick():
if(!g_sig_nueva && cm >= INICIO_UTC && cm < FIN_UTC)
{
   if(c2 > nivel && c1 < nivel)  // sweep bajista → SHORT
   {
      double sl = h1 + 5 * pip;
      EmitSignal("Nombre", "SHORT", bar0, nivel_h, nivel_l,
                 c1, sl, c1-(sl-c1)*InpRR_Ratio, false);
      g_sig_nueva = true;
   }
   else if(c2 < nivel && c1 > nivel)  // sweep alcista → LONG
   {
      double sl = l1 - 5 * pip;
      EmitSignal("Nombre", "LONG", bar0, nivel_h, nivel_l,
                 c1, sl, c1+(c1-sl)*InpRR_Ratio, true);
      g_sig_nueva = true;
   }
}
```

### Paso 4 — Instrucciones de instalación y backtest

Entregar PowerShell para instalar el EA en MT5. Luego Strategy Tester:
- Símbolo: EURUSD | Período: M5 | Rango: 2026.01.01–2026.08.05
- Modelo: Every tick based on real ticks | Depósito: $100

### Paso 5 — Analizar resultados

Parsear el HTML del Strategy Tester con Python (mismo script FIFO de sesiones anteriores).
Calcular por estrategia: trades, wins, WR, gross+, gross-, net P&L, PF.

Criterios:
| Criterio | Umbral | Si falla |
|---|---|---|
| Profit Factor | > 1.0 | DESCARTAR |
| Trades totales | ≥ 20 | DESCARTAR |
| Resultado ambiguo | — | Reportar al usuario antes de decidir |

### Paso 6 — Actualizar el registro

Editar `outputs/estrategias_registro.md`:
- PF > 1.0 y ≥ 20 trades → **APROBADA** con métricas reales
- PF < 1.0 o < 20 trades → **DESCARTADA** con razón documentada

---

## Reglas del proyecto (no negociables)

1. Ninguna hipótesis sin frase falsable + regla de corte primero
2. Si resultado es ambiguo → parar y preguntar al usuario
3. Estrategias descartadas NO se reviven
4. Backtest siempre en el mismo período (comparabilidad)

---

## Pipeline de ideas pendientes

| Idea | Tipo | Prioridad |
|---|---|---|
| Silver Bullet NY (15:00-16:00 UTC) | Nueva estrategia | Alta |
| London Close Sweep (12:30-13:15 UTC) | Nueva estrategia | Alta |
| ATR Regime Filter en Venom | Mejora existente | Media |
| D1 Trend Bias en Venom | Mejora existente | Media |
| GBPUSD backtest (mismo EA) | Expansión de par | Alta |
| Silver Bullet London (08:00-09:00 UTC) | Nueva estrategia | Media |
| NY Close Reversal (20:00-21:00 UTC) | Nueva estrategia | Media |
