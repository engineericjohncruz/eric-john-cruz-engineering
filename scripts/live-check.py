"""Verify every public page, current downloads and removal of obsolete resume URLs."""
import sys,urllib.request,urllib.error,json
base=sys.argv[1].rstrip('/')+'/'
paths=['index.html','engineering.html','technical-sales.html','operations.html','projects.html','experience.html','resumes.html','resume.html','contact.html','case-takeoff.html','case-schedule-review.html','case-equipment-evaluation.html','case-document-control.html','training.html','sample-takeoff.html','sample-schedule-review.html','sample-equipment-evaluation.html','sample-document-control.html','assets/eric-john-cruz.webp']
for ext in ['docx','pdf']:paths.append('downloads/Eric_John_Cruz_Engineering_Resume.'+ext)
for item in paths:
    with urllib.request.urlopen(base+item,timeout=30) as response:
        data=response.read()
        assert response.status==200
        if item.endswith('.pdf'):assert data.startswith(b'%PDF-')
        elif item.endswith('.docx'):assert data.startswith(b'PK')
        elif item.endswith('.webp'):assert data.startswith(b'RIFF') and data[8:12]==b'WEBP'
        else:
            assert b'Eric John Cruz' in data
            assert b'Choose a r' not in data and b'All r' not in data
            assert b'fictional' not in data.lower() and b'Kreeayt' not in data
            if item.startswith(('case-','sample-')):
                assert b'Sample ' in data and b'Assumptions and limits' in data
                assert b'projects.html#sample-basis' in data
            if item=='projects.html':assert b'AI assistance' in data and b'id="sample-basis"' in data
            if item=='training.html':assert b'Ongoing professional training' in data and b'Australian Electrical Estimating' in data
            if item=='resume.html':assert b'Ongoing professional development' in data and b'Portfolio practice' not in data
        print('PASS',base+item,len(data))
for slug in ['takeoff','schedule-review','equipment-evaluation','document-control']:
    with urllib.request.urlopen(base+'samples/'+slug+'.json',timeout=30) as response:
        sample=json.load(response)
        assert sample['classification'].startswith('Sample ')
        assert 'AI assistance' in sample['provenance'] and sample['input_basis'] and sample['limitations']
        print('PASS',base+'samples/'+slug+'.json','input basis and provenance')
obsolete=['resume-engineering.html','resume-technical-sales.html','resume-operations.html']
for stem in ['Electrical_Engineering','Technical_Sales','Engineering_Operations']:
    for ext in ['docx','pdf']:obsolete.append('downloads/Eric_John_Cruz_'+stem+'.'+ext)
for item in obsolete:
    try:
        with urllib.request.urlopen(base+item,timeout=30) as response:raise AssertionError('Obsolete resume is still served: '+item)
    except urllib.error.HTTPError as error:
        assert error.code==404,(item,error.code)
        print('REMOVED',base+item,'404')
