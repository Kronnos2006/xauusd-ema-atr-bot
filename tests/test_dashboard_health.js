const assert = require('node:assert/strict');
const {classifyRuns} = require('../dashboard/health.js');
const now = Date.parse('2026-11-01T20:00:00Z');
const run = (conclusion, status='completed', updated_at='2026-11-01T19:00:00Z') => ({conclusion,status,updated_at});
assert.equal(classifyRuns([], now).state, 'NO VERIFICADO');
assert.equal(classifyRuns([run('success')], now).state, 'MUESTRA SIN FALLAS');
for (const c of ['failure','timed_out','cancelled','startup_failure','action_required','stale'])
  assert.equal(classifyRuns([run(c)], now).state, 'FALLAS OBSERVADAS');
for (const c of [null,'skipped','neutral','unknown'])
  assert.equal(classifyRuns([run(c)], now).state, 'NO VERIFICADO');
for (const t of ['bad','2026-10-30T10:00:00Z','2026-11-02T00:00:00Z'])
  assert.equal(classifyRuns([run('success','completed',t)], now).state, 'NO VERIFICADO');
assert.equal(classifyRuns([run(null,'queued')], now).state, 'EN CURSO');
assert.equal(classifyRuns([run('success'),run('failure')], now).state, 'FALLAS OBSERVADAS');
console.log('Dashboard health: 17 negative and positive checks passed');
