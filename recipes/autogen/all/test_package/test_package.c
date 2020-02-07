#include "list.h"

#include <stdio.h>
#include <stdlib.h>

int main() {
    for (size_t i = 0; i < sizeof(az_name_list)/sizeof(*az_name_list); ++i) {
        printf("%s\n", az_name_list[i]);
    }
    return EXIT_SUCCESS;
}
