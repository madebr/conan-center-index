#include "libtcc.h"

#include <stdio.h>

#define CHECK_RES(FUNC) \
    do { \
        int res = FUNC; \
        if (res != 0) {\
            fprintf(stderr, "Result of '%s' was '%d'\n", #FUNC, res); \
            return 1; \
        } \
    } while (0)


int main(int argc, char **argv) {
    TCCState *tcc_state;
    if (argc < 3) {

        fprintf(stderr, "Too few arguments\n");
        fprintf(stderr, "%s INCPATH SRCPATH\n", argv[0]);
        return 1;
    }

    tcc_state = tcc_new();

    CHECK_RES(tcc_add_sysinclude_path(tcc_state, argv[1]));
    CHECK_RES(tcc_add_file(tcc_state, argv[2]));

    CHECK_RES(tcc_set_output_type(tcc_state, TCC_OUTPUT_OBJ));
    CHECK_RES(tcc_output_file(tcc_state, "output.o"));

    tcc_delete(tcc_state);
    return 0;
}
