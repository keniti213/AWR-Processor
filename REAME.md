Programa AWR Processor

	Este programa serve como alternativa quando houver problemas no processamento pela ferramenta oficial BAR Tool (sizingtool).
	
	E' importante ressaltar que ele NAO SUBSTITUI a ferramenta oficial BAR Tool e serve apenas como ultimo recurso, caso nao se possa usar o BAR Tool.
	
	O Objetivo do programa e' gerar uma planilha para ser usada para popular a planilha "offline Consolidation Workbook" do BAR Tool, disponivel em :
	
	http://sizingtool.oraclecorp.com/apex/download_application_resource?p_id=D558C890F2B498A7E0533C422C0A503F
	
	Esta planilha "offline Consolidation Workbook" possui 3 abas principais :
	
		- "Database Servers"
		- "Databases"
		- "DB <->Server Mappings"
		
	Este programa gera uma planilha com 3 abas, cada uma correspondendo as 3 abas da planilha "offline Consolidation Workbook". Assim, basta que se faca o copy-n-paste
	de cada aba da saida deste programa para a aba correspondente na planilha "offline Consolidation Workbook". Por exemplo, a aba "Databases" da planilha de saida deste
	programa deve ir para a aba "Databases" da planilha "offline Consolidation Workbook". Na aba "Database servers", o modelo de maquina/CPU ainda precisa ser preenchido
	manualmente.
	
	Com a planilha "offline Consolidation Workbook" preenchida, pode-se fazer o upload para o BAR Tool para se continuar o processamento do sizing pela ferramenta oficial.
	
	Alem desta planilha, o programa gera graficos, um resumo dos Databases em formato .csv e tambem disponibiliza as sessoes de MAIN METRICS dos arquivos de saida do
	AWR Miner em formato .csv para os casos em que se queira processar os dados em planilha excel.
	
Pre-requisitos

	- Python 3.x instalado. O programa foi testado com Python 3.6 e acima.
	- Ha pacotes necessarios para a execucao do programa. Estes pacotes estao no arquivo requirements.txt. Caso nao estejam instalados, basta executar:
	
		python -m pip install -r requirements.txt
		
	- Arquivo parameters.yaml : aqui podem ser parametrizados alguns valores para a execucao do programa. 
	  O principal parametro e' o DEFAULT_PERCENTILE que determina a utilizacao de CPU de cada Servidor. Se for 1, todos os picos serao considerados.
	  Se for, por exemplo, 0.95 , serao descartadas 5% das amostras com maior uso de CPU. Deve-se ajusta-lo de acordo as necessidades do projeto.
	
	- Ultima versao do "AWR Miner Collection" script, pois algumas colunas mudaram de nome no arquivo de saida.
	
Execucao

	Os arquivos de saida do AWR Miner deverao ficar em um subdiretorio a partir do diretorio de execucao do programa.
	
	Por exemplo, se o diretorio onde estiver o programa for C:\Users\userx\Desktop\ , criar um subdiretorio, por exemplo "csv", e colocar todos os arquivos 
	do AWR Miner neste subdiretorio C:\Users\userx\Desktop\csv .
	
	Para executar o programa, basta executar :
	
	python offline-workbook-2-8.py <subdiretorio dos arquivos do AWR Miner>
	
	Seguindo o exemplo do subdiretorio com nome "csv", o comando de execucao sera:
	
	python offline-workbook-2-8.py  csv
	
	Serao gerados os seguintes subdiretorios apos a sua execucao :

		- "plots-graphs" : contem arquivos de figura dos graficos de CPU, I/O e Sessoes separados por servidor.
		- "plots-histogram" : contem os histogramas de utilizacao de CPU, I/O e Sessoes separados por Servidor.
		- "reports" : neste subdiretorio sao gerados os seguintes arquivos :

			- planilha de saida para copy-n-paste para a planilha oficial "offline Consolidation Workbook". O prefixo do nome desta planilha esta no parametro "output_excel_file"
 			  do arquivo parameters.yaml e tem valor default 'Offline-Workbook-source'. A este nome sera adicionada a data, hora, minuto e segundo de execucao do programa. 
			  Um exemplo de nome da planilha e' Offline-Workbook-source-20-05-2022-10-10-30.xlsx
			
			- planilha de resumo dos databases. O nome desta planilha esta no parametro "output_summary_file" do arquivo parameters.yaml e contem um resumo dos databases.
			
			- arquivos da sessao MAIN METRICS de cada arquivo do AWR Miner em formato .csv. Estes arquivos podem ser usados caso se queira processar os dados em Excel ao 
			  inves de se usar as saidas deste programa. Sera gerado um arquivo por instancia de cada Database.

Consideracoes sobre o programa

	Como esta nao e' uma ferramenta oficial, e' sempre importante verificar a consistencia dos resultados, pois possiveis bugs podem ocorrer.
