#Sean Fritz - s1346012
#Get an academic audit from webadvisor using webdrivers from selenium
#webadv_audit.py
#Due 4/2/24

#To run:
# python c:/Users/Sean/Desktop/PythonGroupProject/webadv_audit.py [--help / --save-pdf / None] s1346012

#TODO:
#SUBMIT! :DDDDD

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.print_page_options import PrintOptions
import getpass
import time
import sys
import bs4
from bs4 import BeautifulSoup
import re
import fpdf
import base64

#Define help function for below conditionals
def help():
    print("""Usage: python3 webadv_audit.py [--option] [student id, e.g., s1100841]	
   where [--option] can be:
      --help:	     Display this help information and exit
      --save-pdf: Save PDF copy of entire audit to the current folder
                  as audit.pdf"""
)
    
#Init studentent ID and print_pdf
studentID = ""
print_pdf = False

#System Handling for missing input:
if (len(sys.argv)) == 1:
    help()
    exit()

#System Handling for additional arg flags:
if (len(sys.argv) == 3):
    studentID = sys.argv[2]
    #Check for help:
    if sys.argv[1] == "--help":
        help()
        exit()
    if sys.argv[1] == "--save-pdf":
        print_pdf = True

#System Handling for only studentID
if (len(sys.argv) == 2):
    studentID = sys.argv[1]
    #Check for help:
    if sys.argv[1] == "--help":
        help()
        exit()
    if sys.argv[1] == "--save-pdf":
        help()
        print("Please include a Student ID an an argument!!!")
        exit()

#If argvs are proper:
#Use getpass to get password
password = getpass.getpass('Enter password for ' + studentID + ': ')

#Create webdriver instance
driver = webdriver.Chrome()

#Open webpage on webdriver
driver.get('http://webadvisor.monmouth.edu')
assert 'WebAdvisor Main Menu' in driver.title

#Test wait time
time.sleep(1)

#Find login link
driver.find_element(By.ID, 'acctLogin').click()

#Test wait time
time.sleep(1)

#Sign in with username
input_field = driver.find_element(By.ID, "userNameInput")
input_field.clear()
input_field.send_keys(studentID)
input_field.send_keys(Keys.ENTER)

#Test wait time
time.sleep(1)

#Sign in with password
input_field = driver.find_element(By.NAME, 'Password')
input_field.clear()
input_field.send_keys(password)
input_field.send_keys(Keys.ENTER)

#Check for bad password
bad_password_element = driver.find_elements(By.ID, 'errorTextPassword')
assert not bad_password_element, print("Incorrect user ID or password! Exiting.")

#Test wait time
time.sleep(1)

#AFTER LOGGING IN
#Click on Students Menu
driver.find_element(By.CLASS_NAME, 'WBST_Bars').click()

#Test wait time
time.sleep(1)

#Click Academic Audit/Pgm Eval Menu
driver.find_element(By.XPATH, "//span[.='Academic Audit/Pgm Eval']").click()

#Test wait time
time.sleep(1)

#Click Radio Button
driver.find_element(By.ID, "LIST_VAR1_1").click()

#Test wait time
time.sleep(1)

#Click Submit button - poll Academic Audit
driver.find_element(By.NAME, 'SUBMIT2').click()

#Test wait time
time.sleep(1)

#Save HTML source
html_content = driver.page_source
# print(html_content)    #Print HTML Source - for testing

#Save web page to audit.pdf (if enabled):
if print_pdf:
    # driver.execute_script('window.print();')

    print_options = PrintOptions()
    pdf = driver.print_page(print_options = print_options)
    pdf_bytes = base64.b64decode(pdf)
    with open("audit.pdf", "wb") as fh:
        fh.write(pdf_bytes)
    
    print("PDF Successfully printed!")


#Close driver
driver.close()

#init bs4 info gathering here:
audit_soup = bs4.BeautifulSoup(html_content, 'html.parser')

#Parse Name:
#<td class="PersonName"><strong>Student: Sean T. Fritz (1346012)</strong></td>
name_tags = audit_soup.find('td', class_="PersonName")  #Parse name + tags
name = name_tags.text                                   #Turn bs4.tag object into a string object
student_name = name.replace("Student: ", "")            #Remove unnecessary bits here

#Parse Program:
#<td><span class="ReqName">1: Comp. Science BA (CS.BA.MAJ.OUT.22)<b class="StatusInProgress"> (In progress)</b></span></td>
program_tags = audit_soup.find('span', class_="ReqName")  #Parse name + tags
program = program_tags.text                               #Turn bs4.tag object into a string object
program_name = program.replace("1: ", "")                 #Remove some unnecessary bits

#Parse Catalog
#<td class="Bold">Catalog: </td><td>C2223</td>
catalog_match = re.search(r'Catalog: </td><td>(.+?)</td>', html_content)    #Use regex to find catalog
catalog = catalog_match.group(1)

#Parse Anticipated Completion Date:
#Anticipated<br>Completion Date: </td><td valign="bottom">05/14/25</td>
comp_date_match = re.search(r'Anticipated<br>Completion Date: </td><td valign="bottom">([0-9]{2}/[0-9]{2}/[0-9]{2})</td>', html_content)
comp_date = comp_date_match.group(1)

#Parse advisor and class level:
advisor_match = re.search(r'<br> (Advisor: .+?) <br> (Class Level: .+?) <br>', html_content)
advisor = advisor_match.group(1)
class_level = advisor_match.group(2)

#Parse Graduation requirements that are "In Progress":
# <td align="right" width="5%">14.</td><td align="left" width="15%">CS-438</td><td align="left" width="20%">Operating Syst Analysis</td><td align="left" width="18%"></td><td align="left" width="10%">24/SP</td><td align="left" width="7%"></td><td align="right" width="10%">3</td><td width="5%"></td><td align="left" width="10%">
# <table border="0" align="left">
# <tbody><tr>
# <td align="left">*IP</td>
# </tr>
#use re.findall?
#in_progress_match = re.search(r'<td align="right" width="5%">[0-9]{1,2}.</td><td align="left" width="15%">(.+?)</td><td align="left" width="20%">(.+?)</td>.+?<td align="left">*IP</td></tr></tbody></table>')
# ip_pattern = re.compile(r'<td align="left" width="15%">(.+?)</td><td align="left" width="20%">(.+?)</td><td align="left" width="18%">.+?<tbody><tr>(.+?)</tr>', re.DOTALL)
# ip_matches = ip_pattern.findall(html_content)
ip_elements = audit_soup.find_all('span', class_="ReqName")  #Parse name + tags
sub_ip_elements = audit_soup.find_all('td', class_="SubReqName")

#Parse Graduation requirements that are "Not Started"
# ns_pattern = re.compile(r'<td align="left" width="15%">(.+?)</td><td align="left" width="20%">(.+?)</td><td align="left" width="18%">(.+?)</td>', re.DOTALL)
# ns_matches = ns_pattern.findall(html_content)
ns_elements = audit_soup.find_all('span', class_="ReqName")  #Parse name + tags
sub_ns_elements = audit_soup.find_all('td', class_="SubReqName")

#Parse Credits earned at a 200+ level (out of 54 credits required):
# <td> Take a Minimum of 54 Credits at the 200+ Level (54 CRS.) <br>
# </td>
# </tr>
# <tr>
# <td>Credits Earned: 54<br>
# </td>
# </tr>
credit_200plus_pattern = re.search(r'<td>\s*Take a Minimum of \d+ Credits at the 200\+ Level.+?<br>\s*</td>\s*</tr>\s*<tr>\s*<td>Credits Earned: (\d+)<br>', html_content, re.DOTALL)
credit_200plus = credit_200plus_pattern.group(1)


#Parse Total credits earned (out of 120 credits required; including current credits):
#<td class="Bold" align="left">Overall Credits:</td><td>120.00</td><td>97.00</td><td>23.00</td><td>15.00</td><td>8.00</td>
#<td>Credits Earned: 112<br>Required: 120<br>Remaining: 8<br>
total_credits_match = re.search(r'<td>Credits Earned: ([0-9]{1,3})<br>Required: [0-9]{1,3}<br>Remaining: [0-9]{1,3}<br>', html_content)
credits_earned = total_credits_match.group(1)


#Print final report!
print("\nAcademic Audit Summary")
print("======================")
print("Name: " + student_name)
print("Program: " + program_name)
print("Catalog: " + catalog)
print("Anticipated Completion Date: " + comp_date)
print(advisor)
print(class_level)
print("\nGraduation requirements that are \"In Progress\": ")
# #Create empty dict, ensure no dupe classes
# in_progress_classes = {}
# #Iterate through all classes
# for match in ip_matches:
#     #Break down groups from .findall regex above
#     class_code = match[0]
#     class_name = match[1]
#     class_status = match[2]

#     #Create key for key/value
#     key = class_code + " : " + class_name
#     #Populate dict
#     in_progress_classes[key] = class_status

# #Print the stuff
# progress_code = "*IP"
# for key, value in in_progress_classes.items():
#     if progress_code in value:
#         print(key)
for element in ip_elements:
    if '(In progress)' in element.text:
        element = element.text.replace(" (In progress)", "")
        print(element)

for element2 in sub_ip_elements:
    if '(In progress)' in element2.text:
        element2 = element2.text.replace(" (In progress)", "")
        print(element2)


print("\nGraduation requirements that are \"Not Started\": ")
# #create empty dict - ensure no dupe classes
# not_started_classes = {}
# #Iterate through all classes
# for match in ns_matches:
#     #Break down groups from about .findall regex
#     class_code = match[0]
#     class_name = match[1]
#     class_status = match[2]

#     #create key for key/value
#     key = class_code + " : " + class_name
#     #Populate dict
#     not_started_classes[key] = class_status

# #Print the stuff:
# progress_code = "course needed"
# for key, value in not_started_classes.items():
#     if progress_code in value:
#         print(key)
for element in ns_elements:
    if '(Not started)' in element.text:
        element = element.text.replace(" (Not started)", "")
        print(element)

for element2 in sub_ns_elements:
    if '(Not started)' in element2.text:
        element2 = element2.text.replace(" (Not started)", "")
        print(element2)


print("\nCredits earned at a 200+ level (out of 54 credits required): " + credit_200plus)
print("Total Credits Earned: " + credits_earned)

#Defunct code - kept just in case future ref needed - ignore
# if print_pdf:
#     print("\nPrinting PDF!")
#     #Create and init pdf page
#     pdf = fpdf.FPDF()
#     pdf.add_page()
#     pdf.set_font("Arial", size=12)
    
#     #Add content to .pdf
#     pdf.cell(200,10,txt="Academic Audit Summary", ln=1, align="L")
#     pdf.cell(200,10,txt="======================", ln=1, align="L")
#     pdf.cell(200,10,txt="Name: " + student_name, ln=1, align="L")
#     pdf.cell(200,10,txt="Program: " + program_name, ln=1, align="L")
#     pdf.cell(200,10,txt="Catalog: " + catalog, ln=1, align="L")
#     pdf.cell(200,10,txt="Anticipated Completion Date: " + comp_date, ln=1, align="L")
#     pdf.cell(200,10,txt=advisor, ln=1, align="L")
#     pdf.cell(200,10,txt=class_level, ln=1, align="L")
#     # pdf.cell(200,10,txt="Academic Audit Summary", ln=1, align="L")
#     # pdf.cell(200,10,txt="Academic Audit Summary", ln=1, align="L")
#     # pdf.cell(200,10,txt="Academic Audit Summary", ln=1, align="L")
#     pdf.cell(200,10,txt="Total Credits Earned: " + credits_earned, ln=1, align="L")
    
#     #Output pdf file
#     pdf.output("audit.pdf")
    
