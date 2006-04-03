# -*- coding: iso-8859-2 -*-

def Cohen_Sutherland(xa,ya, xb,yb, x_min,x_max,y_min,y_max):
	'''
	Funkcja obcina odcinek algorytmem Cohena-Sutherlanda
	
	xa,ya, xb,yb - współrzędne końców odcinka
	x_min, x_max, y_min, y_max - granice prostokąta
	'''

	def code(x,y):
		'''
		Funkcja wyznacza kod 4-bitowy dla podanego punktu
		'''
		b0 = int(y > y_max)
		b1 = int(y < y_min) << 1
		b2 = int(x > x_max) << 2
		b3 = int(x < x_min) << 3
		return b0 | b1 | b2 | b3
	
	def top(code):    return (code & 0x01) != 0
	def bottom(code): return (code & 0x02) != 0
	def left(code):   return (code & 0x04) != 0
	def right(code):  return (code & 0x08) != 0
	
	code_a = code(xa,ya)
	code_b = code(xb,yb)
	while True:
		# 1. Sprawdzenie, czy odcinek w całości znajduje się w
		#    prostokącie obcinającym - jeśli tak, zwracane są jego współrzędne.
		if code_a == 0 and code_b == 0:
			return ((xa,ya), (xb,yb))
	
		# 2. Sprawdzenie, czy odcinek w całości znajduje się poza
		#    prostokątem obcinającym - jeśli tak jest funkcja kończy się.
		if (code_a & code_b) != 0:
			return None
	
		# 3. Wybranie punktu (a właściwie kodu punktu), który
		#    znajduje się poza prostokątem
		if code_a != 0:
			code_o = code_a
		else:
			code_o = code_b

		# 5. Obcianie:
		# 5a. przez prostą y=y_max
		if top(code_o):
			t = (y_max-ya)/float(yb-ya)
			x = xa + t*(xb-xa)
			y = y_max
		# 5b. przez prostą y=y_min
		elif bottom(code_o):
			t = (y_min-ya)/float(yb-ya)
			x = xa + t*(xb-xa)
			y = y_min
		# 5c. przez prostą x=x_max
		elif left(code_o):
			x = x_max
			t = (x_max-xa)/float(xb-xa)
			y = ya + t*(yb-ya)
		# 5d. przez prostą x=x_min
		elif right(code_o):
			x = x_min
			t = (x_min-xa)/float(xb-xa)
			y = ya + t*(yb-ya)

		# 6. Odrzucenie punktu, który znajduje się poza prostokątem
		#    (tego, który w 3. kroku został wybrany) i zastąpienie
		#    go punktem przecięcia.
		if code_o == code_a:
			xa = x
			ya = y
			code_a = code(x,y)
		else:
			xb = x
			yb = y
			code_b = code(x,y)

if __name__ == '__main__':
	import Image
	import ImageDraw
	from random import randint

	rozdzielczosc = r = 500 # rozdzielczość obrazka
	image = Image.new("RGB", (rozdzielczosc, rozdzielczosc))
	draw  = ImageDraw.Draw(image)

	# Granice prostokąta obcinającego
	y_min = 130
	y_max = 370
	x_min = 50
	x_max = 450

	# Współrzędne odcinka (losowe)
	xa = randint(0,rozdzielczosc)
	ya = randint(0,rozdzielczosc)
	xb = randint(0,rozdzielczosc)
	yb = randint(0,rozdzielczosc)

	# Obcięcie alg. Cohena-Sutherlanda - zmienna 'obciety_odcinek' zawiera albo
	# współrzędne obciętego odcinka, albo None, gdy odcinek znajdował się
	# poza prostokątem obcinającym
	obciety_odcinek = Cohen_Sutherland(xa,ya, xb,yb, x_min,x_max, y_min,y_max)

	# Rysowanie:
	draw.rectangle([0,0,r,r], fill="#fff")
	# * prostych y=y_min, y=y_max, x=x_min, x=x_max
	draw.line([0,y_min, r,y_min], fill="#aaa")
	draw.line([0,y_max, r,y_max], fill="#aaa")
	draw.line([x_min,0, x_min,r], fill="#aaa")
	draw.line([x_max,0, x_max,r], fill="#aaa")

	# * prostokąta obcinającego wyznaczonego przez te proste
	draw.rectangle([x_min,y_min,x_max,y_max], outline="#000")
	
	# * obcinanego odcinka
	draw.line([xa,ya,xb,yb], fill="#0f0")

	# * jeśli istnieje, obciętego odcinka
	if obciety_odcinek:
		draw.line(obciety_odcinek, fill="#f00", width=2)

	# Zapisanie obrazka
	image.save('Cohen_Sutherland.png', 'PNG')
#
