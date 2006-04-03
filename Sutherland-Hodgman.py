# -*- coding: iso-8859-2 -*-

def Sutherland_Hodgman2D(poly1, poly2):
	'''
	Funkcja obcina algorytmem Sutherladna-Hodgmana wielok�t
	'poly1' przez wielok�t obcinaj�cy 'poly2'. Wielok�t obcinaj�cy
	musi by� wypu�y, inaczej algorytm zawiedzie, a punkty s� podane
	w kolejno�ci przeciwnej do wskaz�wek zegara.
	
	Wielok�ty s� dane jako lista par wsp�rz�dnych, tzn.
	[(x0,y0), (x1,y1), ..., (xn,yn)], taki te� jest format
	zwracanego wyniku.
	'''
	assert len(poly1) > 0 and len(poly2) > 0

	poly = poly1[:]
	n = len(poly2)
	for i in xrange(n):
		C = poly2[i]
		D = poly2[(i+1) % n]
		poly = Clip(poly, C,D)

	return poly

def Clip(poly, C,D):
	'''
	Funkcja obcina wielok�t 'poly' przez prost� dan� r�wnaniem parametrycznym
	p(t) = C+t(D-C), zwraca wielok�t�w b�d�cych wynikiem obci�cia.
	'''

	if len(poly) == 0:
		return []

	# przej�cie z r�wnania parametrycznego prostej na ax+by+c=0
	a = D[1]-C[1]
	b = C[0]-D[0]
	c = -(a*C[0] + b*C[1])

	W = []		# wynikowy wielok�t
	n = len(poly)
	
	S = poly[0]
	S_inside = (a*S[0] + b*S[1] + c) >= 0.0
	for i in xrange(0,n):
		N = poly[(i+1) % n]
		N_inside = (a*N[0] + b*N[1] + c) >= 0.0

		# 1. oba wierzcho�ki wewn�trz: dodanie N (przypadek 1)
		if S_inside and N_inside:
			W.append(N)

		# 2. oba wierzcho�ki na zewn�trz: nic nie robimy (przypadek 2)
		elif not (S_inside or N_inside):
			pass

		# 3. odcinek przecina prost�:
		else:
			p = Intersection(S,N, C,D)
			assert p != None
			# 3a. wektor "wychodz�cy", dodawny tylko punkt przeci�cia (przypadek 3)
			if   S_inside and not N_inside:
				W.append(p)
			# 3b. wektor "wchodz�cy", dodawany punkt przeci�cia p oraz N (przypadek 4)
			elif not S_inside and N_inside:
				W.append(p)
				W.append(N)

		S, S_inside = N, N_inside
		
	return W

def Intersection(A,B, C,D):
	'''
	Funkcja sprawdza czy odcinek A,B przecina prost� opisan� r�wnaniem
	parametrycznym p(t)=C+v*(D-C). Zwraca wsp�rz�dne przeci�cie, albo
	None, je�li odcinek nie przecina prostej.
	'''

	xa,ya = map(float, A)
	xb,yb = map(float, B)
	xc,yc = map(float, C)
	xd,yd = map(float, D)

	# rozwi�zanie uk�adu r�wna�:
	#  xa + u(xb-xa) = xc + v(xd-xc)
	#  ya + u(yb-ya) = yc + v(yd-yc)
	#  u \in [0,1]
	#  v \in (-\infty, +\infty)

	#  potrzeba wyznaczy� tylko parametr u

	detA = (xb-xa)*(yc-yd) - (xc-xd)*(yb-ya)
	if abs(detA) < 1e-8: # detA ~= 0.0 - odcinek jest r�wnoleg�y do prostej
		return None
	
	detAu = (xc-xa)*(yc-yd) - (xc-xd)*(yc-ya)
	u = detAu/detA
	if 0.0 <= u <= 1.0: # punkt przeci�cia le�y na odcinku
		return (xa+u*(xb-xa), ya+u*(yb-ya))
	else:
		return None

if __name__ == '__main__':
	import Image
	import ImageDraw

	# wielok�ty:
	# * du�a litera 'W', kt�ra b�dzie obcinana
	W1 = [(0, 0), (675, 4050), (1575, 4050), (2025, 2475), (2475, 4050), (3375, 4050), (4050, 0), (3375, 0), (2925, 3150), (2475, 1800), (1575, 1800), (1125, 3375), (675, 0)]
	# * wielok�t obcinaj�cy (pi�ciok�t wypu�y)
	W2 = [(450, 675), (-225, 2250), (1800, 4050), (3825, 3150), (3150, 225)]

	def poly_minmax(poly):
		'''
		Funkcja zwraca minimalne, maksymalne wsp�rz�dne oraz �rodek
		wielok�ta
		'''
		x = [x for (x,_) in poly]
		y = [y for (_,y) in poly]
		cx = (max(x)+min(x))/2.0
		cy = (max(y)+min(y))/2.0
		return (min(x),min(y), max(x),max(y), cx,cy)

	def poly_trans(poly, dx=0.0,dy=0.0, scale=1.0, angle=0.0, cx=0.0, cy=0.0):
		'''
		Funkcja przekszta�ca wielok�t 'poly':
		* skaluje ze wsp�czynnikiem 'scale'
		* obraca o k�t 'angle' (w stopniach) wok� punktu (cx,cy)
		* przesuwa o wektor (dx,dy)
		'''
		
		from math import sin,cos,pi
		s = sin(pi*angle/180.0)
		c = cos(pi*angle/180.0)
		if angle == 0.0:
			for i, (x,y) in enumerate(poly):
				poly[i] = (x*scale + dx, y*scale + dy)
		else:
			for i, (x,y) in enumerate(poly):
				x -= cx
				y -= cy
				xr = (x*c - y*s) + cx
				yr = (x*s + y*c) + cy
				poly[i] = (xr*scale + dx, yr*scale + dy)
		return poly

	# przeskalowanie (i ewentalnie inne operacje)
	scale = 1/20.0
	W1 = poly_trans(W1, scale=scale)
	W2 = poly_trans(W2, scale=scale)

	# wyznaczenie rozmiaru obrazka
	margines = 10 # margines wok�
	minx,miny,maxx,maxy,_,_ = poly_minmax(W1+W2)
	dx = -minx+margines
	dy = -miny+margines

	# przysuni�cie wielok�t�w do brzegu
	W1 = poly_trans(W1, dx=dx,dy=dy)
	W2 = poly_trans(W2, dx=dx,dy=dy)

	# wyznaczenie rozdzielczo�ci
	rozdzielczosc_x = int(maxx-minx)+2*margines
	rozdzielczosc_y = int(maxy-miny)+2*margines

	image = Image.new("RGB", (rozdzielczosc_x, rozdzielczosc_y))
	draw  = ImageDraw.Draw(image)

	# 1. Narysowanie pocz�tkowej sytuacji
	draw.rectangle([0,0,rozdzielczosc_x,rozdzielczosc_y], fill="#fff")
	draw.polygon(W1, outline="#000", fill="#bbb")
	draw.polygon(W2, outline="#f00")
	image.save('Sutherland-Hodgman-000.bmp', 'BMP')
	
	# 2. Rysowanie kolejnych krok�w algorymtu (to dok�adnie ta sama p�tla
	#    co w funkcji Sutherland_Hodgman(), z tym, �e tutaj jeszcze s�
	#    rysowane r�ne rzeczy)
	n = len(W2)
	for i in xrange(n):
		# obci�cie przez prost�
		W1 = Clip(W1, W2[i], W2[(i+1) % n])

		# wyczyszczenie ekranu
		draw.rectangle([0,0,rozdzielczosc_x,rozdzielczosc_y], fill="#fff")

		# narysowanie obci�tego wielok�ta
		if len(W1):
			draw.polygon(W1, outline="#000", fill="#bbb")
		draw.polygon(W2, outline="#f00")

		# narysowanie prostej (wyd�u�enie odcinka)
		xa,ya = W2[i]
		xb,yb = W2[(i+1) % n]
		t     = 1000.0
		draw.line([xa+t*(xb-xa),ya+t*(yb-ya),xa-t*(xb-xa),ya-t*(yb-ya)], fill="#00f")

		# zapisane obrazka
		image.save('Sutherland-Hodgman-%03d.bmp' % (i+1), 'BMP')

	# 3. Ostateczny wynik obcinania
	draw.rectangle([0,0,rozdzielczosc_x,rozdzielczosc_y], fill="#fff")
	if len(W1):
		draw.polygon(W1, outline="#000", fill="#bbb")
	image.save('Sutherland-Hodgman-%03d.bmp' % (n+1), 'BMP')
#
