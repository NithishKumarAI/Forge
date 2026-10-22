const fs=require('node:fs'),assert=require('node:assert/strict');
const {chromium}=require(process.env.FORGE_PLAYWRIGHT_MODULE);
const state=JSON.parse(fs.readFileSync(process.argv[2],'utf8')),phase=process.argv[3];
(async()=>{const browser=await chromium.launch({headless:true});try{
 const page=await browser.newPage();await page.route('**/*',r=>r.request().url().startsWith(state.base+'/')?r.continue():r.abort());
 await page.goto(`${state.base}/tests/${state.id}`);await page.getByRole('heading',{name:'Timed practice tests',exact:true}).waitFor();
 if(phase==='start'){await page.getByRole('timer').waitFor();assert(await page.locator('article').nth(1).locator('input[value="a"]').isChecked());}
 else{await page.getByRole('heading',{name:/33.33%/}).waitFor();assert.equal(await page.getByRole('timer').count(),0);}
 console.log('PASS actual timed-test browser '+phase);
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
