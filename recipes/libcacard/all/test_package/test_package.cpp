#include "lzo1f.h"
#include <stdio.h>
#include <string.h>

const char *text = "This is a string that lzo should compress to less bytes then before if it is working fine.\n"
"This compression algorithm appears to only compress bigger inputs so put a lot of text here\n.";


int main()
{
    char compressed[2048];
    size_t compressed_len = sizeof(compressed);
    {
        char workMemory[LZO1F_MEM_COMPRESS];
        lzo1f_1_compress((unsigned char*)text, strlen(text), (unsigned char*)compressed, &compressed_len, workMemory);
    }
    printf("Size before compression: %4u bytes\n", strlen(text));
    printf("Size after compression:  %4u bytes\n", compressed_len);


    char decompressed[2048];
    size_t decompressed_len = sizeof(decompressed);
    {
        char workMemory[LZO1F_MEM_DECOMPRESS];
        lzo1f_decompress((unsigned char*)compressed, compressed_len, (unsigned char*)decompressed, &decompressed_len, workMemory);
    }
    int ok = (strlen(text) == decompressed_len) && (strcmp(text, decompressed) == 0);
    printf("Decompression: %s\n", ok ? "Success" : "Failure");

    return ok ? 0 : 1;
}
