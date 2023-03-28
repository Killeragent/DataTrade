import pandas as pd 
import numpy as np
import os

#######################################################
# Code to delete all unnecessary data for next day
#######################################################
# What to delete data or logs











def remove_data_files():
	print("From Data files removal...")
	dirs='../Data/Intraday/'
	folders=os.listdir(dirs)
	print(folders)
	for folder in folders:
		try:
			new_path=dirs+folder+"/"
			all_files=os.listdir(new_path)

			for file in all_files:
				if 'csv' in file:
					filepath=new_path+file
					os.remove(filepath)
					print("{} deleted".format(filepath))


		except Exception as e:
			print(e)

def remove_log_files():
	dirs='../Log/'
	all_files=os.listdir(dirs)

	try:
		for file in all_files:
			filepath=dirs+file
			os.remove(filepath)
			print("{} Deleted...".format(filepath))
	except Exception as e:
		print(e)







def cleanup():
	'''
	Main function: Cleans up the residual file from the servers
	'''
	content=input("Type DATA for deleting data files and LOG for deleting log files :  ")

	if content=='DATA':
		remove_data_files()
	if content=='LOG':
		remove_log_files()
	print(" Files deleted...")

cleanup()


