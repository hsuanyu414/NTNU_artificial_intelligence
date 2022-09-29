import math

while(1):
	input_ = (input().split())	
	a, b, c, d = input_
	a = int(a)
	b = int(b)
	c = int(c)
	d = int(d)
	A = a/b
	B = c/d
	a = A
	b = B
	print(-a*math.log(a, 2)-b*math.log(b, 2))