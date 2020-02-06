#include <libimagequant.h>

#include <stdio.h>

int main(void) {
    printf("libimagequant version %d\n", liq_version());
    const int version = liq_version();
    if (version != LIQ_VERSION) {
        return 1;
    }
    return 0;
}
