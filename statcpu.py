import os, shutil, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


def sectionData(startString, endString, inFileName):
	
    sectionData = []
	
    with open(inFileName, 'r') as inputFile:
        for line in inputFile:
            if startString in line:
                line = next(inputFile)

                #Push Header
                while len(line) <= 1:
                    line = next(inputFile)
                sectionData.append(line.split())

                #Separator Dashed Line used to delimit columns
                line = next(inputFile)
                columns_width = [len(column) for column in line.split()]
                line = next(inputFile)

                while (endString not in line) and (len(line) > 1):
                    # Cannot use simple split because some columns are blank
                    fields = lineSplitter(line, columns_width)
                    sectionData.append(fields)
                    line = next(inputFile)
                sectionLabel = sectionData.pop(0)
                break
    df = pd.DataFrame.from_records(sectionData, columns = sectionLabel)	
    #return(df.loc[df['inst'] == str(InstanceNumber)])
    return df


def lineSplitter(inputLine, columns_width):
    columns = []
    index = 0
    for width in columns_width:
        sub_string = inputLine[index:index+width].strip()
        if len(sub_string) == 0:
            # Blank Fields are replaced with -1.0
            sub_string = '-1.0'
        columns.append(sub_string)
        index = index + width + 1
    return columns


def formatter(input_number):
    return(str('{:.2f}'.format(input_number)))


def plotHistogram(timeSeries, outFile, tittle, xLabel, yLabel="frequencia normalizada"):
#    plt.hist(timeSeries, 25, density=1)
    fig, axs = plt.subplots()
    axs.hist(timeSeries, bins=100, density=True)
    axs.yaxis.set_major_formatter(PercentFormatter(xmax=1))
#    plt.hist(timeSeries, bins=100)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.title(tittle)
    plt.savefig(outFile + ".png")
    plt.close()


def plotGraph(timeSeries, outFile, tittle, xLabel, yLabel="% CPU"):
    plt.plot(timeSeries)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.title(tittle)
    plt.savefig(outFile + ".png")
    plt.close()


def createHostPath(servers, histogram_path, graphs_path):
    for server in servers:
        for sub_dir in histogram_path, graphs_path:
            if not os.path.isdir(sub_dir + server):
                os.makedirs(sub_dir + server)


def main(directory):

    awrDir = "./" + directory + "/"
    reports = "./reports/"
    histDir = "./plots-histogram/"
    graphDir = "./plots-graphs/"

    if not os.path.exists(reports):
        os.makedirs(reports)
    
    for sub_path in histDir, graphDir:
        if not os.path.isdir(sub_path):
            os.makedirs(sub_path)
        else:
            shutil.rmtree(sub_path, ignore_errors=True)
            os.makedirs(sub_path)            

    listaFiles = os.listdir(awrDir)

    outSummaryFile = open(reports + 'resumo-databases-' + directory + '.csv', 'w+')
    outSummaryFile.write("DBName;Instance;AVG CPU;CPU P95;CPU Max;DB CPU Max;DB CPU P95; \
        Read IOPS Max;Write IOPS Max;Read MBPS Max;Write MBPS Max; \
        Redo Log MBPS;Max Sessions\n")

#    for instance in range(1,5):
#        print("instance " + str(instance))
    summaryData = {}
    number_of_cpus = {}
    number_of_instances = {}
    hostnames = {}
    os_data = {}

    for fileName in listaFiles:
        if fileName.endswith(".out") and fileName.startswith("awr"):
            print(fileName)
            dbName = fileName.split('-')[3]

            # BEGIN-OS-INFORMATION Section
            data_os = sectionData('BEGIN-OS-INFORMATION','END-OS-INFORMATION',
                awrDir + fileName)
            if not data_os.empty:
                try:
                    number_of_cpus[dbName] = int(data_os.loc[data_os['STAT_NAME'] == 'NUM_CPUS'].iloc[0]['STAT_VALUE'])
                except:
                    number_of_cpus[dbName] = 'n/a'

                try:
                    number_of_instances[dbName] = int(data_os.loc[data_os['STAT_NAME'] == 'INSTANCES'].iloc[0]['STAT_VALUE'])
                except:
                    number_of_instances[dbName] = 'n/a'

                try:
                    hostnames[dbName] = data_os.loc[data_os['STAT_NAME'] == 'HOSTS'].iloc[0]['STAT_VALUE'].split(",")
                except:
                    hostnames[dbName] = 'n/a'
 
            # BEGIN-MAIN-METRICS Section
            summaryData[dbName] = sectionData('BEGIN-MAIN-METRICS','END-MAIN-METRICS',
                awrDir + fileName)
            if summaryData[dbName].empty:
                print(dbName + " data is empty")

        #Create subdirs under reports dir for each Host. If subdirs exists, clean them up before running next session
        createHostPath(hostnames[dbName], histDir, graphDir )

    for dbname in summaryData:

        for instance in range(1,(number_of_instances[dbname] + 1)):
            data_from_all_instances = summaryData[dbname]
            data_of_instance = data_from_all_instances.loc[data_from_all_instances['inst'] == str(instance)]
            outString = dbname + ";" + str(instance) + ";"

            graphsMainPath = graphDir + hostnames[dbname][instance - 1]
            histMainPath = histDir + hostnames[dbname][instance - 1]
            tittle = dbname + "-instance-" + str(instance)

            # CPU stats
            os_cpu_max = pd.to_numeric(data_of_instance['os_cpu_max'].str.replace(',', '.'))
            plotGraph(os_cpu_max, graphsMainPath + "/cpu-max-" + tittle, tittle, "amostra", "% CPU máxima")
            plotHistogram(os_cpu_max, histMainPath + "/cpu-max-" + tittle, tittle, "% CPU máxima")

            if number_of_cpus[dbname] != 'n/a':
                db_cpu = pd.to_numeric(data_of_instance['cpu_per_s'].str.replace(',', '.'))
                db_cpu = db_cpu/number_of_cpus[dbname]*100
                plotGraph(db_cpu, graphsMainPath + "/db-cpu-" + tittle, tittle, "amostra", "% DB CPU")
                plotHistogram(db_cpu, histMainPath + "/db-cpu-" + tittle, tittle, "% DB CPU")

            # I/O READ MB stats
            read_mb_s_max = pd.to_numeric(data_of_instance['read_mb_s_max'].str.replace(',', '.'))
            plotGraph(read_mb_s_max, graphsMainPath + "/read-MB-max-" + tittle, tittle, "amostra", "Read MB máximo")
            plotHistogram(read_mb_s_max, histMainPath + "/read-MB-max-" + tittle, tittle, "Read MB máximo")

            # I/O READ IOPS Stats
            read_iops_max = pd.to_numeric(data_of_instance['read_iops_max'].str.replace(',', '.'))
            plotGraph(read_iops_max, graphsMainPath + "/read-IOPS-max-" + tittle, tittle, "amostra", "Read IOPS máximo")
            plotHistogram(read_iops_max, histMainPath + "/read-IOPS-max-" + tittle, tittle, "Read IOPS máximo")

            # I/O WRITE MB stats
            write_mb_s_max = pd.to_numeric(data_of_instance['write_mb_s_max'].str.replace(',', '.'))
            plotGraph(write_mb_s_max, graphsMainPath + "/write-MB-max-" + tittle, tittle, "amostra", "Write MB máximo")
            plotHistogram(write_mb_s_max, histMainPath + "/write-MB-max-" + tittle, tittle, "Write MB máximo")

            # I/O WRITE IOPS Stats
            write_iops_max = pd.to_numeric(data_of_instance['write_iops_max'].str.replace(',', '.'))
            plotGraph(write_iops_max, graphsMainPath + "/write-IOPS-max-" + tittle, tittle, "amostra", "Write IOPS máximo")
            plotHistogram(write_iops_max, histMainPath + "/write-IOPS-max-" + tittle, tittle, "Write IOPS máximo")

            # REDO LOG Write
            redo_mb_s = pd.to_numeric(data_of_instance['redo_mb_s'].str.replace(',', '.'))
            plotGraph(redo_mb_s, graphsMainPath + "/REDO-MB-per-sec-" + tittle, tittle, "amostra", "REDO MB/s")
            plotHistogram(redo_mb_s, histMainPath + "/REDO-MB-per-sec-" + tittle, tittle, "REDO MB/s")

            max_sessions = pd.to_numeric(data_of_instance['aas_max'].str.replace(',', '.'))
            plotGraph(max_sessions, graphsMainPath + "/Max-Sessions-" + tittle, tittle, "amostra", "Max Sessions")
            plotHistogram(max_sessions, histMainPath + "/Max-Sessions-" + tittle, tittle, "Max Sessions")

            # csv string
#            outString = outString + formatter(os_cpu_max.mean()) + ";" + formatter(os_cpu_max.max()) + ";"
            outString = outString + formatter(os_cpu_max.mean()) + ";"
            outString = outString + formatter(os_cpu_max.quantile(0.95)) + ";" + formatter(os_cpu_max.max()) + ";"
            outString = outString + formatter(db_cpu.max()) + ";"
            outString = outString + formatter(db_cpu.quantile(0.95)) + ";"
            outString = outString + formatter(read_iops_max.max()) + ";" + formatter(write_iops_max.max()) + ";"
            outString = outString + formatter(read_mb_s_max.max()) + ";" + formatter(write_mb_s_max.max()) + ";"
            outString = outString + formatter(redo_mb_s.max()) + ";" + formatter(max_sessions.quantile(0.95)) + "\n"
            print(outString)
            outSummaryFile.write(outString)

    outSummaryFile.close()


if __name__ == "__main__":

    if (sys.argv != 2) or not os.path.exists(sys.argv[1]):
        print("invalid arguments\n")
        sys.exit

    source_files = sys.argv[1]
    main(source_files)