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
varsFindBugsReport = {}

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
logFile = open(strLogSQL)

# Get the hour of test execution, by the modification time of log file.
import os.path
import datetime
dataHora = datetime.datetime.fromtimestamp(os.path.getmtime(strLogSQL))


# Get revision number
for line in logFile:
	if line.startswith('At revision'):
		revisionNumber = line[12:]
		break

# Default vars that have on any report
varsBDReport['projectName'] = projectName
varsFindBugsReport['projectName'] = projectName
varsBDReport['revision'] = revisionNumber
varsFindBugsReport['revision'] = revisionNumber
varsBDReport['dataExecucao'] = dataHora
varsFindBugsReport['dataExecucao'] = dataHora

# Database report: parse the log file
objetosSQL = []
objSQL = {}
output = []
for line in logFile:
	if ('Executing resource:' in line):
		objSQL['nomeArquivo'] = line[line.rfind('/')+1:]
	elif (':' in line) or ('successfully' in line):
		if "[sql]" in line:
			output.append(line[12:])
		else:
			output.append(line)
	# Only show in report if number of successful statements is not equals of total statements
	if ('SQL statements executed successfully' in line):
		resultsExec = [int(s) for s in line.split() if s.isdigit()]
		if resultsExec[0] != resultsExec[1]:
			objSQL['erros'] = output
			objetosSQL.append(objSQL)
		objSQL = {}
		output = []
varsBDReport['objetosSQL'] = objetosSQL
varsBDReport['errosDoBanco'] = output

# Close the file
logFile.close()

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
bugsList = []
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
	
	bugsList.append(bug)
	
# Sort by priority, highest rank, category, message, allow future groups on report.
# http://stygianvision.net/updates/python-sort-list-object-dictionary-multiple-key/
# http://stackoverflow.com/questions/72899/in-python-how-do-i-sort-a-list-of-dictionaries-by-values-of-the-dictionary
bugsList = sorted(bugsList, key = lambda b: (b['priority'], -int(b['rank']), b['category'], b['message']))

#for i in bugsList:
#	print i['priority'], ' <> ', i['category'], ' <> ', i['type'], ' <> ', i['rank']

varsFindBugsReport['bugs'] = bugsList

# Empty some memory
bugs = None
bugsList = None

renderer = Renderer('templates/templateFindBugs.odt', varsFindBugsReport, 'output/relatorioFindBugs.odt')
renderer.run()

# Arquivo com resultado do selenium: ~/.hudson/jobs/SIGA-SeleniumTrunk/workspace/junit/TEST-org.sigaept.edu.teste.versoes.TSSigaEdu.xml