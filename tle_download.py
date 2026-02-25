# -*- coding: utf-8 -*-
"""
Created on Wed Feb 25 13:58:39 2026

@author: markus.allgaier
"""
def getTle(norad_id):
   from datetime import datetime, date
   from pathlib import Path
   from satellite_tle import fetch_tle_from_celestrak
   
   # Test satellite stuff:
   # Norad ID:
   #norad_id = 43613
   f_name = ''.join([str(norad_id),".txt"])
   
   # Get today's date:
   thetime = datetime.now()
   thedate = date.today()
   
   # When used properly, we want to
   #(1) Check if we already have a TLE on file (if not, download it and save it on file)
   #(2) If we have a TLE on file, check how old it is
   #(3) if it's from today, load and use it, and get a new one if it's olde
   
   # First, check if the file exists already:
   f_path = Path(f_name)
   if f_path.is_file():
      # We have a TLE on file. Load it and check the age
      #open and read the file after the overwriting:
      with open(f_name) as f:
         f_content = f.read()
         f_lines = f_content.split('\n')
         f_date = f_lines[0]
         # Specify date format:
         format_string = '%Y-%m-%d'
         f_date = datetime.strptime(f_date,format_string)
         f_delta = f_date - thetime
         days_old = -1*(f_delta.days+1)
         if days_old<2:
            print("Current TLE on file for NORAD ID",str(norad_id),"object",f_lines[1],"...")
            # Get TLE in the right format, strip leading spaces:
            for i in range(len(f_lines)):
               f_lines[i]=f_lines[i].strip()
            tle_str = '\n'.join(f_lines[1:4])
         else:
            print("TLE on file for NORAD ID",str(norad_id),"object",f_lines[1],"is outdated.")
            # Test TLE (replace with download code later):
            #tle_str = """ICESat-2
            #1 27453U 02032A   26056.53868269  .00000199  00000-0  10195-3 0  9992
            #2 27453  98.8518  21.0417 0010965 320.0273  40.0098 14.26180902231072"""
            # Get new TLE from Celestrak:
            fetched_tle = fetch_tle_from_celestrak(norad_id)
            # Get it formatted:
            tle_str = '\n'.join(fetched_tle)
   
            # Write it to a file in current folder:
            with open(f_name, "w") as f:
               f.write(str(thedate))
               f.write('\n')
               f.write(tle_str)
   
   else:
      # We don't have a tle on file. Get a new one and save it
      print("No TLE on file. Fetching a new one for",str(norad_id),"and creating file ...")
      # Test TLE (replace with download code later):
      #tle_str = """ICESat-2
      #1 27453U 02032A   26056.53868269  .00000199  00000-0  10195-3 0  9992
      #2 27453  98.8518  21.0417 0010965 320.0273  40.0098 14.26180902231072"""
      # Get a TLE from Celestrak:
      fetched_tle = fetch_tle_from_celestrak(norad_id)
      # Get it formatted:
      tle_str = '\n'.join(fetched_tle)
   
      
      # Write it to a file in current folder:
      with open(f_name, "w") as f:
            f.write(str(thedate))
            f.write('\n')
            f.write(tle_str)
   
   print(tle_str)
   return(tle_str)
         
         
         
         
         
         
         
         