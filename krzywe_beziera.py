# -*- coding: iso-8859-2 -*-
# 
# Program rysuje dowoln� liczb� krzywych Beziera dowolnego stopnia.
# Do uruchomienia wymaga biblioteki PIL (Python Imaging Library).

newton_cache = {} # pami�� podr�czna dla wynik�w funkcji newton
def Newton(n,k):
     '''Funkcja oblicza warto�� symbolu Newtona'''
     global newton_cache
     if (n,k) not in newton_cache:
         # licznik = n*(n-1)*...*(n-k+1)
         licznik = 1
         for i in xrange(n-k+1, n+1):
             licznik *= i

         # mianownik = k!
         mianownik = 1
         for i in xrange(1, k+1):
             mianownik *= i

         newton_cache[(n,k)] = licznik/mianownik
     
     return newton_cache[(n,k)]

def B(n,i,t):
     '''
     Funkcja oblicza warto�� wielomianu bazowego Brensteina dla
     zadanego parametru t.
     '''
     return Newton(n,i) * (t**i) * (1.0-t)**(n-i)

def Bezier2D(punkty_kontrolne, k):
     '''
     Funkcja przybli�a dwuwymiarow� krzyw� Beziera za pomoc� �amanej
     z�o�onej z k segment�w. Zwraca list� wierzcho�k�w �amanej.
     
     punkty_kontrolne - lista punkt�w kontrolnych: [(x0,y0), ..., (xn,yn)]
     k                - ilo�� segment�w
     '''

     n  = len(punkty_kontrolne)-1 # stopie� krzywej Beziera

     # funkcja obliczaj�ca wsp�rz�dne (x,y) punktu krzywej dla zadanego t
     def p(t):
         '''
         x = \sum_{i=0}^n x_i B^n_i(t)
         y = \sum_{i=0}^n y_i B^n_i(t)
         '''
         x = 0.0
         y = 0.0
         for i in xrange(n+1):
             x += punkty_kontrolne[i][0]*B(n,i,t)
             y += punkty_kontrolne[i][1]*B(n,i,t)
         return (x,y)
     
     dt = 1.0/k # krok parametru t
     return [p(i*dt) for i in xrange(k+1)]

# program g��wny
if __name__ == '__main__':
     import Image
     import ImageDraw

     # parametry programu
     n = 5              # liczba punkt�w kontrolnych (stopie� krzywej+1)
     
     rozdzielczosc = 600 # rozdzielczo�� obraz�w
     k = 200             # liczba segment�w �amanej przybli�aj�cej krzyw�
     l = 50              # liczba obraz�w generowanych przy jednym
                         # uruchomieniu programu
     
     image = Image.new("RGB", (rozdzielczosc, rozdzielczosc))
     draw  = ImageDraw.Draw(image)
     from random import randint as R

     for i in xrange(l):
         print "Tworzenie krzywej %d z %d" % (i+1, l)
         # 1. Wylosowanie n punkt�w kontrolnych
         #    (oczywi�cie mo�na je wpisa� r�cznie, do czego zach�camy)
         punkty_kontrolne = [(R(0,rozdzielczosc), R(0,rozdzielczosc)) for _ in xrange(n)]

         # 2. Wyznaczenie �amanej p przyli�aj�c� krzyw� Beziera
         p = Bezier2D(punkty_kontrolne, k)

         # 3. Rysowanie krzywej:
         # 3a. wyczyszczenie obrazu (kolorem bia�ym)
         draw.rectangle( [0,0, rozdzielczosc,rozdzielczosc], fill="#fff")

         # 3b. rysowanie �amanej kontrolnej (w kolorze jasnoszarym)
         draw.line(punkty_kontrolne, fill="#ccc")

         # 3c. zaznaczenie niebieskimi k�kami punkt�w kontrolnych
         r = 2 # promie�
         for (x,y) in punkty_kontrolne:
             draw.ellipse([x-r,y-r, x+r,y+r], fill="#00f")

         # 3d. rysowanie krzywej Beziera (w kolorze czerownym)
         draw.line(p, fill="#f00")

         # 4. Zapisanie obrazu do pliku
         image.save("Krzywa-Beziera_%03d_%04d.png" % (n,i), "PNG")
