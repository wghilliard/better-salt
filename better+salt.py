#Grayson Hilliard
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import time
import datetime
from pymongo import MongoClient

#Connecting to Mongo and establishing the data.
client = MongoClient()
bettersalt = client['bettersalt']
players = bettersalt['players']

def waiting():
	print "Waiting on the page to load..."
	time.sleep(12)

def load_waiter(x):
	print "Waiting for the page to load..."
	load_marker = '2'
	while load_marker == '2':
		try: 
			browser.find_element_by_xpath(x)
			load_marker = '1'

		except:
			print "Element is not there! (Give it a sec)"
			load_marker = '2'


def login_check():
	print "Checking login status..."
	load_waiter('//*[@id="p1name"]')

	try:
 		browser.find_element_by_xpath('//*[@id="footer"]/div[1]/a')
		print "winning"

	except:	
		browser.find_element_by_xpath('//*[@id="nav-menu"]/ul/li[2]/a').click()
		print "Logging in!"
		#Selecting and entering in our login info.
		load_waiter('//*[@id="forgotpassword"]')
		login_form = browser.find_element_by_xpath("//*[@id='email']")
		login_form.send_keys("grsn.hilliard@gmail.com")
		login_form = browser.find_element_by_xpath("//*[@id='pword']")
		login_form.send_keys("sk8ter")
		browser.find_element_by_xpath('//*[@id="signinform"]/span[3]/input').click()
		time.sleep(2)

def bet_status():
	status = browser.find_element_by_xpath('//*[@id="betstatus"]').text
	if status == "Bets are OPEN!":
		return 1

	elif "Bets are locked" in status:
		return 2

	elif "Red" in status:
		return 3

	else:
		return 4

def bet_status_text():
	print browser.find_element_by_xpath('//*[@id="betstatus"]').text

def roster_maker(player_name):

	#This little guy checks to see if they are already in the database and then adds them if they aren't!
	#### It also handles the bet token! ####
	
	if bettersalt.players.find_one({'player_name': player_name}) == None:
			print 'Addding "' + player_name + '" to the database...'
			stock_player_data = {
								"player_name" : player_name, 
								"wins" : 0, 
								"losses" : 0, 
								"total_matches" : 0, 
								"ELO" : 1000, 
								"last_fight_date" : unicode(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
								"total_fight_time" : 0,
								"average_fight_time" : 0
								}

			bettersalt.players.update({'player_name' : player_name}, stock_player_data, upsert = True)
			bet_token = 0
			
			if str(player_name) == str(player_one): 
				player_one_data = stock_player_data #bettersalt.players.find_one({'player_name': player_name})
				#bet_token = 1
				#print player_one_data

			else: 
				player_two_data = stock_player_data #bettersalt.players.find_one({'player_name': player_name})
				#bet_token = 1
				#print player_two_data
	else:

		if str(player_name) == str(player_one): 
			print "It looks like " + player_one + " already exists in our database!"
			player_one_data = bettersalt.players.find_one({'player_name': player_name})
			#bet_token = 1

		if str(player_name) == str(player_two):
			print "It looks like " + player_two + " already exists in our database!" 
			player_two_data = bettersalt.players.find_one({'player_name': player_name})
			#bet_token = 1

def record_match_stats(name, outcome):
	#if bet_elo_eval

	new_total_fight_time = (bettersalt.players.find_one({'player_name' : name})['total_fight_time'] + match_time)
	average_fight_time = new_total_fight_time / (bettersalt.players.find_one({'player_name' : name})['total_matches'] + 1) 

	if outcome == 1 and record == 1:
		bettersalt.players.update({'player_name' : name},
															{
															'$inc': { 'wins' : int(1), 'total_matches' : int(1)},
															'$set': {'last_fight_date' : unicode(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))},
															'$set': {'total_fight_time': new_total_fight_time},
															'$set': {'average_fight_time' : average_fight_time},
															'$set': {'bet_ratio' : float(one_over_two_ratio)},
															'$set': {'last_fight_outcome': int(1) }
															}, upsert = True)

		elo_eval(1)	

	if outcome == 2 and record == 1: 
		bettersalt.players.update({'player_name' : name},
															{
															'$inc': { 'losses' : int(1), 'total_matches' : int(1)},
															'$set': {'last_fight_date' : unicode(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))},
															'$set': {'total_fight_time': new_total_fight_time},
															'$set': {'average_fight_time' : average_fight_time},
															'$set': {'bet_ratio' : 1 / float(one_over_two_ratio)},
															'$set': {'last_fight_outcome': int(0)},
															}, upsert = True)
		elo_eval(2)	

	if record == 0: 
		print "Not currently recording data."
	#elif: 														 

def record_match_history(x):
	if x == 1:
		bettersalt.match_history.update({'when' : unicode(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))},
																													{
																													'player_one' : player_one,
																													'player_two' : player_two,
																													'winner' : player_one,
																													'loser' : player_two,
																													"match_time" : match_time,
																													"did_bet" : bet_token,
																													"much_bet" : bet_amount,
																													"bet_who" : 0, #1 or 2 
																													"player_one_bet_total" : int(player_one_bet_total),
																													"player_two_bet_total" : int(player_two_bet_total),
																													"ratio" : float(one_over_two_ratio),
																													}, upsert = True)

	if x == 2:
		bettersalt.match_history.update({'when' : unicode(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))},
																													{
																													'player_one' : player_one,
																													'player_two' : player_two,
																													'winner' : player_two,
																													'loser' : player_one,
																													"match_time" : match_time,
																													"did_bet" : bet_token,
																													"much_bet" : bet_amount,
																													"bet_who" : 0, #1 or 2
																													"player_one_bet_total" : int(player_one_bet_total),
																													"player_two_bet_total" : int(player_two_bet_total),
																													"ratio" : float(one_over_two_ratio),
																													}, upsert = True)
def bet():
	if bet_token == 0:
		bet_box = browser.find_element_by_xpath('//*[@id="wager"]')
		bet_amount = 0
		bet_box.send_keys(bet_amount)
		browser.find_element_by_xpath('//*[@id="fightcard"]/div[1]/div[2]/span/input').click()
		print "Test Bet placed!(DATASCRAPE)"
	
	else:
		print "executing crossfingers.exe"

def mid_round_research():
	
	print
	print "Gathering community bet data..."
	player_one_bet_total = browser.find_element_by_xpath('//*[@id="player1wager"]').text
	print "The community has placed " + str(player_one_bet_total) + " on " + player_one
	player_one_bet_total = player_one_bet_total.replace('$', '')
	player_one_bet_total = player_one_bet_total.replace(',', '')
	player_one_bet_total = long(player_one_bet_total)

	player_two_bet_total = browser.find_element_by_xpath('//*[@id="player2wager"]').text
	print "The community has placed " + str(player_two_bet_total) + " on " + player_two
	player_two_bet_total = player_two_bet_total.replace('$', '')
	player_two_bet_total = player_two_bet_total.replace(',', '')
	player_two_bet_total = long(player_two_bet_total)

	one_over_two_ratio = float(player_one_bet_total) / float(player_two_bet_total)
	print "The 1/2 ratio is " + str(one_over_two_ratio)

def elo_eval(winner):
	player_one_elo = bettersalt.players.find_one({'player_name' : player_one})['ELO']
	player_two_elo = bettersalt.players.find_one({'player_name' : player_two})['ELO']
	higher_elo = max(player_two_elo, player_one_elo)
	lower_elo = min(player_one_elo, player_two_elo)

	comp_elo = higher_elo - lower_elo

	if comp_elo <= 300:
		if winner == 1:
			bettersalt.players.update({'player_name' : player_one}, {
																		'$inc' : {'ELO' : 100}
																	})
			bettersalt.players.update({'player_name' : player_two}, {
																		'$inc' : {'ELO' : -100}
																	})
			print player_one + " has gained 100 ELO!"
			print player_two + " has lost 100 ELO!"

		if winner == 2:
			bettersalt.players.update({'player_name' : player_one}, {
																		'$inc' : {'ELO' : -100}
																	})
			bettersalt.players.update({'player_name' : player_two}, {
																		'$inc' : {'ELO' : 100}
																	})
			print player_two + " has gained 100 ELO!"
			print player_one + " has lost 100 ELO!"

	elif comp_elo > 300:
		if winner == 1 and player_one_elo == higher_elo:
			bettersalt.players.update({'player_name' : player_one}, {
																		'$inc' : {'ELO' : 20}
																	})
			bettersalt.players.update({'player_name' : player_two}, {
																		'$inc' : {'ELO' : -10}
																	})
			print player_one + " has gained 20 ELO!"
			print player_two + " has lost 10 ELO!"

		elif winner == 1 and player_two_elo == higher_elo:
			bettersalt.players.update({'player_name' : player_one}, {
																		'$inc' : {'ELO' : 300}
																	})
			bettersalt.players.update({'player_name' : player_two}, {
																		'$inc' : {'ELO' : -150}
																	})
			print player_one + " has gained 300 ELO!"
			print player_two + " has lost 150 ELO!"

		elif winner == 2 and player_one_elo == higher_elo:
			bettersalt.players.update({'player_name' : player_one}, {
																		'$inc' : {'ELO' : -150}
																	})
			bettersalt.players.update({'player_name' : player_two}, {
																		'$inc' : {'ELO' : 300}
																	})
			print player_two + " has gained 300 ELO!"
			print player_one + " has lost 150 ELO!"

		elif winner == 2 and player_two_elo == higher_elo:
			bettersalt.players.update({'player_name' : player_one}, {
																		'$inc' : {'ELO' : -10}
																	})
			bettersalt.players.update({'player_name' : player_two}, {
																		'$inc' : {'ELO' : 20}
																	})
			print player_two + " has gained 20 ELO!"
			print player_one + " has lost 10 ELO!"


#Initiallizing key variables!
print "Initiallizing key variables"
run_counter = 1
bet_token = 0
bet_elo_eval = 0
match_time = 0
record = 0
bet_amount = 0
player_one_bet_total = 0
player_two_bet_total = 0
one_over_two_ratio = float(1.0)
#---START OF CODE---

#   Opening the page.
print "Opening the page!"
browser = webdriver.Firefox()
browser.get('http://www.saltybet.com/')

#   Checking if we're logged in!
login_check()

#Optimizing...
# browser.find_element_by_xpath('').click()
# print "Pausing the Stream"

# browser.find_element_by_xpath('//*[@id="chatOff"]').click()
# print "Turning off chat..."

#Betting and Logging Loop
while run_counter == 1:
	
	print
	print
	print "We've seen " + str(bettersalt.players.count()) + " total fighters!"
	print "We've seen " + str(bettersalt.match_history.count()) + " matches!"

	my_current_money = int(browser.find_element_by_xpath('//*[@id="balance"]').text)
	print "Current Balance: " + str(my_current_money)


	#print "The average fight time is " + str()
	player_one = browser.find_element_by_xpath('//*[@id="p1name"]').text
	player_two = browser.find_element_by_xpath('//*[@id="p2name"]').text

	if bet_status() == 1: #Bets Open!
		record = 1
	
		#Check to see if they're new or nah
		roster_maker(player_one) 
		roster_maker(player_two)

		if "Team" in (player_one or player_two):
			bet_token == 0 #Teams too risky.
			print "Bet is too risky! No bet for buk buk lou!!"


		#Make bet
		bet()
		print "Waiting for betting period to end..."
		while bet_status() == 1:
			time.sleep(1)


	if bet_status() == 2:
		
		match_start_time = time.time()

		mid_round_research()

		print "Waiting for round to end..."
		if record == 0:
			print "(Not Recording Current Fight)"
		while bet_status() == 2:
			time.sleep(1)
		match_time = time.time() - match_start_time
		print "Match Time: " + str(match_time)

	if bet_status() == 3 and record == 1:
		print "Red Side Wins!" + "(" + player_one + ")"
		print "Updating " + player_one + "'s stats!"
		record_match_stats(player_one, 1) #Record Match Stats
		print "Updating " + player_two + "'s stats!"
		record_match_stats(player_two, 2) #Record Match Stats
		record_match_history(1)
		while bet_status() == 3:
			time.sleep(1)
		
			
	if bet_status() == 4 and record == 1:	
		print "Blue Side Wins!" + "(" + player_two + ")"
		print "Updating " + player_one + "'s stats!"
		record_match_stats(player_one, 2) #Record Match Stats
		print "Updating " + player_two + "'s stats!"
		record_match_stats(player_two, 1) #Record Match Stats
		record_match_history(2)
		while bet_status() == 4:
			time.sleep(1)
		

	# if bet_status() == (3 or 4) and record != 1: 
	# 	print "That awkward wait..."
	# 	while bet_status() == 3 or 4:
	# 		time.sleep(1)
	# 		if bet_status == 1:
	# 			break

	else:
		time.sleep(5)
			


# SPARE CODE			
# 	bettersalt.players.update({"player_name" : player_one}, player_one_data, upsert = True)
# 	bettersalt.players.update({"player_name" : player_two}, player_two_data, upsert = True)