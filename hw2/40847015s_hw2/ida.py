import time
import copy
import os


ans = []
step = []
time_rec = []
mem_rec = []
visited = set()
mem = 0
id_table = []
id_block = {}
count = 1
cnt_max = 0
recorded = 0
table_max = 0
shapey, shapex = 0, 0
inverse = {"U":"D", "D":"U", "L":"R", "R":"L"}
class node:
	# 建構式
	def __init__(self, table, block_data):
		self.table = table
		self.last_inverse_op = 'None'
		self.block_data = block_data
		self.gn = int(0)
		#node 視為一個 state，紀錄當前狀態的盤面，最大的方塊編號，上一步的動作，盤面中所有方塊的資訊
	def cal_fn(self):
		# 計算並回傳 f(n)
		global id_block
		manhatten = int(0)
		for i in range(1, table_max+1):
			loc = self.block_data[str(i)]['loc']
			id_loc = id_block[str(i)]
			# 以下分別為使用 hamming distance 與 manhatten distance
			# if(loc[0]!=id_loc[0] or loc[1]!=id_loc[1]):
			# 	manhatten += 1
			manhatten += abs(loc[0]-id_loc[0])
			manhatten += abs(loc[1]-id_loc[1])
		return manhatten+self.gn
	
	def successor(self):
		#尋找當前 node 可以展開的動作，回傳動作的 list
		succ_list = []
		for i in range (1, table_max+1):# for every block
			str_i = str(i)
			table = self.table
			ybound, xbound = shapey-1, shapex-1
			block_shapey, block_shapex = self.block_data[str_i]['shape']
			luy, lux = self.block_data[str_i]['loc']
			ruy, rux = luy, lux+block_shapex-1
			ldy, ldx = luy+block_shapey-1, lux
			rdy, rdx = luy+block_shapey-1, lux+block_shapex-1
			# 確認移動目標位置在邊界內
				# 確認移動目標位置沒有其他方塊
			# order 1, 2, 3, 4; 上, 下, 左, 右
			if(luy > 0 and ruy > 0):
				if(table[luy-1][lux] == 0 and table[ruy-1][rux] == 0):
					succ_list.append(str_i+"U")
			if(ldy < ybound and rdy < ybound):
				if(table[ldy+1][ldx] == 0 and table[rdy+1][rdx] == 0):
					succ_list.append(str_i+"D")
			if(lux > 0 and ldx > 0):
				if(table[luy][lux-1] == 0 and table[ldy][ldx-1] == 0):
					succ_list.append(str_i+"L")
			if(rux < xbound and rdx < xbound):
				if(table[ruy][rux+1] == 0 and table[rdy][rdx+1] == 0):
					succ_list.append(str_i+"R")
		# 將上一步的反動作拿出
		if(self.last_inverse_op!='None'):
			succ_list.remove(self.last_inverse_op)
		return succ_list
	def move(self, operation):
		#移動方塊 operation 包含目標方塊及方向
		block = operation[:-1]
		direc = operation[-1]
		newnode = copy.deepcopy(self)
		block_loc = newnode.block_data[block]['loc']
		if(direc == 'U'):
			block_loc[0] -= 1
		if(direc == 'D'):
			block_loc[0] += 1
		if(direc == 'L'):
			block_loc[1] -= 1
		if(direc == 'R'):
			block_loc[1] += 1
		# 更新 table
		table = [[0 for i in range(shapex)] for j in range(shapey)]
		for i in range(1, table_max+1):
			locx, locy = newnode.block_data[str(i)]['loc']
			block_shapex, block_shapey = newnode.block_data[str(i)]['shape']
			table[locx][locy] = i
			table[locx+block_shapex-1][locy] = i
			table[locx][locy+block_shapey-1] = i
			table[locx+block_shapex-1][locy+block_shapey-1] = i
		newnode.table = table
		newnode.gn += 1
		return newnode
	def final_state(self):
		#判斷 final state
		return((id_table==self.table))

def IDA_STAR(root):
	bound = root.cal_fn()
	node_path = [root]
	table_path = [root.table]
	while True:
		#每次迭代開始前會檢查，如果以執行超過一小時，將會回傳無解
		if(round(time.time()-start)>3600):
			return 'NOT FOUND'
		cnt_max = 0
		count = 0
		t = search(node_path, table_path, 0, bound)
		if t == 'FOUND':
			return (node_path, table_path, bound)
		#IDA* f-limit 上限
		if t >= 1000:
			return 'NOT FOUND'
		bound = t

def search(node_path, table_path, g, bound):
	node = node_path[-1]
	fn = node.cal_fn()
	if(fn > bound):
		return fn
	if(node.final_state()):
		return 'FOUND'
	min_ = 1000
	succ = []
	for i in node.successor():
		newnode = node.move(i)
		newnode.last_inverse_op = i[:-1]+inverse[i[-1]]
		succ.append(newnode)
	# 對每個 succ 做搜索
	for i in succ:
		if(i.table not in table_path):
			node_path.append(i)
			table_path.append(i)
			t = search(node_path, table_path, g+1, bound)
			if(t == 'FOUND'):
				ans.append(i.last_inverse_op[:-1]+inverse[i.last_inverse_op[-1]])
				return 'FOUND'
			if(fn < min_):
				min_ = t
			node_path.pop()
			table_path.pop()
	#如果沒找到就 return 下一次的 f-limit
	return min_




def readfile():
	root = 'NONE'
	global table_max
	global shapey, shapex
	with open(r'C:\\input.txt') as f:
		#read table from txt input file
		a = f.readline().split()
		if(len(a)!=2):
			print('ERROR : WRONG INPUT')
			return
		else:
			shape = (int(a[0]), int(a[1]))
		table = []
		for line in f.readlines():
			row = []
			for element in line.split():
				table_max = max(int(element), table_max)
				row.append(int(element))
			if(len(row)!= shape[1]):
				print("ERROR : INPUT TABLE ERROR")	
				return False
			table.append(row)
		if(len(table)!= shape[0]):
			print("ERROR : INPUT TABLE ERROR")	
			return False
		if(table_max==0):
			print("ERROR : INPUT TABLE ERROR")	
			return False
		shapey, shapex = shape
		block_data = {}
		#read the block infomation from the table
		for i in range(shape[0]):
			for j in range(shape[1]) :
				element = table[i][j]
				if(element == 0):
					continue
				if(str(element) not in block_data):
					block_data[str(element)] = {"loc":[i, j], "shape":[1, 1]}
				else:
					block = block_data[str(element)]
					h = abs(block["loc"][0]-i)
					w = abs(block["loc"][1]-j)
					if(w == 1):
						if(h==1):
							continue
						if(block["shape"] == [1, 1]):
							block["shape"] = [1, 2]
					elif(h == 1):
						if(block["shape"] == [1, 1]):
							block["shape"] = [2, 1]
						elif(block["shape"] == [1, 2]):
							block["shape"] = [2, 2]
		root = node(table, block_data)
		return root

# cal ideal state(ideal table, ideal block_data)
def ideal(node):
	global id_table
	global id_block
	id_table = [[0 for i in range(shapex)] for j in range(shapey)]
	for i in range(1, table_max+1):
		#put the block into the table in block number order
		if(str(i) not in node.block_data):
			return None
		block_shape = node.block_data[str(i)]["shape"]
		skip = 0
		#find the left up most space to place block
		for j in range(shapey):
			if(skip):
				break
			for k in range(shapex):
				if(skip):
					break
				if(id_table[j][k] == 0):#check if that space is empty
					if( j+block_shape[0]-1<shapey and k+block_shape[1]-1<shapex
								and id_table[j+block_shape[0]-1][k] == 0 
								and id_table[j][k+block_shape[1]-1] == 0 
								and id_table[j+block_shape[0]-1][k+block_shape[1]-1] == 0):
						#check if that place can place that block
						id_table[j][k] = i
						id_table[j+block_shape[0]-1][k] = i
						id_table[j][k+block_shape[1]-1] = i
						id_table[j+block_shape[0]-1][k+block_shape[1]-1] = i
						id_block[str(i)] = [j, k]
						skip = 1
						# if a new block have been placed, then skip to next block 
					else:
						return None
						# if block can't be fit in order means no solution
	return True

def main():
	global start
	#read the file and setting the root node's information
	root = readfile()
	#setup the file output
	fdo = open(r'C:\\output.txt', 'w')
	# if having ideal state
	if(ideal(root)):
		pass
	else:
		print('no solution')
		print('no solution', file=fdo)
		return
	if(root):
		start = time.time()
		if(IDA_STAR(root)!='NOT FOUND'):
			end = time.time()
			total_step = len(ans)
			#print the answer to the terminal and the output txt
			print('Total run time = {} seconds.'.format(round(end-start, 3)))
			print('An optimal solution has {} moves:'.format(total_step))
			print('Total run time = {} seconds.'.format(round(end-start, 3)), file=fdo)
			print('An optimal solution has {} moves:'.format(total_step), file=fdo)
			for i in ans[::-1]:
				print(i, end=' ')
				print(i, end=' ', file=fdo)
			print('')
			print('', file=fdo)
		else:
			print('no solution')
			print('no solution', file=fdo)
	else:
		print('no solution')
		print('no solution', file=fdo)
main()
input('Press Enter to continue...')