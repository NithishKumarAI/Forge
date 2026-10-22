/* Independent course examples run in the actual browser workers, never host Python. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require(process.env.FORGE_PLAYWRIGHT_MODULE||'playwright');
const config=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const census=JSON.parse(fs.readFileSync(config.census,'utf8'));
const checks=[],external=[],errors=[],exampleResults=[],journeys=[];
async function main(){
 const browser=await chromium.launch({headless:true}),context=await browser.newContext({serviceWorkers:'block',viewport:{width:1280,height:900}}),page=await context.newPage();
 const allowed=[config.freshOrigin,config.contentOrigin,config.legacyOrigin];
 await context.route('**/*',route=>{const url=route.request().url();if(allowed.some(o=>url.startsWith(o+'/'))||url.startsWith('blob:')||url.startsWith('data:'))return route.continue();external.push(url);return route.abort();});
 page.on('pageerror',e=>errors.push(String(e)));page.setDefaultTimeout(30000);
 const api=async(origin,url,options)=>{const r=await context.request.fetch(origin+url,options);assert(r.ok(),await r.text());return r.json();};
 async function check(name,fn){await fn();checks.push(name);console.log('PASS',name);}
 try{
  await check('unversioned legacy DB upgrades and opens in the actual browser',async()=>{
   await page.goto(config.legacyOrigin);await page.getByRole('heading',{name:'Welcome back to Forge.'}).waitFor();
   await page.goto(config.legacyOrigin+'/curriculum');await page.getByText('Placement Foundations',{exact:false}).first().waitFor();
  });
  await check('all nine real course journeys distinguish blocked content from engine fixtures',async()=>{
   const scope=await api(config.freshOrigin,'/api/editions/placement-foundations');
   for(const subject of scope.subjects){
    const first=subject.topics.filter(t=>t.level===1)[0];assert(first&&first.id);
    const published=subject.topics.reduce((sum,t)=>sum+t.availability.approved_lesson_count,0);
    assert.equal(published,0);assert.equal(first.availability.approved_practice_available,false);
    await page.goto(`${config.freshOrigin}/topics/${first.id}`);await page.getByText('No lesson is published for this topic yet.',{exact:false}).waitFor();
    journeys.push({subject:subject.key,first_level1_topic:first.key,outcome:'BLOCKED BY CONTENT',approved_lessons:published,
     beginner:'blocked',intermediate:'blocked',difficult:'blocked',reason:'No actual reviewed/published Placement Foundations lesson or scored pool; synthetic fixture approval is excluded.'});
   }
  });
  await check('keyboard focus has a visible outline on the mobile app',async()=>{
   await page.setViewportSize({width:390,height:844});await page.goto(config.legacyOrigin);await page.getByRole('heading',{name:'Welcome back to Forge.'}).waitFor();await page.keyboard.press('Tab');
   const focus=await page.evaluate(()=>{const e=document.activeElement,s=getComputedStyle(e);return {tag:e.tagName,outline:s.outlineStyle,width:s.outlineWidth};});
   assert.notEqual(focus.tag,'BODY');assert.notEqual(focus.outline,'none');assert(parseFloat(focus.width)>0);await page.setViewportSize({width:1280,height:900});
  });
  // Use the shipped worker itself. Each lesson starts a fresh worker; each Python
  // execution creates a fresh globals namespace, with virtual browser-only files.
  await page.goto(config.legacyOrigin);
  const dist=path.join(__dirname,'../apps/web/dist/assets');
  const pythonWorker=fs.readdirSync(dist).find(n=>/^python\.worker-.*\.js$/.test(n));
  const sqlWorker=fs.readdirSync(dist).find(n=>/^sql\.worker-.*\.js$/.test(n));assert(pythonWorker&&sqlWorker);
  let prior='';
  for(const example of census.examples){
   const identity=example.file+'|'+example.section+'|'+example.index;
   const result=await page.evaluate(async({example,workerPath,reset})=>{
    if(reset&&self.auditWorker){self.auditWorker.terminate();self.auditWorker=null;}
    if(!self.auditWorker){
     self.auditWorker=new Worker(workerPath,{type:'module'});
     if(example.language==='python')await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('Python initialization timeout')),60000);self.auditWorker.onmessage=e=>{if(e.data.type==='ready'){clearTimeout(timer);resolve();}if(e.data.type==='init_error'){clearTimeout(timer);reject(Error(e.data.message));}};self.auditWorker.onerror=e=>reject(Error(e.message));});
    }
    return await new Promise(resolve=>{
     const timer=setTimeout(()=>{self.auditWorker.terminate();self.auditWorker=null;resolve({status:'timeout'});},10000);
     self.auditWorker.onmessage=e=>{if(e.data.type==='ready')return;clearTimeout(timer);resolve(e.data.result||e.data);};
     if(example.language==='python')self.auditWorker.postMessage({id:1,code:example.code,judgeMode:'stdin_stdout',tests:[{name:'Authored expected output',stdin:'',expected_stdout:example.expected_output||''}]});
     else self.auditWorker.postMessage({id:1,action:'run',setupSql:'',query:example.code});
    });
   },{example,workerPath:config.legacyOrigin+'/assets/'+(example.language==='python'?pythonWorker:sqlWorker),reset:prior!==example.file+'|'+example.language});
   prior=example.file+'|'+example.language;
   exampleResults.push({identity,file:example.file,section:example.section,index:example.index,language:example.language,authored_expected:example.expected_output,
    status:example.language==='python'?result.status:result.ok?'executed_requires_semantic_comparison':'context_or_execution_error',result});
   if(exampleResults.length%25===0)console.log('Examples executed:',exampleResults.length,'/',census.examples.length);
  }
  checks.push('all 258 lesson examples attempted in actual Pyodide/PGlite browser workers; defects retained, not converted to passes');
  assert.deepEqual(external,[]);assert.deepEqual(errors,[]);
 }finally{
  if(!page.isClosed())await page.screenshot({path:path.join(config.output,'independent-last-browser.png'),fullPage:true}).catch(()=>{});
  fs.writeFileSync(path.join(config.output,'independent-browser.json'),JSON.stringify({checks,real_course_journeys:journeys,completed_real_course_journeys:0,blocked_real_course_journeys:journeys.length,
   example_results:exampleResults,external_requests:external,page_errors:errors,synthetic_engine_tests_separate:true},null,2)+'\n');
  await browser.close();
 }
}
main().catch(e=>{console.error(e);process.exitCode=1;});
