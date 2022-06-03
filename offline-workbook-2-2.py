#
# Version 1.0 10-Mar-2021
# Updates
# V2.0 (24-Maio-2021) - Alteracao no plot dos graficos no tempo com correcao do eixo X (data)
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
    plt.close()


def createHostPath(servers, histogram_path, graphs_path):
    for server in servers:
        for sub_dir in histogram_path, graphs_path:
            if not os.path.isdir(sub_dir + server):
                os.makedirs(sub_dir + server)


def getServersTemplate():
    server_columns = ['environment', 
        'server_name', 
        'server_model', 
        'chip_count',
        'cores_per_chip', 
        'cpu_utilization', 
        'system_memory',
        'memory_util', 
        'io_bandwidth'
    ]
    return pd.DataFrame(columns=server_columns)


def renameColumnsServerDf(server_df):
    renamedColumns = { 'environment': 'Environment', 
        'server_name': 'Server Name', 
        'server_model': 'Server Model Name', 
        'chip_count': 'Chip Count (actual)',
        'cores_per_chip': 'Cores Per Chip (Actual)', 
        'cpu_utilization': 'CPU Utilization Peak (%)', 
        'system_memory': 'System Memory-RAM (GB)',
        'memory_util': 'Memory Utilization (%)', 
        'io_bandwdth': 'I/O Bandwidth MBPS (Peak)'
    }
    return df.rename(columns=renamedColumns)


def getDBTemplate():
    db_columns = ['environment', 
        'database_name', 
        'number_instances', 
        'vendor_name',
        'database_version', 
        'clustered', 
        'database_size', 
        'redo_log_space',
        'backup_size', 
        'landing_pad', 
        'db_memory',
        'shared_memory',
        'peak_connections'
    ]
    return pd.DataFrame(columns=db_columns)


def renameColumnsDBDf(server_df):
    renamedColumns = { 'environment':'Environment', 
        'database_name':'Database Name', 
        'number_instances':'Number of Instances', 
        'vendor_name':'DBMS Vendor Name',
        'database_version':'DBMS Version', 
        'clustered':'Clustered Database?', 
        'database_size':'Database Size (GB)', 
        'redo_log_space':'Redo Log Space (GB)',
        'backup_size':'Backup Size (GB)', 
        'landing_pad':'Landing Pad Size (GB)', 
        'db_memory':'DB Memory GB)',
        'shared_memory':'DB Shared Memory (GB)',
        'peak_connections':'Connections (Peak)'
    }
    return df.rename(columns=renamedColumns)


def getMappingTemplate():
    mapping_columns = ['database',
        'instance',
        'server',
        'io_growth',
        'read_requests',
        'write_requests',
        'read_optimization',
        'write_optimization',
        'flash_seg_total',
        'db_average_util',
        'sga_size_gb',
        'pga_size_gb'
    ]
    return pd.DataFrame(columns=mapping_columns)


def renameColumnsMappingDf(server_df):
    renamedColumns = { 'database':'Database*',
        'instance':'Instance*',
        'server':'Server*',
        'io_growth':'I/O Growth %*',
        'read_requests':'Read Requests/Sec (from AWR)',
        'write_requests':'Write Requests/Sec (from AWR)',
        'read_optimization':'Read Optimization Total I/O',
        'write_optimization':'Write Optimization Total I/O',
        'flash_seg_total':'Flash Seg Total GB',
        'db_average_util':'DB Average CPU Util %',
        'sga_size_gb':'SGA Size GB',
        'pga_size_gb':'PGA Size GB'
    }
    return df.rename(columns=renamedColumns)


# Build a Line corresponding to one of the DataFramed for ServerTemplate , DBTemplate or MappingTemplate
def insertLine(**kargs):
    line_series = {}
    for key, value in kargs.items():
        line_series[key] = value
    return line_series


def getShortDBVersion(db_version):
    major_version = db_version.split('.')
    versions = { '19': '19c', '18': '18c', '12': '12c',
        '11': '11g', '10': '10g', '9': '9i'}
    return versions[str(major_version[0])]


def convertToPoint(col):
    return col.str.replace(',', '.')


# Creates the Databases and DB<->Server Mappings tabs in the OfflineCustomerWorkbook sizingtool spreadsheet 
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

    outSummaryFile = open(reports + 'resumo-databases-2-' + directory + '.csv', 'w+')
    outSummaryFile.write("DBName;Instance;AVG CPU;CPU P95;CPU Max;DB CPU Max;DB CPU P95; \
        Read IOPS Max;Write IOPS Max;Read MBPS Max;Write MBPS Max; \
        Redo Log MBPS;Max Sessions\n")

#    for instance in range(1,5):
#        print("instance " + str(instance))
    main_metrics = {}
    number_of_cpus = {}
    number_of_cores = {}
    number_of_sockets = {}
    number_of_instances = {}
    physical_memory = {}
    db_version = {}
    hostnames = {}
    os_data = {}
    disk_size = {}
    sga_size = {}
    pga_size = {}
    sga_pga_total = {}

    # Create ServersDataFrame, DBDataFrame and MappingDataFrame
    servers_df = getServersTemplate()
    db_df = getDBTemplate()
    mapping_df = getMappingTemplate()

    for fileName in listaFiles:
        if fileName.endswith(".out") and fileName.startswith("awr"):
            print(fileName)
            db_name = fileName.split('-')[3]

            # This Section Gets information about Servers to populate the ServerDataFrame
            data_os = sectionData('BEGIN-OS-INFORMATION','END-OS-INFORMATION',
                awrDir + fileName)
            if not data_os.empty:
                try:
                    number_of_cpus[db_name] = int(data_os.loc[data_os['STAT_NAME'] == 'NUM_CPUS'].iloc[0]['STAT_VALUE'])
                except:
                    number_of_cpus[db_name] = ''

                try:
                    number_of_cores[db_name] = int(data_os.loc[data_os['STAT_NAME'] == 'NUM_CPU_CORES'].iloc[0]['STAT_VALUE'])
                except:
                    number_of_cores[db_name] = ''

                try:
                    number_of_sockets[db_name] = int(data_os.loc[data_os['STAT_NAME'] == 'NUM_CPU_SOCKETS'].iloc[0]['STAT_VALUE'])
                except:
                    number_of_sockets[db_name] = ''

                try:
                    physical_memory[db_name] = data_os.loc[data_os['STAT_NAME'] == 'PHYSICAL_MEMORY_GB'].iloc[0]['STAT_VALUE']
                    physical_memory[db_name] = float(physical_memory[db_name].replace(',','.'))
                except:
                    physical_memory[db_name] = ''

                try:
                    db_version[db_name] = data_os.loc[data_os['STAT_NAME'] == 'VERSION'].iloc[0]['STAT_VALUE']
                except:
                    db_version[db_name] = ''

                try:
                    number_of_instances[db_name] = int(data_os.loc[data_os['STAT_NAME'] == 'INSTANCES'].iloc[0]['STAT_VALUE'])
                except:
                    number_of_instances[db_name] = 0

                try:
                    hostnames[db_name] = data_os.loc[data_os['STAT_NAME'] == 'HOSTS'].iloc[0]['STAT_VALUE'].split(",")
                except:
                    hostnames[db_name] = None
            else:
                number_of_cpus[db_name] = ''
                number_of_cores[db_name] = ''
                number_of_sockets[db_name] = ''
                physical_memory[db_name] = ''
                db_version[db_name] = ''
                number_instances[db_name] = 0
                hostnames[db_name] = None

            # End of Section to populate ServerDataFrame

            #This Section gets informatiom about Disk Space to populate the DBDataFrame
            disk_data = sectionData('BEGIN-SIZE-ON-DISK','END-SIZE-ON-DISK',awrDir + fileName)
            if not disk_data.empty:    
                disk_size[db_name] = pd.to_numeric(disk_data['SIZE_GB'].str.replace(',', '.')).max()
            else: 
                disk_size[db_name] = None
            # End of Section to populate Disk Information of DBDataFrame
 
            # This Section gets Main info to populate DBDataFrame and MappingDataFrame
            main_metrics[db_name] = sectionData('BEGIN-MAIN-METRICS','END-MAIN-METRICS',
                awrDir + fileName)
            if main_metrics[db_name].empty:
                print(db_name + " Main metrics is empty. Skipping this Database")
                main_metrics.pop(db_name)
                continue
            # end of Section to get Main info to populate DBDataFrame and MappingDataFrame

            #This Section gets informatiom about SGA and PGA to populate the MappingDataFrame
            memory_data = sectionData('~BEGIN-MEMORY~','~END-MEMORY~',awrDir + fileName)
            if not memory_data.empty:
                sga_size[db_name] = ''
                pga_size[db_name] = ''
                sga_pga_total[db_name] = ''

                for instance in range(1, number_of_instances[db_name] + 1):
                    instance_number = main_metrics[db_name].iloc[instance]['inst']                    
                    instance_data = memory_data.loc[memory_data['INSTANCE_NUMBER'] == str(instance_number)]
                    total_sga = pd.to_numeric(instance_data['SGA'].str.replace(',', '.'))
                    total_pga = pd.to_numeric(instance_data['PGA'].str.replace(',', '.'))
                    total_memory = pd.to_numeric(instance_data['TOTAL'].str.replace(',', '.'))
                    sga_size[db_name] = total_sga.max()
                    pga_size[db_name] = total_pga.max()
                    sga_pga_total[db_name] = total_memory.max()
            else:
                sga_size[db_name] = ''
                pga_size[db_name] = ''
                sga_pga_total[db_name] = ''

            # End of Section to populate Disk Information of MappingDataFrame

        #Create subdirs under reports dir for each Host. If subdirs exists, clean them up before running next session
        createHostPath(hostnames[db_name], histDir, graphDir )

    for dbname in main_metrics:
        print("Working on " + dbname + " Database")
        # 
        # Initialize parameters to Populate DBDataFrame
        # Include entry in DBDataFrame
        #
        environment = ENVIRONMENT
        database_name = dbname
        number_instances = number_of_instances[dbname]
        vendor_name = 'ORACLE'
        database_version = getShortDBVersion(db_version[dbname])
        clustered = 'CLUSTERED' if number_of_instances[dbname] > 1 else 'NON-CLUSTERED'
        database_size = disk_size[dbname] if disk_size[dbname] != None else ''
        redo_log_space = (REDO_LOG_RATE * database_size) if database_size != '' else ''
        backup_size = ''
        landing_pad = ''
        db_memory = physical_memory[dbname] if physical_memory[dbname] != '' else ''
        shared_memory = sga_size[dbname] if sga_size[dbname] != '' else ''
        peak_connections = pd.to_numeric(main_metrics[dbname]['aas_max'].str.replace(',', '.')).max()

        line_to_append = insertLine(
            environment = environment,
            database_name = database_name,
            number_instances = number_instances,
            vendor_name = vendor_name,
            database_version = database_version,
            clustered = clustered,
            database_size = database_size,
            redo_log_space = redo_log_space,
            backup_size = backup_size,
            landing_pad = landing_pad,
            db_memory = db_memory, 
            shared_memory = shared_memory,
            peak_connections = peak_connections
            )
        
        db_df = db_df.append(line_to_append, ignore_index=True)
        # End of DBDataFrame insert

        for instance in range(1, (number_of_instances[dbname] + 1)):
            data_from_all_instances = main_metrics[dbname]

            instance_number = data_from_all_instances.iloc[instance]['inst']

            data_of_instance = data_from_all_instances.loc[data_from_all_instances['inst'] == str(instance_number)]
            outString = dbname + ";" + str(instance_number) + ";"

            graphsMainPath = graphDir + hostnames[dbname][instance - 1]
            histMainPath = histDir + hostnames[dbname][instance - 1]
            title = dbname + "-instance-" + str(instance_number)

            print("<--------- ANTES CHECK------------------->")
            # Convert comma to point and convert columns to number
            data_of_instance = data_of_instance.set_index("end")

            data_of_instance = data_of_instance.iloc[:,1:].apply(convertToPoint)

            data_of_instance = data_of_instance.iloc[:,1:].apply(pd.to_numeric)
            # Set index as the "end" columns, that is the timestamp of each AWR sample
            print(data_of_instance.head())
            data_of_instance.to_csv(reports + db_name + "main-metrics.csv")
            print("<--------- DEPOIS CHECK------------------->")
            # CPU stats
            plotGraph(data_of_instance, "os_cpu_max", graphsMainPath + "/cpu-max-" + title, title, "Timestamp", "% CPU máxima")
            plotHistogram(data_of_instance["os_cpu_max"], histMainPath + "/cpu-max-" + title, title, "% CPU máxima")

            if number_of_cpus[dbname] != '':
                data_of_instance["db_cpu"] = data_of_instance["cpu_per_s"]/number_of_cpus[dbname]*100
                plotGraph(data_of_instance, "db_cpu", graphsMainPath + "/db-cpu-" + title, title, "amostra", "% DB CPU")
                plotHistogram(data_of_instance["db_cpu"], histMainPath + "/db-cpu-" + title, title, "% DB CPU")

            # I/O READ MB stats
            plotGraph(data_of_instance, "read_mb_s_max", graphsMainPath + "/read-MB-max-" + title, title, "amostra", "Read MB máximo")
            plotHistogram(data_of_instance["read_mb_s_max"], histMainPath + "/read-MB-max-" + title, title, "Read MB máximo")

            # I/O READ IOPS Stats
            #read_iops_max = pd.to_numeric(data_of_instance['read_iops_max'].str.replace(',', '.'))
            plotGraph(data_of_instance, "read_iops_max", graphsMainPath + "/read-IOPS-max-" + title, title, "amostra", "Read IOPS máximo")
            plotHistogram(data_of_instance["read_iops_max"], histMainPath + "/read-IOPS-max-" + title, title, "Read IOPS máximo")

            # I/O WRITE MB stats
            #write_mb_s_max = pd.to_numeric(data_of_instance['write_mb_s_max'].str.replace(',', '.'))
            plotGraph(data_of_instance, "write_mb_s_max", graphsMainPath + "/write-MB-max-" + title, title, "amostra", "Write MB máximo")
            plotHistogram(data_of_instance["write_mb_s_max"], histMainPath + "/write-MB-max-" + title, title, "Write MB máximo")

            # I/O WRITE IOPS Stats
            #write_iops_max = pd.to_numeric(data_of_instance['write_iops_max'].str.replace(',', '.'))
            plotGraph(data_of_instance, "write_iops_max", graphsMainPath + "/write-IOPS-max-" + title, title, "amostra", "Write IOPS máximo")
            plotHistogram(data_of_instance["write_iops_max"], histMainPath + "/write-IOPS-max-" + title, title, "Write IOPS máximo")

            # REDO LOG Write
            #redo_mb_s = pd.to_numeric(data_of_instance['redo_mb_s'].str.replace(',', '.'))
            plotGraph(data_of_instance, "redo_mb_s", graphsMainPath + "/REDO-MB-per-sec-" + title, title, "amostra", "REDO MB/s")
            plotHistogram(data_of_instance["redo_mb_s"], histMainPath + "/REDO-MB-per-sec-" + title, title, "REDO MB/s")

            #max_sessions = pd.to_numeric(data_of_instance['aas_max'].str.replace(',', '.'))
            plotGraph(data_of_instance, "aas_max", graphsMainPath + "/Max-Sessions-" + title, title, "amostra", "Max Sessions")
            plotHistogram(data_of_instance["aas_max"], histMainPath + "/Max-Sessions-" + title, title, "Max Sessions")

            # csv string
#            outString = outString + formatter(os_cpu_max.mean()) + ";" + formatter(os_cpu_max.max()) + ";"
            outString = outString + formatter(data_of_instance["os_cpu_max"].mean()) + ";"
            outString = outString + formatter(data_of_instance["os_cpu_max"].quantile(DEFAULT_PERCENTILE)) + ";" \
                + formatter(data_of_instance["os_cpu_max"].max()) + ";"
            outString = outString + formatter(data_of_instance["db_cpu"].max()) + ";"
            outString = outString + formatter(data_of_instance["db_cpu"].quantile(DEFAULT_PERCENTILE)) + ";"
            outString = outString + formatter(data_of_instance["read_iops_max"].max()) + ";" \
                + formatter(data_of_instance["write_iops_max"].max()) + ";"
            outString = outString + formatter(data_of_instance["read_mb_s_max"].max()) + ";" \
                + formatter(data_of_instance["write_mb_s_max"].max()) + ";"
            outString = outString + formatter(data_of_instance["redo_mb_s"].mean()) + ";" \
                + formatter(data_of_instance["aas_max"].max()) + "\n"
            print(outString)
            outSummaryFile.write(outString)

            # 
            # Initialize parameters to Populate ServerDataFrame
            # Include entry in ServerDataFrame
            #
            environment = ENVIRONMENT 
            server_name = hostnames[dbname][instance -1] if hostnames[dbname] != None else ''
            # Server Model Name needs to be filled out manually
            server_model = ''
            chip_count = number_of_sockets[dbname] if number_of_sockets[dbname] != '' else ''
            # If the NUM CPUs equals NM CORES then the server is likely to be virtualized
            if (number_of_cores[dbname] != '') and (number_of_cpus[dbname] != ''):
                if number_of_cores[dbname] == number_of_cpus[dbname]:
                    cores_per_chip = number_of_cores[dbname]/2
                else:
                    cores_per_chip = number_of_cores[dbname]
            cpu_utilization = numFormatter(data_of_instance["os_cpu_max"].quantile(DEFAULT_PERCENTILE))
            system_memory = physical_memory[dbname] if physical_memory[dbname] != '' else ''
            # Size for Maximum present memory
            memory_util = 100
            io_bandwdth = (data_of_instance["read_mb_s_max"] + data_of_instance["write_mb_s_max"]).mean()

            line_to_append = insertLine(
                environment = environment, 
                server_name = server_name, 
                server_model = server_model, 
                chip_count = chip_count,
                cores_per_chip = cores_per_chip, 
                cpu_utilization = cpu_utilization, 
                system_memory = system_memory, 
                memory_util = memory_util, 
                io_bandwdth = io_bandwdth
                )
            
            servers_df = servers_df.append(line_to_append, ignore_index=True)
            #End of ServerDataFrame update

            # 
            # Initialize parameters to Populate ServerDataFrame
            # Include entry in ServerDataFrame
            #
            database = dbname
            instance = instance
            server = hostnames[dbname][instance -1] if hostnames[dbname] != None else ''
            io_growth = 10
            read_requests = numFormatter(data_of_instance["read_iops_max"].max())
            write_requests = numFormatter(data_of_instance["write_iops_max"].max())
            read_optimization = ''
            write_optimization = ''
            flash_seg_total = ''
            db_average_util = numFormatter(data_of_instance["db_cpu"].quantile(DEFAULT_PERCENTILE))
            sga_size_gb = sga_size[dbname] if sga_size[dbname] != '' else ''
            pga_size_gb = pga_size[dbname] if sga_size[dbname] != '' else ''

            line_to_append = insertLine(
                database = database,
                instance = instance,
                server = server,
                io_growth = io_growth,
                read_requests = read_requests,
                write_requests = write_requests,
                read_optimization = read_optimization,
                write_optimization = write_optimization,
                flash_seg_total = flash_seg_total,
                db_average_util = db_average_util,
                sga_size_gb = sga_size_gb,
                pga_size_gb = pga_size_gb
                )

            mapping_df = mapping_df.append(line_to_append, ignore_index=True)
            # End of MappingDataFrame Section

    outSummaryFile.close()

    # Aggregate duplicate Servers
    servers_df = servers_df.groupby(['environment', 'server_name'], as_index=False).agg({
        'server_model': 'first',
        'chip_count': 'first',
        'cores_per_chip': 'first',
        'cpu_utilization': 'max',
        'system_memory': 'max',
        'memory_util': 'max',
        'io_bandwidth': 'sum'
        })

    # Write DataFrames to Excel
    #print(servers_df)
    #print(db_df)
    #print(mapping_df)
    
    writer = pd.ExcelWriter(reports + output_excel_file, engine='xlsxwriter')
    servers_df.to_excel(writer, sheet_name = 'Database Servers')
    db_df.to_excel(writer, sheet_name = 'Databases')
    mapping_df.to_excel(writer, sheet_name = 'DB<-> Server Mappings')
    writer.save()
    print("Created " + reports + output_excel_file + " successfully")


if __name__ == "__main__":

    # DEFAULT PARAMETERS
    ENVIRONMENT = "PROD"
    DEFAULT_PERCENTILE = 0.95
    DEFAULT_ANNUAL_GROWTH = 10
    REDO_LOG_RATE = 0.1
    output_excel_file = 'Offline-Workbook-source.xlsx'

    dirname = os.getcwd()

    if (len(sys.argv) == 2) and os.path.exists(dirname + os.sep + sys.argv[1]):
        source_files = sys.argv[1]
        main(source_files)

    else:    
        print("invalid arguments: Offline-Workbook-2-2 <input files directory>\n")
        sys.exit