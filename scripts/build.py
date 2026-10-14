"""Generate the static career package from shared facts and checked demo inputs."""
from pathlib import Path
from html import escape as esc
import argparse, json, shutil, math, re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
PROFILE = json.loads((ROOT / 'content/profile.json').read_text(encoding='utf-8'))
BASE = ''

def table(headers, rows, caption=''):
    head = ''.join(f'<th scope="col">{esc(str(x))}</th>' for x in headers)
    body = ''.join('<tr>'+''.join(f'<td>{esc(str(v))}</td>' for v in row)+'</tr>' for row in rows)
    return f'<div class="table-wrap" role="region" aria-label="{esc(caption or "Data table")}" tabindex="0"><table>{"<caption>"+esc(caption)+"</caption>" if caption else ""}<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'

def ul(items): return '<ul>'+''.join('<li>'+esc(x)+'</li>' for x in items)+'</ul>'
def p(text): return '<p>'+esc(text)+'</p>'
def btn(text, href, secondary=False): return f'<a class="button{" secondary" if secondary else ""}" href="{esc(href)}">{esc(text)}</a>'

def svg_shell(body, label, dark=False):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 360" role="img" aria-label="{esc(label)}"><title>{esc(label)}</title><rect width="600" height="360" fill="{"#183b43" if dark else "#e7efe7"}"/>{body}</svg>'

POINTS = {
  'lighting': [(x,y) for y in [105,180,255] for x in [145,250,355,460]],
  'outlets': [(x,y) for x,y in [(95,100),(95,170),(95,250),(185,300),(280,300),(380,300),(485,300),(515,100),(515,175),(515,250),(185,65),(315,65),(445,65)]]
}

def plan_svg(dark=False):
    color='#c6e4d6' if dark else '#2d6453'
    b=f'<g fill="none" stroke="{color}" stroke-width="2"><path d="M85 55H525V310H85Z M305 55V135 M305 225V310"/><path d="M305 135A90 90 0 0 1 395 225" stroke-dasharray="4 5"/><path d="M305 225H395"/>'
    for x,y in POINTS['lighting']:b+=f'<circle cx="{x}" cy="{y}" r="12"/><path d="M{x-8} {y-8}l16 16m-16 0l16 -16"/>'
    for x,y in POINTS['outlets']:b+=f'<rect x="{x-6}" y="{y-6}" width="12" height="12" fill="{color}"/>'
    b+=f'</g><g font-family="Arial,sans-serif" fill="{color}" font-size="13"><text x="85" y="30">E-DEMO-01 / SYMBOL COUNT EXERCISE</text><text x="85" y="340">12 LIGHT POINTS</text><text x="275" y="340">13 OUTLET LOCATIONS</text><text x="85" y="290">ZONE A</text><text x="355" y="290">ZONE B</text></g>'
    return svg_shell(b,'Original fictional floor plan with twelve light points and thirteen outlet locations. Not to scale.',dark)

def load_svg():
    b='<g font-family="Arial,sans-serif" fill="#173c43"><text x="45" y="42" font-size="15">CONNECTED LOAD / DEMONSTRATION</text>'
    for label,value,y,width in [('Lighting',0.384,90,76.8),('Workstations',1.32,155,264),('Network equipment',0.09,220,18)]:
        b+=f'<text x="45" y="{y}" font-size="16">{label}</text><rect x="45" y="{y+12}" width="{width}" height="17" rx="3" fill="#32725a"/><text x="465" y="{y+27}" font-size="18">{value:.3f} kVA</text>'
    b+='<text x="45" y="322" font-size="22">Total 1.794 kVA / 7.80 A at 230 V</text></g>'
    return svg_shell(b,'Connected apparent load: lighting 0.384 kVA, workstations 1.320 kVA, network 0.090 kVA; total 1.794 kVA.')

def equipment_svg():
    b='<g font-family="Arial,sans-serif" fill="#173c43"><text x="42" y="40" font-size="15">24 V DC / STEADY-STATE CAPACITY</text>'
    for x,label,amps,state in [(42,'A',1.5,'Below target'),(224,'B',2.5,'Meets target'),(406,'C',1.7,'Derated below')]:
        b+=f'<rect x="{x}" y="75" width="152" height="205" rx="8" fill="white" stroke="#a8bcb0"/><text x="{x+18}" y="110" font-size="17">OPTION {label}</text><text x="{x+18}" y="158" font-size="30">{amps:.1f} A</text><text x="{x+18}" y="197" font-size="12">{state}</text><path d="M{x+18} 225h115m-115 10h115m-115 10h115" stroke="#a8bcb0"/>'
    b+='<text x="42" y="325" font-size="19">Comparison target: 1.875 A / 45 W</text></g>'
    return svg_shell(b,'Fictional power supply options A 1.5 A, B 2.5 A, C 1.7 A after assumed derating. Target is 1.875 A.')

def records_svg():
    b='<g font-family="Arial,sans-serif" fill="#173c43"><text x="42" y="38" font-size="15">DOCUMENT CONTROL / REVIEW STATUS</text>'
    for i,(title,status,rev) in enumerate([('Equipment register','Current','C'),('Cable schedule','Awaiting review','B'),('Test record','Missing attachment','A')]):
        y=70+i*80;b+=f'<rect x="42" y="{y}" width="516" height="63" rx="4" fill="white" stroke="#a8bcb0"/><text x="60" y="{y+25}" font-size="17">{title}</text><text x="60" y="{y+46}" font-size="12">{status}</text><text x="480" y="{y+37}" font-size="18">REV {rev}</text>'
    b+='</g>';return svg_shell(b,'Fictional document register: equipment register current revision C, cable schedule awaiting review, test record missing attachment.')

CASES = [
 {'slug':'takeoff','title':'Office lighting and outlet takeoff (practice)','category':'Electrical estimating','classification':'Practice exercise · fictional data','intro':'A small office example that separates counted devices, measured routes and explicit allowances before they reach the quantity schedule.','visual':plan_svg,
  'context':'A fictional office tender includes two zones, a symbol plan and three route segments. The estimator needs an auditable quantity schedule without converting missing design information into invented quantities.',
  'objective':'Produce a consistent symbol count, route-length build-up and clarification register that another estimator can check.',
  'role':'This is a fictional takeoff exercise prepared with AI assistance for this portfolio, not an estimate delivered to a client.',
  'approach':'Assign stable point IDs, count each symbol once, and reconcile the total against the point register. Keep route length separate from cable quantity. Add vertical and termination allowances explicitly, then apply a stated procurement allowance. No cable size, circuit design or unit price is inferred.',
  'tools':'Structured point register, Python checks, original SVG plan and browser-readable schedule. GroundPlan is part of the related training background; this example was not measured in GroundPlan.',
  'deliverables':'An original symbol plan, 25-row point register, quantity schedule, route build-up and RFI register.',
  'checks':'Confirmed 12 unique lighting points and 13 unique outlet locations, with no duplicate IDs. Route segments total 39 m. Adding 6 m for rises and terminations gives 45 m; a 10% illustrative allowance gives 49.5 m. Quantities in the visual and downloadable data agree.',
  'result':'The quantity table shows where each count and allowance came from, and what remains unresolved.',
  'limit':'The drawing is not to scale. Route lengths and allowances are fictional inputs. The example does not establish cable sizes, circuit suitability, installation compliance, labour or price.'},
 {'slug':'schedule-review','title':'Small office connected-load worksheet (practice)','category':'Electrical documentation','classification':'Practice exercise · fictional data','intro':'A connected-load schedule with units, source assumptions and a review trail. Breaker ratings are kept separate from equipment demand.','visual':load_svg,
  'context':'A preliminary office schedule needs a transparent load total. Using breaker ratings as if they were equipment loads would obscure the actual calculation.',
  'objective':'Create a reviewable schedule from fictional equipment apparent-power inputs and identify the design information still required.',
  'role':'This calculation exercise uses fictional equipment data and was prepared with AI assistance. It is not an issued electrical design.',
  'approach':'Record quantity and apparent power per item in VA, then multiply and sum. At an assumed single-phase 230 V supply, divide total VA by voltage to illustrate aggregate connected current. Apply no diversity. Leave protection and cable sizing outside the numerical load check.',
  'tools':'Structured schedule data, Python arithmetic checks and an original load visual.',
  'deliverables':'Connected-load schedule, calculation note, assumptions and a design review question list.',
  'checks':'12 lights at 32 VA = 384 VA; six workstations at 220 VA = 1,320 VA; one network load at 90 VA = 90 VA. Total = 1,794 VA. Aggregate illustrative current = 1,794 / 230 = 7.80 A. This is not a selected protective-device rating.',
  'result':'Every load in the example can be traced to a quantity and an assumed VA value.',
  'limit':'All loads and voltage are assumed. Actual nameplates, simultaneity, harmonics, starting current, installation conditions, fault level, voltage drop and applicable design requirements remain to be established. No engineering approval is claimed.'},
 {'slug':'equipment-evaluation','title':'24 V DC power supply comparison (practice)','category':'Technical sales support','classification':'Practice exercise · fictional data','intro':'A 24 V DC equipment comparison showing why headline wattage alone is not enough for a quotation recommendation.','visual':equipment_svg,
  'context':'A fictional control panel needs a 24 V DC supply for four device groups. Three fictional supply options have different available output capacities.',
  'objective':'Prepare a concise technical comparison and supplier clarification list before a quotation decision.',
  'role':'This fictional equipment comparison was prepared with AI assistance for this portfolio. No sale or customer procurement decision took place.',
  'approach':'Sum steady-state current and add a stated 25% design reserve for the example. Compare that requirement with each option’s assumed available current, including a hypothetical temperature derating for Option C. Separate a numerical shortlist from a release-to-purchase decision.',
  'tools':'Requirement schedule, comparison matrix, interactive browser calculator and Python checks.',
  'deliverables':'Device current budget, three-option matrix and quotation clarification checklist.',
  'checks':'The four fictional loads total 1.500 A. With 25% reserve, the comparison target is 1.875 A, equivalent to 45 W at 24 V DC. Only Option B’s 2.5 A available capacity meets that target. Option C is assessed at its assumed derated 1.7 A, not its nominal 2.0 A.',
  'result':'Option B passes the example current-capacity check; actual purchasing would still require supplier data.',
  'limit':'Options and specifications are fictional. Reserve is an example assumption, not a code requirement. Inrush, overload behaviour, input supply, ambient conditions, dimensions, approvals, availability and warranty require actual manufacturer data.'},
 {'slug':'document-control','title':'Engineering document revision register (practice)','category':'Engineering operations','classification':'Practice exercise · fictional data','intro':'A fictional industrial document register that separates revisions, missing evidence and review authority so a handover does not hide open work.','visual':records_svg,
  'context':'An engineering team is collecting equipment records, schedules and test documentation. A file existing in a folder does not mean it is current, complete or approved.',
  'objective':'Build an actionable document register and an exception log for a small fictional handover package.',
  'role':'This fictional register is based on the types of records handled in document-control work. It was prepared with AI assistance and contains no employer documents.',
  'approach':'Assign each record a stable ID, required revision, received revision, review status and next owner. Use explicit hold conditions for missing attachments or unresolved revision mismatches. Close a record only when both evidence and review requirements are satisfied.',
  'tools':'Structured document register, JSON records, browser-readable exception table and Python validation.',
  'deliverables':'Five-record document register, three-item exception log, naming convention and handover checklist.',
  'checks':'Confirmed one unique row per document. Three records remain on hold: a cable-schedule revision mismatch, a missing test attachment and an unresolved manual review. The example never reports the complete package as approved.',
  'result':'The register identifies three documents that must remain on hold until their records are corrected or reviewed.',
  'limit':'Every document ID, status and role assignment is fictional. No real facility identifiers, test results, maintenance instructions or proprietary drawings are published.'}
]

DEMO = {
 'classification':'Portfolio practice exercises with fictional inputs; created with AI assistance.',
 'points':[{'id':f'{prefix}{i:02d}','type':kind,'x':x,'y':y} for kind,prefix in [('lighting','L'),('outlets','P')] for i,(x,y) in enumerate(POINTS[kind],1)],
 'route':{'segments_m':[18,12,9],'rise_and_termination_allowance_m':6,'procurement_allowance_fraction':0.10},
 'loads':[{'item':'LED luminaires','quantity':12,'unit_va':32},{'item':'Workstations','quantity':6,'unit_va':220},{'item':'Network equipment','quantity':1,'unit_va':90}],
 'supply':{'voltage_v':24,'load_a':[0.30,0.80,0.15,0.25],'reserve_fraction':0.25,'options':[{'name':'A','nominal_a':1.5,'available_a':1.5},{'name':'B','nominal_a':2.5,'available_a':2.5},{'name':'C','nominal_a':2.0,'available_a':1.7}]},
 'records':[
  {'id':'DOC-001','name':'Equipment register','required':'C','received':'C','review':'Reviewed','attachment':True,'owner':'Document coordinator','next':'File current register'},
  {'id':'DOC-002','name':'Cable schedule','required':'C','received':'B','review':'Pending','attachment':True,'owner':'Discipline engineer','next':'Provide revision C and review'},
  {'id':'DOC-003','name':'Test record','required':'A','received':'A','review':'Pending','attachment':False,'owner':'Site engineer','next':'Attach signed record for review'},
  {'id':'DOC-004','name':'Equipment manual','required':'B','received':'B','review':'Pending','attachment':True,'owner':'Discipline engineer','next':'Complete manual review'},
  {'id':'DOC-005','name':'Drawing index','required':'C','received':'C','review':'Reviewed','attachment':True,'owner':'Document coordinator','next':'Include in transmittal'}]
}

def record_ready(r): return r['required']==r['received'] and r['review']=='Reviewed' and r['attachment']

def details(slug):
    if slug=='takeoff':
        return table(['Item','Basis','Quantity','Unit'],[['Lighting points','Counted symbols',12,'each'],['Outlet locations','Counted symbols',13,'each'],['Horizontal route','18 + 12 + 9',39,'m'],['Rises / terminations','Explicit assumed allowance',6,'m'],['Net route build-up','39 + 6',45,'m'],['Procurement quantity','45 × 1.10',49.5,'m']], 'Takeoff summary')+p('Open RFIs: confirm circuit allocation and cable specification; confirm actual route and vertical dimensions; confirm whether termination slack is already included in the project measurement rules.')
    if slug=='schedule-review':
        rows=[[x['item'],x['quantity'],x['unit_va'],x['quantity']*x['unit_va']] for x in DEMO['loads']]
        return table(['Equipment','Quantity','VA per item','Connected VA'],rows+[['Total','','',1794]],'Connected apparent load')+p('Calculation: 1,794 VA ÷ 230 V = 7.80 A. An apparent-power sum is a preliminary connected-load budget. It does not replace demand assessment or circuit design.')
    if slug=='equipment-evaluation':
        rows=[['Controller',0.30],['Actuators',0.80],['Sensors',0.15],['Auxiliaries',0.25]]
        return table(['Device group','Assumed current at 24 V DC (A)'],rows,'Steady-state load inputs')+table(['Fictional option','Nominal A','Available A','Against 1.875 A'],[['A',1.5,1.5,'Below target'],['B',2.5,2.5,'Meets numerical target'],['C',2.0,1.7,'Below target after assumed derating']],'Quotation comparison')+'''<div class="calculator"><h3>Explore the capacity requirement</h3><p class="small">Change the fictional steady-state load or reserve. Output is a capacity comparison only.</p><form id="supply-form"><div class="fields"><label for="load">Total load at 24 V DC (A)<input id="load" name="load" type="number" min="0" max="20" step="0.01" value="1.5" required></label><label for="reserve">Additional reserve (%)<input id="reserve" name="reserve" type="number" min="0" max="100" step="1" value="25" required></label></div><p class="result" id="supply-result" aria-live="polite">Required capacity: 1.875 A at 24 V DC (45.0 W). Option B meets this numerical check. Supplier confirmation remains required.</p></form></div>'''+p('Supplier questions: confirm continuous output at the actual enclosure temperature, transient load response, input range, dimensions and mounting, protection characteristics, lead time and quotation exclusions. No price comparison is invented.')
    return table(['Record','Required / received','Review','Next action'],[[r['name'],r['required']+' / '+r['received'], 'Ready for transmittal' if record_ready(r) else 'Hold',r['next']] for r in DEMO['records']],'Handover register')+p('Naming example: DEMO_DOC-002_Cable-Schedule_Rev-C. Preserve the original received file, record its revision, and create a reviewed issue without silently overwriting the earlier record. Only the authorized reviewer can approve technical content.')

def page(filename,title,description,body,current='',robots=True):
    nav=''.join(f'<a href="{path}"'+(' aria-current="page"' if current==key else '')+f'>{label}</a>' for key,label,path in [('projects','Work samples','projects.html'),('expertise','Expertise','engineering.html'),('experience','Experience','experience.html'),('resumes','Résumés','resumes.html'),('contact','Contact','contact.html')])
    canonical=f'<link rel="canonical" href="{BASE}/{filename if filename!="index.html" else ""}"><meta property="og:url" content="{BASE}/{filename if filename!="index.html" else ""}">' if BASE else '<meta name="robots" content="noindex, nofollow">'
    out=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | Eric John Cruz, REE</title><meta name="description" content="{esc(description)}"><meta name="theme-color" content="#122c35"><meta property="og:type" content="website"><meta property="og:title" content="{esc(title)} | Eric John Cruz, REE"><meta property="og:description" content="{esc(description)}">{canonical}<link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/site.css"><script src="assets/site.js" defer></script></head><body><a class="skip" href="#main">Skip to content</a><header class="header"><div class="wrap"><a class="brand" href="index.html"><span class="brand-mark" aria-hidden="true">EC</span><span>Eric John Cruz<small>Registered Electrical Engineer</small></span></a><button class="menu" aria-expanded="false" aria-controls="primary-nav" type="button">Menu</button><nav class="nav" id="primary-nav" aria-label="Primary">{nav}</nav></div></header><main class="wrap" id="main">{body}</main><footer class="footer"><div class="wrap"><p>Eric John Cruz, REE<br>Puerto Princesa City, Philippines</p><p><a href="mailto:{PROFILE['email']}">{PROFILE['email']}</a><br><a href="{PROFILE['linkedin']}">LinkedIn</a></p><p>Philippine engineering credential.<br>© 2026 Eric John Cruz</p></div></footer></body></html>'''
    if filename == '404.html' and BASE:
        # Pages serves this document at arbitrary missing paths, including nested URLs.
        out = re.sub(r'((?:href|src)=")([^"#][^"]*)"',
                     lambda m: m.group(0) if re.match(r'[a-zA-Z][a-zA-Z0-9+.-]*:|//',m.group(2))
                     else m.group(1)+esc(BASE)+'/'+m.group(2)+'"',out)
    (OUT/filename).write_text(out,encoding='utf-8')

def pagehead(kicker,title,intro):return f'<div class="page-head"><span class="eyebrow">{esc(kicker)}</span><h1>{esc(title)}</h1><p class="intro">{esc(intro)}</p></div>'
def project_card(c): return f'''<article class="card project"><div class="visual">{c['visual']()}</div><div class="card-body"><span class="tag">{esc(c['classification'])} · {esc(c['category'])}</span><h3><a href="case-{c['slug']}.html">{esc(c['title'])}</a></h3><p>{esc(c['intro'])}</p><a class="text-link" href="case-{c['slug']}.html">View worksheet and assumptions</a></div></article>'''

PATHWAYS = [
 ('engineering','01','Electrical engineering and estimating','Drawing review, quantity takeoffs, BOQs and technical documentation that make scope easier to check.'),
 ('technical-sales','02','Technical sales and applications','Technical research, requirement comparisons and organized quotation inputs, supported by client communication experience.'),
 ('operations','03','Engineering operations and remote support','Document control, project follow-up, reporting and practical coordination across technical and business teams.')
]

def portrait(priority=False):
    return '<img class="professional-portrait" src="assets/eric-john-cruz.webp" width="232" height="232" alt="Eric John Cruz, Registered Electrical Engineer." decoding="async"'+(' fetchpriority="high"' if priority else ' loading="lazy"')+'>'

def render_site():
    home=f'''<section class="hero"><div><span class="eyebrow">Eric John Cruz, REE · Philippines</span><h1>Electrical drawings, quantity takeoffs and technical records.</h1><p class="intro">I am a Registered Electrical Engineer in the Philippines. My work has included building electrical layouts and schedules, power plant document records, and municipal engineering inspection support. I also have experience with spreadsheet reporting and remote coordination.</p><div class="actions">{btn('View practice examples','projects.html')}{btn('Choose a résumé','resumes.html',True)}</div><p class="location">Based in Puerto Princesa City · Open to engineering and technical support opportunities</p></div><figure class="hero-figure"><div class="label">Practice example / Fictional office plan</div>{plan_svg(True)}<figcaption><span>Fictional office plan<br>Takeoff practice only.</span><a href="case-takeoff.html">View the worksheet ↗</a></figcaption></figure></section><div class="credentials"><div><small>Professional qualification</small>Registered Electrical Engineer, Philippines</div><div><small>Engineering education</small>BS Electrical Engineering · Palawan State University</div><div><small>Professional background</small>Engineering documentation + remote operations</div></div>'''
    home=home.replace('<h1>', '<div class="hero-identity">'+portrait(True)+'<div><strong>Registered Electrical Engineer</strong><p>Electrical Engineering | Technical Sales | Engineering Support</p></div></div><h1>',1)
    home+='<section class="section"><div class="section-head"><h2>Areas of work</h2><p>Engineering documentation, estimating practice, equipment research and records management.</p></div><div class="grid">'
    for slug,num,title,desc in PATHWAYS:home+=f'<article class="card"><span class="number">{num}</span><h3>{title}</h3><p>{desc}</p><a class="text-link" href="{slug}.html">See details</a></article>'
    home+='''</div></section><section class="section"><div class="section-head"><h2>Engineering work I have done</h2><p>My work history covers drawings, engineering records and supervised site documentation. Project files and employer records are not displayed publicly.</p></div><div class="grid two"><article class="card"><h3>Independent electrical projects</h3><p>Prepared layouts, single-line diagrams, panel and load schedules, material lists and bills of quantities for small building projects.</p></article><article class="card"><h3>Power plant technical records</h3><p>Maintained equipment lists, cable and panel schedules, manuals and test records. Checked references and followed up on missing information with site engineers.</p></article><article class="card"><h3>Municipal engineering placement</h3><p>Assisted with street-lighting and building inspection records, AutoCAD drawings and cost estimates under supervision.</p></article></div><div class="actions">${btn('See the experience details','experience.html')}</div></section>'''
    home+='<section class="section"><div class="section-head"><div><span class="eyebrow">Practice examples</span><h2>Practice worksheets and calculations</h2></div><p>These fictional exercises show sample calculations, registers and review notes. They are not completed customer projects.</p></div><div class="grid two">'+''.join(project_card(c) for c in CASES)+'</div></section>'
    home+='<section class="section"><div class="section-head"><h2>Résumés and contact</h2><p>Download an engineering-focused résumé or contact me about a relevant opening.</p></div><div class="actions">'+btn('View the résumé hub','resumes.html')+btn('Contact Eric','contact.html',True)+'</div></section>'
    page('index.html','Electrical Engineering and Documentation','Eric John Cruz, Philippine Registered Electrical Engineer. Building electrical drawings, schedules, engineering records and quantity takeoffs.',home)

    exp=pagehead('Experience','Electrical drawings, plant records and reporting','I've worked on small-building electrical drawings and schedules, handled electrical and automation records in a power plant assignment, and assisted with municipal inspection documentation.')
    exp='<div class="experience-intro">'+exp+'<figure class="experience-portrait">'+portrait()+'<figcaption>Eric John Cruz, REE</figcaption></figure></div>'
    exp+='<section><h2>Engineering experience</h2><div class="timeline">'
    def job(e):return f'<article class="job"><div class="date">{esc(e["dates"])}<br>{esc(e["type"])}</div><div><h3>{esc(e["title"])}</h3><p class="company">{esc(e["company"])}</p>{ul(e["bullets"])}</div></article>'
    exp+=''.join(job(e) for e in PROFILE['experience'][:3])+'</div></section><section class="section"><h2>Remote business and customer support</h2><p class="intro">This is separate from my electrical engineering work, but involved reporting, record keeping and following up on outstanding tasks.</p>'+''.join(job(e) for e in PROFILE['experience'][3:])+'</section>'
    exp+='<section class="section"><h2>Education and professional development</h2><p><strong>'+PROFILE['education']+'</strong><br>'+PROFILE['university']+' · '+PROFILE['education_dates']+'</p><p><strong>Registered Electrical Engineer</strong><br>Philippine professional qualification</p><p>Electrical estimating training and GroundPlan practice cover drawing review, system-by-system takeoff, assumptions, clarification registers and RFQ preparation.</p><a class="text-link" href="training.html">Read the training approach</a></section>'
    exp+='<section class="section"><h2>Tools in context</h2><dl class="tool-list">'+''.join(f'<div><dt>{esc(t["name"])}</dt><dd>{esc(t["context"])}</dd></div>' for t in PROFILE['tools'])+'</dl></section>'
    page('experience.html','Professional Experience','Engineering, documentation, customer support and remote professional experience of Eric John Cruz.',exp,'experience')

    configs={
     'engineering':('Electrical engineering and estimating','Electrical drawings and quantity takeoffs','Support with drawings, takeoffs, schedules and the documentation that connects engineering information to project decisions.',
      [('Drawing and scope review','Read electrical layouts, legends, schedules and scope notes. Identify missing information and carry it into a clarification register.'),('Takeoffs and BOQs','Organize device counts and material quantities with drawing references, units, assumptions and revision notes.'),('Design documentation support','Prepare or revise electrical layouts, single-line diagrams and load/panel schedules for review within the agreed project scope.'),('Estimating development','Continue GroundPlan practice and structured tender review. Training-based activities are labelled as practice.')],['takeoff','schedule-review'],'engineering'),
     'technical-sales':('Technical sales and applications','Equipment research and quotation support','Engineering knowledge paired with research, customer communication and organized commercial support.',
      [('Requirements clarification','Translate a request into a structured list of technical inputs, open questions and acceptance needs.'),('Equipment research and comparison','Compare supplied specifications and identify missing data, assumptions, alternatives and manufacturer confirmations.'),('Quotation support','Prepare scope summaries, schedules and supplier questions. Track inclusions, exclusions, validity and follow-up actions.'),('Customer communication','Bring customer support, escalation handling and remote client communication to technical sales support roles.')],['equipment-evaluation','takeoff'],'technical-sales'),
     'operations':('Engineering operations and remote support','Document registers and project follow-up','Practical support for records, project administration, research and follow-up across remote teams.',
      [('Document control','Track document IDs, revisions, received evidence, review status and the responsible next owner.'),('Project coordination','Maintain action lists and concise updates. Clarify dependencies and escalate missing inputs before they become silent delays.'),('Research and reporting','Turn source information into clear summaries, comparison tables and status reports for review.'),('Technical administration','Support estimate files, procurement records, tender registers, quality checks and structured handovers.')],['document-control','equipment-evaluation'],'operations')
    }
    for slug,(kicker,title,intro,blocks,selected,variant) in configs.items():
        body=pagehead(kicker,title,intro)+'<section class="section"><div class="grid two">'+''.join(f'<article class="card"><h2 style="font-size:1.5rem">{esc(h)}</h2><p>{esc(t)}</p></article>' for h,t in blocks)+'</div></section>'
        if slug=='technical-sales':body+='<p class="notice">I am applying engineering and transferable client support skills to technical-commercial work. The portfolio does not claim sales quotas, closed deals or previous employment as a sales engineer.</p>'
        if slug=='engineering':body+='<p class="notice">Engineering work follows the agreed scope and applicable review requirements. My REE credential is a Philippine qualification; overseas regulated design and approval require the relevant local authority.</p>'
        body+='<section class="section"><h2>Related practice exercises</h2><div class="grid two">'+''.join(project_card(c) for c in CASES if c['slug'] in selected)+'</div></section><div class="actions">'+btn('Open the relevant résumé',f'resume-{variant}.html')+btn('Contact me','contact.html',True)+'</div>'
        page(slug+'.html',kicker,intro,body,'expertise')

    body=pagehead('Projects and work samples','Practice exercises, with assumptions shown','Four fictional worksheets prepared with AI assistance, plus an account of my Australian estimating training. These are not client case studies.')
    body+='<h2>Technical practice exercises</h2><div class="grid two">'+''.join(project_card(c) for c in CASES)+'</div><section class="section"><article class="card"><span class="tag">Training and practice</span><h2>Residential tender scope review</h2><p>My training work on drawing notes, quantity counts, allowances and supplier-quoted scope. The project drawings are not published.</p><a class="text-link" href="training.html">Read the training account</a></article></section>'
    page('projects.html','Practice Calculations and Registers','Browse fictional takeoff, load calculation, equipment comparison and document-register exercises.',body,'projects')

    for c in CASES:
        body='<div class="page-head"><p class="breadcrumb"><a href="projects.html">Practice examples</a> / '+esc(c['category'])+'</p><span class="eyebrow">'+esc(c['classification'])+'</span><h1>'+esc(c['title'])+'</h1><p class="intro">'+esc(c['intro'])+'</p></div>'
        body+='<div class="content-grid"><article class="prose"><figure class="figure">'+c['visual']()+'<figcaption>Fictional inputs for a portfolio exercise, not a site drawing or client deliverable.</figcaption></figure>'
        for key,label in [('context','Context'),('objective','Objective'),('role','About this example'),('approach','Technical approach')]:body+='<h2>'+label+'</h2>'+p(c[key])
        body+=details(c['slug'])
        for key,label in [('deliverables','Deliverables'),('checks','Checks performed'),('result','What the checks show'),('limit','Assumptions and limits')]:body+='<h2>'+label+'</h2>'+p(c[key])
        body+='</article><aside class="aside"><h2>At a glance</h2><dl><dt>Classification</dt><dd>'+esc(c['classification'])+'</dd><dt>Focus</dt><dd>'+esc(c['category'])+'</dd><dt>Tools</dt><dd>'+esc(c['tools'])+'</dd><dt>Use</dt><dd>Practice calculation, not for construction or procurement approval.</dd></dl><div class="actions">'+btn('Open the sample sheet','sample-'+c['slug']+'.html')+f'<a class="button secondary" href="samples/{c["slug"]}.json" download>Download the example data</a></div></aside></div>'
        page('case-'+c['slug']+'.html',c['title'],c['intro'],body,'projects')
        sample=pagehead('Practice worksheet',c['title'],'Fictional figures prepared with AI assistance; this is not a completed client assignment.')+'<h2>Inputs and outputs</h2>'+details(c['slug'])
        if c['slug']=='takeoff':sample+=table(['Point ID','Type','Drawing X','Drawing Y'],[[v['id'],v['type'],v['x'],v['y']] for v in DEMO['points']],'Point register in SVG drawing coordinates')
        sample+='<div class="prose"><h2>Checks</h2>'+p(c['checks'])+'<h2>Limits</h2>'+p(c['limit'])+'</div><div class="actions">'+btn('Return to the case study','case-'+c['slug']+'.html')+'</div>'
        page('sample-'+c['slug']+'.html',c['title']+' Sample',c['intro'],sample,'projects')

    train=pagehead('Training and practice','Residential tender scope review','My Australian estimating training covers drawing notes, quantity counts, GroundPlan measurements and questions raised with my instructor.')
    train+='<div class="content-grid"><article class="prose">'+''.join('<h2>'+h+'</h2>'+p(t) for h,t in [
      ('Context','An Australian residential estimating training project involves multiple electrical systems, general notes and supplier-quoted packages. The public account describes the method without publishing the project drawings, specification or course material.'),
      ('Objective','Practice separating measured quantities, allowances and unresolved scope so the takeoff can be reviewed without losing the basis of each item.'),
      ('My role','Review drawings and notes, organize system-based takeoff items, and raise clarification questions during training. This is developing estimating experience, not a completed professional tender or trainer-approved estimate.'),
      ('Technical approach','Start with the drawing register and known scale references. Read notes and legends before counting. Label an allowance in the item name and carry the fuller explanation into the assumptions register. Keep supplier package inclusions visible when reviewing quotations.'),
      ('Tools','GroundPlan for practice measurements and counts; spreadsheets and written registers for assumptions, revisions and scope questions.'),
      ('Deliverables and checks','The training records show work on note-based items, conduit allowances, communications questions and switchboard RFQ scope. Reconcile per-system quantities, distinguish counts from allowances, and cross-check package inclusions against the supplied specification.'),
      ('Current result','This is still training work. Final takeoff quantities and trainer approval are not documented here.')])+'</article><aside class="aside"><h2>Evidence boundary</h2><p class="small">Training documents establish the learning context. They are not public case-study assets or proof of an approved estimate.</p><div class="actions">'+btn('See a takeoff practice exercise','case-takeoff.html')+'</div></aside></div>'
    page('training.html','Estimating Training','GroundPlan and residential tender review training: quantities, assumptions, RFIs and supplier package scope.',train,'projects')

    contact=pagehead('Contact','Contact Eric John Cruz','Email me about an electrical engineering, estimating or technical support position.')
    contact+='<div class="grid two"><section class="contact-block"><h2>Email Eric</h2><p><a class="wide-link" href="mailto:'+PROFILE['email']+'?subject=Engineering%20or%20technical%20support%20opportunity">'+PROFILE['email']+'</a></p><button class="copy" data-copy-email type="button">Copy email address</button><p class="small" id="copy-status" aria-live="polite"></p><p class="small">Puerto Princesa City, Palawan, Philippines</p></section><section class="contact-block"><h2>Useful details to include</h2>'+ul(['Role or project focus','Type of drawings, records or technical information involved','Expected deliverables and review process','Location, working arrangement and target timing'])+'<a class="text-link" href="'+PROFILE['linkedin']+'">View my LinkedIn profile</a></section></div><div class="actions">'+btn('Choose a résumé','resumes.html')+btn('View practice examples','projects.html',True)+'</div>'
    page('contact.html','Contact','Contact Eric John Cruz about engineering, estimating, technical support and remote operations opportunities.',contact,'contact')

VARIANTS={
 'engineering':{
  'label':'Electrical Engineering and Estimating','filename':'Eric_John_Cruz_Electrical_Engineering',
  'summary':'Philippine Registered Electrical Engineer with experience in electrical design support, quantity takeoffs, BOQs and technical records. Background includes independent engineering projects, power plant electrical and automation documentation, and supervised municipal engineering work. Continuing structured electrical estimating and GroundPlan practice, supported by remote coordination and customer communication experience.',
  'skills':['Drawing and specification review; electrical layouts and single-line diagrams.','Quantity takeoffs, material lists, BOQs, load and panel schedules.','Drawing revisions, assumptions, clarification registers and technical file organization.','AutoCAD 2D, Bluebeam Revu, Excel and Google Sheets; GroundPlan training and practice.'],
  'projects':['Quantity takeoff practice: office example with symbol register, measured inputs, explicit allowances and reconciliation checks.','Connected-load practice: apparent-load calculation with traceable inputs and a clear separation between demand and device ratings.'],
  'ids':['freelance','rapid','kalayaan']},
 'technical-sales':{
  'label':'Technical Sales and Applications Support','filename':'Eric_John_Cruz_Technical_Sales',
  'summary':'Philippine Registered Electrical Engineer combining technical documentation, research and client communication. Prepares clear scope information, compares technical inputs and coordinates follow-up across engineering and remote business workflows. Customer support and Subject Matter Expert experience provide a practical foundation for technical sales, applications support and quotation coordination.',
  'skills':['Technical requirement interpretation, equipment research and specification comparison.','Quotation inputs, material schedules, assumptions and supplier clarification lists.','Customer communication, escalation support, documentation and remote coordination.','Excel, Google Sheets, AutoCAD 2D, Google Workspace, Basecamp and CRM workflows.'],
  'projects':['Equipment comparison practice: 24 V DC capacity comparison with a current budget, stated reserve and supplier clarification list.','Takeoff practice: scope and material quantity example supporting clearer quotation inputs.'],
  'ids':['freelance','rapid','kalayaan']},
 'operations':{
  'label':'Engineering Operations and Remote Support','filename':'Eric_John_Cruz_Engineering_Operations',
  'summary':'Philippine Registered Electrical Engineer with technical records, remote operations and customer support experience. Organizes drawings, schedules, documentation gaps, reports and follow-up actions so teams have clear information for review. Combines electrical understanding with spreadsheet work, written communication and quality checks across technical and business environments.',
  'skills':['Engineering document control, revision tracking and equipment records.','Project administration, action tracking, reporting and handover preparation.','Takeoff and BOQ documentation, research and procurement record support.','Excel, Google Sheets, Microsoft Office, Google Workspace, Basecamp and CRM workflows.'],
  'projects':['Document register practice: example showing required versus received revisions, missing attachments and explicit review holds.','Equipment comparison practice: requirements worksheet with documented next actions.'],
  'ids':['rapid','freelance','kalayaan']}
}

def resume_sections(key):
    v=VARIANTS[key];items=[]
    items += [('h2','Professional summary'),('p',v['summary']),('h2','Relevant capabilities')]
    items += [('bullet',x) for x in v['skills']]
    items += [('h2','Engineering experience')]
    for id in v['ids']:
        e=next(x for x in PROFILE['experience'] if x['id']==id)
        items += [('h3',e['title']),('meta',e['company']+' | '+e['dates'])]
        bullets=e['bullets'][:2] if key!='engineering' else e['bullets']
        items += [('bullet',x) for x in bullets]
    items += [('break',''),('h2','Remote operations and customer support')]
    for e in PROFILE['experience'][3:]:
        items += [('h3',e['title']),('meta',e['company']+' | '+e['dates'])]+[('bullet',x) for x in e['bullets']]
    items += [('h2','Technical practice exercises'),('p','Fictional practice exercises created with AI assistance, not completed client assignments.')]+[('bullet',x) for x in v['projects']]
    items += [('h2','Education and credential'),('p',PROFILE['education']+' | '+PROFILE['university']+' | '+PROFILE['education_dates']),('p',PROFILE['credential'])]
    items += [('h2','Professional development'),('p','Electrical estimating training: drawing and scope review, GroundPlan practice, quantity reconciliation, RFQs, assumptions and clarification records.')]
    if BASE:items += [('h2','Portfolio'),('p',BASE+'/')]
    return items

def resume_html(key,sections):
    v=VARIANTS[key]
    s='<article class="resume-paper"><h1>'+PROFILE['name']+', REE</h1><p><strong>'+v['label']+'</strong></p><p class="resume-meta">'+PROFILE['location']+'<br><a href="mailto:'+PROFILE['email']+'">'+PROFILE['email']+'</a><br><a href="'+PROFILE['linkedin']+'">linkedin.com/in/eric-john-cruz-ree/</a></p>'
    inlist=False
    for kind,text in sections:
        if kind=='bullet':
            if not inlist:s+='<ul>';inlist=True
            s+='<li>'+esc(text)+'</li>';continue
        if inlist:s+='</ul>';inlist=False
        if kind=='break':s+='<div class="page-break"></div>'
        elif kind in ['h2','h3']:s+=f'<{kind}>{esc(text)}</{kind}>'
        else:s+=f'<p{" class="+chr(34)+"resume-meta"+chr(34) if kind=="meta" else ""}>{esc(text)}</p>'
    if inlist:s+='</ul>'
    return s+'</article>'

def create_docx(key,sections):
    from docx import Document
    from docx.shared import Inches,Pt,RGBColor
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    d=Document();sec=d.sections[0];sec.page_width=Inches(8.5);sec.page_height=Inches(11)
    sec.top_margin=sec.bottom_margin=Inches(.58);sec.left_margin=sec.right_margin=Inches(.66)
    for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','List Bullet']:
        st=d.styles[name];st.font.name='Arial';st.font.color.rgb=RGBColor(0,0,0)
    normal=d.styles['Normal'];normal.font.size=Pt(10.5);normal.paragraph_format.space_after=Pt(5);normal.paragraph_format.line_spacing=1.08
    d.styles['Title'].font.size=Pt(23);d.styles['Title'].paragraph_format.space_after=Pt(6)
    for name,size in [('Heading 1',11),('Heading 2',10.5)]:
        st=d.styles[name];st.font.size=Pt(size);st.font.bold=True;st.paragraph_format.space_before=Pt(11);st.paragraph_format.space_after=Pt(5)
    d.styles['List Bullet'].paragraph_format.space_after=Pt(4)
    d.core_properties.author=PROFILE['name'];d.core_properties.title=VARIANTS[key]['label'];d.core_properties.subject='Professional resume';d.core_properties.keywords=''
    d.add_paragraph(PROFILE['name']+' REE',style='Title')
    q=d.add_paragraph();q.add_run(VARIANTS[key]['label']).bold=True
    for x in [PROFILE['location'],PROFILE['email'],PROFILE['linkedin']]:
        q=d.add_paragraph(x);q.paragraph_format.space_after=Pt(3);q.runs[0].font.size=Pt(9)
    for kind,text in sections:
        if kind=='break':d.add_page_break();continue
        if kind=='h2':q=d.add_paragraph(text.upper(),style='Heading 1')
        elif kind=='h3':q=d.add_paragraph(text,style='Heading 2')
        elif kind=='bullet':q=d.add_paragraph(text,style='List Bullet')
        else:
            q=d.add_paragraph(text)
            if kind=='meta':
                for r in q.runs:r.font.size=Pt(9)
                q.paragraph_format.keep_with_next=True
        q.paragraph_format.widow_control=True
    footer=sec.footer.paragraphs[0];footer.alignment=2
    footer.add_run(PROFILE['name']+' | ')
    fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');footer._p.append(fld)
    for r in footer.runs:r.font.size=Pt(8)
    d.save(OUT/'downloads'/(VARIANTS[key]['filename']+'.docx'))

def create_pdf(key,sections):
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak
    from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Name',fontName='Helvetica-Bold',fontSize=23,leading=26,spaceAfter=9))
    styles.add(ParagraphStyle(name='Role',fontName='Helvetica-Bold',fontSize=11,leading=14,spaceAfter=7))
    styles.add(ParagraphStyle(name='Contact',fontName='Helvetica',fontSize=9,leading=12,spaceAfter=2))
    styles.add(ParagraphStyle(name='Section',fontName='Helvetica-Bold',fontSize=11,leading=14,spaceBefore=12,spaceAfter=5,keepWithNext=True))
    styles.add(ParagraphStyle(name='Job',fontName='Helvetica-Bold',fontSize=10.5,leading=13,spaceBefore=8,spaceAfter=3,keepWithNext=True))
    styles.add(ParagraphStyle(name='Meta',fontName='Helvetica',fontSize=9,leading=12,spaceAfter=4,keepWithNext=True))
    styles.add(ParagraphStyle(name='Copy',fontName='Helvetica',fontSize=10.5,leading=13.2,spaceAfter=5))
    styles.add(ParagraphStyle(name='BulletText',parent=styles['Copy'],leftIndent=11,firstLineIndent=-9,spaceAfter=4))
    doc=SimpleDocTemplate(str(OUT/'downloads'/(VARIANTS[key]['filename']+'.pdf')),pagesize=letter,leftMargin=47.5,rightMargin=47.5,topMargin=41.8,bottomMargin=41.8,title=VARIANTS[key]['label'],author=PROFILE['name'])
    story=[Paragraph(esc(PROFILE['name']+' REE'),styles['Name']),Paragraph(esc(VARIANTS[key]['label']),styles['Role'])]
    for x in [PROFILE['location'],PROFILE['email'],PROFILE['linkedin']]:story.append(Paragraph(esc(x),styles['Contact']))
    for kind,text in sections:
        if kind=='break':story.append(PageBreak());continue
        style={'h2':'Section','h3':'Job','meta':'Meta','p':'Copy','bullet':'BulletText'}[kind]
        text=text.upper() if kind=='h2' else text
        story.append(Paragraph(('• ' if kind=='bullet' else '')+esc(text),styles[style]))
    def footer(canvas,doc):
        canvas.setFont('Helvetica',8);canvas.drawRightString(564,24,f'{PROFILE["name"]} | {doc.page}')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)

def render_resumes():
    hub=pagehead('Résumés','Choose the version that fits your opening.','The same professional background, organized for three types of opportunity. Read online or download an editable Word file and searchable PDF.')+'<div class="grid">'
    for key,v in VARIANTS.items():
        sec=resume_sections(key);create_docx(key,sec);create_pdf(key,sec)
        hub+='<article class="card"><h2 style="font-size:1.55rem">'+v['label']+'</h2><p>'+({'engineering':'For electrical drawing support, estimating and technical documentation roles.','technical-sales':'For equipment research, technical sales support and quotation coordination.','operations':'For technical records, reporting and engineering administration.'}[key])+'</p><div class="download-row">'+btn('Read online','resume-'+key+'.html')+'</div><p class="small" style="margin-top:20px"><a href="downloads/'+v['filename']+'.docx" download>Download Word</a> · <a href="downloads/'+v['filename']+'.pdf" download>Download PDF</a></p></article>'
        body='<div class="actions no-print">'+btn('Download PDF','downloads/'+v['filename']+'.pdf')+btn('Download Word','downloads/'+v['filename']+'.docx',True)+'<a class="button secondary" href="resumes.html">All résumé versions</a></div>'+resume_html(key,sec)
        page('resume-'+key+'.html',v['label']+' Resume',v['summary'],body,'resumes')
    page('resumes.html','Resume Downloads','Choose electrical engineering, technical sales or engineering operations resumes in HTML, Word and PDF.',hub+'</div>','resumes')

def main():
    global BASE
    parser=argparse.ArgumentParser();parser.add_argument('--base-url',default='');args=parser.parse_args();BASE=args.base_url.rstrip('/')
    if BASE and not re.fullmatch(r'https://[A-Za-z0-9.-]+(?:/[A-Za-z0-9._~-]+)*',BASE):raise ValueError('Use an HTTPS base URL with no query or fragment.')
    for folder in ['assets','downloads','samples']:(OUT/folder).mkdir(parents=True,exist_ok=True)
    for file in (ROOT/'assets').iterdir():shutil.copyfile(file,OUT/'assets'/file.name)
    (OUT/'assets/favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="32" fill="#122c35"/><text x="32" y="41" text-anchor="middle" font-family="Georgia,serif" font-size="29" fill="white">EC</text></svg>',encoding='utf-8')
    data={'takeoff':{'points':DEMO['points'],'route':DEMO['route']},'schedule-review':{'voltage_v':230,'loads':DEMO['loads']},'equipment-evaluation':DEMO['supply'],'document-control':DEMO['records']}
    for slug,value in data.items():(OUT/'samples'/(slug+'.json')).write_text(json.dumps({'classification':DEMO['classification'],'inputs':value},indent=2),encoding='utf-8')
    render_site();render_resumes()
    page('404.html','Page Not Found','This page could not be found.',pagehead('Page not found','Let’s get you back to the work.','Use the navigation to find projects, experience or résumés.')+btn('Open the homepage','index.html'))
    (OUT/'.nojekyll').write_text('')
    if BASE:
        urls=[BASE+'/'+x.name for x in sorted(OUT.glob('*.html')) if x.name not in ['404.html'] and not x.name.startswith('sample-')]
        (OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+esc(u)+'</loc></url>' for u in urls)+'</urlset>',encoding='utf-8')
        (OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+BASE+'/sitemap.xml\n')
    else:
        (OUT/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
        if (OUT/'sitemap.xml').exists():(OUT/'sitemap.xml').unlink()
    (ROOT/'qa').mkdir(exist_ok=True)
    (ROOT/'qa/build.json').write_text(json.dumps({'base_url':BASE,'pages':len(list(OUT.glob('*.html'))),'resume_variants':list(VARIANTS),'status':'Built locally; deployment verification separate'},indent=2))
    print(f'Built {len(list(OUT.glob("*.html")))} pages, 3 DOCX resumes, 3 PDFs and 4 example datasets.')

if __name__=='__main__':main()
