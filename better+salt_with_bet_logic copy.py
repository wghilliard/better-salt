#Grayson Hilliard
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import time
import datetime
from pymongo import MongoClient
import math

#Connecting to Mongo and establishing the data.
client = MongoClient()
bettersalt = client['bettersalt']
players = bettersalt['players']
match_history = bettersalt['match_history']
bot_stats = bettersalt['bot_stats']

def waiting():
	print "Waiting on the page to load..."
	time.sleep(12)

def load_waiter(x):
	
	load_marker = '2'
	while load_marker == '2':
		try: 
			browser.find_element_by_xpath(x)
			load_marker = '1'

		except:
			print
			print "Waiting for the page to load..."
			print
			load_marker = '2'


def login_check():
	print "Checking login status..."
	load_waiter('//*[@id="p1name"]')

	try:
 		browser.find_element_by_xpath('//*[@id="nav-menu"]/ul/li[1]/h2/a')
		print "winning"

	except:	
		browser.find_element_by_xpath('//*[@id="nav-menu"]/ul/li[2]/a/span').click()
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
			bet_token_setter(player_name, 0)
			
			if str(player_name) == str(player_one): 
				player_one_data = stock_player_data #bettersalt.players.find_one({'player_name': player_name})

			else: 
				player_two_data = stock_player_data #bettersalt.players.find_one({'player_name': player_name})
				
	else:

		if str(player_name) == str(player_one): 
			print 'It looks like ' + '"'  + player_one + '"' + ' already exists in our database!'
			player_one_data = bettersalt.players.find_one({'player_name': player_name})
			bet_token_setter(player_one, 1)
			print '"' + player_one + '" has ' + str(player_one_data['ELO']) + ' ELO.' 

		if str(player_name) == str(player_two):
			print "It looks like " + '"' + player_two + '"' + ' already exists in our database!' 
			player_two_data = bettersalt.players.find_one({'player_name': player_name})
			bet_token_setter(player_two, 1)
			print '"' + player_two + '" has ' + str(player_two_data['ELO']) + ' ELO.'

def bet_token_setter(player, token):
	if player == player_one:
		global bet_token_one 
		bet_token_one = token

	elif player == player_two:
		global bet_token_two
		bet_token_two = token

def bet_token_handler():
	global bet_token

	if (bet_token_one == 0) or (bet_token_two == 0):
		bet_token = 0

		

	else:
		bet_token = 1

def record_match_stats(name, outcome, match_time):

	#new_total_fight_time = (bettersalt.players.find_one({'player_name' : name})['total_fight_time'] + match_time)
	#average_fight_time = new_total_fight_time / (bettersalt.players.find_one({'player_name' : name})['total_matches'] + 1) 

	if outcome == 1 and record == 1:
		bettersalt.players.update({'player_name' : name},
															{
															'$inc': { 'wins' : int(1), 'total_matches' : int(1)},
															'$set': {'last_fight_date' : unicode(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))},
															#'$set' : {'total_fight_time': new_total_fight_time},
															#'$set' : {'average_fight_time' : average_fight_time},
															'$set': {'bet_ratio' : float(one_over_two_ratio)},
															'$set': {'last_fight_outcome': int(1) }
															}, upsert = True)
	

	if outcome == 2 and record == 1: 
		bettersalt.players.update({'player_name' : name},
															{
															'$inc': { 'losses' : int(1), 'total_matches' : int(1)},
															'$set': {'last_fight_date' : unicode(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))},
															#'$set' : {'total_fight_time': new_total_fight_time},
															#'$set' : {'average_fight_time' : average_fight_time},
															'$set': {'bet_ratio' : 1 / float(one_over_two_ratio)},
															'$set': {'last_fight_outcome': int(0)},
															}, upsert = True)

	if record == 0: 
		print "Not currently recording data."												 

def record_match_history(x, player_one_total, player_two_total, bet_token, bet_amount, bet_who, one_over_two_ratio):
	if x == 1:
		bettersalt.match_history.insert(
										{
										'when' : unicode(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
										'player_one' : player_one,
										'player_two' : player_two,
										'winner' : player_one,
										'loser' : player_two,
										"match_time" : match_time,
										"did_bet" : bet_token,
										"much_bet" : bet_amount,
										"bet_who" : bet_who, 
										'player_one_bet_total' : player_one_total,
										'player_two_bet_total' : player_two_total,
										"ratio" : float(one_over_two_ratio),
										})

	if x == 2:
		bettersalt.match_history.insert(
										{
										'when' : unicode(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
										'player_one' : player_one,
										'player_two' : player_two,
										'winner' : player_two,
										'loser' : player_one,
										"match_time" : match_time,
										"did_bet" : bet_token,
										"much_bet" : bet_amount,
										"bet_who" : bet_who, 
										'player_one_bet_total' : player_one_total,
										'player_two_bet_total' : player_two_total,
										"ratio" : float(1 / one_over_two_ratio),
										})

def bet_logic():
	bet_token_handler()
	global bet_amount
	try:
		 test_case = bettersalt.match_history.find_one({'player_one' : player_one, 'player_two': player_two})
		 bet_clicker(my_bet_money, test_case['winner'])
	
	except:
		if bet_token == 0:
			print 'Test Bet!(DATAHARVEST MODE)'
			bet_clicker(1, player_one)
		
		


		elif bet_token == 1:
			player_one_elo = bettersalt.players.find_one({'player_name' : player_one})['ELO']
			player_two_elo = bettersalt.players.find_one({'player_name' : player_two})['ELO']
			higher_elo = max(player_two_elo, player_one_elo)

			
				

			if player_one_elo == higher_elo:
				my_pick = player_one
				bet_who = 1


			if player_two_elo == higher_elo:
				my_pick = player_two
				bet_who = 2
			


			if player_one_elo == player_two_elo:
				print 'Looks like it\'s an even match! Better play it safe!'
				bet_clicker(1, player_one)

			if 1 <= abs(player_one_elo - player_two_elo) <= 100:
				bet_amount = math.ceil(my_bet_money * float(.2))
				bet_clicker(str(bet_amount), my_pick)

			if 101 <= abs(player_one_elo - player_two_elo) <= 250:
				bet_amount = int(math.ceil(my_bet_money * float(.4)))
				bet_clicker(str(bet_amount), my_pick)

			if 251 <= abs(player_one_elo - player_two_elo) <= 400:
				bet_amount = int(math.ceil(my_bet_money * float(.5)))
				bet_clicker(str(bet_amount), my_pick)

			if abs(player_one_elo - player_two_elo) > 400:
				bet_amount = int(math.ceil(my_bet_money))
				bet_clicker(str(bet_amount), my_pick)

			print 'executing crossfingers.exe'

	

def bet_clicker(bet_amount, player):
	bet_box = browser.find_element_by_xpath('//*[@id="wager"]')
	bet_box.clear()
	bet_amount = str(bet_amount)
	bet_amount_x, sep, extra = bet_amount.partition('.')


	if "Team" in (player_one or player_two):
				print "Bet is too risky! No real bet for buk buk lou!!"
				bet_box.send_keys(1)
				browser.find_element_by_xpath('//*[@id="bet-table"]/div[1]/div/div[2]/span/input').click()

	else:

		if player == player_one:
			bet_box.send_keys(bet_amount_x)
			browser.find_element_by_xpath('//*[@id="bet-table"]/div[1]/div/div[2]/span/input').click()


		elif player == player_two:
			bet_box.send_keys(bet_amount_x)
			browser.find_element_by_xpath('//*[@id="bet-table"]/div[3]/div/div[1]/span/input').click()
	print	
	print '### Betting $' + str(bet_amount) + ' on ' + str(player) + '! ###'
	print

def mid_round_research():
	
	print
	print "Gathering community bet data..."
	load_waiter('//*[@id="player1wager"]')
	load_waiter('//*[@id="player2wager"]')
	player_one_bet_total = browser.find_element_by_xpath('//*[@id="lastbet"]/span[1]').text
	print "The community has placed " + str(player_one_bet_total) + ' on ' + '"' + player_one + '"' + '...'
	player_one_bet_total = long(player_one_bet_total.replace('$', '').replace(',', '').replace(' ', ''))
	# player_one_bet_total = player_one_bet_total.replace(',', '')
	# player_one_bet_total = player_one_bet_total.replace(' ', '')
	# player_one_bet_total = long(player_one_bet_total)

	#print 'DEBUG: "' + str(player_one_bet_total) + '"'

	player_two_bet_total = browser.find_element_by_xpath('//*[@id="lastbet"]/span[2]').text
	print "The community has placed " + str(player_two_bet_total) + ' on ' + '"' + player_two + '"' + '...'
	player_two_bet_total = long(player_two_bet_total.replace('$', '').replace(',', '').replace(' ', ''))
	# player_two_bet_total = player_two_bet_total.replace(',', '')
	# player_two_bet_total = player_two_bet_total.replace(' ', '')
	# player_two_bet_total = long(player_two_bet_total)

	#print 'DEBUG: "' + str(player_two_bet_total) + '"'

	# if player_one_bet_total or player_two_bet_total == None:
	# 	print "An Error has occured! Reloading bet totals!"

	# 	player_one_bet_total = browser.find_element_by_xpath('//*[@id="player1wager"]').text
	# 	print "The community has placed " + str(player_one_bet_total) + ' on ' + '"' + player_one + '"' + '...'
	# 	player_one_bet_total = player_one_bet_total.replace('$', '')
	# 	player_one_bet_total = player_one_bet_total.replace(',', '')
	# 	player_one_bet_total = float(player_one_bet_total)

	# 	player_two_bet_total = browser.find_element_by_xpath('//*[@id="player2wager"]').text
	# 	print "The community has placed " + str(player_two_bet_total) + ' on ' + '"' + player_two + '"' + '...'
	# 	player_two_bet_total = player_two_bet_total.replace('$', '')
	# 	player_two_bet_total = player_two_bet_total.replace(',', '')
	# 	player_two_bet_total = float(player_two_bet_total)

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
																		'$inc' : {'ELO' : -50}
																	})
			print '"' + player_one + '" has gained 100 ELO!'
			print '"' + player_two + '" has lost 50 ELO!'

		elif winner == 2:
			bettersalt.players.update({'player_name' : player_one}, {
																		'$inc' : {'ELO' : -50}
																	})
			bettersalt.players.update({'player_name' : player_two}, {
																		'$inc' : {'ELO' : 100}
																	})
			print '"' + player_two + '" has gained 100 ELO!'
			print '"' + player_one + '" has lost 50 ELO!'

	elif comp_elo > 300:
		if winner == 1 and player_one_elo == higher_elo:
			bettersalt.players.update({'player_name' : player_one}, {
																		'$inc' : {'ELO' : 20}
																	})
			bettersalt.players.update({'player_name' : player_two}, {
																		'$inc' : {'ELO' : -10}
																	})
			print '"' + player_one + '" has gained 20 ELO!'
			print '"' + player_two + '" has lost 10 ELO!'

		elif winner == 1 and player_two_elo == higher_elo:
			bettersalt.players.update({'player_name' : player_one}, {
																		'$inc' : {'ELO' : 300}
																	})
			bettersalt.players.update({'player_name' : player_two}, {
																		'$inc' : {'ELO' : -150}
																	})
			print '"' + player_one + '" has gained 300 ELO!'
			print '"' + player_two + '" has lost 150 ELO!'

		elif winner == 2 and player_one_elo == higher_elo:
			bettersalt.players.update({'player_name' : player_one}, {
																		'$inc' : {'ELO' : -150}
																	})
			bettersalt.players.update({'player_name' : player_two}, {
																		'$inc' : {'ELO' : 300}
																	})
			print '"' + player_two + '" has gained 300 ELO!'
			print '"' + player_one + '" has lost 150 ELO!'

		elif winner == 2 and player_two_elo == higher_elo:
			bettersalt.players.update({'player_name' : player_one}, {
																		'$inc' : {'ELO' : -10}
																	})
			bettersalt.players.update({'player_name' : player_two}, {
																		'$inc' : {'ELO' : 20}
																	})
			print player_two + " has gained 20 ELO!"
			print player_one + " has lost 10 ELO!"

		
def money_made(bet_amount):
	
	#debug(bet_amount)

	try:
		dough = float(browser.find_element_by_xpath('//*[@id="lastbet"]/span[2]')
	except:
		load_waiter('//*[@id="lastbet"]/span[2]')
		dough = float(browser.find_element_by_xpath('//*[@id="lastbet"]/span[2]')
		 
	# if delta > 0:
	# 	if bet_amount != 1:
	# 		acc_track(1)
	# 	return '### We made $' + str(delta) + '! :3 ###'

	# elif delta < 0: 
	# 	delta = abs(delta)
	# 	if bet_amount != 1:	
	# 		acc_track(2)
	# 	return '### We lost $' + str(delta) + '! :( ###'

	# else: 
	# 	return '### No money gained or lost. ###'

def acc_track(x):
	

	if x == 1:
		bettersalt.bot_stats.update({'version' : '1'}, {
														'$inc' : {'won' : 1} 
														}, upsert = True )



	if x == 2:
		bettersalt.bot_stats.update({'version' : '1'}, {
														'$inc' : {'loss' : 1} 
														}, upsert = True )


	bettersalt.bot_stats.update({'version' : '1'}, {
													'$inc' : {'guesses' : 1} 
													}, upsert = True )
	
	one = float(bettersalt.bot_stats.find_one({'version' : '1'})['won'])
	two = float(bettersalt.bot_stats.find_one({'version' : '1'})['guesses'])
	print 'Our guess percentage is ' + str((one/two)*100) + '%' + ' acurate.'

def debug(x):
	print 'DEBUG MESSAGE: ' + str(x)

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---START OF CODE---
#Initiallizing key variables!
print "Initiallizing key variables"
run_counter = 1
bet_token = 0
bet_elo_eval = 0
match_time = 0
record = 0
global bet_amount
bet_amount = 0
player_one_bet_total = 0
player_two_bet_total = 0
one_over_two_ratio = float(1.0)
bet_token_one = 10
bet_token_two = 10
my_current_money = 0
bet_who = 0
player_one_data = []
player_two_data = []
global dough
dough = 0

#   Opening the page.
print "Opening the page!"
browser = webdriver.Firefox()
browser.get('http://www.saltybet.com/')

#   Checking if we're logged in!
login_check()

#Betting and Logging Loop
while run_counter == 1:
	
	print
	print
	print "We've seen " + str(bettersalt.players.count()) + " total fighters!"
	print "We've seen " + str(bettersalt.match_history.count()) + " matches!"



	#print "The average fight time is " + str()
	player_one = browser.find_element_by_xpath('//*[@id="p1name"]').text
	player_two = browser.find_element_by_xpath('//*[@id="p2name"]').text


	if bet_status() == 1: #Bets Open!
		record = 1
		
		my_current_money = float(browser.find_element_by_xpath('//*[@id="balance"]').text)
		my_bet_money = math.ceil(float(my_current_money * .5))
		print "Current Balance: " + str(my_current_money)

		#Check to see if they're new or nah
		roster_maker(player_one) 
		roster_maker(player_two)

		#Make bet
		bet_logic()
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
		print

	if bet_status() == 3 and record == 1:
		print "Red Side Wins!" + "(" + player_one + ")"
		print 'Updating "' + player_one + '"\'s stats!'
		record_match_stats(player_one, 1, match_time) #Record Match Stats
		print 'Updating "' + player_two + '"\'s stats!"'
		record_match_stats(player_two, 2, match_time) #Record Match Stats
		record_match_history(1, player_one_bet_total, player_two_bet_total, bet_token, bet_amount, bet_who, one_over_two_ratio)
		elo_eval(1)
		print
		print '"' + player_one + '" now has ' + str(bettersalt.players.find_one({'player_name' : player_one})['ELO']) + 'ELO!'
		print '"' + player_two + '" now has ' + str(bettersalt.players.find_one({'player_name' : player_two})['ELO']) + 'ELO!'
		print 
		print money_made(bet_amount)
		print

		while bet_status() == 3:
			time.sleep(1)
		
	if bet_status() == 4 and record == 1:	
		print "Blue Side Wins!" + "(" + player_two + ")"
		
		print 'Updating "' + player_one + '"\'s stats!'
		record_match_stats(player_one, 2, match_time) #Record Match Stats
		print 'Updating "' + player_two + '"\'s stats!"'
		record_match_stats(player_two, 1, match_time) #Record Match Stats
		record_match_history(2, player_one_bet_total, player_two_bet_total, bet_token, bet_amount, bet_who, one_over_two_ratio)
		elo_eval(2)
		print '"' + player_one + '" now has ' + str(bettersalt.players.find_one({'player_name' : player_one})['ELO']) + 'ELO!'
		print '"' + player_two + '" now has ' + str(bettersalt.players.find_one({'player_name' : player_two})['ELO']) + 'ELO!'
		print 
		print money_made(bet_amount)
		print

		while bet_status() == 4:
			time.sleep(1)
		
	else:
		time.sleep(5)
			