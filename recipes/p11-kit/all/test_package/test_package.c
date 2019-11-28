#include "p11-kit/p11-kit.h"

#include <stdio.h>
#include <stdlib.h>

int main(int argc, const char *argv[]) {
    p11_kit_be_loud();

    p11_kit_set_progname(argv[0]);

    return EXIT_SUCCESS;
}
