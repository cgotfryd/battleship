from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib
import battleship
import leaderboard

#define user class. objects passed temporarily during requests then returned to state as dictionary
class User:
	def __init__(self,board,scoreboard,guesses,ship_state):
		self.board = board
		self.scoreboard = scoreboard
		self.guesses = guesses
		self.ship_state = ship_state
		
	#function to update user profile in state and returns serialized user as string for convenient use
	def serialize(self,name):
		user_profile = {'board':self.board,'scoreboard':self.scoreboard,'guesses':self.guesses,'ship_state':self.ship_state}
		serialized_user = json.dumps(user_profile)
		state[name] = user_profile
		return serialized_user

class BattleServer(BaseHTTPRequestHandler):
	#function to create user class object for use in server requests
	def get_profile(self,user_name):
		user_data = state[user_name]
		user = User(user_data['board'],user_data['scoreboard'],user_data['guesses'],user_data['ship_state'])
		return user
	
	#function to create new profile for user on registration
	def generate_profile(self,user_name):
		#checks for repeat username in state
		if user_name in state:
			return 'Username already taken'
		else:
			#creates board for user and initial ship placement
			new_game = battleship.initialize()
			#adds user to server state
			state[user_name] = {'board':new_game['board'],'scoreboard':[],'guesses':0,'ship_state':new_game['ships']}
			return 'Welcome %s' %(user_name.title())
	
	#funciton to execute guess requests
	def do_guess(self, user_name, user_guess, user_profile):
			#call guess function from battleship.py
			guess_result = battleship.guess(user_guess,user_profile.board,user_profile.ship_state)
			message = guess_result['message']
			user_profile.ship_state = guess_result['ships']
			win = False
			#to execute valid guesses
			if message == None or message == 'You sunk my battleship!' or message == 'You hit my battleship!':
				user_profile.guesses += 1
				
				#to check win condition
				win = True
				for ship in user_profile.ship_state:
					if user_profile.ship_state[ship]['hp'] > 0:
						win = False
				
				#on miss
				if message == None:
					battle_response = {'message':'Miss', 'win':win,'guesses':user_profile.guesses}
				
				#on hit
				else:
					battle_response = {'message': message,'win':win,'guesses':user_profile.guesses}
					if win:
						global global_leaderboard
						battle_response['board'] = user_profile.board
						
						#update user scoreboard, global leaderboard. Reset guess count, board, ship_status
						user_profile.scoreboard = leaderboard.update_scoreboard(user_name, user_profile.scoreboard, user_profile.guesses)
						global_leaderboard = leaderboard.update_leaderboard(user_profile.scoreboard,global_leaderboard)
						user_profile.guesses = 0
						new_game = battleship.initialize()
						user_profile.board = new_game['board']
						user_profile.ship_state = new_game['ships']
						print(user_profile.ship_state)

			#to execute invalid guesses
			else:
				battle_response = {'message': message,'win':win,'guesses':user_profile.guesses}
			
			return battle_response	
		
		
	
	def do_GET(self):

		#default reponse
		battle_response = 'Invalid request'
		path = self.path.strip('/')
		if path == 'favicon.ico':
			pass
		
		#to display leaderboard
		elif path.startswith('leaderboard'):
			#do leaderboard things
			battle_response = global_leaderboard
		
		#to register new user
		elif path.startswith('register'):		
			new_user = path.split('/')[1].lower()
			message = self.generate_profile(new_user)
			print(state[new_user])
			battle_response = message
		
		#to execute user specific requests
		else:
			try:
				#get user profile and path command
				path_user = path.split('/')[0].lower()
				path_command = path.split('/')[1]
				if path_user in state:
					user_profile = self.get_profile(path_user)
				else:
					battle_response = 'Invalid username'
				
				#to display board
				if path_command == 'view':
					battle_response = {'board':user_profile.board,'guesses':user_profile.guesses}
				
				#to execute guesses
				elif path_command == 'guess':
					user_guess = path.split('/')[2]
					battle_response = self.do_guess(path_user, user_guess, user_profile) 
				
				#to display user's scoreboard
				elif path_command == 'scoreboard':
					#do user_scoreboard things
					battle_response = user_profile.scoreboard
					
				#invalid path command
				else:
					pass
				
				user_profile.serialize(path_user)
			
			#invalid request
			except:
				pass
			
		#send server response
		self.send_response(200)
		self.send_header('Content-Type','text/plain')
		self.end_headers()
		self.wfile.write(json.dumps(battle_response).encode())
		
#establish state
state = {}
#establish leaderboard
global_leaderboard = []

#run server
battleserver = HTTPServer(('localhost',80), BattleServer)
print('server online...')
battleserver.serve_forever()
