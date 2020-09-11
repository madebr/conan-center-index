#include "tomcrypt.h"
#include "tommath.h"

#include <stdio.h>
#include <stdlib.h>

#define check_crypt(V)                            \
    if ((V) != CRYPT_OK) {                  \
        fprintf(stderr, #V " FAILURE\n");   \
        return 1;                           \
}

#define check_math(V)                            \
    if ((V) != MP_OKAY) {                  \
        fprintf(stderr, #V " FAILURE\n");   \
        return 1;                           \
}

int main() {
    unsigned char buf[65];
    hash_state state;
    check_crypt(sha512_init(&state));
    check_crypt(sha512_process(&state, (const unsigned char *)"0123456789", 10));
    check_crypt(sha512_done(&state, buf));

    mp_int mp;
    check_crypt(mp_init(&mp));
    check_crypt(mp_from_ubin(&mp, buf, 64));

    printf("hash =     ");
    check_math(mp_fwrite(&mp, 16, stdout));
    printf("\n");
    mp_clear(&mp);
    printf("expected = BB96C2FC40D2D54617D6F276FEBE571F623A8DADF0B734855299B0E107FDA32CF6B69F2DA32B36445D73690B93CBD0F7BFC20E0F7F28553D2A4428F23B716E90\n");

    return 0;
}

/*
import hashlib
h = hashlib.sha512()
h.update(b"0123456789")
print(h.hexdigest())
*/
