/*
	Quantize colors
	
	Wojciech Mu³a

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
// wo³ana z: -
// opis    : funkcja dokonuje kwantyzacji kolorów
// wej¶cie : image24bpp - wska¼nik na obraz true color
//           image8bpp  - wska¼nik na obraz 8bpp (wyj¶ciowy)
//           palette    - paleta kolorów
//           count      - ilo¶æ pikseli
//           colors     - liczba wymagana liczna kolorów (2..256)
//           sort_by    - kolejno¶æ dzielenia kostek; najpierw kostki...
//                        0 - ... zawieraj±ce najwiêcej pikseli
//                        1 - ... zawieraj±ce najwiêcej kolorów (najlepsze efekty)
//                        2 - ... o najwiêkszej objêto¶ci       (najgorsze efekty)
//           verbose    - gdy równe 1 na standardowe wyj¶cie 
//                        wypisywane s± komunikaty
//
// wyj¶cie : zero       - bez b³êdów
//           niezerowe  - wyst±pi³ b³±d (errno ustawione)
int quantize_colors(RGBpixel* image24bpp, byte* image8bpp, RGBpixel palette[256], int count, int colors, int sort_by, char verbose=0);

#endif
