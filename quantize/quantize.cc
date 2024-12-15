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

#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <assert.h>
#include "quantize.h"

void error(const char* s, int err) {puts(s); errno=err;}

typedef unsigned int  dword;

// opis piksela w przestrzeni RGB
typedef struct {
                union { struct {byte r,g,b,_;}; // ARGB
			int    d; };            // 
		int  count; // liczba wyst±pieñ piksela w obrazie
	       } pixel;
	       
// opis kostki w przestrzeni RGB
typedef struct {
	  struct { int r,g,b; } min; // naprzeciwleg³e
	  struct { int r,g,b; } max; // wierzcho³ki
	  int    size;   // liczba kolorów
	  int    pixels; // liczba pikseli
	  pixel *data;   // lista pikseli
	} RGB_subspace;
	
/*** dane globalne (w module) *************************************************/
extern int errno;

static RGBpixel *image24bpp;  // obraz wej¶ciowy
static int      count;        // liczba pikseli w obrazie
static byte     *image8bpp;   // obraz wynikowy
static char     verbose;      // wypisuj na standardowe wyj¶cie wszystko

static RGB_subspace list[256];// lista kostek RGB

/*** prototypy fukcji lokalnych *********************************************************/

// funkcja : build_cube4image
// wo³ana z: quantize_colors
// opis    : funkcja tworzy kostkê dla obrazu; kostka zapisywana 
//           jest w pierwszym elemencie list (list[0])
// wej¶cie : brak (u¿ywane zmienne globalne)
// wyj¶cie : zero       - bez b³êdów
//           niezerowe  - wyst±pi³ b³±d (errno ustawione)
int build_cube4image();

// funkcja : split_RGB_subspace
// wo³ana z: quantize_colors
// opis    : funkcja dzieli na dwie czê¶ci kostkê
// wej¶cie : src        - dzielona kostka
//           A,B        - dwie czê¶ci kostki
// wyj¶cie : zero       - bez b³êdów
//           niezerowe  - wyst±pi³ b³±d (errno ustawione)
int split_RGB_subspace(RGB_subspace src, RGB_subspace& A, RGB_subspace& B);

// funkcja : sort
// wo³ana z: build_cube4image
// opis    : sortuje piksele
// wej¶cie : standardowe parametry algorytmu quick-sort
// wyj¶cie : brak
void sort(pixel* list, int first, int last);

// funkcja : findbest_by_xxxxx
// wo³ana z: quantize_colors
// opis    : szuka kostki:
//           * colorscount - zawieraj±cej najwiêcej kolorów
//           * pixelcount  - zawieraj±cej najwiêcej pikseli
//           * cubevolume  - o najwiêkszej objêto¶ci
// wej¶cie : list_size - rozmiar listy (szuka w indeksach od 0 do list_size-1)
// wyj¶cie : indeks kostki
int findbest_by_colorcount(int list_size);
int findbest_by_pixelcount(int list_size);
int findbest_by_cubevolume(int list_size);

/*** implementacje ************************************************************/

int quantize_colors(RGBpixel* image24bpp, byte* image8bpp, RGBpixel palette[256], int count, int colors, int sort_by, char verbose)
{
 int (*findbest)(int);
 errno = 0;
 if (colors < 2 || colors > 256)
 	{ error("number of colors must lie in range 2 to 256", EINVAL);
	  return 1; }
 if (image24bpp == NULL)
 	{ error("input image is empty", ENXIO);
	  return 1; }
 if (image8bpp == NULL)
 	{ error("output image is empty", ENXIO);
	  return 1; }
 if (count == 0)
 	{ error("input image is empty", EINVAL);
	  return 1; }
	  
 switch (sort_by)
 	{
 	 case 0: findbest = findbest_by_colorcount; break;
 	 case 1: findbest = findbest_by_pixelcount; break;
 	 case 2: findbest = findbest_by_cubevolume; break;
	 default: error("bad argument; sort_by can be 0, 1 or 2", EINVAL);
	          return 1;
	}

 // w obrazie nie ma wiêcej pikseli ni¿ kolorów, wiêc mo¿na bezpo¶rednio
 // przepisaæ kolory z obrazu 24bpp do palety
 if (count <= colors)
 	{
	 for (int i=0; i<count; i++)
	 	{
	 	 palette[i]    = image24bpp[i];
		 image8bpp[i]  = i;
		}
	 return 0;
	}
	
 ::image24bpp = image24bpp;
 ::image8bpp  = image8bpp;
 ::count      = count;
 ::verbose    = verbose;

 if (build_cube4image()) return 1;
 
/* if (list[0].size <= colors)
 	{
	 error("sorry, not implemented yet", ENOSYS);
	 return 1;
	}
 else*/
 	{
	 int list_size = 1;
	 while (list_size < colors)
	 	{
		 RGB_subspace A,B;
		 int best = findbest(list_size);
	 	 if (verbose)
		 	{
			 printf("quantizing... %3d%%\r", (list_size*100)/colors);
			 fflush(stdout);
			}

		 split_RGB_subspace(list[best], A, B);
		 free(list[best].data);

		 list[best]        = A;
		 list[list_size++] = B;
		}
	 if (verbose) puts("quantizing... done ");
	}

 static unsigned char R[256][256];
 static unsigned char G[256][256];
 static unsigned char B[256][256];
 static int mR[256];
 static int mG[256];
 static int mB[256];
 
 for (int i=0; i<256; i++) mR[i]=mG[i]=mB[i] = 0;
 
 for (int i=0; i<256; i++)
	 for (int j=0; j<256; j++)
	 	{
	 	 if (j >= list[i].min.r && j <= list[i].max.r)
			 R[j][mR[j]++] = i;
	 	 if (j >= list[i].min.g && j <= list[i].max.g)
			 G[j][mG[j]++] = i;
	 	 if (j >= list[i].min.b && j <= list[i].max.b)
			 B[j][mB[j]++] = i;
		}
		
 for (int i=0; i<count; i++)
 	{
	 if (verbose)
	 	{
		 if (i % 1024 == 0)
		 	{
		 	 printf("aquiring indexes... %3d%%\r", (i*100)/count);
		 	 fflush(stdout); }
		}
	 byte r = image24bpp[i].r;
	 byte g = image24bpp[i].g;
	 byte b = image24bpp[i].b;
	 
	 int  ir=0, ib=0, ig=0;
	 int  m;
	 
	 while (R[r][ir] != G[g][ig] || R[r][ir] != B[b][ib])
	 	{
		 m = G[g][ig];
		 if (R[r][ir] > m) m = R[r][ir];
		 if (B[b][ib] > m) m = B[b][ib];
		 
		 while (R[r][ir] < m && ir < mR[r])
		 	ir++;
		 while (G[g][ig] < m && ig < mG[g])
		 	ig++;
		 while (B[b][ib] < m && ib < mB[b])
		 	ib++;
		}
	 image8bpp[i] = R[r][ir];
	}
/* int i,j;
 for (i=0; i<count; i++)
 	{
	 if (verbose)
	 	{
		 if (i % 1024 == 0)
		 	{
		 	 printf("aquiring indexes... %3d%%\r", (i*100)/count);
		 	 fflush(stdout); }
		}
	 for (j=0; j<256; j++)
	 	{
		 if (image24bpp[i].r < list[j].min.r) continue;
		 if (image24bpp[i].g < list[j].min.g) continue;
		 if (image24bpp[i].b < list[j].min.b) continue;

		 if (image24bpp[i].r > list[j].max.r) continue;
		 if (image24bpp[i].g > list[j].max.g) continue;
		 if (image24bpp[i].b > list[j].max.b) continue;
		 image8bpp[i] = j;
		 break;
		}
	 assert(j < 256);
	}*/
 if (verbose)
 	puts("aquiring indexes... done ");

 if (verbose) {printf("building color palette... "); fflush(stdout); }
 for (int i=0; i<256; i++)
 	{
	 int r=0, g=0, b=0;

	 for (int j=0; j<list[i].size; j++)
	 	{
		 r += list[i].data[j].r * list[i].data[j].count;
		 g += list[i].data[j].g * list[i].data[j].count;
		 b += list[i].data[j].b * list[i].data[j].count;
		}
	 assert(list[i].pixels > 0);

	 palette[i].r = r/list[i].pixels;
	 palette[i].g = g/list[i].pixels;
	 palette[i].b = b/list[i].pixels;
	}
 if (verbose) puts("done");
 
 if (verbose) {printf("freeing memory... "); fflush(stdout); }
 for (int i=0; i<colors; i++)
 	free(list[i].data);
 if (verbose) puts("done");
 
 return 0;
} /*quantize_colors*/

int split_RGB_subspace(RGB_subspace src, RGB_subspace& A, RGB_subspace& B)
{
 int dim_r = src.max.r - src.min.r; // wymiary kostki
 int dim_g = src.max.g - src.min.g;
 int dim_b = src.max.b - src.min.b;
 int half;
 
 A.data = (pixel*)malloc(src.size * sizeof(pixel));
 B.data = (pixel*)malloc(src.size * sizeof(pixel));

 if (A.data == NULL || B.data == NULL)
 	{ error("no free mem", ENOMEM);
	  return 1; }
 
 A.size   = B.size   = 0;
 A.pixels = B.pixels = 0;

 A.min.r = A.min.g = A.min.b = 256;
 B.min.r = B.min.g = B.min.b = 256;
 
 A.max.r = A.max.g = A.max.b = -1;
 B.max.r = B.max.g = B.max.b = -1;
 
 RGB_subspace *S;
 
 // dzielenie kostki wzd³u¿ jej najd³u¿szej krawêdzi
 if (dim_r >= dim_g && dim_r >= dim_b)
 	{
	 half = (src.max.r + src.min.r)/2;
	 
	 for (int i=0; i<src.size; i++)
	 	{
		 S = (src.data[i].r <= half) ? &A : &B;

		 if (src.data[i].r > S->max.r) S->max.r = src.data[i].r;
		 if (src.data[i].r < S->min.r) S->min.r = src.data[i].r;
		 if (src.data[i].g > S->max.g) S->max.g = src.data[i].g;
		 if (src.data[i].g < S->min.g) S->min.g = src.data[i].g;
		 if (src.data[i].b > S->max.b) S->max.b = src.data[i].b;
		 if (src.data[i].b < S->min.b) S->min.b = src.data[i].b;

		 S->data[S->size++] = src.data[i];
		 S->pixels += src.data[i].count;
		}
	}
 else
 if (dim_g >= dim_r && dim_g >= dim_b)
 	{
	 half = (src.max.g + src.min.g)/2;

	 for (int i=0; i<src.size; i++)
	 	{
		 S = (src.data[i].g <= half) ? &A : &B;

		 if (src.data[i].r > S->max.r) S->max.r = src.data[i].r;
		 if (src.data[i].r < S->min.r) S->min.r = src.data[i].r;
		 if (src.data[i].g > S->max.g) S->max.g = src.data[i].g;
		 if (src.data[i].g < S->min.g) S->min.g = src.data[i].g;
		 if (src.data[i].b > S->max.b) S->max.b = src.data[i].b;
		 if (src.data[i].b < S->min.b) S->min.b = src.data[i].b;

		 S->data[S->size++] = src.data[i];
		 S->pixels += src.data[i].count;
		}
	}
 else
 if (dim_b >= dim_g && dim_b >= dim_r)
 	{
	 half = (src.max.b + src.min.b)/2;

	 for (int i=0; i<src.size; i++)
	 	{
		 S = (src.data[i].b <= half) ? &A : &B;

		 if (src.data[i].r > S->max.r) S->max.r = src.data[i].r;
		 if (src.data[i].r < S->min.r) S->min.r = src.data[i].r;
		 if (src.data[i].g > S->max.g) S->max.g = src.data[i].g;
		 if (src.data[i].g < S->min.g) S->min.g = src.data[i].g;
		 if (src.data[i].b > S->max.b) S->max.b = src.data[i].b;
		 if (src.data[i].b < S->min.b) S->min.b = src.data[i].b;

		 S->data[S->size++] = src.data[i];
		 S->pixels += src.data[i].count;
		}
	}
	
 A.data = (pixel*)realloc(A.data, A.size * sizeof(pixel));
 B.data = (pixel*)realloc(B.data, B.size * sizeof(pixel));
 
 assert(A.data != NULL);
 assert(B.data != NULL);
 
 return 0;
} /*split_RGB_subspace*/

int build_cube4image()
{
#define s list[0]

 if (verbose) puts("building first cube...");
 s.min.r  = s.min.g = s.min.b = 256;
 s.max.r  = s.max.g = s.max.b = -1;
 s.size   = 0;
 s.pixels = count;
 s.data   = (pixel*)malloc(count * sizeof(pixel));

 if (s.data == NULL)
 	{ error("no free mem", ENOMEM);
	  return 1; }

 if (verbose) {printf("* copying data... "); fflush(stdout);}
 for (int i=0; i<count; i++) 
 	{

	 s.data[i].r = image24bpp[i].r;
	 s.data[i].g = image24bpp[i].g;
	 s.data[i].b = image24bpp[i].b;
	 s.data[i]._ = 0x00;
	 s.data[i].count = 1;
	}
 if (verbose) puts("done");

 if (verbose) {printf("* sorting... "); fflush(stdout);}
 sort(s.data, 0, count-1);
 if (verbose) puts("done");
 
 if (verbose) {printf("* uniqing... "); fflush(stdout);}
 int j = 0;

 s.min.r = s.max.r = image24bpp[0].r;
 s.min.g = s.max.g = image24bpp[0].g;
 s.min.b = s.max.b = image24bpp[0].b;
 for (int i=1; i<count; i++)
	 if (s.data[j].d != s.data[i].d)
	 	{
		 if (s.min.r > image24bpp[i].r) s.min.r = image24bpp[i].r; else
		 if (s.max.r < image24bpp[i].r) s.max.r = image24bpp[i].r;

		 if (s.min.g > image24bpp[i].g) s.min.g = image24bpp[i].g; else
		 if (s.max.g < image24bpp[i].g) s.max.g = image24bpp[i].g;

		 if (s.min.b > image24bpp[i].b) s.min.b = image24bpp[i].b; else
		 if (s.max.b < image24bpp[i].b) s.max.b = image24bpp[i].b;

		 s.data[++j] = s.data[i];
		}
	 else
		 s.data[j].count++;
 if (verbose) printf("number of unique colors is %d\n", j+1);
 
 if (verbose) {printf("* freeing unused memory... "); fflush(stdout);}

 s.size = j+1;
 s.data = (pixel*)realloc(s.data, s.size * sizeof(pixel));
 if (s.data == NULL)
 	{ error("realloc failed", ENOMEM);
	  return 1; }
 else if (verbose) puts("ok");

 return 0;
#undef s
} /*build_cube4image*/

void sort(pixel* list, int first, int last)
{
 int lower = first;
 int upper = last;
 int bound = list[(first+last)/2].d;
 
 while (lower <= upper)
 	{
	 while (list[lower].d < bound)
	 	lower++;
	 while (list[upper].d > bound)
	 	upper--;
		
	 if (lower < upper)
	 	{
		 pixel   tmp = list[lower];
		 list[lower] = list[upper];
		 list[upper] = tmp;
		 lower++, upper--;	
		}
	 else lower++;
	}

 if (first < upper)
 	sort(list, first, upper);
 if (upper+1 < last)
 	sort(list, upper+1, last);
} /*sort*/

int findbest_by_colorcount(int list_size)
{
 int best = 0; 
 int max  = list[0].size;
 for (int i=1; i<list_size; i++)
	if (list[i].pixels > max)
	 	max = list[best=i].pixels;
 
 return best;
}

int findbest_by_pixelcount(int list_size)
{
 int best = 0; 
 int max  = list[0].pixels;
 for (int i=1; i<list_size; i++)
	if (list[i].pixels > max)
	 	max = list[best=i].pixels;
 
 return best;
}

int findbest_by_cubevolume(int list_size)
{
#define volume(i) ((list[i].max.r-list[i].min.r)*(list[i].max.g-list[i].min.g)*(list[i].max.b-list[i].min.b))
 int tmp;
 int best = 0; 
 int max  = volume(0);
	    
 for (int i=1; i<list_size; i++)
	{
	 tmp = volume(i);
	 if (tmp > max)
	 	max = tmp, best=i;
	}
 return best;
#undef volume
}

/* EOF */
