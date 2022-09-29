import copy
Role = None

movement_r = { "1":[ 7, 2, 6], "2":[ 8, 3, 7], "3":[ 9, 4, 8], "4":[10, 5, 9], "5":[10], 
			   "6":[12, 7,11], "7":[13, 8,12], "8":[14, 9,13], "9":[15,10,14],"10":[15],
			  "11":[17,12,16],"12":[18,13,17],"13":[19,14,18],"14":[20,15,19],"15":[20],
			  "16":[22,17,21],"17":[23,18,22],"18":[24,19,23],"19":[25,20,24],"20":[25],
			  "21":[22]      ,"22":[23]      ,"23":[24]      ,"24":[25]
}
#movement dict for color red
movement_b = {                 "2":[ 1]      , "3":[ 2]      , "4":[ 3]      , "5":[ 4], 
			   "6":[ 1]      , "7":[ 1, 2, 6], "8":[ 2, 3, 7], "9":[ 3, 4, 8],"10":[ 4, 5, 9],
			  "11":[ 6]      ,"12":[ 6, 7,11],"13":[ 7, 8,12],"14":[ 8, 9,13],"15":[ 9,10,14],
			  "16":[11]      ,"17":[11,12,16],"18":[12,13,17],"19":[13,14,18],"20":[14,15,19],
			  "21":[16]      ,"22":[16,17,21],"23":[17,18,22],"24":[18,19,23],"25":[19,20,24], 
}

r_score_dict = {   "1": 0, "2": 1, "3":  6,  "4": 18,  "5":40,  
				   "6": 1, "7": 6, "8": 18,  "9": 40, "10":75, 
		  	 	  "11": 6,"12":18,"13": 40, "14": 75, "15":126, 
		  	 	  "16":18,"17":40,"18": 75, "19":126, "20":196, 
		  	 	  "21":40,"22":75,"23":126, "24":196, "25":288
}
#movement dict for color blue

def alphabetapru(node, depth, alpha, beta, player_1st):
	if(depth==0 or node.is_terminal_node()):
		eva = node.evaluate()
		node.score = eva
		return eva 
	if(player_1st):
		maxEva = -99999
		for succ in node.succ:
			evaTemp = alphabetapru(succ, depth-1, alpha, beta, 0)
			maxEva = max(maxEva, evaTemp)
			if(beta <= alpha):
				break
		node.score = maxEva
		return maxEva
	else:
		minEva = 99999
		for succ in node.succ:
			evaTemp = alphabetapru(succ, depth-1, alpha, beta, 1)
			minEva = min(minEva, evaTemp)
			if(beta <= alpha):
				break
		node.score = minEva
		return minEva
#doing alpha beta pruming and update the score

def build_tree(root, depth, to_move):
	if(depth==0):
		return
	root.succ = root.successor(to_move)
	for succ in root.succ:
		to_move = []
		if(succ.color == 'R'):
			for i in range(6):
				num = place[i+6]
				if(num):
					to_move.append(i+1)
		else:
			for i in range(6):
				num = place[i]
				if(num):
					to_move.append(i+1)
		build_tree(succ, depth-1, to_move)
	return
#bulid a tree for alpha beta pruming to work 

class node(object):
	"""docstring for Node"""
	def __init__(self, table, place, color):
		self.table = table
		self.place = place
		self.succ = []
		self.color = color
		self.last_move = None
		self.score = 0
	def move(self, from_to):
		#enter to src and dst to move and return a node
		newnode = copy.deepcopy(self)
		from_, to_ = from_to[0], from_to[1] 
		table = newnode.table
		place = newnode.place
		for i in range(12):
			if(place[i]==from_):
				place[i] = to_
			elif(place[i]==to_):
				place[i] = 0
		from_, to_ = from_-1, to_-1
		#chage from 1~25 to 0~24
		table[from_],table[to_] = 0,table[from_]
		if(newnode.color == 'R'):
			newnode.color = 'B'
		else:
			newnode.color = 'R'
		# change the color to the new node
		newnode.last_move = from_to
		return newnode   
	def evaluate(self):
		table = self.table
		r_cnt = 0
		r_score = 0
		b_cnt = 0
		b_score = 0
		for i in range(5):
			for j in range(5):
				num = table[i*5+j]
				if(num == 0):
					continue
				else:
					if(num//7):
						r_cnt += 1
						on_table = i*4+j+1
						r_score += r_score_dict[str(on_table)]
						if(on_table==25):
							r_score += 10000
					else:
						b_cnt += 1
						on_table = i*4+j+1
						b_score += r_score_dict[str(26-on_table)]
						if(on_table==1):
							b_score += 10000
		if(r_cnt!=0):
			r_score = (r_score)/r_cnt
			if(r_cnt>4):
				r_score -= r_cnt*100
			# else:
			# 	r_score += r_cnt*100
		else:
			b_score += 10000
		if(b_cnt!=0):
			b_score = (b_score)/b_cnt-b_cnt*100
			if(b_cnt>4):
				b_score -= b_cnt*100
			# else:
			# 	b_score += b_cnt*100
		else:
			r_score += 10000
		if(Role==0):
			return b_score-r_score
		else:
			return r_score-b_score
		#return the score according to the Role
	def successor(self, to_move):
		succ = []
		if(self.color=='R'):
			for i in to_move:
				from_ = place[i-1+6]
				list_ = movement_r[str(from_)]
				for j in list_:
					succ.append(self.move([from_, j]))
		else:
			for i in to_move:
				from_ = place[i-1]
				list_ = movement_b[str(from_)]
				for j in list_:
					succ.append(self.move([from_, j]))
		return succ
		#enter the node and to_move(which number to move to get the successor of one node)
	def is_terminal_node(self):
		table = self.table
		if(table[0]//7==0 and table[0]!=0):
			return True
		if(table[24]//7==1):
			return True
		place = self.place
		for i in range(6):
			if(place[i]!=0):
				return False
		for i in range(6):
			if(place[i+6]!=0):
				return False
		return True
		#determine whether it is the final state

while(True):
	command = input()
	command = command.split()
	if(command[0] == 'ini'):
	#init command
		Role = command[1]
		if(Role=='R'):
			print('1 2 3 7 11 6')#default placemant for Red
		else:
			print('25 24 23 20 19 15')#default placemant for Blue
	elif(command[0] == 'get'):
	#get command
		Role = 1*(command[1]=='R')
		dice = int(command[2])
		table = [0 for i in range(25)]
		place = [0 for i in range(12)]
		for i in range(12):
			pos = int(command[3+i])
			place[i] = pos
			if(pos):
				table[pos-1] = i+1
		root=node(table, place, command[1])
		to_move = []
		if(place[dice-1+Role*6]==0):
			for i in range(dice-1, 0, -1):
				if(place[i-1+Role*6]!=0):
					to_move.append(i)
					break
			for i in range(dice+1, 7, 1):
				if(place[i-1+Role*6]!=0):
					to_move.append(i)
					break
		else:
			to_move.append(dice)

		depth = 3
		build_tree(root, depth, to_move)
		#build the tree for alpha beta below to search
		target = alphabetapru(root, depth, -99999, 99999, 1)
		for i in root.succ:
			if target == i.score:
				print(i.last_move[0], i.last_move[1])
				break
		#to see the matching move
	elif(command[0]=='exit'):
		break
	else:
		break




