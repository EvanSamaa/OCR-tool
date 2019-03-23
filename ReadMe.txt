
WHAT THE PROGRAM DOES
--------------------------------------------------------



SETUP ()
--------------------------------------------------------
If you don't have python3, install it here

https://www.python.org/downloads/windows/ 
download the Windows x86-64 executable installer

open the installer and make sure you tick the box: add python 3.X to path, then click install now

After installing python, open command prompt (if you have win10, open start menu, type in "cmd" then press enter)

in command prompt, type in the following commands to install all necessary packages (note you should press enter after typing in each one to actually make it go)

pip install tesseract 
pip install pyocr
pip install opencv-python
pip install prettytable
pip install pillow
pip install pandas
pip install numpy

now you want to add tesseract.exe to your path, best way to do so is to ask Muhammad. Alternatively, in start menu, search for "tesseract.exe", right click it and choose "open file location". Then you want to copy it's location, which should look something like 

"C:\Users\Evan\AppData\Local\Tesseract-OCR"

Now you've got the location, you want to add it to your path. Again, go to start menu and type in "edit the system environment variables" and choose the first/and only result that matches it. 

There, there should be a button that reads "Environment Variables...". Click that and a new window will pop out. In that window, there are two sections. One is "User variables for XXXX", the other being "System variables". In "User variables for XXXX", single click "path" and cick the button that reads "Edit...". This should open another window. From there just click New and paste the path to Tesseract that you've found before. Now click "OK" or "Save" or buttons along that line to save all your changes. And you should be all set adding tesseract to path!

Lastly, this is optional. If you are comfortable enough with the idea of coding. I would recommand downloading an editor like sublimetext. 

--------------------------------------------------------

USING PROGRAM

you first want to get all your pdfs and pick one, name it "sample". This will be the on the code with get position and calibration data from. Now go to the learn() function in the code and add the information you wish to extract from the series of pdfs. Run the code once. It should create two folders in the directory its in. Place Sample into TempStorage and place the rest of the pdfs + sample into "putPDFsHere" Now run the code again and you will find your excel sheet in TempsStorage/Correct

