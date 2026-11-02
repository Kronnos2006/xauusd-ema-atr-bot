/* UI acceptance test. Requires Playwright; uses only local snapshot and mocked API. */
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

(async () => {
  const out = process.env.UI_QA_OUT || '.local/mobile-qa';
  fs.mkdirSync(out, {recursive:true});
  const channel = process.env.UI_BROWSER || 'msedge';
  const browser = await chromium.launch(channel==='chromium' ? {headless:true} : {channel,headless:true});
  const evidence = [];
  try {
    for (const width of [360,390,1280]) {
      const context = await browser.newContext({viewport:{width,height:844}});
      const page = await context.newPage();
      const errors=[];
      page.on('pageerror', e => errors.push(e.message));
      await page.route('https://api.github.com/**', route => route.fulfill({status:503,body:'API unavailable (test)'}));
      await page.goto(process.env.UI_QA_URL || 'http://127.0.0.1:8765', {waitUntil:'networkidle'});
      await page.locator('#module-evidence .rowline').first().waitFor();
      assert.equal(await page.locator('#module-evidence .rowline').count(),4);
      await page.waitForFunction(() => document.getElementById('alerts').textContent.includes('NO VERIFICADO'));
      for (const tab of ['overview','models','agents','operations','live']) {
        await page.locator(`[data-tab="${tab}"]`).click();
        assert(await page.locator('#'+tab).isVisible());
        const dims=await page.evaluate(() => ({viewport:innerWidth,document:document.documentElement.scrollWidth}));
        assert(dims.document<=dims.viewport+1, `${width}/${tab}: horizontal overflow ${dims.document}`);
        evidence.push({width,tab,...dims});
      }
      await page.locator('[data-tab="overview"]').click();
      await page.screenshot({path:path.join(out,`panel-${width}.png`),fullPage:true});
      assert.deepEqual(errors,[]);
      await context.close();
    }
    fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({status:'PASS',api:'MOCKED_503',checks:evidence},null,2));
    console.log(JSON.stringify({status:'PASS',views:evidence.length,out}));
  } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exitCode=1;});
