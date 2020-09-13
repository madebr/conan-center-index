#include "unbound.h"

#include <stdio.h>

int main(int argc, char *argv[]) {
    struct ub_ctx *ctx = ub_ctx_create();
    struct ub_result *result;

    if (argc < 2) {
        fprintf(stderr, "Need an argument\n");
        return 1;
    }

    int err = ub_resolve(ctx, argv[1], 1, 1, &result);
    if (err != 0) {
        fprintf(stderr, "ub_resolve failed\n");
        return 1;
    }
    printf("qname=%s\n", result->qname);
    for(int i = 0; result->data[i] != NULL; ++i) {
        const char *joiner;
        if (result->len[i] == 4) {
            joiner = ".";
        } else {
            joiner = "::";
        }
        printf("data[%d]=", i);
        for(int j = 0; j < result->len[i]; ++ j) {
            printf("%u", (unsigned char)result->data[i][j]);
            if (j != result->len[i] - 1) {
                printf("%s", joiner);
            }
        }
        printf("\n");
    }
    printf("canonical name=%s\n", result->canonname);

    ub_resolve_free(result);
    ub_ctx_delete(ctx);
    return 0;
}
