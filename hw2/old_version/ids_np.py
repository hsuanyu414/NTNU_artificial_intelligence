import numpy as np
import time
import pprint
import copy
import os
import psutil
import matplotlib.pyplot as plt


pid = os.getpid()
py = psutil.Process(pid)
ans = []
step = []
time_rec = []
mem_rec = []
visited = set()
mem = 0
id_table = []
id_block = {}
recorded = 0
table_max = 0
inverse = {"U":"D", "D":"U", "L":"R", "R":"L"}
class node:
	# 建構式
	def __init__(self, table, block_data):
		self.table = table
		self.last_inverse_op = 'None'
		self.block_data = block_data
		#node 視為一個 state，紀錄當前狀態的盤面，最大的方塊編號，上一步的動作，盤面中所有方塊的資訊
	def successor(self):
		#尋找當前 node 可以展開的動作，回傳動作的 list
		succ_list = []
		for i in range (1, table_max+1):# for every block
			str_i = str(i)
			table = self.table
			ybound, xbound = table.shape[0]-1, table.shape[1]-1
			shapey, shapex = self.block_data[str_i]['shape']
			luy, lux = self.block_data[str_i]['loc']
			# ruy, rux = loc[1]
			# ldy, ldx = loc[2]
			# rdy, rdx = loc[3]
			
			ruy, rux = luy, lux+shapex-1
			ldy, ldx = luy+shapey-1, lux
			rdy, rdx = luy+shapey-1, lux+shapex-1
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
		table = np.zeros(self.table.shape, dtype=int)
		for i in range(1, table_max+1):
			locx, locy = newnode.block_data[str(i)]['loc']
			shapex, shapey = newnode.block_data[str(i)]['shape']
			table[locx][locy] = i
			table[locx+shapex-1][locy] = i
			table[locx][locy+shapey-1] = i
			table[locx+shapex-1][locy+shapey-1] = i

		newnode.table = table
		return newnode
	def final_state(self):
		#判斷 final state
		return((id_table==self.table).all())

def IDDFS(node, max_depth):
	global visited
	global recorded
	for depth in range(max_depth):
		recorded = 0
		if(DFS(node, depth)):
			time_rec.append(round(time.time()-start, 3))
			return True
		# time_rec.append(round(time.time()-start, 3))
		# mem_rec.append(mem-base)
		# print('Total run time = {} seconds.'.format(round(time.time()-start, 3)))
		# print('Total memory usage = {} KBs'.format(mem-base))
		
	return False

def DFS(node, limit):
	global visited
	global mem
	global recorded
	# mem = psutil.Process().memory_info().rss/2.**10
	if(node.final_state()):
		return True
	if(limit <= 0):
		return False
	for i in node.successor():
		newnode = node.move(i)
		newnode.last_inverse_op = i[:-1]+inverse[i[-1]]
		h = str(list(newnode.table.flatten()))
		if(h in visited):
			continue
		visited.add(h)
		if(DFS(newnode, limit-1)):
			ans.append(i)
			# step.append(newnode.table)
			return True
		visited.remove(h)
	return False




def readfile(inputfile):
	root = 'NONE'
	global table_max
	with open(inputfile) as f:
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
				row.append(int(element))
			table.append(row)
		table = np.array(table)
		if(table.shape!=shape):
			print("ERROR : INPUT TABLE ERROR")
			return
		block_data = {}
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
		table_max = table.max()
		return root

def ideal(node):
	# cal ideal state
	global id_table
	global id_block
	shape = node.table.shape
	id_table = np.zeros(node.table.shape, dtype = np.int32)
	for i in range(1, table_max+1):
		block_shape = node.block_data[str(i)]["shape"]
		skip = 0
		for j in range(shape[0]):
			if(skip):
				break
			for k in range(shape[1]):
				if(skip):
					break
				if(id_table[j][k] == 0):
					if( j+block_shape[0]-1<shape[0] and k+block_shape[1]-1<shape[1]
								and id_table[j+block_shape[0]-1][k] == 0 
								and id_table[j][k+block_shape[1]-1] == 0 
								and id_table[j+block_shape[0]-1][k+block_shape[1]-1] == 0):
						id_table[j][k] = i
						id_table[j+block_shape[0]-1][k] = i
						id_table[j][k+block_shape[1]-1] = i
						id_table[j+block_shape[0]-1][k+block_shape[1]-1] = i
						skip = 1
					else:
						return None
	return True

# filename = input('Please enter the file name: ')
filename = '3x3_12.txt'
root = readfile(filename)
# if having ideal state
if(ideal(root)):
	pass
else:
	print('No answer')
if(root):
	visited.add(str(list(root.table.flatten())))
	start = time.time()
	# base = psutil.Process().memory_info().rss/2.**10
	if(IDDFS(root, 100)):
		end = time.time()

		total_step = len(ans)
		print('Total run time = {} seconds.'.format(round(end-start, 3)))
		print('An optimal solution has {} moves:'.format(total_step))
		for i in ans[::-1]:
			print(i, end=' ')
		print('')
	else:
		print('No answer')

	# pprint.pprint(root.table)
	# for i in range (total_step):
	# 	print(ans[total_step-i-1])
	# 	print('===========')
	# 	pprint.pprint(step[total_step-i-1])
	# 	print('===========')

	# plt.plot(range(len(ans)), mem_rec)
	# plt.show()
else:
	print('No answer')