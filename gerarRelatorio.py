#encoding: utf8
# O 'template' ODT é um documento normal, os "Fields" que serão substituídos
# são apenas 'mudanças registradas' no OpenOffice.
# Faz o documento normal deixando o espaço reservado para os fields e então 
# vai em no menu "Editar -> Alterações -> Registrar", enquanto isto estiver
# habilitavo você estará na verdade adicionando fields de relatório  no template.
#
# Sites documentando o template:
#  http://appyframework.org/pod.html
#  http://appyframework.org/podWritingTemplates.html
#  http://appyframework.org/podWritingAdvancedTemplates.html

from appy.pod.renderer import Renderer
import simplexmlparse

# Global variables: used alongside the code.
projectName = 'WYSIWYG Project'
revisionNumber = None
strLogSQL = 'consoleSQL.log'

#Dicionario com os itens que serao passado para o relatório
varsBDReport = {}
varsFindBugs = {}

#Remover arquivos no output, se existir
import os
try:
	os.remove('output/relatorioBD.odt')
	os.remove('output/relatorioFindBugs.odt')
except OSError:
	pass

# Open the log file, to parse it on Python.
# This file is located on lastJob folder
# ~/.hudson/jobs/JobName/builds/lastJob/log
# lastJob number can be obtained reading the file 'JobName/nextBuildNumber' and sub 1.
arquivoLog = open(strLogSQL)

# Get the hour of test execution, by the modification time of log file.
import os.path
import datetime
dataHora = datetime.datetime.fromtimestamp(os.path.getmtime(strLogSQL))


# Get revision number
for linha in arquivoLog:
	if linha.startswith('At revision'):
		revisionNumber = linha[12:]
		break

# Default vars that have on any report
varsBDReport['projectName'] = projectName
varsFindBugs['projectName'] = projectName
varsBDReport['revision'] = revisionNumber
varsFindBugs['revision'] = revisionNumber
varsBDReport['dataExecucao'] = dataHora
varsFindBugs['dataExecucao'] = dataHora

# Database report: parse the log file
objetosSQL = []
objSQL = {}
output = []
for linha in arquivoLog:
	if ('Executing resource:' in linha):
		objSQL['nomeArquivo'] = linha[linha.rfind('/')+1:]
	elif (':' in linha) or ('successfully' in linha):
		if "[sql]" in linha:
			output.append(linha[12:])
		else:
			output.append(linha)
	# Only show in report if number of successful statements is not equals of total statements
	if ('SQL statements executed successfully' in linha):
		numerosExecucao = [int(s) for s in linha.split() if s.isdigit()]
		if numerosExecucao[0] != numerosExecucao[1]:
			objSQL['erros'] = output
			objetosSQL.append(objSQL)
		objSQL = {}
		output = []
varsBDReport['objetosSQL'] = objetosSQL
varsBDReport['errosDoBanco'] = output

# Create the renderer, passing the dict, and run it. More details on POD docs.
renderer = Renderer('templates/templateBD.odt', varsBDReport, 'output/relatorioBD.odt')
renderer.run()


# FindBugs Report
# o arquivo que contem os erros é o findbugs-warnings.xml localizado em
# ~/.hudson/jobs/SIGA-BuildTrunk/builds/33/findbugs-warnings.xml

# Fazer parse de xml para objeto Python:
# com o minidom parece ter mais futuro: http://www.faqs.org/docs/diveintopython/kgp_parse.html
#  http://www.evanjones.ca/software/simplexmlparse.html

from xml.dom import minidom
# Object list of DOM elements, each one representing a bug.
bugs = minidom.parse('findbugs-warnings.xml').getElementsByTagName('bug')
listaBugs = []
# Transform DOM elements in Python dicts
for b in bugs:
	bug = {}
	bug['message'] = b.getElementsByTagName('message')[0].firstChild.data
	bug['priority'] = b.getElementsByTagName('priority')[0].firstChild.data
	bug['lineRange'] = {'start': b.getElementsByTagName('lineRanges')[0].getElementsByTagName('start')[0].firstChild.data, 'end': b.getElementsByTagName('lineRanges')[0].getElementsByTagName('end')[0].firstChild.data}
	bug['fileName'] = b.getElementsByTagName('fileName')[0].firstChild.data
#	bug['moduleName'] = b.getElementsByTagName('moduleName')[0].firstChild.data
	bug['packageName'] = b.getElementsByTagName('packageName')[0].firstChild.data
	bug['category'] = b.getElementsByTagName('category')[0].firstChild.data
	bug['type'] = b.getElementsByTagName('type')[0].firstChild.data
	bug['pathName'] = b.getElementsByTagName('pathName')[0].firstChild.data
	bug['rank'] = b.getElementsByTagName('rank')[0].firstChild.data
	
	listaBugs.append(bug)
	
# Sort by priority, highest rank, category, message, allow future groups on report.
# http://stygianvision.net/updates/python-sort-list-object-dictionary-multiple-key/
# http://stackoverflow.com/questions/72899/in-python-how-do-i-sort-a-list-of-dictionaries-by-values-of-the-dictionary
listaBugs = sorted(listaBugs, key = lambda b: (b['priority'], -int(b['rank']), b['category'], b['message']))

#for i in listaBugs:
#	print i['priority'], ' <> ', i['category'], ' <> ', i['type'], ' <> ', i['rank']

varsFindBugs['bugs'] = listaBugs

renderer = Renderer('templates/templateFindBugs.odt', varsFindBugs, 'output/relatorioFindBugs.odt')
renderer.run()

# Arquivo com resultado do selenium: ~/.hudson/jobs/SIGA-SeleniumTrunk/workspace/junit/TEST-org.sigaept.edu.teste.versoes.TSSigaEdu.xml