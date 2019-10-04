#imports and utility functions
from random import randint
import os
import json
def clear():
	os.system('cls')

#function to coerce letter co-ordinate to relative number
def to_num(letter):
	return(ord(letter.lower())-97)

#build board
def build_board():
	global board	
	board = [['.' for j in range(10)] for i in range(10)]
	
#function to display board
def display_board(user_board):
	header = ['  ']
	[header.append(' '+str(i+1)) for i in range(10)]
	str_board = ''.join(header)
	
	row_num = 97
	
	for row in user_board:
		temp = []
		[temp.append(' '+square) for square in row]
		str_board += chr(row_num).upper() + ' ' + ''.join(temp)
		row_num += 1
	return str_board

#function to execute guesses
def guess(cords,user_board, user_ships):
	
	#checks for valid input and convert to array indexes
	try:
		cords = cords.split(',')
		r = int(cords[0])
		c = int(cords[1])
		
	except:
		return({'message':'!! Input must be in <row>,<col> format !!','ships':user_ships})
	
	if r > 9:
		return({'message':'!! Row is out of range !!','ships':user_ships})
	elif c > 10:
		return({'message':'!! Column is out of range !!','ships':user_ships})
	elif r < 0:
		return({'message':'!! Row cannot be negative !!','ships':user_ships})
	elif c < 0:
		return({'message':'!! Column cannot be negative !!','ships':user_ships})
	
	if user_board[r][c] == 'x' or user_board[r][c] == '-':
		return({'message':'You already guessed that square','ships':user_ships})
		
	#check guess co-ordinates against ship co-ordinates
	hit_ship = None
	for ship in user_ships:
		ship_rows = user_ships[ship]['cords'][0]
		ship_cols = user_ships[ship]['cords'][1]
		for i in range(len(ship_rows)):
			if ship_rows[i] == r and ship_cols[i] == c:
				user_board[r][c] = 'x'
				hit_ship = ship
	
	if hit_ship == None:
		user_board[r][c] = '-'
		return {'message':None,'ships':user_ships}
	
	else:
		user_ships[hit_ship]['hp'] -= 1
		if user_ships[hit_ship]['hp'] == 0:
			return {'message':'You sunk my battleship!','ships':user_ships}
		else:
			return {'message':'You hit my battleship!','ships':user_ships}

#function to select random co-ordinates of ship based on type
def generate_ship(ship_type):
	global ships
	
	#establish length of ship by name
	ship_len = ships[ship_type]['hp']
	
	#randomly chooses starting co-ordinate and direction to extend ship
	invalid = True
	while invalid:
		ship_row = [randint(0,9)]
		ship_col = [randint(0,9)]
		
		direction = randint(1,4)

		if direction == 1:
			if ship_col[0] - ship_len-1 < 0:
				continue
			[ship_row.append(ship_row[i]) for i in range(ship_len-1)]
			[ship_col.append(ship_col[i]-1) for i in range(ship_len-1)]
		elif direction == 2:
			if ship_col[0] + ship_len-1 > 9:
				continue
			[ship_row.append(ship_row[i]) for i in range(ship_len-1)]
			[ship_col.append(ship_col[i]+1) for i in range(ship_len-1)]
		elif direction == 3:
			if ship_row[0] - ship_len-1 < 0:
				continue
			[ship_row.append(ship_row[i]-1) for i in range(ship_len-1)]
			[ship_col.append(ship_col[i]) for i in range(ship_len-1)]
		elif direction == 4:
			if ship_row[0] + ship_len-1 > 9:
				continue
			[ship_row.append(ship_row[i]+1) for i in range(ship_len-1)]
			[ship_col.append(ship_col[i]) for i in range(ship_len-1)]
		
		invalid = False
		
	return(ship_row, ship_col)
	
#function to prevent ship co-ordinates from overlapping
def collision_control():
	global ships
	
	ships = {'battleship':{'cords':None,'hp':5},
			'cruiser':{'cords':None,'hp':4},
			'dest_a':{'cords':None,'hp':3},
			'dest_b':{'cords':None,'hp':3},
			'frigate':{'cords':None,'hp':2}}
	placed_r = list()
	placed_c = list()
	
	for ship_type in ships:
		ship = ships[ship_type]
		invalid = True
		while invalid:
			invalid = False
			cords = generate_ship(ship_type)
			for i in range(ship['hp']):
				for j in range(len(placed_r)):
					if cords[0][i] == placed_r[j]:
						if cords[1][i] == placed_c[j]:
							invalid = True
							
		[placed_r.append(cords[0][i]) for i in range(len(cords[0]))]
		[placed_c.append(cords[1][i]) for i in range(len(cords[1]))]
		
		ship['cords'] = cords
	
	
#initialize board setup
def initialize():
	build_board()
	collision_control()
	return {'board':board,'ships':ships}

#play game
def play():
	guesses = 0
	playing = True
	
	while playing:
		display_board()
		print('Can you find my battleship?')
		cords = input('Select target ')
		result = guess(cords)
		guesses += 1
		clear()
		
		#interpret restult of guess
		if result != None:
			print(result)
		#Win condition
		win = True
		for ship in ships:
			ship_hp = ships[ship]['hp']
			if ship_hp > 0:
				win = False
		
		if win:
			playing = False

def The_Game():
	initialize()
	play()
	print('That was my last battleship! You sunk my fleet in '+str(guesses)+' turns')
	display_board()
	input('Press enter to play again')	
