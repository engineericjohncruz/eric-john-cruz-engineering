from pathlib import Path
from pypdf import PdfReader
import json,sys
root=Path(__file__).resolve().parents[1]
files=list((root/'qa/word-renders').glob('*.pdf'))
assert len(files)==1,'Expected one rendered Word PDF'
result=[]
for file in files:
    reader=PdfReader(file)
    assert len(reader.pages)==2,f'{file.name}: expected 2 pages, found {len(reader.pages)}'
    text=' '.join(page.extract_text() or '' for page in reader.pages)
    for phrase in ['Eric John Cruz','Palawan State University','Foundever','Rapid Care','June 2024','March 2025','June 2022']:
        assert phrase in text,f'{file.name}: missing {phrase}'
    result.append({'file':file.name,'pages':len(reader.pages),'text_characters':len(text)})
(root/'qa/word-checks.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
