/* Pure presentation policy; no network, credentials or workflow mutations. */
"use strict";
function classifyRuns(runs, now = Date.now()) {
  if (!Array.isArray(runs) || !runs.length) return {state: 'NO VERIFICADO', reason: 'Sin ejecuciones verificables'};
  const bad = new Set(['failure', 'timed_out', 'cancelled', 'startup_failure', 'action_required', 'stale']);
  const active = new Set(['queued', 'in_progress', 'waiting', 'pending', 'requested']);
  let failures = 0, pending = 0, unknown = 0;
  for (const run of runs) {
    const stamp = Date.parse(run.updated_at);
    if (!Number.isFinite(stamp) || stamp > now || now - stamp > 86400000) { unknown++; continue; }
    if (active.has(run.status)) { pending++; continue; }
    if (run.status !== 'completed') { unknown++; continue; }
    if (bad.has(run.conclusion)) failures++;
    else if (run.conclusion !== 'success') unknown++;
  }
  return {state: failures ? 'FALLAS OBSERVADAS' : unknown ? 'NO VERIFICADO' : pending ? 'EN CURSO' : 'MUESTRA SIN FALLAS',
    reason: `${failures} fallas; ${pending} activas; ${unknown} sin verificar. Muestra limitada: no certifica todo el sistema.`};
}
if (typeof module !== 'undefined') module.exports = {classifyRuns};
