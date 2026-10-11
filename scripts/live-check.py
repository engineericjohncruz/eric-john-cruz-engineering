"""Verify the actual deployed Pages URL and binary download signatures."""
import sys,urllib.request,time
base=sys.argv[1].rstrip('/')+'/'
paths=['index.html','engineering.html','technical-sales.html','operations.html','projects.html','experience.html','resumes.html','contact.html','case-takeoff.html','case-schedule-review.html','case-equipment-evaluation.html','case-document-control.html','training.html']
for stem in ['Electrical_Engineering','Technical_Sales','Engineering_Operations']:
    for ext in ['docx','pdf']:paths.append(f'downloads/Eric_John_Cruz_{stem}.{ext}')
for item in paths:
    with urllib.request.urlopen(base+item,timeout=30) as response:
        data=response.read()
        assert response.status==200
        if item.endswith('.pdf'):assert data.startswith(b'%PDF-')
        elif item.endswith('.docx'):assert data.startswith(b'PK')
        else:assert b'Eric John Cruz' in data
        print('PASS',base+item,len(data))
