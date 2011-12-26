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


#Remover arquivos no output, se existir
import os
try:
	os.remove('output/relatorioBD.odt')
except OSError:
	pass

# Abre o arquivo de log, para fazer o parse no python
# Este arquivo fica localizado na pasta do ultimoBuild
# ~/.hudson/jobs/NomeDoJob/builds/NumeroUltimoJob/log
# O NumeroUltimoJob pode ser conseguido lendo o arquivo (NomeDoJob/nextBuildNumber) e subtraindo 1.
arquivoLog = open('consoleSQL.log')

#Dicionario com os itens que serao passado para o relatório
varsRelat={}

# Pegar o numero da revisão
for linha in arquivoLog:
	if linha.startswith('At revision'):
		varsRelat['numeroRevisao'] = linha[12:]
		break

#Pegando as partes importantes do log do BD, relatando arquivos OK e em falha
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
	# Se numero de sucesso igual total, nao adiciona objSQL na lista
	if ('SQL statements executed successfully' in linha):
		numerosExecucao = [int(s) for s in linha.split() if s.isdigit()]
		if numerosExecucao[0] != numerosExecucao[1]:
			objSQL['erros'] = output
			objetosSQL.append(objSQL)
		objSQL = {}
		output = []
varsRelat['objetosSQL'] = objetosSQL
varsRelat['errosDoBanco'] = output

# e setando os itens
varsRelat['dataExecucao']='14/12/2011 às 13:13'

# cria o renderizador, passando o dicionário, e então renderiza pro arquivo de saída, usando o template
renderer = Renderer('templates/templateBD.odt', varsRelat, 'output/relatorioBD.odt')
renderer.run()



'''
# Relatorio do findbugs
# o arquivo que contem os erros é o findbugs-warnings.xml localizado em
# ~/.hudson/jobs/SIGA-BuildTrunk/builds/33/findbugs-warnings.xml

# Fazer parse de xml para objeto Python:
# com o minidom parece ter mais futuro: http://www.faqs.org/docs/diveintopython/kgp_parse.html
#  http://www.evanjones.ca/software/simplexmlparse.html

from xml.dom import minidom
# Lista de objetos DOM bug
bugs = minidom.parse('findbugs-warnings.xml').getElementsByTagName('bug')
listaBugs = []
for b in bugs:
	bug = {}
	bug['message'] = b.getElementsByTagName('message')[0].firstChild.data
	bug['priority'] = b.getElementsByTagName('priority')[0].firstChild.data
	bug['lineRanges'] = {'start': b.getElementsByTagName('lineRanges')[0].getElementsByTagName('start')[0].firstChild.data, 'end': b.getElementsByTagName('lineRanges')[0].getElementsByTagName('end')[0].firstChild.data}
	bug['fileName'] = b.getElementsByTagName('fileName')[0].firstChild.data
	bug['moduleName'] = b.getElementsByTagName('moduleName')[0].firstChild.data
	bug['packageName'] = b.getElementsByTagName('packageName')[0].firstChild.data
	bug['category'] = b.getElementsByTagName('category')[0].firstChild.data
	bug['type'] = b.getElementsByTagName('type')[0].firstChild.data
	bug['pathName'] = b.getElementsByTagName('pathName')[0].firstChild.data
	bug['rank'] = b.getElementsByTagName('rank')[0].firstChild.data
	
	listaBugs.append(bug)
	
# ordenada por prioridade
# http://stygianvision.net/updates/python-sort-list-object-dictionary-multiple-key/
# http://stackoverflow.com/questions/72899/in-python-how-do-i-sort-a-list-of-dictionaries-by-values-of-the-dictionary
listaSorted = sorted(listaBugs, key = lambda b: b['priority'])
'''

# Arquivo com resultado do selenium: ~/.hudson/jobs/SIGA-SeleniumTrunk/workspace/junit/TEST-org.sigaept.edu.teste.versoes.TSSigaEdu.xml