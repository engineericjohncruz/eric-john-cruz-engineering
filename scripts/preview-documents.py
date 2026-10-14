"""Expose rendered résumé pages for remote visual review; no source/private files."""
from pathlib import Path
import base64,subprocess
root=Path(__file__).resolve().parents[1]
for source in [root/'dist/downloads/Eric_John_Cruz_Engineering_Resume.pdf',root/'qa/word-renders/Eric_John_Cruz_Engineering_Resume.pdf']:
    label='word' if 'word-renders' in str(source) else 'pdf'
    target=root/'qa'/('resume-'+label)
    subprocess.run(['pdftoppm','-scale-to','1300','-jpeg','-jpegopt','quality=70',str(source),str(target)],check=True)
    for file in sorted((root/'qa').glob('resume-'+label+'-*.jpg')):
        print('DOCUMENT_PREVIEW',file.stem,base64.b64encode(file.read_bytes()).decode())
