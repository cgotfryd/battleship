import json

leaderboard = []

def new_scoreboard(user):
	scoreboard = [{'name':user,'score':0} for i in range(10)]
	return scoreboard
	
def update_scoreboard(user,user_scoreboard,new_score):
	new_highscore = False
	if len(user_scoreboard) > 10:
		for entry in user_scoreboard:
			if new_score < entry['score']:
				new_highscore = True
	else:
		new_highscore = True
	
	if new_highscore:
		user_scoreboard.append({'name':user,'score':new_score})
		user_scoreboard = sorted(user_scoreboard, key = lambda key : key['score'])
		
		if len(user_scoreboard) > 10:
			user_scoreboard.remove(user_scoreboard[10])
			
	return user_scoreboard
	
def update_leaderboard(user_scoreboard,leaderboard):
	user = user_scoreboard[0]['name']
	new_best = user_scoreboard[0]['score']
	
	for entry in leaderboard:
		if entry['name'] == user:
			leaderboard.remove(entry)
	
	leaderboard.append({'name':user,'score':new_best})
	leaderboard = sorted(leaderboard,key = lambda key : key['score'])
	
	return leaderboard
