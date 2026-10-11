const { chromium } = require('playwright');
const fs=require('node:fs');const path=require('node:path');
const base=(process.argv[2]||'http://127.0.0.1:8080/').replace(/\/?$/,'/');
const qa=path.join(__dirname,'..','qa');fs.mkdirSync(qa,{recursive:true});
const local=base.startsWith('file:');
(async()=>{
  const launch={headless:true};
  if(process.env.CHROMIUM_EXECUTABLE)launch.executablePath=process.env.CHROMIUM_EXECUTABLE;
  const browser=await chromium.launch(launch);const page=await browser.newPage();
  const failures=[],checks=[],networkErrors=[];page.on('pageerror',e=>failures.push('JavaScript: '+e.message));
  page.on('response',r=>{if(r.url().startsWith(base)&&r.status()>=400)networkErrors.push(r.url()+': '+r.status());});
  const pages=['index.html','experience.html','engineering.html','technical-sales.html','operations.html','projects.html','resumes.html','contact.html','case-takeoff.html','case-schedule-review.html','case-equipment-evaluation.html','case-document-control.html','training.html','resume-engineering.html','resume-technical-sales.html','resume-operations.html','sample-takeoff.html','sample-schedule-review.html','sample-equipment-evaluation.html','sample-document-control.html','404.html'];
  let axePath;try{axePath=require.resolve('axe-core/axe.min.js');}catch{}
  const a11y=[],focusedAudit=[];
  for(const width of [320,390,768,1365]){
    await page.setViewportSize({width,height:950});
    for(const file of pages){
      const resp=await page.goto(base+file);if(!local&&(!resp||resp.status()!==200))failures.push(file+': non-200');
      const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);
      if(overflow)failures.push(`${file} overflow at ${width}`);
      checks.push({page:file,width,overflow});
      if(width===390){
        const problems=await page.evaluate(()=>{
          const issues=[];
          if(document.querySelectorAll('main').length!==1)issues.push('Exactly one main landmark required');
          for(const el of document.querySelectorAll('a,button')){if(!el.textContent.trim()&&!el.getAttribute('aria-label'))issues.push('Unnamed link or button');}
          for(const el of document.querySelectorAll('input')){if(!el.labels?.length&&!el.getAttribute('aria-label'))issues.push('Unlabelled input');}
          for(const el of document.querySelectorAll('[aria-controls]')){if(!document.getElementById(el.getAttribute('aria-controls')))issues.push('Missing aria-controls target');}
          let prior=0;for(const el of document.querySelectorAll('main h1,main h2,main h3,main h4')){const n=Number(el.tagName[1]);if(prior&&n>prior+1)issues.push('Skipped heading level at '+el.textContent);prior=n;}
          const rgb=s=>(s.match(/[\d.]+/g)||[]).map(Number);
          const lum=a=>a.slice(0,3).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
          for(const el of document.querySelectorAll('main *,header *,footer *')){
            if(!Array.from(el.childNodes).some(n=>n.nodeType===3&&n.textContent.trim())||el.namespaceURI!=='http://www.w3.org/1999/xhtml'||!el.getClientRects().length)continue;
            const st=getComputedStyle(el);if(st.display==='none'||st.visibility==='hidden')continue;
            const fg=rgb(st.color);let bg=[255,255,255,1],at=el;
            while(at){const c=rgb(getComputedStyle(at).backgroundColor);if(c.length===3||c[3]===1){bg=c;break;}at=at.parentElement;}
            const l1=lum(fg),l2=lum(bg),ratio=(Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05);
            const size=parseFloat(st.fontSize),bold=parseInt(st.fontWeight)>=700,minimum=size>=24||(bold&&size>=18.66)?3:4.5;
            if(ratio+.02<minimum)issues.push('Text contrast '+ratio.toFixed(2)+': '+el.textContent.trim().slice(0,50));
          }
          return issues;
        });focusedAudit.push({page:file,issues:problems});failures.push(...problems.map(x=>file+': '+x));
      }
      if(width===390&&['index.html','projects.html','case-equipment-evaluation.html','resumes.html'].includes(file)||width===1365&&['index.html','experience.html','case-takeoff.html'].includes(file))await page.screenshot({path:path.join(qa,`${file.replace('.html','')}-${width}.png`),fullPage:true});
      if(axePath&&width===390){await page.addScriptTag({path:axePath});const result=await page.evaluate(async()=>await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}}));for(const v of result.violations)a11y.push({page:file,id:v.id,impact:v.impact,nodes:v.nodes.length});}
    }
  }
  await page.setViewportSize({width:390,height:850});await page.goto(base+'index.html');
  await page.keyboard.press('Tab');if(await page.locator(':focus').textContent()!=='Skip to content')failures.push('Skip link not first keyboard target');
  await page.getByRole('button',{name:'Menu',exact:true}).click();
  if(await page.locator('.menu').getAttribute('aria-expanded')!=='true')failures.push('Mobile menu did not open');
  await page.keyboard.press('Escape');if(await page.locator('.menu').getAttribute('aria-expanded')!=='false')failures.push('Escape did not close menu');
  await page.goto(base+'case-equipment-evaluation.html');
  await page.locator('#load').fill('3');if(!(await page.locator('#supply-result').textContent()).includes('does not meet'))failures.push('Calculator high-load boundary');
  await page.locator('#load').fill('');if(!(await page.locator('#supply-result').textContent()).includes('Enter a load'))failures.push('Calculator blank boundary');
  await page.locator('#load').fill('0');if(!(await page.locator('#supply-result').textContent()).includes('0.000 A'))failures.push('Calculator zero boundary');
  await page.locator('#load').fill('1.5');await page.locator('#reserve').fill('25');if(!(await page.locator('#supply-result').textContent()).includes('1.875 A'))failures.push('Calculator baseline');
  const downloads=[];
  await page.goto(base+'resumes.html');
  for(const href of await page.locator('main a[download]').evaluateAll(a=>a.map(x=>x.getAttribute('href')))){
    let data,status;
    if(local){data=fs.readFileSync(require('node:url').fileURLToPath(base+href));status='local file';}
    else{const resp=await page.request.get(base+href);data=await resp.body();status=resp.status();}
    const valid=href.endsWith('.pdf')?data.subarray(0,5).toString()==='%PDF-':data.subarray(0,2).toString()==='PK';
    downloads.push({path:href,status,bytes:data.length,valid});if((!local&&status!==200)||!valid)failures.push('Invalid download '+href);
  }
  failures.push(...networkErrors);if(a11y.length)failures.push('Accessibility violations: '+a11y.length);
  const report={base,responsive_checks:checks.length,checks,keyboard_menu:'completed',calculator_boundaries:'completed',automated_accessibility:axePath?'axe WCAG A/AA and focused checks completed':'Focused landmark, names, labels, heading, ARIA target and text contrast checks completed; full axe scan unavailable locally',focusedAudit,a11y,downloads,failures};
  fs.writeFileSync(path.join(qa,'browser-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({...report,checks:undefined},null,2));await browser.close();if(failures.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
