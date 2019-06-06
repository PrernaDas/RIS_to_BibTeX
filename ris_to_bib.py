import os
import re
import codecs
from collections import defaultdict
import unicodedata



def normalize_unicode_to_ascii(s):
	"""

	"""
	return unicodedata.normalize('NFKD', unicode(s)).encode('ascii', 'ignore')


def ris_to_bib(input_ris_file_name):
	path = os.path.split(input_ris_file_name)[0]
	ris_file_name = os.path.split(input_ris_file_name)[1]
	if len(path)!=0:
		output_bib_file_name=path+'/'+ris_file_name.rsplit('.', 1)[0]+'.bib'
	else:
		output_bib_file_name=ris_file_name.rsplit('.', 1)[0]+'.bib'	

	
	master_list = []

	DOI_tags = ['https://dx.doi.org/', 'http://dx.doi.org/']
	with codecs.open(input_ris_file_name, 'r', encoding='utf-8') as ris_file, open(output_bib_file_name, 'w') as bib_file:
		for line in ris_file:
			if line.strip().startswith('TY') or line.strip().startswith('ID'):
				d = defaultdict(lambda: ' ') # provides the default value for a nonexistent key.
				all_author =[]
		
			if line.startswith('DO'):
				DOI = line.split('-')[1].lstrip().rstrip().strip('\n').replace('https://dx.doi.org/', '').replace('http://dx.doi.org/', '')
				d['DO'] = DOI
				
			if line.strip().startswith('SN'):
				d['SN'] = line.split('-', 1)[1].lstrip().rstrip().strip('\n').split(',')[0]
					
			if line.strip().startswith('JA'):
				d['JA'] = line.split('-', 1)[1].lstrip().rstrip().strip('\n').replace('=', ' ')

			if line.strip().startswith('JO'):
				d['JF'] = line.split('-', 1)[1].lstrip().rstrip().strip('\n').replace('=', ' ')	

			if line.strip().startswith('JF'):
				d['JF'] = line.split('-', 1)[1].lstrip().rstrip().strip('\n').replace('=', ' ')


			if line.strip().startswith('SP'):
				d['SP'] = line.split('-', 1)[1].lstrip().rstrip().strip('\n')
				characters = [c for c in d['SP']]
				# print characters
				if u'\u2010' in characters:
					pages = re.sub(u'\u2010', '-', d['SP'])
					d['pages'] = pages
						
			
			if line.strip().startswith('EP'):
				d['EP'] = line.split('-', 1)[1].lstrip().rstrip().strip('\n')
				if len(d['SP'])>len(d['EP']):
					diff=len(d['SP'])-len(d['EP'])
					d['EP']=d['SP'][:diff]+d['EP']
					d['pages']=d['SP']+'-'+d['EP']
				else:	
					d['pages'] = d['SP']+'-'+d['EP']
				
			
			if line.strip().startswith('T1'):
				d['T1'] = line.split('-', 1)[1].replace('"', '').lstrip().rstrip().strip('\n')
				if not d['T1'].endswith('.'):
					d['T1']=d['T1']+'.'
				
				
			if line.strip().startswith('TI'):
				d['T1'] = line.split('-', 1)[1].replace('"', '').lstrip().rstrip().strip('\n')	
				if not d['T1'].endswith('.'):
					d['T1']=d['T1']+'.'
					
			
			if line.strip().startswith('A1'):
				all_author.append(line.split('-', 1)[1].lstrip().rstrip().strip('\n'))
				d['first_author_last_name']=all_author[0].split(',')[0]
				d['A1'] = '\nand '.join(all_author)
			
			if line.strip().startswith('AU'):
				all_author.append(line.split('-', 1)[1].lstrip().rstrip().strip('\n'))
				first_author = all_author[0]
				char_first_author = [c for c in first_author]
				if ',' in char_first_author:
					d['first_author_last_name']=first_author.split(',')[0]
				else:
					d['first_author_last_name']=first_author.split(' ', 1)[0]	
				d['A1'] = '\nand '.join(all_author)	
			
			if line.strip().startswith('Y1'):
				year = re.search(r'(\d{4})', line)	
				d['Y1'] = 	year.group()


			if line.strip().startswith('PY'):
				year = re.search(r'(\d{4})', line)	
				d['Y1'] = 	year.group()

			if line.strip().startswith('IS'):
				issue = line.split('-', 1)[1].lstrip().rstrip().strip('\n')
				d['IS'] = issue

			if line.strip().startswith('VL'):
				volume = line.split('-', 1)[1].lstrip().rstrip().strip('\n')
				if volume.isnumeric():
					d['VL'] = volume
				else:
					d['VL'] = ' '
							
				
			
			if line.strip().startswith('ER'):
				if len(d['pages']) !=0:
					first_page = d['pages'].split('-', 1)[0]
					if first_page.isdigit():
						d['at_article'] = d['first_author_last_name'].replace(' ', '')+d['Y1']+first_page
					else:
						d['at_article'] = d['first_author_last_name'].replace(' ', '')+d['Y1']	
				
					
								
				master_list.append(d)

		
		




		for record in master_list:
			bib_file.write(normalize_unicode_to_ascii('@Article{'+record['at_article']+','+'\n').replace(' ', ''))
			bib_file.write(normalize_unicode_to_ascii('author'+'='+'"%s"'%(record['A1'])+','+'\n'))
			bib_file.write(normalize_unicode_to_ascii('doi'+'='+'"%s"'%(record['DO'])+','+'\n'))
			bib_file.write(normalize_unicode_to_ascii('issn'+'='+'"%s"'%(record['SN'])+','+'\n'))
			if len(d['JF']) > 1:
				bib_file.write(normalize_unicode_to_ascii('journal'+'='+'"%s"'%(record['JF'])+','+'\n'))
			else:
				bib_file.write(normalize_unicode_to_ascii('journal'+'='+'"%s"'%(record['JA'])+','+'\n'))	
			bib_file.write(normalize_unicode_to_ascii('pages'+'='+'"%s"'%(record['pages'])+','+'\n'))
			bib_file.write(normalize_unicode_to_ascii('title'+'='+'"%s"'%(record['T1'])+','+'\n'))
			bib_file.write(normalize_unicode_to_ascii('volume'+'='+'"%s"'%(record['VL'])+','+'\n'))
			bib_file.write(normalize_unicode_to_ascii('issue'+'='+'"%s"'%(record['IS'])+','+'\n'))
			bib_file.write(normalize_unicode_to_ascii('year'+'='+'"%s"'%(record['Y1'])))
			bib_file.write('}'+'\n')
			bib_file.write(' '+'\n')

	return output_bib_file_name





ris_to_bib("/Users/dasp/Desktop/Deduplicator_Pipeline/cc/417_medline.ris")