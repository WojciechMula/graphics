# -*- coding: iso-8859-2 -*-
# 
# Program rysuje dowolną liczbę krzywych Beziera dowolnego stopnia.
# Do uruchomienia wymaga biblioteki PIL (Python Imaging Library).

newton_cache = {} # pamięć podręczna dla wyników funkcji newton
def Newton(n,k):
     '''Funkcja oblicza wartość symbolu Newtona'''
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
     Funkcja oblicza wartość wielomianu bazowego Brensteina dla
     zadanego parametru t.
     '''
     return Newton(n,i) * (t**i) * (1.0-t)**(n-i)

def Bezier2D(punkty_kontrolne, k):
     '''
     Funkcja przybliża dwuwymiarową krzywą Beziera za pomocą łamanej
     złożonej z k segmentów. Zwraca listę wierzchołków łamanej.
     
     punkty_kontrolne - lista punktów kontrolnych: [(x0,y0), ..., (xn,yn)]
     k                - ilość segmentów
     '''

     n  = len(punkty_kontrolne)-1 # stopień krzywej Beziera

     # funkcja obliczająca współrzędne (x,y) punktu krzywej dla zadanego t
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

# program główny
if __name__ == '__main__':
     import Image
     import ImageDraw

     # parametry programu
     n = 5              # liczba punktów kontrolnych (stopień krzywej+1)
     
     rozdzielczosc = 600 # rozdzielczość obrazów
     k = 200             # liczba segmentów łamanej przybliżającej krzywą
     l = 50              # liczba obrazów generowanych przy jednym
                         # uruchomieniu programu
     
     image = Image.new("RGB", (rozdzielczosc, rozdzielczosc))
     draw  = ImageDraw.Draw(image)
     from random import randint as R

     for i in xrange(l):
         print "Tworzenie krzywej %d z %d" % (i+1, l)
         # 1. Wylosowanie n punktów kontrolnych
         #    (oczywiście można je wpisać ręcznie, do czego zachęcamy)
         punkty_kontrolne = [(R(0,rozdzielczosc), R(0,rozdzielczosc)) for _ in xrange(n)]

         # 2. Wyznaczenie łamanej p przyliżającą krzywą Beziera
         p = Bezier2D(punkty_kontrolne, k)

         # 3. Rysowanie krzywej:
         # 3a. wyczyszczenie obrazu (kolorem białym)
         draw.rectangle( [0,0, rozdzielczosc,rozdzielczosc], fill="#fff")

         # 3b. rysowanie łamanej kontrolnej (w kolorze jasnoszarym)
         draw.line(punkty_kontrolne, fill="#ccc")

         # 3c. zaznaczenie niebieskimi kółkami punktów kontrolnych
         r = 2 # promień
         for (x,y) in punkty_kontrolne:
             draw.ellipse([x-r,y-r, x+r,y+r], fill="#00f")

         # 3d. rysowanie krzywej Beziera (w kolorze czerownym)
         draw.line(p, fill="#f00")

         # 4. Zapisanie obrazu do pliku
         image.save("Krzywa-Beziera_%03d_%04d.png" % (n,i), "PNG")
