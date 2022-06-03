import os, pandas as pd

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


def main(directory):

    awrDir = directory
    reports = "./reports/"
    listaFiles = os.listdir(awrDir)

    if not os.path.isdir(reports):
        os.makedirs(reports)

    outFile = open(reports + 'resumo-memoria-sga-pga-bs' + '.csv', "w+")
    outFile.write("DBNAME;Instance;Total Memory GB\n")

    for fileName in listaFiles:
        if fileName.startswith("awr-hist"):
            dbName = fileName.split('-')[3]

        # BEGIN-MEMORY Section
            data = sectionData('~BEGIN-MEMORY~','~END-MEMORY~',awrDir + fileName)

            for instance in range(1,5):
                if not data.empty:
                    instance_data = data.loc[data['INSTANCE_NUMBER'] == str(instance)]
                    total_memory = pd.to_numeric(instance_data['TOTAL'].str.replace(',', '.'))
                    if not total_memory.empty:
                        print("dbname: " + dbName + "[" + str(instance) + "] " + str(total_memory.max()))
                        outFile.write(dbName + ";" + str(instance) + ";" + str(total_memory.max()) + "\n")

    outFile.close()


if __name__ == "__main__":

    files_list = "./csv/"
    main(files_list)