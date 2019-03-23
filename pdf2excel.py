#for OCR
from PIL import Image 
import pyocr.builders
import pyocr
import cv2
#just for improve testing
import pickle
#utility
import os
import io
#output/table related libraries
from prettytable import PrettyTable
from pandas import DataFrame
from pandas import ExcelWriter
import pandas
#miscellaneous
import shutil
import sys
import numpy as np


class tempStorage():
	def __init__(self, dataTocollect):
		# self.toAccum = toAccum #this is an index for the thing to accum on, can be -1 if it's not useful
		# self.accumTo = accumTo # this will be a list of what is accumed
		dataTocollect = dataTocollect + ["Flag"]
		self.columns = dataTocollect # [docName, type, amount, unitCost,............, flagged or nah] the data you wish to collect
		self.store = [] 
		self.FlagStore = []
		for i in dataTocollect:
			self.store = self.store + [[]] # docName, type, amount, unitCost, flagged or nah
			self.FlagStore = self.FlagStore + [[]] 
	def add(self, info):
		if info[len(self.columns) - 1] == "FLAGGED":
			self.FlagAdd(info)
			return 0
		size = len(self.store[0])
		# exists = False
		# for i in range (0, size):
		# 	if (info[self.toAccum] == self.store[self.toAccum][i]) and (self.toAccum > 0):
		# 		for index in self.accumTo:
		# 			try:
		# 				self.store[index][i] = float(self.store[index][i]) + float(info[i])
		# 			except:
		# 				exopists = False
		# 		exists = True
		# 		break
		# if exists == False:
		for i in range(0, len(self.store)):
			self.store[i] = self.store[i] + [info[i]]
		return 0;
	def FlagAdd(self, info):
		for i in range(0, len(self.store)):
				self.FlagStore[i] = self.FlagStore[i] + [info[i]]
		return 0
	def disp (self):
		temp = np.array(self.store).T.tolist()#clear up for dataframe
		df = DataFrame(temp, columns = self.columns)#input into dataframe
		# df.sort_values(self.columns[self.toAccum])#

		temp2 = np.array(self.FlagStore).T.tolist()#clear up for dataframe
		df2 = DataFrame(temp2, columns = self.columns)#input into dataframe
		# df2.sort_values(self.columns[self.toAccum])		

		#export to excel
		writer = ExcelWriter('./TempStorage/Correct/dataSheet.xlsx', engine = 'xlsxwriter')
		df.to_excel(writer,'Sheet1')
		df2.to_excel(writer,'Sheet2')
		writer.save()
		#console output
		self.display()
		self.FlagDisplay()
		#for further processing
		return [df, df2]
	def FlagDisp (self):
		temp = np.array(self.FlagStore).T.tolist()#clear up for dataframe
		df = DataFrame(temp, columns = self.columns)#input into dataframe
		# df.sort_values(self.columns[self.toAccum])#
		#export to excel
		writer = ExcelWriter('./TempStorage/Correct/dataSheet.xlsx', engine = 'xlsxwriter')
		df.to_excel(writer,'Sheet2')
		writer.save()
		#console output
		self.FlagDisplay()
		#for further processing
		return df
	def merge (self, other):
		temp = np.array(other.store).T.tolist()
		for k in temp:
				self.add(k)
		temp2 = np.array(other.FlagStore).T.tolist()
		for l in temp2:
			self.FlagAdd(l)
		return 0
	def display (self):
		t = PrettyTable(self.columns)
		for i in range (0, len(self.store[0])):
			row = []
			for k in range (0, len(self.store)):
				row = row + [self.store[k][i]]	
			t.add_row(row)
		print (t) 
	def FlagDisplay (self):
		t = PrettyTable(self.columns)
		for i in range (0, len(self.FlagStore[0])):
			row = []
			for k in range (0, len(self.store)):
				row = row + [self.FlagStore[k][i]]	
			t.add_row(row)
		print (t) 
	def Deflag(self):
		temp_FlagStore = np.array(self.FlagStore).T.tolist()
		for entry in temp_FlagStore:
			NEWentry = [entry]
			t = PrettyTable(self.columns)
			t.add_row(entry)
			print(t)
			print("Because of my inferior AI algorithm, I can't identify the info from this invoice, Please help me hooman")
			NEWentry[1] = input("Please enter the type of concrete I missed\n")
			NEWentry[2] = float(input("Please enter the quantity\n"))
			NEWentry[3] = float(input ("Please enter the Unit Price\n"))
			print (NEWentry)
		return 0
	def store2FlagStore(self):
		i = 0;
		while (True):
			try:
				if (float(self.store[3][i]) > 200) or (float(self.store[3][i]) < 80):
					self.FlagAdd([self.store[0][i], self.store[1][i], self.store[2][i], self.store[3][i], "FLAGGED"])
					for j in range (0, 5):
						self.store[j].pop(i)
				i = i + 1
			except:
				i = i + 1
			if (i >= len(self.store[0])):
				break
		return 
#save listt into a pickle file! It will always save it at the 'location', as "Save.pkl" 
def toPKL(location ,listt):
	with open(location + 'Save.pkl', 'wb') as output:
		pickle.dump(listt, output, pickle.HIGHEST_PROTOCOL)
#load the saved save.pkl        
def fromPKL(location):
	with open(location + 'Save.pkl', 'rb') as input:
		retn = pickle.load(input)
	return retn;

def GetNumberOutOfString(StringOfTextt):
	start = 0
	end = 0
	FOUND = False
	for i in range (0, len(StringOfTextt)):
		try:
			num = float(StringOfTextt[i])
			start = i
			break
		except:
			k = ("ok")
	for i in range (start + 1, len(StringOfTextt)):
		try:
			num = float(StringOfTextt[start:i])
			end = i
			FOUND = True
		except:
			break
	if end != 0:
		return StringOfTextt[start:end]
	else:
		return -1 
#initilize setup the folder paths so that the save files and the temporarily stored images will have a place
def readFloatProperly(number):
	number = str(number) #making sure it is in the form of a string
	newNum = number.replace(",", "")
	return newNum
def initilize():
	Initialized = False
	for items in os.listdir("./"):
		if "TempStorage" in items:
			Initialized = True
			break
	if Initialized == False:
		os.system("mkdir TempStorage")
		os.system("mkdir Correct")
		os.system("move Correct TempStorage")
		os.system("mkdir putPDFsHere")
	return 0
#convertOnePDFToItsJPEGs takes in a name of a pdf file without the suffix, and change it into a series of jpeg files. 
#the names of the jpeg files are returned as a list. the format of the names are in "{pdf file name}_{page number}.pdf"
def convertOnePDFToItsJPEGs(name, directory):
	names = [] # store the names of the jpegs the pdf is converted to
	PDFname = directory + name + ".pdf" # the name of the pdf
	# print(PDFname)
	Jpegname = directory + name + ".jpeg" # a section of the name of the jpeg
	os.system('convert -density 300 -background White -layers flatten ' + '"'+ PDFname + '"' + ' ' + '"'+Jpegname+'"') # using this to convert to jpeg, instead of imageMagik
	DirList = os.listdir(directory) # get the names of all the files in the target directory of all the jpegs
	for i in range (0, 2): # cycle through those to find the jpeg the current pdf is converted to
		if (".pdf" not in DirList[i]) and (name in DirList[i]): # condition to determine which jpegs are related to the current pdf
			names = names + [DirList[i]]
	return names # return the jpeg names
def convertOnePDFToItsJPEGsPrime(name, directory, directoryTo):
	names = [] # store the names of the jpegs the pdf is converted to
	PDFname = directory + name + ".pdf" # the name of the pdf
	Jpegname = directory + name + ".jpeg" # a section of the name of the jpeg
	os.system('convert -density 300 -background White -layers flatten ' + '"'+ PDFname + '"' + ' ' + '"'+ Jpegname+'"') # using this to convert to jpeg, instead of imageMagik
	DirList = os.listdir(directory) # get the names of all the files in the target directory of all the jpegs
	for i in range (0, len(DirList)): # cycle through those to find the jpeg the current pdf is converted to
		if (".pdf" not in DirList[i]) and (name in DirList[i]): # condition to determine which jpegs are related to the current pdf
			names = names + [DirList[i]]
	for name in names:
		img = cv2.imread(directory + name)
		ret,thresh = cv2.threshold(img,127,255,cv2.THRESH_BINARY)
		cv2.imwrite(directory + name,thresh)

	return names # return the jpeg names
#get_jpeg_Names will get the names of all the jpeg in a directory and return them
def get_jpeg_Names(directory):
	info2 = os.listdir(directory)
	PDFs = []
	for i in info2:
		ending = i[len(i) - 5:len(i)]
		if ".jpeg" == ending:
			temp1 = list(i)
			temp2 = ""
			for i in range(0, len(temp1)):
				if temp1[i] == "." and temp1[i+1] == 'j':
					break
				temp2 = temp2 + temp1[i]
			PDFs = PDFs + [directory + temp2 + ".jpeg"]
	return PDFs
#get_PDF_Names will get the names of all the pdfs in a directory and return them
def get_PDF_Names(directory):
	info2 = os.listdir(directory)
	PDFs = []
	for i in info2:
		ending = i[len(i) - 4:len(i)]
		if ".pdf" == ending:
			temp1 = list(i)
			temp2 = ""
			for i in range(0, len(temp1)):
				if temp1[i] == "." and temp1[i+1] == 'p':
					break
				temp2 = temp2 + temp1[i]
			PDFs = PDFs + [temp2]
	return PDFs
#lineRemoval function removes horizontal lines in a table, which interferes with reading data
def lineRemoval(imageName, directory, length):
	img = cv2.imread(directory + imageName)
	img_gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	img_binary = cv2.threshold(img_gray,125,255,cv2.THRESH_BINARY)

	row,col,aosdjfaiosr = img.shape #get size of the image in terms of pixels
	if length < 0:
		length = 1000
	acum = 0
	acumStart = 0
	acumEnd = 0
	for i in range (0, row):
		acum = 0
		for j in range (0, col):
			# print(img_binary[0][i, j])
			if (img_binary[1][i, j] == 0) and (acum == 0):
				acumStart = j
				acum = acum + 1
			elif img_binary[1][i, j] == 0 and acum > 0:
				acum = acum + 1
			elif img_binary[1][i, j] != 0:
				acumEnd = j
				if acum > length:
					cv2.line(img_binary[1],(acumStart,i),(acumEnd,i),(255,255,255),1)
	cv2.imwrite(directory + imageName,img_binary[1])
	return 0
# this function crops pictures. The first parameter is the name of the jpeg, which includes the location as well, the second parameter is a list of potential locations of which a certain item is at. 
def cropForThings(jpegName, locationsOfData, dirFrom, dirTo):
	listOfCroppedImages = []
	img = Image.open(dirFrom+jpegName)	
	for i in range (0, len(locationsOfData)):# will iterate through potential locations
		tempName = jpegName[:-5] + "_"+ str(i) + ".jpeg"
		area = locationsOfData[i]
		cropped_img = img.crop(area)
		cropped_img.save(dirTo + tempName, "JPEG")
		listOfCroppedImages = listOfCroppedImages + [tempName]
	return listOfCroppedImages
#Get the namees of the company, utilizes cropping
def get_info_as_snips(INDEXSET1_location, INDEXSET2_jpegNameList, IndexSet2_calibration_translation, IndexSet2_calibration_sizing, dirFrom, dirTo, IndexSet2_Flags, Calibration_dataSet, IndexSet2_calibration_NewLocation):
	# print(IndexSet2_calibration_sizing)
	# INDEXSET2_jpegNameList = get_jpeg_Names(directory)# this program requires the pdfs to be converted into jpegs first.
	INDEXSET2_Cropped_Section_list = []
	# print(INDEXSET2_jpegNameList)
	# print(IndexSet2_calibration_translation)
	# print(INDEXSET1_location)
	for i in range (0, len(INDEXSET2_jpegNameList)): # iterate with each file
		try:
			calibrated_location = INDEXSET1_location.copy() 
			Coordinated_location = INDEXSET1_location.copy()
			for j in range (0, len(INDEXSET1_location)): # for each location/piece of data
				Hor_BLURR = 10
				Ver_BLURR = 10
				Extension_BLURR = 30
				calibrated_location[j] = [INDEXSET1_location[j][0] + IndexSet2_calibration_translation[i][0] - Hor_BLURR, INDEXSET1_location[j][1] + IndexSet2_calibration_translation[i][1] - Ver_BLURR, INDEXSET1_location[j][2] + IndexSet2_calibration_translation[i][0] + Extension_BLURR, INDEXSET1_location[j][3] + IndexSet2_calibration_translation[i][1] + Ver_BLURR]
			# CALIBRATION FOR SIZE ========================================================================================================================================================================================================================
				# if j == 0:
				Coordinated_location[j] = calibrated_location[j].copy()
				# else:
					# print(Coordinated_location[j])
				# print(IndexSet2_calibration_NewLocation)
				Coordinated_location[j] = [calibrated_location[j][0] - IndexSet2_calibration_NewLocation[i][0], calibrated_location[j][1] - IndexSet2_calibration_NewLocation[i][1], calibrated_location[j][2] - IndexSet2_calibration_NewLocation[i][2], calibrated_location[j][3] - IndexSet2_calibration_NewLocation[i][3]] 
				# print(Coordinated_location[j])
				# Coordinated_location[j] = [int(element*IndexSet2_calibration_sizing[i][1] + thing) for element, thing in zip(Coordinated_location[j], IndexSet2_calibration_NewLocation[i])]
				Coordinated_location[j] = [int(Coordinated_location[j][0]*IndexSet2_calibration_sizing[i][0] + IndexSet2_calibration_NewLocation[i][0]), int(Coordinated_location[j][1]*IndexSet2_calibration_sizing[i][1] + IndexSet2_calibration_NewLocation[i][1]), int(Coordinated_location[j][2]*IndexSet2_calibration_sizing[i][0] + IndexSet2_calibration_NewLocation[i][2]), int(Coordinated_location[j][3]*IndexSet2_calibration_sizing[i][1] + IndexSet2_calibration_NewLocation[i][3])]
				# print(Coordinated_location[j])
				# print(Coordinated_location[j])
			# print(Coordinated_location)
			for k in range (1, len(calibrated_location)):
				calibrated_location[k] = [Coordinated_location[k][0] + Calibration_dataSet[0][0][0], Coordinated_location[k][1] + Calibration_dataSet[0][0][1], Coordinated_location[k][2] + Calibration_dataSet[0][0][2], Coordinated_location[k][3] + Calibration_dataSet[0][0][3]]
			# print(calibrated_location)
			# CALIBRATION FOR SIZE ========================================================================================================================================================================================================================
			# for m in range (1, len(INDEXSET1_location)):
			# 	for k in range (0, 4):
			# 		Coordinated_location[m][k] = [calibrated_location[m][0] - calibrated_location[0][0], calibrated_location[m][1] - calibrated_location[0][1], calibrated_location[m][2] - calibrated_location[0][2], calibrated_location[m][3] - calibrated_location[0][3]]
			
			listOfCroppedImages = cropForThings(INDEXSET2_jpegNameList[i], Coordinated_location, dirFrom, dirTo) # crop first
			INDEXSET2_Cropped_Section_list = INDEXSET2_Cropped_Section_list + [listOfCroppedImages]
			# added = False
			# for comp in INDEXSET1_companyNames: # check validity and then add if valid
			# 	if (checkValidityOfCrop(listOfCroppedImages, comp)):
			# 		INDEXSET2_nameList = INDEXSET2_nameList + [comp]
			# 		added = True
			# 		break
			# if added == False: # if not valid, in its index it will have unknown instead of the company name. It
			# 	INDEXSET2_nameList = INDEXSET2_nameList + ["unknown"]
			# CleanUp(listOfCroppedImages)
		except:
			IndexSet2_Flags[i] = "FLAGGED"
	# print(INDEXSET2_Cropped_Section_list)
	return INDEXSET2_Cropped_Section_list
def extractionFromSnips(INDEXSET2_All, dirFrom, storage, IndexSet1_dataType):

	IndexSet2_fileNames, IndexSet2_calibration_translation, IndexSet2_calibration_sizing, INDEXSET2_Cropped_Section_list, IndexSet2_Flags = INDEXSET2_All
	# print(INDEXSET2_Cropped_Section_list)
	tools = pyocr.get_available_tools()#initialized OCR
	tool = tools[0]#initialized OCR
	for i in range (0, len(INDEXSET2_Cropped_Section_list)): #for each doc
		if IndexSet2_Flags[i] == "OK":
			Input = []
			for k in range (0, len(INDEXSET2_Cropped_Section_list[i])): # for each snip
				info = tool.image_to_string( # extract all lines in each page
					Image.open(dirFrom  + INDEXSET2_Cropped_Section_list[i][k]), 
					lang = "eng",
					builder = pyocr.builders.LineBoxBuilder()
				)
				# print(info)
				data = ""
				for thing in info:
					data = data + thing.content
				# print(data)
				if IndexSet1_dataType[k] == "float":
					newData = readFloatProperly(data)
					newData = GetNumberOutOfString(newData)
					if newData == -1:
						data = "0"
					else:
						data = newData

				Input = Input + [data] 
				# print(input)
				# print(len(Input), k)
				# print(IndexSet1_dataType[k])
				# if len(Input) <= k and IndexSet1_dataType[k] == "float":
				# 	Input = Input + ["0.00"]
				if len(Input) <= k and IndexSet1_dataType[k] == "non_float":
					Input = Input + ["unknown"]
			Input = [IndexSet2_fileNames[i]] + Input + [IndexSet2_Flags[i]]
			# if len(Input) < (len(IndexSet1_dataType) + 1) and IndexSet2_Flags[i] == "FLAGGED":
			# 	Input = []
			# 	for num in range(0, len(IndexSet1_dataType)):
			# 		Input = Input + [0]
			# 	Input = Input + "FLAGGED"
			
		else:
			Input = []
			for k in range (0, len(IndexSet1_dataType)):
				Input = Input + ["unknown"]
			Input = [IndexSet2_fileNames[i]] + Input + ["FLAGGED"]
		storage.add(Input)
	storage.disp()

	return 0
# this cleans up everything
def CleanUp(filenames): 
	for i in range (0, len(filenames)):
		os.remove(filenames[i])
	return 0;


def learn():
	IndexSet1_dataTocollect = ["RMXS25N511X", "James Dick Concrete"]
	IndexSet1_nameOfData = ["concrete mix", "supplier"]
	IndexSet1_dataIncoordinate = [[566, 1225, 2327, 1276]]
	IndexSet1_dataIncoordinateName = ["location"]

	Calibration_data = ["RESULTS", "COMPRESSIVE"]
	IndexSet1_dataType = []
	for num in IndexSet1_dataTocollect:
		try:
			num = readFloatProperly(num)
			float(num)
			IndexSet1_dataType = IndexSet1_dataType + ["float"]
		except:
			IndexSet1_dataType = IndexSet1_dataType + ["non_float"]
	samples = convertOnePDFToItsJPEGs("sample", "./TempStorage/")
	tools = pyocr.get_available_tools()#initialized OCR
	tool = tools[0]#initialized OCR
	# samples = ["houghlines3.jpeg"]
	for img in samples:
		lineRemoval(img, "./TempStorage/", -1)
		temp = Image.open("./TempStorage/" + img)
		temp = temp.convert('L')
		temp.save("./TempStorage/" + img)
		page = tool.image_to_string( # extract all lines in each page
			Image.open("./TempStorage/" + img), 
			lang = "eng",
			builder = pyocr.builders.LineBoxBuilder()
		)
		IndexSet1_rtv = []
		for item in IndexSet1_dataTocollect: # try to find one item
			for line in page: # locate the line of the item
				if (item in line.content): # if located
					locations = []
					adding = False
					for wordbox in line.word_boxes:
						if ((str(wordbox.content) in item) and (not(wordbox.content.isspace())) and (wordbox.content != "")):
							adding = True
						if ((str(wordbox.content) not in item) and (not(wordbox.content.isspace())) and (wordbox.content != "")):
							adding = False
						if adding == True:
							locations = locations + [wordbox.position]
					IndexSet1_rtv = IndexSet1_rtv + [locations]
					break
		cloneOfRtv = IndexSet1_rtv.copy()
		IndexSet1_rtv = []
		for thing in cloneOfRtv: #get the FULL coordinate of the piece of data, done by adding pieces together.
			if len(thing) == 1:
				# print(thing)
				newThing = [thing[0][0][0], thing[0][0][1], thing[0][1][0], thing[0][1][1]]
				IndexSet1_rtv = IndexSet1_rtv + [newThing]
			else:
				newThing = [thing[0][0][0],thing[0][0][1],thing[len(thing)-1][1][0], thing[len(thing)-1][1][1]]
				# print(newThing)
				IndexSet1_rtv = IndexSet1_rtv + [newThing]
		Calibration_data_location = []
		for item in Calibration_data: # try to find calibration data
			for line in page: # locate the line of the item
				if (item in line.content): # if located
					locations = []
					adding = False
					for wordbox in line.word_boxes:
						if ((str(wordbox.content) in item) and (not(wordbox.content.isspace())) and (wordbox.content != "")):
							adding = True
						if ((str(wordbox.content) not in item) and (not(wordbox.content.isspace())) and (wordbox.content != "")):
							adding = False
						if adding == True:
							locations = locations + [wordbox.position]
					Calibration_data_location = Calibration_data_location + [locations]
					break

		cloneOf_Calibration_data_location = Calibration_data_location.copy()
		Calibration_data_location = []
		print(len(cloneOf_Calibration_data_location))
		for thing in cloneOf_Calibration_data_location: #get the FULL coordinate of the piece of data, done by adding pieces together.
			if len(thing) == 1:
				newThing = [thing[0][0][0], thing[0][0][1], thing[0][1][0], thing[0][1][1]]
				Calibration_data_location = Calibration_data_location + [newThing]
			else:
				newThing = [thing[0][0][0], thing[0][0][1], thing[len(thing)-1][1][0], thing[len(thing)-1][1][1]]
				# print(newThing)
				Calibration_data_location = Calibration_data_location + [newThing]
		print(Calibration_data_location)
		IndexSet1_nameOfData = IndexSet1_nameOfData + IndexSet1_dataIncoordinateName
		IndexSet1_rtv = IndexSet1_rtv + IndexSet1_dataIncoordinate
		return [IndexSet1_rtv, IndexSet1_dataTocollect, IndexSet1_nameOfData, IndexSet1_dataType], [Calibration_data_location, Calibration_data]
def Scan(IndexSet1_All, validations, Calibration_dataSet):	
	IndexSet1_location, IndexSet1_dataTocollect, IndexSet1_nameOfData, IndexSet1_dataType = IndexSet1_All[0], IndexSet1_All[1], IndexSet1_All[2], IndexSet1_All[3] #set up varaibles
	Calibration_data, Calibration_data_location = Calibration_dataSet
	storage = tempStorage(["file_Name"] + IndexSet1_nameOfData)
	IndexSet2_fileNames = get_PDF_Names('./putPDFsHere/') 	# get file Names
	# print(IndexSet2_fileNames)
	for pdf in range(0, len(IndexSet2_fileNames)):
		# print(IndexSet2_fileNames[pdf])
		temp = convertOnePDFToItsJPEGsPrime(IndexSet2_fileNames[pdf], './putPDFsHere/', "./TempStorage/")
		IndexSet2_fileNames[pdf] = temp[0] #only taking the first paging, assuming we only need one page of info
		# command = "move " + './putPDFsHere/' + '"'+temp[0]+'"' +" ./TempStorage"
		# os.rename('./putPDFsHere/' + '"'+temp[0]+'"', "./TempStorage/"+ '"'+temp[0]+'"')
		# print(command)
	IndexSet2_calibration_translation = []
	IndexSet2_calibration_sizing = []
	IndexSet2_calibration_NewLocation = []
	IndexSet2_Flags = []
	for i in IndexSet2_fileNames:
		try: # mostly for docs that became destroyed after changed into complete darkness after changed
			temp = calibration(Calibration_dataSet, i) # return the shift of the current image and the sizing
			IndexSet2_calibration_translation = IndexSet2_calibration_translation + [temp[0]]
			IndexSet2_calibration_sizing = IndexSet2_calibration_sizing + [temp[1]]
			IndexSet2_calibration_NewLocation = IndexSet2_calibration_NewLocation + [temp[2]]
			IndexSet2_Flags = IndexSet2_Flags + ["OK"]
		except:# first round of flagging
			IndexSet2_Flags = IndexSet2_Flags + ["FLAGGED"]
	INDEXSET2_Cropped_Section_list = get_info_as_snips(IndexSet1_location, IndexSet2_fileNames, IndexSet2_calibration_translation, IndexSet2_calibration_sizing, "./putPDFsHere/", "./TempStorage/", IndexSet2_Flags, Calibration_dataSet, IndexSet2_calibration_NewLocation)
	INDEXSET2_All = [IndexSet2_fileNames, IndexSet2_calibration_translation, IndexSet2_calibration_sizing, INDEXSET2_Cropped_Section_list, IndexSet2_Flags]
	extractionFromSnips(INDEXSET2_All, "./TempStorage/", storage, IndexSet1_dataType)
	return IndexSet2_fileNames
def calibration(Calibration_dataSet, jpeg):
		RealCoordinate = Calibration_dataSet[0][0].copy() #coordinate of the calibrationValue
		calibrationValue =  Calibration_dataSet[1][0] # the value inside that coordinate
		calibrationValue2 = Calibration_dataSet[1][1]
		Blurr = 100
		RealCoordinate = [Calibration_dataSet[0][0][0] - Blurr, Calibration_dataSet[0][0][1] - Blurr, Calibration_dataSet[0][0][2] + Blurr, Calibration_dataSet[0][0][3] + Blurr] # make the area broader
		RealCoordinate2 = [Calibration_dataSet[0][1][0] - Blurr, Calibration_dataSet[0][1][1] - Blurr, Calibration_dataSet[0][1][2] + Blurr, Calibration_dataSet[0][1][3] + Blurr]
		Portion = cropForThings(jpeg, [RealCoordinate], "./putPDFsHere/", "./TempStorage/")[0] #testing with the first image
		print(Portion)

		tools = pyocr.get_available_tools()#initialized OCR
		tool = tools[0]#initialized OCR
		
		page = tool.image_to_string( # extract all lines in each page
			Image.open("./TempStorage/" + Portion), 
			lang = "eng",
			builder = pyocr.builders.LineBoxBuilder()
		)
		temporaryCoord = []
		for line in page: # locate the line of the item
			if (calibrationValue in line.content): # if located
				locations = []
				adding = False
				for wordbox in line.word_boxes:
					if ((str(wordbox.content) in calibrationValue) and (not(wordbox.content.isspace())) and (wordbox.content != "")):
						adding = True
					if ((str(wordbox.content) not in calibrationValue) and (not(wordbox.content.isspace())) and (wordbox.content != "")):
						adding = False
					if adding == True:
						locations = locations + [wordbox.position]
				temporaryCoord = temporaryCoord + [locations]
		NEWCoordinate = [temporaryCoord[0][0][0][0],temporaryCoord[0][0][0][1],temporaryCoord[0][len(temporaryCoord)-1][1][0], temporaryCoord[0][len(temporaryCoord)-1][1][1]]
		Portion2 = cropForThings(jpeg, [RealCoordinate2], "./putPDFsHere/", "./TempStorage/")[0]
		page2 = tool.image_to_string( # extract all lines in each page
			Image.open("./TempStorage/" + Portion2), 
			lang = "eng",
			builder = pyocr.builders.LineBoxBuilder()
		)

		temporaryCoord2 = []
		for line in page2: # locate the line of the item
			if (calibrationValue2 in line.content): # if located
				locations = []
				adding = False
				for wordbox in line.word_boxes:
					if ((str(wordbox.content) in calibrationValue2) and (not(wordbox.content.isspace())) and (wordbox.content != "")):
						adding = True
					if ((str(wordbox.content) not in calibrationValue2) and (not(wordbox.content.isspace())) and (wordbox.content != "")):
						adding = False
					if adding == True:
						locations = locations + [wordbox.position]
				temporaryCoord2 = temporaryCoord2 + [locations]

		NEWCoordinate2 = [temporaryCoord2[0][0][0][0],temporaryCoord2[0][0][0][1],temporaryCoord2[0][len(temporaryCoord2)-1][1][0], temporaryCoord2[0][len(temporaryCoord2)-1][1][1]]
		shift = [NEWCoordinate[0] + RealCoordinate[0] - Calibration_dataSet[0][0][0], NEWCoordinate[1] + RealCoordinate[1] - Calibration_dataSet[0][0][1]] 
		sizeA = [NEWCoordinate[0] + RealCoordinate[0] - NEWCoordinate2[0] - RealCoordinate2[0],  NEWCoordinate[1] + RealCoordinate[1] - NEWCoordinate2[1] - RealCoordinate2[1]]
		# print (shift)
		originalSize = [Calibration_dataSet[0][0][0] - Calibration_dataSet[0][1][0], Calibration_dataSet[0][0][1] - Calibration_dataSet[0][1][1]]
		
		sizing = [abs(float(sizeA[0])/originalSize[0]), abs(float(sizeA[1])/originalSize[1])] # one is vertical stretch one is horizontal
		# print(Indexset[0][0])
		# print(NEWCoordinate)
		# print (originalSize)
		# print (shift)
		return [shift,sizing, NEWCoordinate2]
		# calibrated_coordinate = [Indexset[0][0][0] + shift[0], Indexset[0][0][1] + shift[1], Indexset[0][0][2] + shift[0], Indexset[0][0][3] + shift[1]]
		# cropForThings(jpegs[1], [calibrated_coordinate], "./putPDFsHere/", "./TempStorage/")

		# break

initilize()
# learn()
Indexset, calibrationDataSet = learn()
toPKL("./TempStorage/Correct/" ,[Indexset, calibrationDataSet])
Indexset, calibrationDataSet = fromPKL("./TempStorage/Correct/")
print(Indexset, calibrationDataSet)

# input()
jpegs = Scan(Indexset, 0, calibrationDataSet) #get the list of images

toDelete = get_jpeg_Names("./TempStorage/")
toDelete = toDelete + get_jpeg_Names("./putPDFsHere/")
CleanUp(toDelete)

input()

