#include "libsoup/soup.h"

#include <stdio.h>

int main() {
    printf("soup version: %d.%d.%d\n",
        soup_get_major_version(),
        soup_get_minor_version(),
        soup_get_micro_version())
    return 0
}
