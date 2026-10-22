/* Actual installed Chromium journeys. Every browser external request is denied. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require(process.env.FORGE_PLAYWRIGHT_MODULE||'playwright');
const config=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const fixture=JSON.parse(fs.readFileSync(config.fixture,'utf8'));
const checks=[],external=[],pageErrors=[],consoleErrors=[],requests=[];
let browser,context,page,base=config.contentOrigin;
const startTime=Date.now();
function waitResponse(predicate){const pending=page.waitForResponse(predicate);pending.catch(()=>{});return pending;}
async function check(name,run){const started=Date.now();try{await run();checks.push({name,status:'passed',milliseconds:Date.now()-started});console.log('PASS',name);}catch(error){checks.push({name,status:'failed',error:String(error)});throw error;}}
async function api(endpoint,method='GET',body){
 const response=await context.request.fetch(base+endpoint,{method,data:body});
 if(!response.ok())throw Error(`${method} ${endpoint}: ${response.status()} ${await response.text()}`);
 return response.json();
}
function safe(item){const text=JSON.stringify(item.contract);for(const key of ['reference_solution','hidden_tests','hidden_datasets','expected_rows','"correct":'])assert(!text.includes(key),`Answer leak: ${key}`);}
async function editor(scope,source){
 const input=scope.locator('.monaco-editor').first();await input.waitFor({state:'visible',timeout:60000});
 // Modern Monaco uses the browser EditContext API instead of a hidden textarea.
 await input.click({position:{x:100,y:30}});await page.keyboard.press('Control+A');await page.keyboard.insertText(source);
}
async function fill(scope,item,wrong=false){
 if(item.kind==='python'||item.kind==='sql'){
  assert(fixture.sources[item.item_key],`Missing fixture source for ${item.item_key}`);await editor(scope,fixture.sources[item.item_key]);
 }else if(item.kind==='numeric')await scope.getByLabel('Decimal answer',{exact:true}).fill(wrong?'99999':fixture.answers[item.item_key]);
 else if(item.kind==='single_choice'){
  const correct=fixture.answers[item.item_key]||'a',key=wrong?Object.keys(item.contract.choices).find(k=>k!==correct):correct;
  await scope.locator(`input[value="${key}"]`).check();
 }else throw Error('Unexpected fixture kind '+item.kind);
}
async function practice(subject,{wrong=false,run=false}={}){
 await page.goto(`${base}/topics/${fixture.topics[subject]}/practice`);
 const response=waitResponse(r=>r.url()===base+'/api/assessment/start'&&r.request().method()==='POST');
 await page.getByRole('button',{name:'Start',exact:true}).click();const selected=await (await response).json();safe(selected);
 const card=page.locator('article').first();await fill(card,selected,wrong);
 if(run){await card.getByRole('button',{name:'Run public samples',exact:true}).click();
  const status=card.getByRole('status');await status.waitFor({timeout:90000});
  const output=await status.innerText();assert(output.includes(selected.kind==='python'?'Public samples: passed':'"id"'),output);
 }
 const submitted=waitResponse(r=>r.url().endsWith(`/api/assessment/${selected.id}/submit`)&&r.request().method()==='POST');
 await card.getByRole('button',{name:'Submit',exact:true}).click();const result=await submitted;assert(result.ok(),await result.text());
 const value=await result.json();assert.equal(value.result.passed,!wrong);await card.getByText(wrong?/Not passed/:/Passed ·/).waitFor();
 return {selected,result:value,body:result.request().postDataJSON()};
}

async function main(){
 browser=await chromium.launch({headless:true});context=await browser.newContext({viewport:{width:1280,height:900},serviceWorkers:'block'});
 const allowed=[config.contentOrigin,config.freshOrigin];
 await context.route('**/*',route=>{const url=route.request().url();if(allowed.some(origin=>url.startsWith(origin+'/'))||url.startsWith('blob:')||url.startsWith('data:'))return route.continue();external.push(url);return route.abort();});
 page=await context.newPage();page.setDefaultTimeout(20000);
 page.on('pageerror',error=>pageErrors.push(String(error)));
 page.on('console',message=>{if(message.type()==='error')consoleErrors.push(message.text());});
 context.on('request',request=>{if(request.url().includes('/assets/'))requests.push(request.url());});
 try{
  await check('new installation, preview, explicit confirmation/activation and missing pools',async()=>{
   await page.goto(config.freshOrigin);await page.getByRole('heading',{name:'Welcome back to Forge.'}).waitFor();
   await page.goto(config.freshOrigin+'/curriculum');await page.getByRole('button',{name:'Create reviewable draft',exact:true}).click();
   await page.getByRole('button',{name:'Review curriculum',exact:true}).click();
   await page.getByLabel('Your name',{exact:true}).fill('SYNTHETIC BROWSER TEST REVIEWER');
   await page.getByRole('checkbox',{name:'I reviewed all nine subjects',exact:false}).check();
   await page.getByRole('checkbox',{name:'I understand which content is missing',exact:false}).check();
   await page.getByRole('button',{name:'Confirm reviewed curriculum',exact:true}).click();
   await page.getByRole('button',{name:'Activate this curriculum',exact:true}).click();
   await page.getByText('Your active Placement Foundations curriculum',{exact:true}).waitFor();
   const overview=await (await context.request.get(config.freshOrigin+'/api/editions/placement-foundations')).json();
   const first=overview.subjects[0].topics[0].id;await page.goto(`${config.freshOrigin}/topics/${first}/practice`);
   await page.getByRole('button',{name:'Start',exact:true}).click();await page.getByRole('alert').filter({hasText:'No approved questions'}).waitFor();
   await page.goto(config.freshOrigin+'/tests');await page.getByRole('button',{name:'Start timed test',exact:true}).click();
   await page.getByRole('alert').filter({hasText:'No approved unused test pool'}).waitFor();
  });
  await check('approved fixture lesson navigation and section completion do not change mastery',async()=>{
   const before=await api(`/api/topics/${fixture.topics.python}/mastery`);await page.goto(`${base}/topics/${fixture.topics.python}/learn`);
   await page.getByRole('heading',{name:'Goal and intuition',exact:true}).waitFor();await page.getByRole('button',{name:'Next',exact:true}).click();
   await page.getByRole('heading',{name:'A worked example and why it works',exact:true}).waitFor();
   assert.equal((await api(`/api/topics/${fixture.topics.python}/mastery`)).mastery_score,before.mastery_score);
  });
  await check('static local search, exact revision navigation and legacy chat',async()=>{
   await page.goto(base+'/guidance');await page.getByLabel('Search local lessons').fill('stationery');await page.getByRole('button',{name:'Search',exact:true}).click();
   await page.locator('article').first().waitFor();assert((await page.locator('article').first().innerText()).includes('revision'));
   await page.locator('article').first().getByRole('link').first().click();await page.getByRole('heading',{name:'A worked example and why it works',exact:true}).waitFor();
   await page.goto(base+'/guidance');await page.getByRole('button',{name:'Read legacy conversation history',exact:true}).click();
   await page.getByText('SYNTHETIC HISTORICAL CHAT:',{exact:false}).waitFor();
  });
  await check('MCQ incorrect response and exact numeric grading with duplicate-submit protection',async()=>{
   await practice('verbal-english',{wrong:true});const result=await practice('quantitative-aptitude');
   const before=await api(`/api/practice/topics/${fixture.topics['quantitative-aptitude']}/history`);
   const duplicate=await api(`/api/assessment/${result.selected.id}/submit`,'POST',result.body);assert.equal(duplicate.id,result.selected.id);
   assert.equal((await api(`/api/practice/topics/${fixture.topics['quantitative-aptitude']}/history`)).attempt_count,before.attempt_count);
   const stale=await context.request.post(base+`/api/assessment/${result.selected.id}/submit`,{data:{...result.body,content_sha256:'0'.repeat(64)}});assert.equal(stale.status(),409);
  });
  await check('Python browser Run and backend Submit on two independent practice items',async()=>{await practice('python',{run:true});await practice('python');});
  await check('SQL browser Run and full backend Submit use isolated databases',async()=>{await practice('sql-postgresql',{run:true});});
  await check('clean Python transfer uses stored independent variant and preserves 89 cap',async()=>{
   await page.goto(`${base}/topics/${fixture.topics.python}/transfer`);const pending=waitResponse(r=>r.url().endsWith('/api/assessment/start'));
   await page.getByRole('button',{name:'Start',exact:true}).click();const item=await (await pending).json();assert.equal(item.purpose,'transfer');safe(item);
   await fill(page.locator('article').first(),item);await page.getByRole('button',{name:'Submit',exact:true}).click();await page.getByText(/Passed · 100%/).waitFor();
   assert.equal((await api(`/api/topics/${fixture.topics.python}/mastery`)).mastery_score,89);
  });
  await check('due delayed recall after actual 24-hour fixture gate updates FSRS/mastery',async()=>{
   await page.goto(base+'/review');const pending=waitResponse(r=>r.url().endsWith('/api/assessment/start'));
   await page.getByRole('button',{name:'Start due recall',exact:true}).first().click();const item=await (await pending).json();assert.equal(item.topic_id,fixture.topics.dsa);
   await fill(page.locator('article').first(),item);await page.getByRole('button',{name:'Submit',exact:true}).click();await page.getByText(/Passed · 100%/).waitFor();
   assert((await api(`/api/topics/${fixture.topics.dsa}/mastery`)).mastery_score>=90);
  });
  await check('Arena failure, tracked hint, pass and explicit pre-pass Give Up',async()=>{
   await page.goto(base+'/arena/problems/python-normalize-name');await page.getByRole('heading',{name:'Normalize a display name',exact:true}).waitFor();
   assert.equal(await page.getByRole('heading',{name:'Forge solution',exact:true}).count(),0);
   await editor(page,"def normalize_name(value):\n    return 'wrong'");let pending=waitResponse(r=>r.url().endsWith('/python-normalize-name/submit'));
   await page.getByRole('button',{name:'Submit',exact:true}).click();assert.equal((await (await pending).json()).passed,false);
   await page.getByRole('button',{name:'Reveal hint',exact:false}).click();await editor(page,"def normalize_name(value):\n    return ' '.join(value.split()).title()");
   pending=waitResponse(r=>r.url().endsWith('/python-normalize-name/submit'));await page.getByRole('button',{name:'Submit',exact:true}).click();assert.equal((await (await pending).json()).passed,true);
   await page.getByRole('heading',{name:'Forge solution',exact:true}).waitFor();
   await page.goto(base+'/arena/problems/python-count-vowels');await page.getByRole('button',{name:'Give up',exact:true}).click();await page.getByRole('heading',{name:'Forge solution',exact:true}).waitFor();
  });
  await check('coding timed test uses local workers and embargoes feedback until completion',async()=>{
   const before=await api(`/api/topics/${fixture.topics.python}/mastery`);await page.goto(base+'/tests');
   await page.getByLabel('Test type',{exact:true}).selectOption('coding');let pending=waitResponse(r=>r.url().endsWith('/api/timed-tests/start'));
   await page.getByRole('button',{name:'Start timed test',exact:true}).click();const session=await(await pending).json();assert.equal(session.questions.length,3);
   for(const q of session.questions){safe(q.assessment);const card=page.locator('article').nth(q.position);await fill(card,q.assessment);
    pending=waitResponse(r=>r.url().includes('/answer'));await card.getByRole('button',{name:'Submit',exact:true}).click();await pending;await card.getByText(/Response saved/).waitFor();}
   assert.equal(await page.getByText('Worked answer after completion',{exact:true}).count(),0);
   await page.getByRole('button',{name:'Finish test and view report',exact:true}).click();await page.getByRole('heading',{name:/100%/}).waitFor();
   assert.equal((await api(`/api/topics/${fixture.topics.python}/mastery`)).mastery_score,before.mastery_score);
  });
  await check('timed draft survives refresh with its original deadline and fixed scoring',async()=>{
   await page.goto(base+'/tests');await page.getByLabel('Subject',{exact:true}).selectOption('quantitative-aptitude');
   let pending=waitResponse(r=>r.url().endsWith('/api/timed-tests/start'));await page.getByRole('button',{name:'Start timed test',exact:true}).click();const session=await(await pending).json();
   await fill(page.locator('article').first(),session.questions[0].assessment);pending=waitResponse(r=>r.url().includes('/draft'));
   await page.locator('article').first().getByRole('button',{name:'Save draft',exact:true}).click();await pending;await page.reload();await page.getByRole('timer').waitFor();
   assert.equal((await api('/api/timed-tests/'+session.id)).deadline_at,session.deadline_at);assert(await page.locator('article').first().locator('input[value="a"]').isChecked());
   for(const q of session.questions){const card=page.locator('article').nth(q.position);await fill(card,q.assessment,q.position===2);pending=waitResponse(r=>r.url().includes('/answer'));await card.getByRole('button',{name:'Submit',exact:true}).click();await pending;await card.getByText(/Response saved/).waitFor();}
   await page.getByRole('button',{name:'Finish test and view report',exact:true}).click();await page.getByRole('heading',{name:/66.67%/}).waitFor();
  });
  await check('mixed test applies the disclosed fixed negative marking',async()=>{
   await page.goto(base+'/tests');await page.getByLabel('Test type',{exact:true}).selectOption('mixed');let pending=waitResponse(r=>r.url().endsWith('/api/timed-tests/start'));
   await page.getByRole('button',{name:'Start timed test',exact:true}).click();const session=await(await pending).json();
   for(const q of session.questions){const card=page.locator('article').nth(q.position);await fill(card,q.assessment,q.position===0);pending=waitResponse(r=>r.url().includes('/answer'));await card.getByRole('button',{name:'Submit',exact:true}).click();await pending;await card.getByText(/Response saved/).waitFor();}
   await page.getByRole('button',{name:'Finish test and view report',exact:true}).click();await page.getByRole('heading',{name:/79.17%/}).waitFor();
  });
  await check('objective interview withholds feedback and communication remains unscored',async()=>{
   await page.goto(base+'/interview');let pending=waitResponse(r=>r.url().endsWith('/api/interviews/start'));
   await page.getByRole('button',{name:'Start objective interview',exact:true}).click();const session=await(await pending).json();
   const denied=await context.request.get(base+'/api/guidance/search?q=help');assert.equal(denied.status(),409);
   for(const [index,q] of session.questions.entries()){safe(q.assessment);const card=page.locator('article').nth(index);await fill(card,q.assessment);
    pending=waitResponse(r=>r.url().endsWith(`/api/interviews/${session.id}/answer`));await card.getByRole('button',{name:'Submit',exact:true}).click();await pending;await card.getByText(/Response saved/).waitFor();}
   assert.equal(await page.getByText(/Passed · 100%/).count(),0);await page.getByRole('button',{name:'Complete and view report',exact:true}).click();await page.getByText('Forge Interview Score: 100%',{exact:true}).waitFor();
   await page.goto(base+'/interview');await page.getByRole('button',{name:'Start communication rehearsal',exact:true}).click();await page.getByLabel('Reflection response').first().waitFor();
   for(let i=0;i<7;i++){await page.locator('textarea:not([disabled])').first().fill('Synthetic rehearsal: I built a notes project, checked search, and can explain its limits.');await page.getByRole('button',{name:'Save reflection',exact:true}).first().click();await page.waitForFunction(n=>document.querySelectorAll('textarea:not([disabled])').length===n,6-i);}
   await page.getByRole('button',{name:'Complete and view report',exact:true}).click();await page.getByRole('heading',{name:'Saved interview report',exact:true}).waitFor();await page.getByText('Reflection only',{exact:true}).waitFor();
  });
  await check('saved legacy report remains readable with its original raw fields',async()=>{
   await page.goto(`${base}/interview/${fixture.legacy_interview_id}/report`);await page.getByText('HISTORICAL_SYNTHETIC_NOT_REWRITTEN',{exact:false}).waitFor();
  });
  await check('planner presets regenerate explicitly and preserve terminal task history',async()=>{
   await page.goto(base);await page.getByRole('heading',{name:'Today’s study plan',exact:true}).waitFor();
   for(const hours of [5,6,8]){await page.getByRole('button',{name:`${hours} hours · ${hours*60} min`,exact:true}).click();await page.getByRole('status').filter({hasText:'Target saved'}).waitFor();
    let pending=waitResponse(r=>r.url().endsWith('/api/planner/regenerate'));await page.getByRole('button',{name:'Regenerate plan safely',exact:true}).click();const plan=await(await pending).json();assert.equal(plan.target_minutes,hours*60);assert.equal(plan.scheduled_minutes+plan.completed_minutes+plan.unallocated_minutes,plan.target_minutes);}
   const before=await api('/api/planner/today');if(before.items.length){await page.getByRole('button',{name:/^Complete /}).first().click();await page.getByText(/min · completed/).first().waitFor();const done=(await api('/api/planner/today')).items.find(i=>i.status==='completed');assert(done);
    await page.getByRole('button',{name:'Regenerate plan safely',exact:true}).click();await page.getByText(/min · completed/).first().waitFor();assert((await api('/api/planner/today')).items.some(i=>i.id===done.id&&i.status==='completed'));}
  });
  await check('mobile layout and visible keyboard focus',async()=>{
   await page.setViewportSize({width:390,height:844});await page.goto(base);await page.getByRole('heading',{name:'Today’s study plan',exact:true}).waitFor();
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));await page.screenshot({path:path.join(config.images,'synthetic-mobile-dashboard.png'),fullPage:true});
   await page.keyboard.press('Tab');assert(await page.evaluate(()=>document.activeElement!==document.body));
   await page.goto(base+'/tests');await page.getByRole('heading',{name:'Timed practice tests',exact:true}).waitFor();assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));
   await page.screenshot({path:path.join(config.images,'synthetic-mobile-tests.png'),fullPage:true});
  });
  await check('all exercised browser assets remain local with no page errors',async()=>{
   assert.deepEqual(external,[]);assert.deepEqual(pageErrors,[]);assert(requests.some(url=>url.includes('.wasm')),'No local worker WASM was requested');
  });
 }finally{
  if(page&&!page.isClosed())await page.screenshot({path:path.join(config.images,'last-browser-state.png'),fullPage:true}).catch(()=>{});
  const report={checks,passed:checks.filter(c=>c.status==='passed').length,failed:checks.filter(c=>c.status==='failed').length,external_requests:external,page_errors:pageErrors,console_errors:consoleErrors,
   asset_requests:[...new Set(requests)],external_browser_network_denied:true,python_network_provider_guard:true,synthetic_fixtures_only:true,duration_ms:Date.now()-startTime};
  fs.writeFileSync(config.report,JSON.stringify(report,null,2)+'\n');await browser.close();
 }
}
main().catch(error=>{console.error(error);process.exitCode=1;});
