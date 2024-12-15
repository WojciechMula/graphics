#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>

#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

#include "quantize.h"
#include "bmp.h"

extern int errno;

int  width=-1, height=-1; // rozmiary obrazka

int  sort_by=1; // sposób kwantyzacji
int  verbose=0; // 
int  swapRB =0;

char infile [257] = "";
char outfile[257] = "";
char palfile[257] = "";

void parse_opt(int argc, char* argv[]);
void help();

int main(int argc, char* argv[])
{
 parse_opt(argc, argv);
 
 byte     *image8bpp;
 RGBpixel *image24bpp;
 RGBpixel  palette[256];
 int       count = width*height;
 
 image24bpp = (RGBpixel*)malloc(count*sizeof(RGBpixel));
 if (image24bpp == NULL)
 	{ fputs("no free mem\n", stderr) ; exit(1); }

 image8bpp  =     (byte*)malloc(count*sizeof(byte));
 if (image8bpp == NULL)
 	{ fputs("no free mem\n", stderr); exit(1); }
 
 FILE *f;

 errno = 0; 
 f = fopen(infile, "r");
 if (errno) 
 	{ fprintf(stderr, "fopen: %s\n", strerror(errno));
	  exit(1); }

 struct stat buf;
 stat(infile, &buf);
 if (errno)
 	{ fprintf(stderr, "fstat: %s\n", strerror(errno));
	  exit(1); }

 fseek(f, buf.st_size - count*sizeof(RGBpixel), SEEK_SET);
 if (errno) 
 	{ fprintf(stderr, "fseek: %s\n", strerror(errno));
	  exit(1); }

 fread(image24bpp, count, sizeof(RGBpixel), f);
 if (errno) 
 	{ fprintf(stderr, "fread: %s\n", strerror(errno));
	  exit(1); }
 fclose(f);

 if (quantize_colors(image24bpp, image8bpp, palette, count, 256, sort_by, verbose))
 	{ fprintf(stderr, "quantize_colors: %s\n", strerror(errno));
	  exit(1); }
	
 f = fopen(outfile, "w");
 if (errno)
 	{ fprintf(stderr, "fopen: %s\n", strerror(errno));
	  exit(1); }

 bmp_FileHeader fh = {bmp_magic, 0,0,0, sizeof(bmp_FileHeader)+sizeof(bmp_InfoHeader)+256*sizeof(bmp_Quad)};
 bmp_InfoHeader ih = {sizeof(bmp_InfoHeader), width, height, 1, 8, 0,0,0,0,0,0};
 bmp_Quad       pal[256];
 
 for (int i=0; i<256; i++)
 	if (swapRB)
		{
 		 pal[i].R = palette[i].b;
 		 pal[i].G = palette[i].g;
 		 pal[i].B = palette[i].r;
		}
	else
		{
 		 pal[i].R = palette[i].r;
 		 pal[i].G = palette[i].g;
 		 pal[i].B = palette[i].b;
		}
		
 fwrite(&fh, sizeof(bmp_FileHeader), 1, f);
 if (errno)
 	{ fprintf(stderr, "fwrite: %s\n", strerror(errno));
	  exit(1); }
 fwrite(&ih, sizeof(bmp_InfoHeader), 1, f);
 if (errno)
 	{ fprintf(stderr, "fwrite: %s\n", strerror(errno));
	  exit(1); }
 fwrite(pal, sizeof(bmp_Quad), 256, f);
 if (errno)
 	{ fprintf(stderr, "fwrite: %s\n", strerror(errno));
	  exit(1); }
 fwrite(image8bpp, count, sizeof(byte), f);
 if (errno)
 	{ fprintf(stderr, "fwrite: %s\n", strerror(errno));
	  exit(1); }
 fclose(f);
 if (errno)
 	{ fprintf(stderr, "fclose: %s\n", strerror(errno));
	  exit(1); }
	  
 if (*palfile != '\0')
 	{
	 f = fopen(palfile, "w");
	 for (int i=0; i<256; i++)
	 	fprintf(f, "%3d %3d %3d\n", palette[i].r, palette[i].g, palette[i].b);
	 fclose(f);
	}
 
 return 0;
}

void about()
{ puts("qunatize colors by Wojciech Mula (wojciech_mula(at)poczta.onet.pl)."); }

void help()
{
 puts("-w=width    -- width of image\n"
      "-h=height   -- height of image\n"
      "-i=filename -- input truecolor file\n"
      "               Program read last width*height*3 bytes of image\n"
      "               so it handle well uncompressed TGA, BMP and PNM files.\n"
      "-o=filename -- output indexed file\n"
      "-p=filename -- optional palette file\n"
      "               Each color is saved in separated line; numbers are decimal ASCII.\n"
      "-s=c|p|v    -- attribute of cube using to select one\n"
      "                c - num of colors enclosed in cube (best results)\n"
      "                p - num of pixels in cube\n"
      "                v - volume of cube (worst results)\n"
      "--swap      -- swap R with B\n"
      "--verbose   -- display additional information, such as progress of work\n"
      "               I recomended to turn it on when you converting a big images\n"
      "               or if your cpu is slow.\n"
      "--help      -- this help\n"
      "--version   -- print info about program\n"
     );
}

void parse_opt(int argc, char* argv[])
{
 char *err;
 for (int i=1; i<argc; i++)
 	{
	 if (strcmp(argv[i], "--swap") == 0)
		swapRB = 1;
	 else
	 if (strcmp(argv[i], "--verbose") == 0)
	 	verbose = 1;
	 else
	 if (strcmp(argv[i], "--version") == 0)
	 	{about(); exit(0);}
	 else
	 if (strcmp(argv[i], "--help") == 0)
	 	{help(); exit(0);}
	 else
	 if (strncmp(argv[i], "-h=", 3) == 0)
	 	{
		 height = strtol(&argv[i][3], &err, 10);
		 if (*err != '\0')
		 	{ fputs("bad height\n", stderr);  exit(1); }
		}
	 else
	 if (strncmp(argv[i], "-w=", 3) == 0)
	 	{
		 width = strtol(&argv[i][3], &err, 10);
		 if (*err != '\0')
		 	{ fputs("bad width\n", stderr);  exit(1); }
		}
	 else
	 if (strncmp(argv[i], "-i=", 3) == 0)
	 	{
	 	 strncpy(infile, &argv[i][3], 256);
		 infile[strlen(&argv[i][3])] = '\0';
		}
	 else
	 if (strncmp(argv[i], "-o=", 3) == 0)
	 	{
	 	 strncpy(outfile, &argv[i][3], 256);
		 outfile[strlen(&argv[i][3])] = '\0';
		}
	 else
	 if (strncmp(argv[i], "-p=", 3) == 0)
	 	{
	 	 strncpy(palfile, &argv[i][3], 256);
		 palfile[strlen(&argv[i][3])] = '\0';
		}
	 else
	 if (strncmp(argv[i], "-s=", 3)==0)
	 	{
		 switch (argv[i][3])
		 	{
			 case 'c': sort_by=1; break;
			 case 'p': sort_by=0; break;
			 case 'v': sort_by=0; break;
			 default : help();
			           exit(1);
			}
		}
	 else
	 	{
		 printf("wrong argument `%s'\n", argv[i]);
		 help();
		 exit(1);
		}
	}

 if (*infile == '\0')
 	{
	 fprintf(stderr, "you missed input filename\n");
	 help();
	 exit(1);
	}
 if (*outfile == '\0')
 	{
	 fprintf(stderr, "you missed output filename\n");
	 help();
	 exit(1);
	}
 if (width <= 0 || width <= 0)
 	{
	 fprintf(stderr, "image size is wrong\n");
	 help();
	 exit(1);
	}
 if ((strcmp(infile, outfile) == 0) || 
     (strcmp(infile, palfile) == 0) ||
     (strcmp(palfile, outfile) == 0))
     	{
	 fprintf(stderr, "some filenames are equal\n");
	 exit(1);
	}
 printf("%s (%dx%d) -> %s\n", infile, width, height, outfile);
}
