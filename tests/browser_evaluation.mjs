// Environment adapter for Ego Lite only; not a mandatory skill dependency.
// Run: UI_EVALUATION_OUTPUT=/absolute/output ego-browser nodejs < tests/browser_evaluation.mjs
const fs = await import('node:fs/promises');
const cp = await import('node:child_process');
const path = await import('node:path');
const output = process.env.UI_EVALUATION_OUTPUT;
if (!output || !path.isAbsolute(output)) throw new Error('UI_EVALUATION_OUTPUT must be an absolute isolated directory');
const python = process.env.UI_SKILL_PYTHON || 'python3';
const helper = path.resolve('tests/browser_evaluation.py');
const command = (...args) => JSON.parse(cp.execFileSync(python, [helper, ...args], {encoding:'utf8'}));
const phase = process.env.UI_EVALUATION_PHASE || 'initial';
const records = JSON.parse(await fs.readFile(path.join(output,'config.json'),'utf8'));
const task = await taskSpace(process.env.UI_EVALUATION_SPACE ? Number(process.env.UI_EVALUATION_SPACE) : 'UI v2.1 browser fixtures');
console.log({spaceId:task.spaceId, phase});
const page = task.page('p1');
await page.cdp('Network.enable');
await page.cdp('Network.setCacheDisabled',{cacheDisabled:true});
for (const record of records) {
  if (phase==='repair' && record.name!=='responsive') continue;
  const run = JSON.parse(await fs.readFile(path.join(record.run,'run.json'),'utf8'));
  const captures = phase==='repair' ? JSON.parse(await fs.readFile(path.join(record.run,'captures.json'),'utf8')) : [];
  const capture = async (id, url, role, iteration, width) => {
    const revisionBefore = command('snapshot',record.run);
    await page.cdp('Emulation.setDeviceMetricsOverride',{width,height:900,deviceScaleFactor:1,mobile:false});
    await page.cdp('Emulation.setEmulatedMedia',{features:[{name:'prefers-color-scheme',value:'light'},{name:'prefers-reduced-motion',value:'reduce'}]});
    await page.goto(url);
    await page.evaluate(async()=>{await document.fonts.ready;window.scrollTo(0,0)});
    const data = await page.evaluate(()=>{
      const box=document.querySelector('#hero').getBoundingClientRect();
      const x=Math.max(0,Math.floor(box.x*devicePixelRatio)),y=Math.max(0,Math.floor(box.y*devicePixelRatio));
      return {url:location.href,route:location.pathname,viewport:[innerWidth,innerHeight],dpr:devicePixelRatio,theme:matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light',state:'default',scroll:[scrollX,scrollY],
        regions:{hero:[x,y,Math.min(Math.ceil(box.width*devicePixelRatio),Math.round(innerWidth*devicePixelRatio)-x),Math.min(Math.ceil(box.height*devicePixelRatio),Math.round(innerHeight*devicePixelRatio)-y)]},
        ctaRight:document.querySelector('.cta').getBoundingClientRect().right,scrollWidth:document.documentElement.scrollWidth};
    });
    const file=id+'.png';await page.screenshot({path:path.join(record.run,file)});
    const revisionAfter = command('snapshot',record.run);
    if (revisionBefore!==revisionAfter) throw new Error('Code changed during capture');
    const {ctaRight,scrollWidth,...contract}=data;
    captures.push({id,file,role,capture:{...contract,run_id:run.run_id,iteration,captured_at:new Date().toISOString(),source_revision:revisionBefore},bounds:{ctaRight,scrollWidth}});
    console.log({fixture:record.name,id,viewport:data.viewport,ctaRight,scrollWidth});
  };
  if (phase==='initial') {
    await capture('before-desktop',record.url,'reference',1,1200);
    await capture('ref-desktop',record.url.replace('index.html','reference.html'),'reference',1,1200);
    await capture('ref-mobile',record.url.replace('index.html','reference.html'),'reference',1,390);
    await fs.copyFile(path.join(record.project,'candidate.html'),path.join(record.project,'index.html'));
  } else {
    await fs.access(path.join(record.run,'qa-2.json')); // Preserve recorded failure before repair.
    const source=await fs.readFile(path.join(record.project,'index.html'),'utf8');
    if (!source.includes('.cta{min-width:560px;white-space:nowrap}')) throw new Error('Expected fixture state missing');
    await fs.writeFile(path.join(record.project,'index.html'),source.replace('.cta{min-width:560px;white-space:nowrap}', '.cta{min-width:0;white-space:normal}'));
  }
  const prefix=phase==='repair'?'fixed':'candidate',iteration=phase==='repair'?3:2;
  await capture(prefix+'-desktop',record.url,'implementation',iteration,1200);
  await capture(prefix+'-mobile',record.url,'implementation',iteration,390);
  console.log((await page.snapshot()).slice(0,1800));
  const counts=[];
  for (const query of ['agent','missing','','video']) {
    await page.fill('loc=css:#search',query);
    const expected=query==='missing'?'0 projects':query===''?'2 projects':'1 projects';
    await page.waitForFunction(expected=>document.querySelector('#count').textContent===expected,expected);
    counts.push(await page.evaluate(()=>[...document.querySelectorAll('[data-project]')].filter(c=>!c.hidden).length));
  }
  await page.fill('loc=css:#search','');
  await page.click('loc=css:.cta');
  await page.waitForURL('**#contact');
  const preserved=await page.evaluate(()=>({links:[...document.querySelectorAll('a')].map(a=>a.getAttribute('href')),
     copy:[document.querySelector('h1').textContent,...document.querySelectorAll('article p')].map(x=>typeof x==='string'?x:x.textContent),contact:location.hash==='#contact'}));
  if (!preserved.contact) throw new Error('CTA click did not navigate');
  const identity={schema_version:1,run_id:run.run_id,iteration,captured_at:new Date().toISOString(),source_revision:command('snapshot',record.run)};
  const expectedLinks=['#contact','#agent','#video'],expectedCopy=['Ideas into useful AI experiences.','Prototype / task orchestration','Prototype / batch editing'];
  const checks=[['links',expectedLinks,preserved.links,'browser-dom'],['copy',expectedCopy,preserved.copy,'browser-dom'],['search',[1,0,2,1],counts,'browser-interaction']].map(([id,expected,observed,method])=>({id,expected,observed,passed:JSON.stringify(expected)===JSON.stringify(observed),method}));
  const html=await fs.readFile(path.join(record.project,'index.html'),'utf8');
  cp.execFileSync(process.execPath,['--check'],{input:html.match(/<script>([\s\S]*?)<\/script>/)[1]});
  await fs.writeFile(path.join(record.run,prefix+'-code.json'),JSON.stringify({...identity,status:'passed',command:'node --check (extracted actual inline script)',exit_code:0},null,2));
  await fs.writeFile(path.join(record.run,prefix+'-preserve.json'),JSON.stringify({...identity,status:checks.every(c=>c.passed)?'passed':'failed',checks,cta_navigation:preserved.contact},null,2));
  await fs.writeFile(path.join(record.run,'captures.json'),JSON.stringify(captures,null,2));
  console.log({fixture:record.name,searchCounts:counts,cta_navigation:preserved.contact});
}
console.log('Captures ready. Inspect screenshots, record actual observations, then assemble QA. Space remains open for the next phase.');
