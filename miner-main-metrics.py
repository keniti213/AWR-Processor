#
# Version 1.0 10-Mar-2021
#
import os, shutil, sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter


def sectionData(startString, endString, inFileName):
	
    sectionData = []
    found_section_flag = False
	
    with open(inFileName, 'r') as inputFile:
        for line in inputFile:
            if startString in line:
                found_section_flag = True
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
    if found_section_flag:
        return pd.DataFrame.from_records(sectionData, columns = sectionLabel)
    else:
        return pd.DataFrame()


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


def numFormatter(input_number):
    return('{:.2f}'.format(input_number))


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


def plotGraph(dataFrame, column, outFile, title, xLabel="Timestamp", yLabel="% CPU"):
    dataFrame.plot(y=column)
    plt.ylabel(yLabel)
    plt.title(title)
    plt.xticks(rotation=60)
    plt.xlabel("Timestamp")
    plt.tight_layout()
    plt.savefig(outFile + ".png")
    plt.show()
    plt.close()


def createHostPath(servers, histogram_path, graphs_path):
    for server in servers:
        for sub_dir in histogram_path, graphs_path:
            if not os.path.isdir(sub_dir + server):
                os.makedirs(sub_dir + server)


def convertToPoint(col):
    return col.str.replace(',', '.')


# Creates the Databases and DB<->Server Mappings tabs in the OfflineCustomerWorkbook sizingtool spreadsheet 
def main(directory):

    awrDir = "./" + directory + "/"
    reports = "./reports-main-metrics/"
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

    main_metrics = {}
    cpu_metrics = pd.DataFrame()

    distribution_df = pd.DataFrame(columns=["10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%", "Total Samples"])
    #distribution_df = pd.DataFrame()

    for fileName in listaFiles:
        if fileName.endswith(".out") and fileName.startswith("awr"):
            print(fileName)
            db_name = fileName.split('-')[3]

            # This Section gets Main info to populate DBDataFrame and MappingDataFrame
            main_metrics[db_name] = sectionData('BEGIN-MAIN-METRICS','END-MAIN-METRICS',
                awrDir + fileName)
            if main_metrics[db_name].empty:
                print(db_name + " Main metrics is empty. Skipping this Database")
                main_metrics.pop(db_name)
                continue
            # end of Section to get Main info to populate DBDataFrame and MappingDataFrame

            # Write DataFrame to csv
            total_snaps = len(main_metrics[db_name])
            main_metrics[db_name]["os_cpu_max"] = main_metrics[db_name]["os_cpu_max"].str.replace(',', '.')
            main_metrics[db_name]["os_cpu_max"] = main_metrics[db_name]["os_cpu_max"].astype(float)

            hour_minute = main_metrics[db_name]["end"].str.split(" ", n =1, expand = True)
            main_metrics[db_name]["hhmm"] = hour_minute[1]

            cpu_metrics = main_metrics[db_name][["hhmm","os_cpu", "os_cpu_max"]]

            index = 0
            distribution = []
            cumulative = 0

            for quartil in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:

                sample_count = len(main_metrics[db_name]["os_cpu_max"][main_metrics[db_name]["os_cpu_max"] <= quartil])

                if index == 0:
                    distribution.append(round((sample_count/total_snaps*100), 2))
                    cumulative += sample_count
                else:
                    distribution.append(round(((sample_count - cumulative)/total_snaps*100), 2))
                    cumulative = sample_count

                index += 1

            distribution.append(total_snaps)

            distribution_df.loc[db_name] = distribution
            distribution_df.to_csv("cpu_distribution.csv")
            print(distribution_df)


            #main_metrics[db_name]["db_cpu"] = main_metrics[db_name]["os_cpu_max"]/10
            print("Writing File : ", reports + db_name + "main-metrics.csv")
            main_metrics[db_name].to_csv(reports + db_name + "main-metrics.csv")
            cpu_metrics.to_csv(reports + db_name + "cpu-metrics.csv")
            #plotGraph(main_metrics[db_name], "os_cpu", db_name + "-os_cpu", db_name + " os_cpu", xLabel="Timestamp", yLabel="% CPU")
            #plotHistogram(main_metrics[db_name]["os_cpu"], db_name + "-os-cpu-HIST", db_name + "os_cpu", "% CPU", yLabel="frequencia normalizada")

            #plotGraph(main_metrics[db_name], "db_cpu", db_name + "-db_cpu", db_name + " db_cpu", xLabel="Timestamp", yLabel="% DB CPU")


if __name__ == "__main__":

    dirname = os.path.dirname(os.path.realpath(__file__))

    if (len(sys.argv) == 2) and os.path.exists(dirname + os.sep + sys.argv[1]):
        source_files = sys.argv[1]
        main(source_files)

    else:    
        print("invalid arguments: miner-main-metrics <input files directory>\n")
        sys.exit

#    main(source_files)