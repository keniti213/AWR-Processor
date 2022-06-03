import os, pandas as pd

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
                # fix column labels
                #sectionLabel.insert(3, "hour_minute")
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

def main(directory):

    awrDir = directory
    reports = "./reports/"
    listaFiles = os.listdir(awrDir)

    if not os.path.exists(reports):
        os.makedirs(reports)
        
    outSummaryFile = open(reports + 'resumo-servidores.csv', 'w+')
    headerStringPrefix = "DBName;"
    headerStringSufix = "CPU_COUNT (vCPU);CPU_CORE_COUNT;PLATFORM_NAME;VERSION;INSTANCES\n"

    #outSummaryFile.write("DBName;NUM_CPU_CORES;NUM_CPU_SOCKETS;CPU_CORE_COUNT;CPU_SOCKET_COUNT;PLATFORM_NAME;VERSION;INSTANCES\n")

    summaryData = {}

    for fileName in listaFiles:
        if fileName.startswith("awr"):
            dbName = fileName.split('-')[3]
    		
    # BEGIN-SIZE-ON-DISK Section
            data = sectionData('BEGIN-OS-INFORMATION','END-OS-INFORMATION',awrDir + fileName)
            if not data.empty:    
                summaryData[dbName] = data
            
    dfsum = pd.DataFrame()
    maxHosts = 0
    numHosts = 0
    outStringPrefix = {}
    outStringSufix = {}

    for dbname in summaryData:
        outStringPrefix[dbname] = dbname + ";"
        df = summaryData[dbname]
        print(dbname)
        print(df)

        cpu_count = df.loc[df['STAT_NAME'] == '!CPU_COUNT'].iloc[0]['STAT_VALUE']
        cpu_core_count = df.loc[df['STAT_NAME'] == '!CPU_CORE_COUNT'].iloc[0]['STAT_VALUE']
        platform_name = df.loc[df['STAT_NAME'] == 'PLATFORM_NAME'].iloc[0]['STAT_VALUE']
        db_version = df.loc[df['STAT_NAME'] == 'VERSION'].iloc[0]['STAT_VALUE']
        num_instances = df.loc[df['STAT_NAME'] == 'INSTANCES'].iloc[0]['STAT_VALUE']
        hostnames = df.loc[df['STAT_NAME'] == 'HOSTS'].iloc[0]['STAT_VALUE']

        hostsArr = hostnames.split(",")
        numHosts = len(hostsArr)

        if numHosts > maxHosts:
            maxHosts = numHosts

        for host in hostsArr:
            outStringPrefix[dbname] += host + ";"

        outStringSufix[dbname] = cpu_count + ";" + cpu_core_count + ";" + platform_name + ";" + db_version + ";" + num_instances + "\n"

    for index in range(1, (maxHosts + 1)):
        headerStringPrefix += "Hostname-" + str(index) + ";"

    #Write Header
    outSummaryFile.write(headerStringPrefix + headerStringSufix + "\n")

    #Write db string
    for dbname in outStringPrefix:
        numHosts = len(outStringPrefix[dbname].split(";")) - 1

        for index in range(numHosts, maxHosts + 1):
            outStringPrefix[dbname] += ";"

        print(outStringPrefix[dbname] + outStringSufix[dbname])
        outSummaryFile.write(outStringPrefix[dbname] + outStringSufix[dbname])

    outSummaryFile.close()


if __name__ == "__main__":

    files_path = "./csv/"
    main(files_path)