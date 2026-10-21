---
tipo: referencia
estado: vigente
actualizado: 2026-10-20
tags: [automatizacion, github-actions, tareas-programadas, panel]
---

# Automatizaciones

Índice: [[00 Inicio]] · Uso diario: [[Guía de uso]] · Infraestructura de la PC: [[Infraestructura]]

Todo lo que corre sin la PC encendida.

## GitHub Actions

### KT-002 — `.github/workflows/kt002.yml`
- **Disparadores:** cron horario (`7 * * * *`), push del script o del workflow, el archivo `data/kt002/despertar.txt` y ejecución manual.
- **Cómo corre:** instala el entorno fijado una vez y repite el script en el minuto 7 de cada hora durante ~4 h 45 min, haciendo commit de `data/kt002/` en cada vuelta.
- **Concurrencia:** grupo `kt002`; una corrida a la vez.

### KT-003 — `.github/workflows/kt003.yml`
- **Disparador:** solo editar `data/kt003/lanzar.txt` en `master` (o a mano). Nunca al fusionar código.
- **Trabajos:** `modo` → (`datos` → `prueba`) o (`pronosticar` ×16 → `unir`). Solo corre desde `master`.
- **Protecciones:** hash de los datos sellados, conjunto de bases verificado, reintentos por shard, reproducibilidad obligatoria.

> [!info] Límites de GitHub
> Repo público: Actions es gratis. GitHub deja correr unas 11 tareas a la vez en esta cuenta. Si KT-003 está corriendo, KT-002 queda en cola.

## Tareas programadas de Claude
| Nombre | Horario | Qué hace |
|---|---|---|
| Gerente: informe diario | 6:30 a. m. Costa Rica | Revisa todo, convoca jefes solo si hace falta, relanza lo parado y te rinde cuentas en ≤ 5 líneas |
| Vigía de datos | Cada 2 horas | Mira si KT-002 registra; solo relanza lo parado o fallido y deja constancia al gerente en la Oficina. Sin mensaje si todo está bien |

KT-002 se mantiene solo: cuando termina una corrida larga, arranca la siguiente del cron horario de GitHub.

Se ven y se pausan desde la app de Claude, en la lista de tareas programadas.

## Panel
[Panel KT-002 BTC](https://claude.ai/artifact/2CJcKXjLjG2usbvqnp3nDN): tablero de Claude con BTC en vivo y las predicciones encima, acierto, tabla de resultados y registro de cambios. Lee los datos con el conector TinyFish (API pública de Binance y archivos crudos del repo). Ver [[Guía de uso#1. Ver cómo va todo]].

## Coordinación
`docs/coordination/CONTEXTO_COMPARTIDO.md` registra quién hizo qué (Claude/Codex), decisiones y pendientes.
