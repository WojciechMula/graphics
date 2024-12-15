#ifndef __bmp_h_included__
#define __bmp_h_included__

#ifdef __GNUC__
     #define pack __attribute__ ((packed))
#else
     #define pack
#endif

typedef unsigned char      byte;
typedef unsigned short int word;
typedef unsigned int       dword;

const word bmp_magic = 0x4d42; // 'BM' string

typedef struct {
  word Type      pack; /* 'MB' == 0x4d42 */
 dword Size      pack; /* size of file in bytes, sometimes sucks */
  word Reserved1 pack; /* must be zero */
  word Reserved2 pack; /* must be zero */
 dword OffBits   pack; /* offset [in bytes] from this structure */
                       /* to raw pixels data                    */
} bmp_FileHeader;

typedef struct  {
 dword Size          pack; /* size of this structure [in bytes] */
 dword Width         pack;
 dword Height        pack;
  word Planes        pack; /* number of bitplanes, always=1 */
  word BitCount      pack; /* bits per pixel: {1,4,8,24}    */
 dword Compression   pack; /* type of commpresion: 0-none   */
 dword SizeImage     pack; /* 0 - when uncommpressed        */
 dword XPelsPerMeter pack; /* information for printers      */
 dword YPelsPerMeter pack; /*                               */
 dword ClrUsed       pack; /* colors used                   */
 dword ClrImportant  pack; /* colors important              */
                           /* if 0 then all colors are important (or used) */
} bmp_InfoHeader;

typedef struct {
 byte B pack;  /* blue  */
 byte G pack;  /* green */
 byte R pack;  /* red   */
 byte __unused pack; /* reserved */
} bmp_Quad;

/* bmp structure

	bmp_FileHeader fh;
	bmp_InfoHeader ih;
	bmp_Quad       palette[ih.ClrUsed];
	byte           raw_data[ih.Width * ih.Height];
*/

#endif
