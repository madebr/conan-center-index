#include "fontconfig.h"

#include <stdio.h>

int main() {
    FcInit();
    const int version = FcGetVersion();
    if (FC_VERSION != version) {
        fprintf(stderr, "Version in library and header do not match\n");
        return 1;
    }
    FcFini();
    return 0;
}
