# Converts iRacing ibt telemetry file to a csv file readable by the StintAnalyzer

# region ----- IMPORTS -----
# imports pyirsdk by kutu https://github.com/kutu/pyirsdk
import pyirsdk_convert
import pandas as pd
# endregion

# region ----- COLUMN DEFINITION ----- 
# specifies the required columns and defines the data type or data format
columns_float_1_factor_100 = "LapDistPct".split()
columns_float_2 = "AirPressure AirTemp Brake dcBrakeBias FrameRate FuelLevel FuelUsePerHour LapDist LFcoldPressure LFpressure LFtempL LFtempM LFtempR LRcoldPressure LRpressure LRtempL LRtempM LRtempR RFcoldPressure RFpressure RFtempL RFtempM RFtempR RRcoldPressure RRpressure RRtempL RRtempM RRtempR ThrottleRaw TrackTemp".split()
columns_float_4 = "AirDensity CpuUsageBG CpuUsageFG GpuUsage LapCurrentLapTime LapLastLapTime RelativeHumidity SessionTime".split()
columns_float_8 = "Lat Lon".split()
columns_float_2_factor_100 = "LFrideHeight LRrideHeight RFrideHeight RRrideHeight".split()
columns_float_2_factor_3_6 = "Speed".split()
columns_int = "dcABS dcTractionControl Gear Lap PlayerTireCompound RPM".split()
columns_bool = "BrakeABSactive OnPitRoad".split()
columns = columns_float_1_factor_100 + columns_float_2 + columns_float_4 + columns_float_8 + columns_float_2_factor_100 + columns_float_2_factor_3_6 + columns_int + columns_bool
# endregion

# variable for the while loop
convert_again : str = 'y'

# console title and intro
print("\nIBT-CONVERTER\n-------------")
print("Converts iRacing ibt telemetry file to a csv file readable by the StintAnalyzer (www.klaus-andres.de)\n")

while convert_again == 'y':
        
# region ----- INPUT FILE NAME ----
    file_name : str = str(input("Please drag you ibt-file in this window or enter the filename (.ibt not necessary) and press ENTER -> "))

    # validate file name
    # draged file with space in filename / the filename gets a "& '"" fronting and a "'"" ending / delete this
    if file_name[0:3] == "& '" and file_name[-1:] == "'":
        file_name = file_name[3:-1]

    # or they get a " at the beginning and the ending
    if file_name[0] == '"' and file_name[-1:] == '"':
        file_name = file_name[1:-1]
        
    # check if there is an .ibt ending or not
    if not file_name[-4:] == '.ibt':
        file_name = file_name + '.ibt'
# endregion

# region ----- INPUT COMPRESSION -----    
    compress_data = ''

    while compress_data not in ['y', 'n']:
        compress_data = str(input("\nCompress the data set? (y/n)\nThe data set contains 60 data points per second. WARNING: If you compress it, you will save disk and memory space and have a faster processing, but you may reduce the accuracy of the evaluation -> "))
        if compress_data not in ['y', 'n']:
            print("Please press 'y' or 'n'")

    if compress_data == 'y':
        compression_level = 0
        while compression_level < 6 or compression_level > 30:
            try:
                compression_level = int(input('\nPlease set the number of data points per second (min. 6 / max. 30) -> '))
                if compression_level < 6 or compression_level > 30:
                    raise ValueError
            except ValueError:
                print('Please enter an integer between 6 and 30.')
# endregion

# region ----- INPUT DIVIDE STINTS -----
    divide_stints = ''

    while divide_stints not in ['y', 'n']:

        divide_stints = str(input("\nDivide stints in separate csv-files? (y/n)\nA stint is completed by a regular pit entry. A pit stop due to a reset does not count as the end of a stint -> "))
        if divide_stints not in ['y', 'n']:
            print("Please press 'y' or 'n'")
# endregion

    print("\nStart converting ...")

# region ----- IMPORT TELEMETRY DATA AND CONVERT -----
    
    iribt = pyirsdk_convert.IBT()

    try:
        iribt.open(file_name)

        # number of datapoints in the dataset
        data_number = len(iribt.get_all('Speed'))
        
        # dict to create the pandas datafram
        data_dict = {}

        # gets the data for each column / if there is no such column in the ibt-file, the column gets the value 0
        for col in columns:
            data = iribt.get_all(col)
            if not data:
                data_dict[col] = [0] * (data_number)
            else:
                data_dict[col] = data

        # create the dataframe out of the column data
        df = pd.DataFrame(data_dict)
        
        # region ----- CONVERT THE DATA ----
        
        # float with two decimal places
        for col in columns_float_2:
            df[col] = df[col].round(2)

        # float with four decimal places
        for col in columns_float_4:
            df[col] = df[col].round(4)

        # float with eight decimal places
        for col in columns_float_8:
            df[col] = df[col].round(8)

        # float with one decimal place * 100
        for col in columns_float_1_factor_100:
            df[col] = df[col] * 100
            df[col] = df[col].round(1)

        # float with two decimal places * 100
        for col in columns_float_2_factor_100:
            df[col] = df[col] * 100
            df[col] = df[col].round(2)

        # float with two decimal places and factor 3.6 (Speed from m/s to km/h)
        for col in columns_float_2_factor_3_6:
            df[col] = df[col] * 3.6
            df[col] = df[col].round(2)

        # int
        for col in columns_int:
            df[col] = df[col].astype('int8')

        # bool
        for col in columns_bool:
            df[col] = df[col].astype('bool')

        # compress the data according to the compression_level (delete rows)
        if compress_data == 'y':
            df = df.iloc[::int(60/compression_level)]          
            # set the index fom 0 to n
            df.reset_index(inplace=True, drop=True)
        # endregion

        iribt.close()
# endregion

# region ----- IMPORT SESSION DATA AND CONVERT -----
        
        irsdk = pyirsdk_convert.IRSDK()
        irsdk.startup(test_file = file_name)
        
        # name of all session data keys that will be imported. String with a '*' between the keys (to create a list with the .split-command). 
        # written to the DataFrame in the column "SessionData" row [0] 
        session_keys = 'TrackName*TrackDisplayName*TrackConfigName*TrackLength*TrackCity*TrackCountry*TrackAltitude*TrackNumTurns*TrackWeatherType*TrackSkies*TrackSurfaceTemp*TrackAirTemp*TrackAirPressure*TrackWindVel*TrackRelativeHumidity*TrackFogLevel*TrackPrecipitation*EventType*TimeOfDay*Date*UserName*CarScreenName*CarScreenNameShort*IRating*LicString'

        # creates a string with all the session data according to session_key. Data is divided by a '*' to create a list with the .split-command.
        # written to the DataFrame in the column "SessionData" row [1]
        session_data : str = ''

        # region ----- TRACK DATA -----
        if irsdk['WeekendInfo']['TrackName']: session_data += (irsdk['WeekendInfo']['TrackName']) + '*'
        else: session_data += 'no information' + '*'

        if irsdk['WeekendInfo']['TrackDisplayName']: session_data += (irsdk['WeekendInfo']['TrackDisplayName']) + '*'
        else: session_data += 'no informatione' + '*'
        
        if irsdk['WeekendInfo']['TrackConfigName']: session_data += (irsdk['WeekendInfo']['TrackConfigName']) + '*'
        else: session_data += 'no information' + '*'
        
        if irsdk['WeekendInfo']['TrackLength']: session_data += (irsdk['WeekendInfo']['TrackLength']) + '*'
        else: session_data += 'no information' + '*'
        
        if irsdk['WeekendInfo']['TrackCity']: session_data += (irsdk['WeekendInfo']['TrackCity']) + '*'
        else: session_data += 'no information' + '*'
        
        if irsdk['WeekendInfo']['TrackCountry']: session_data += (irsdk['WeekendInfo']['TrackCountry']) + '*'
        else: session_data += 'no information' + '*'
        
        if irsdk['WeekendInfo']['TrackAltitude']: session_data += (irsdk['WeekendInfo']['TrackAltitude']) + '*'
        else: session_data += 'no information' + '*'
        
        if irsdk['WeekendInfo']['TrackNumTurns']: session_data += (str(irsdk['WeekendInfo']['TrackNumTurns'])) + '*'
        else: session_data += 'no information' + '*'
        
        if irsdk['WeekendInfo']['TrackWeatherType']: session_data += (irsdk['WeekendInfo']['TrackWeatherType']) + '*'
        else: session_data += 'no information' + '*'
        
        if irsdk['WeekendInfo']['TrackSkies']: session_data += (irsdk['WeekendInfo']['TrackSkies']) + '*'
        else: session_data += 'no information' + '*'
        
        if irsdk['WeekendInfo']['TrackSurfaceTemp']: session_data += (irsdk['WeekendInfo']['TrackSurfaceTemp']) + '*'
        else: session_data += 'no information' + '*'
        
        if irsdk['WeekendInfo']['TrackAirTemp']: session_data += (irsdk['WeekendInfo']['TrackAirTemp']) + '*'
        else: session_data += 'no information' + '*'
        
        if irsdk['WeekendInfo']['TrackAirPressure']: session_data += (irsdk['WeekendInfo']['TrackAirPressure']) + '*'
        else: session_data += 'no information' + '*'
        
        if irsdk['WeekendInfo']['TrackWindVel']: session_data += (irsdk['WeekendInfo']['TrackWindVel']) + '*'
        else: session_data += 'no information' + '*'
        
        if irsdk['WeekendInfo']['TrackRelativeHumidity']: session_data += (irsdk['WeekendInfo']['TrackRelativeHumidity']) + '*'
        else: session_data += 'no information' + '*'
        
        if irsdk['WeekendInfo']['TrackFogLevel']: session_data += (irsdk['WeekendInfo']['TrackFogLevel']) + '*'
        else: session_data += 'no information' + '*'
        
        if irsdk['WeekendInfo']['TrackPrecipitation']: session_data += (irsdk['WeekendInfo']['TrackPrecipitation']) + '*'
        else: session_data += 'no information' + '*'
        
        if irsdk['WeekendInfo']['EventType']: session_data += (irsdk['WeekendInfo']['EventType']) + '*'
        else: session_data += 'no information' + '*'
        
        if irsdk['WeekendInfo']['WeekendOptions']['TimeOfDay']: session_data += (irsdk['WeekendInfo']['WeekendOptions']['TimeOfDay']) + '*'
        else: session_data += 'no information' + '*'
        
        if irsdk['WeekendInfo']['WeekendOptions']['Date']: session_data += (irsdk['WeekendInfo']['WeekendOptions']['Date']) + '*'
        else: session_data += 'no information' + '*'
        # endregion

        # region ----- DRIVER DATA -----
        driver_data = [driver for driver in irsdk['DriverInfo']['Drivers'] if driver['CarIdx'] == irsdk['DriverInfo']['DriverCarIdx']][0]
        
        if driver_data['UserName']: session_data += (driver_data['UserName']) + '*'
        else: session_data += 'no information' + '*'

        if driver_data['CarScreenName']: session_data += (driver_data['CarScreenName']) + '*'
        else: session_data += 'no information' + '*'

        if driver_data['CarScreenNameShort']: session_data += (driver_data['CarScreenNameShort']) + '*'
        else: session_data += 'no information' + '*'

        if driver_data['IRating']: session_data += (str(driver_data['IRating'])) + '*'
        else: session_data += 'no information' + '*'

        if driver_data['LicString']: session_data += (driver_data['LicString'])
        else: session_data += 'no information' + '*'
        
        # endregion

        # region ----- SECTOR DATA -----
        
        # number of the sectors as a string divided by a '*' (to create a list with the .split-command)
        # written to the DataFrame in the column "SessionData" row [2]
        sector_number = ''
        
        # lap percentage (0 to 1) for the sectors start point as a string divided by a '*' (to create a list with the .split-command)
        # written to the DataFrame in the column "SessionData" row [3]
        sector_pct = ''
        
        sector_data = irsdk['SplitTimeInfo']['Sectors']
        for dic in sector_data:
            sector_number += str(dic['SectorNum']) + '*'
            sector_pct += str(dic['SectorStartPct']) + '*'
        
        # delete the last '*'
        sector_number = sector_number[0:-1]
        # delete the last '*'
        sector_pct = sector_pct[0:-1]
        # endregion

        irsdk.shutdown()

        # put the session_data into the dataframe to the column 'SessionData' into the rows 0,1,2,3
        # fill the rest of the column with '-'
        df_len : int = len(df.Speed)
        df['SessionData'] = [session_keys] + [session_data] + [sector_number] + [sector_pct] + ['-'] * (df_len - 4)
# endregion

# region ----- WRITE THE DATAFRAME TO THE DISK -----

        # delete the extension of the filename
        file_name = file_name[:-4]

        # write one .csv-file
        if divide_stints == 'n':
            df.to_csv(file_name + ".csv")
            print("\nFinished converting\n'" + file_name + ".csv' written to your disk\n")


        # write several .csv-files 
        elif divide_stints == 'y':
            # list of lap numbers with pitroad "contact"
            laps_in_pit = list(df[df.OnPitRoad == True].Lap.unique())

            # no pit stop in the whole race
            if len(laps_in_pit) in [0, 1]:
                stint_data=[[df.Lap.min(), df.Lap.max()]]

            # pit stop during the race
            else:
                # list with the first and last laps of the stint: [[0,5], [6,12], [13,15]]
                stint_data = []

                for index in range(len(laps_in_pit)):
                    try:
                        # always start with the first lap
                        if index == 0:
                            stint = [0]
                        # correct drive-in and drive-out of the pitraod -> set the ending of a stint
                        elif laps_in_pit[index + 1] - laps_in_pit[index] == 1:
                            stint.append(laps_in_pit[index])
                            if len(stint) == 2:
                                stint_data.append(stint)
                                stint = [laps_in_pit[index + 1]]
                    # end of list reached 
                    except IndexError:
                        if laps_in_pit[-1] - laps_in_pit[-2] == 1:
                            break
                        else:
                            stint.append(laps_in_pit[index])
                            stint_data.append(stint)
                            break
            
            # write a separate csv-file for each stint to the sidk
            for index in range(len(stint_data)):
                df[(df.Lap >= stint_data[index][0]) & (df.Lap <= stint_data[index][1])].to_csv(file_name + '_stint' + str(index + 1) + '.csv')

            print("\nFinished converting\nStints of '" + file_name + ".csv' written to your disk\n")
# endregion
        
# region ----- EXCEPTION HANDLING -----
        
    # wrong filename or path    
    except FileNotFoundError:
        print("Something went wrong. Please check the filename '" + file_name + ".ibt' and if the file is at the correct path!")

    # key not available in the ibt-File 
    except KeyError:
        print("Some data isn't available in the ibt-file. Please contact the developer to clarify this issue!")
# endregion
        
    convert_again = ''

    while convert_again not in ['y', 'n']:
        convert_again = input("Do you want to convert another file (y/n) -> ")
        if convert_again not in ['y', 'n']:
            print("Please press 'y' or 'n'")





