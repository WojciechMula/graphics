/*
	Quantize colors
	
	Wojciech Mu�a

	28.10.2002
	29.10.2002
	30.10.2002
	 1.11.2002
	 2.11.2002
	 4.11.2002
*/

#ifndef __quantize_h_included__
#define __quantize_h_included__

typedef unsigned char byte;
// fizyczna reprezentacja pikseli w obrazie
typedef struct {byte r,g,b;} __attribute__ ((packed)) RGBpixel;

// funkcja : quantize colors
// wo�ana z: -
// opis    : funkcja dokonuje kwantyzacji kolor�w
// wej�cie : image24bpp - wska�nik na obraz true color
//           image8bpp  - wska�nik na obraz 8bpp (wyj�ciowy)
//           palette    - paleta kolor�w
//           count      - ilo�� pikseli
//           colors     - liczba wymagana liczna kolor�w (2..256)
//           sort_by    - kolejno�� dzielenia kostek; najpierw kostki...
//                        0 - ... zawieraj�ce najwi�cej pikseli
//                        1 - ... zawieraj�ce najwi�cej kolor�w (najlepsze efekty)
//                        2 - ... o najwi�kszej obj�to�ci       (najgorsze efekty)
//           verbose    - gdy r�wne 1 na standardowe wyj�cie 
//                        wypisywane s� komunikaty
//
// wyj�cie : zero       - bez b��d�w
//           niezerowe  - wyst�pi� b��d (errno ustawione)
int quantize_colors(RGBpixel* image24bpp, byte* image8bpp, RGBpixel palette[256], int count, int colors, int sort_by, char verbose=0);

#endif
