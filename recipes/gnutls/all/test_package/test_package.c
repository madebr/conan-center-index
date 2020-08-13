#include <gnutls.h>

#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#define CHECK(x) do { \
    if (x < 0) { \
        fprintf(stderr, "%s failed\n", #x); \
        return 1; \
    } \
} while (0)

int main() {
    if (gnutls_check_version("3.4.6") == NULL) {
        fprintf(stderr, "GnuTLS 3.4.6 or later is required for this example\n");
        return 1;
    }

    /* for backwards compatibility with gnutls < 3.3.0 */
    CHECK(gnutls_global_init());

//    CHECK(gnutls_bye(session, GNUTLS_SHUT_RDWR));

    gnutls_global_deinit();
}
