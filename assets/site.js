document.documentElement.classList.add('js');
const menu = document.querySelector('.menu');
const nav = document.querySelector('.nav');
if(menu && nav){
  menu.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));nav.classList.toggle('open',open);});
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&menu.getAttribute('aria-expanded')==='true'){menu.setAttribute('aria-expanded','false');nav.classList.remove('open');menu.focus();}});
}
const copy=document.querySelector('[data-copy-email]');
if(copy){copy.addEventListener('click',async()=>{const status=document.querySelector('#copy-status');try{await navigator.clipboard.writeText('cruzericjohn@gmail.com');status.textContent='Email address copied.';}catch{status.textContent='Please select and copy the email address above.';}});}
const form=document.querySelector('#supply-form');
if(form){
  const update=()=>{const loadEl=form.querySelector('#load'),reserveEl=form.querySelector('#reserve'),result=form.querySelector('#supply-result');const load=Number(loadEl.value),reserve=Number(reserveEl.value);if(loadEl.value===''||reserveEl.value===''||!Number.isFinite(load)||!Number.isFinite(reserve)||load<0||load>20||reserve<0||reserve>100){result.textContent='Enter a load from 0 to 20 A and reserve from 0 to 100%.';return;}const need=load*(1+reserve/100);result.innerHTML=`Required steady-state capacity: <strong>${need.toFixed(3)} A</strong> at 24 V DC (${(need*24).toFixed(1)} W). ${need<=2.5?'Option B meets this numerical capacity check.':'Option B does not meet this numerical capacity check.'} Inrush, installation and supplier confirmation remain required.`;};
  form.addEventListener('input',update);form.addEventListener('submit',e=>e.preventDefault());update();
}
