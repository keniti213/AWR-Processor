import os, pandas as pd
import matplotlib.pyplot as plt


def sectionData(startString, endString, inFileName):
    
    sectionData = []
    emptyFlag = True
    with open(inFileName, 'r') as inputFile:
        for line in inputFile:
            if startString in line:
                emptyFlag = False
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
    if emptyFlag:
        return pd.DataFrame()
    else:
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



def main(directory):

    awrDir = directory
    reports = "./reports/"
    histDir = "./plots-histogram/"
    graphDir = "./plots-graphs/"

    listaFiles = [fileName for fileName in os.listdir(awrDir) if fileName.startswith('awr-')]
    
    if not os.path.isdir(reports):
        os.makedirs(reports)

    outSummaryFile = open(reports + 'resumo-storage-bs' + '.csv', 'w+')
    outSummaryFile.write("DBName;TOTAL SIZE_GB\n")

    summaryData = {}

    for fileName in listaFiles:
        dbName = fileName.split('-')[3]
        print("Processing ", fileName)
    # BEGIN-SIZE-ON-DISK Section
        data = sectionData('BEGIN-SIZE-ON-DISK','END-SIZE-ON-DISK',awrDir + fileName)
        if not data.empty:    
            summaryData[dbName] = data
        else: 
            continue
            
    dfsum = pd.DataFrame()

    for dbname in summaryData:
        graphsMainPath = graphDir
        histMainPath = histDir
        tittle = dbname
        outString = dbname + ";"
        diskStorage = pd.to_numeric(summaryData[dbname]['SIZE_GB'].str.replace(',', '.'))
        plotGraph(diskStorage, graphsMainPath + "/Storage-GB-" + tittle, tittle, "amostra", "Storage GB")
        outString = outString + formatter(diskStorage.max()) + "\n"
        print(outString)
        outSummaryFile.write(outString)


    outSummaryFile.close()


if __name__ == "__main__":

    files_list = "./csv/"
    main(files_list)