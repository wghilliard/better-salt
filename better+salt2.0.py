from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import time
import datetime
import pymongo
from pymongo import MongoClient
import math

def main():
	#Opening the page.
	print ("Opening the page!")
	browser = webdriver.Firefox()
	browser.get('http://www.saltybet.com/')

	login_check()

def login_check():
	print ("Checking login status...")
	load_waiter('//*[@id="nav-menu"]/ul/li[1]/a/span')

	#Selecting and entering in our login info.
	print ("Logging in!")
	browser.find_element_by_xpath('//*[@id="nav-menu"]/ul/li[2]/a/span').click() #Clicking 
	load_waiter('//*[@id="forgotpassword"]')
	login_form = browser.find_element_by_xpath("//*[@id='email']")
	login_form.send_keys("grsn.hilliard@gmail.com")
	login_form = browser.find_element_by_xpath("//*[@id='pword']")
	login_form.send_keys("sk8ter")
	browser.find_element_by_xpath('//*[@id="signinform"]/span[3]/input').click()
	time.sleep(2)

def load_waiter(x):
	load_marker = '2'
	while load_marker == '2':
		try: 
			browser.find_element_by_xpath(x)
			load_marker = '1'

		except:

			print ("\nWaiting for the page to load...\n")
			load_marker = '2'

main()

