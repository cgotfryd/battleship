from tkinter import *
import json
from urllib import request

user_name = 'sample'

#server request to register user
def server_register():
	global user_name, hit_count
	
	#disallow usernames with spaces or slashes
	user_name = name_box.get()
	if ' ' in user_name:
		info.config(text='Username cannot contain spaces',fg = 'red')
		return
	elif '\\' in user_name:
		info.config(text='Username cannot contain \'\\\'',fg = 'red')
		return
	elif '/' in user_name:
		info.config(text='Username cannot contain \'/\'',fg = 'red')
		return
	
	#make registration request to server
	else:
		url = 'http://localhost/register/%s' %(user_name)
		response = request.urlopen(url)
		content = json.loads(response.read())
		response.close()
		
		#username exists serverside
		if content == 'Username already taken':
			info.config(text = content,fg = 'red')
		
		#registration successful
		else:
			hit_count = 0
			start_game()
			response_label.config(text=content)
			guess_label.config(text = 'Guess Count: 0')
		return

#server request to load user's board	
def server_load():
	global user_name
	if user_name == 'sample':
		user_name = name_box.get()
	url = 'http://localhost/%s/view' %(user_name)
	response = request.urlopen(url)
	content = json.loads(response.read())
	response.close
	
	#no user exists in server memory
	if content == 'Invalid username':
		info.config(text = content,fg='red')
	
	else:
		start_game()
		client_load(content)
		
		

def client_load(data):
	global hit_count
	
	hit_count = 0
	for row in range(10):
		for column in range(10):
			server_square = data['board'][row][column]
			client_square = squares[row][column]
			if server_square == '.':
				client_square.config(bg = '#2493a6',image='',height=2,width=4)
			else:
				client_square.config(bg = 'blue')
				if server_square == 'x':
					hit_count+=1
					client_square.config(image=hit_img,width=32,height=35,bg='blue')
	guess_label.config(text = 'Guess Count: '+str(data['guesses']))
	remaining_count.config(text='Hits: %d/17'%(hit_count))

#dialogue to create new user profile
def register_prompt():
	global name_box, info
	
	new_user.destroy()
	returning_user.destroy()
	
	info = Label(login,text='Enter a new username')
	name_box = Entry(login)
	register = Button(login,text='Register',command=server_register)
	back_btn = Button(login, image = back_img, command=login_window)
	
	info.pack()
	name_box.pack(pady=5)
	register.pack()
	back_btn.pack(side = LEFT)

#dialogue to log in existing user
def load_prompt():
	global name_box, info
	
	new_user.destroy()
	returning_user.destroy()
	
	info = Label(login,text='Enter your username')
	name_box = Entry(login)
	register = Button(login,text='Login',command=server_load)
	back_btn = Button(login, image = back_img, command=login_window)
	
	info.pack()
	name_box.pack(pady=5)
	register.pack()
	back_btn.pack(side = LEFT)

#send guess request to server
def server_guess(cords):
	global user_name
	
	url = 'http://localhost/%s/guess/%s' % (user_name,cords)
	response = request.urlopen(url)
	content = json.loads(response.read())
	response.close()
	
	return content

#execute guess in GUI client-side
def client_guess(square):
	global hit_count
	
	info = square.grid_info()
	row = info['row']-1
	col = info['column']-1
	#cords = chr(row+96).upper() + str(col)
	cords = '%s,%s' %(str(row),str(col))
	
	#square already guessed - do nothing
	if square.cget('bg') == 'blue':
		return
	
	#square not guessed - do server guess
	result = server_guess(cords)
	message = result['message']
	guess_count = result['guesses']
	guess_label.config(text = 'Guess Count: '+str(guess_count))
	
	#valid guess
	if message == 'Miss' or message == 'You sunk my battleship!' or message == 'You hit my battleship!':
		square.config(bg='blue')
		response_label.config(text=message,fg='black')
		#hit successful
		if message != 'Miss':
			square.config(image=hit_img,width=32,height=35,bg='blue')
			hit_count += 1
			remaining_count.config(text = 'Hits: %d/17'%(hit_count))
			if message == 'You sunk my battleship!':
				response_label.config(fg = 'red')
	#invalid guess
	else:
		pass
	
	if result['win']:
		win(result)
	
#create button for game grid
def generate_squares(x,y):
	square = Button(game_frame)
	square.config(bg='#2493a6',bd=2,relief = GROOVE,height=2,width=4,command=lambda:client_guess(square))
	square.grid(column = x+1,row = y+1)
	return square

#creates login dialogue window
def login_window():
	global new_user, returning_user, login, x, y
	
	try:
		login.destroy()
	except:
		pass
	
	login = Toplevel(root)
	login.geometry('250x175+%d+%d' %(x+100,y+100))
	login.title('Battleship Login')
	login.resizable(False,False)
	login.transient(root)
	
	logo = Label(login, image = logo_img)
	logo.pack()
	
	new_user = Button(login)
	returning_user = Button(login)
	new_user.config(text = 'New User', command = register_prompt)
	returning_user.config(text = 'Returning User', command = load_prompt)
	
	new_user.pack(pady=5)
	returning_user.pack()

#removes login dialogue	
def start_game():
	global response_label, guess_label, bottom_spacing_frame, remaining_count, response_frame
	
	login.destroy()
	bottom_frame.destroy()
	
	response_frame = Frame(root)
	response_frame.pack(fill=BOTH)
	
	for i in range(3):
		bottom_spacing_frame = Frame(response_frame,height=10,width=420/3)
		bottom_spacing_frame.grid(row=0,column=i)
			
	response_label = Label(response_frame,font=('Times',14))
	response_label.grid(row=1,columnspan=3)
	
	guess_label = Label(response_frame, text = 'Guess Count:')
	guess_label.grid(row=2,column=2)
	
	remaining_count = Label(response_frame, text = 'Hits: 0/17')
	remaining_count.grid(row=2,column=0)
	
	scores_menu.entryconfig(0,state='normal')

#on game win
def win(data):
	global win_window, x, y
	
	url = 'http://localhost/%s/scoreboard' %(user_name)
	response = request.urlopen(url)
	content = json.loads(response.read())
	response.close()
	
	guess_label.config(text='Guess Count:')
	response_label.config(text='You sunk my fleet!')
	
	win_window = Toplevel(root)
	win_window.geometry('250x170+%d+%d' %(x+100,y+100))
	win_window.transient(root)
	win_window.title('Win!')
	win_window.resizable(False,False)
	
	victory_label = Label(win_window,image=victory_img)
	victory_label.pack()
	
	score_info = Label(win_window,height=2,font=('Times',14))
	score_text = 'Total Guesses: %d' %(data['guesses'])
	if data['guesses'] == content[0]['score']:
		score_text = 'NEW HIGHSCORE!\n'+score_text
	score_info.config(text=score_text)
	score_info.pack()
	
	new_game = Button(win_window, text = 'New Game',command=reset_game)
	new_game.pack(pady=5)

#reset after game win
def reset_game():
	win_window.destroy()
	response_frame.destroy()
	server_load()
	
#view personal scorebaord
def view_scoreboard():
	url = 'http://localhost/%s/scoreboard' %(user_name)
	response = request.urlopen(url)
	content = json.loads(response.read())
	response.close()
	
	scores_view(content)

#view global leaderboard
def view_leaderboard():
	url = 'http://localhost/leaderboard'
	response = request.urlopen(url)
	content = json.loads(response.read())
	response.close()	
	
	scores_view(content)

def scores_view(data):
	global x, y
	
	score_popup = Toplevel(root)
	score_popup.geometry('150x250+%d+%d' %(x+100,y+100))
	score_popup.transient(root)
	score_popup.resizable(False,False)
	score_popup.title('Scoreboard')
	
	score_img_label = Label(score_popup,image=score_img)
	score_img_label.pack(side=TOP)
	
	scores_area = Label(score_popup,anchor=NW)
	scores_area.pack(side=LEFT,fill=BOTH)
	scores_text = ''
	
	for score in data:
		scores_text += score['name'].title() + ': '+str(score['score']) + '\n'
		scores_area.config(text = scores_text,font = ('Times',12))
	

#define root window
root = Tk()
root.title('Battleship')
root.resizable(False,False)

#center root window
ws = root.winfo_screenwidth()
hs = root.winfo_screenheight()
x = (ws/4) #- (wr/2)
y = (hs/6) #- (hr/2)
root.geometry('420x510+%d+%d' %(x,y))

#menu bar
menubar = Menu(root)
scores_menu = Menu(menubar, tearoff = 0)
scores_menu.add_command(label = 'Personal', command = view_scoreboard,state='disabled')
scores_menu.add_command(label = 'Global', command = view_leaderboard)

menubar.add_cascade(label = 'Scores', menu = scores_menu)
root.config(menu = menubar)

#graphics
back_img = PhotoImage(file='back.png')
back_img = back_img.subsample(12,12)
initial_background = PhotoImage(file = 'startup.png')
logo_img = PhotoImage(file = 'logo.png')
hit_img = PhotoImage(file='hit.png')
hit_img = hit_img.subsample(5,5)
victory_img = PhotoImage(file='win.png')
score_img = PhotoImage(file = 'scoreboard.png')

#define log in window
login_window()

#define game elements
game_frame = Frame(root,bg='white',bd=5,relief=RIDGE)
game_frame.pack(side=TOP)

spacing_frame = Frame(game_frame,bg='white',width=10)
spacing_frame.grid(column=12)
spacing_frame = Frame(game_frame,bg='white',height=10)
spacing_frame.grid(row=12)

bottom_frame = Label(root,image=initial_background)
bottom_frame.pack()

#create 10x10 game grid for buttons
squares = [[generate_squares(x,y) for x in range(10)] for y in range(10)]

#create labels for grid coordinates
for i in range(10):
	row_head_sq = Label(game_frame)
	row_head_sq.config(height=1,width=2,bg='white',text=chr(i+97).upper())
	row_head_sq.grid(row=i+1,column=0)
	
	col_head_sq = Label(game_frame)
	col_head_sq.config(height=1,width=2,bg='white',text=str(i+1))
	col_head_sq.grid(row=0,column=i+1)

root.mainloop()
