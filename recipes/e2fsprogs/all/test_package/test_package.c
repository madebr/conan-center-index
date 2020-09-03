#include "ss/ss.h"

#include <stdio.h>
#include <stdlib.h>

extern ss_request_table test_package_commands;

static const char *version = "0.1";

void do_hello_world(int argc, char **argv, int sci_idx, void *infop)
{
    printf("Called do_hello_world(%d)\n", argc);
}

void do_work(int argc, char **argv, int sci_idx, void *infop)
{
    printf("Called do_work(%d)\n", argc);
}

void do_clean(int argc, char **argv, int sci_idx, void *infop)
{
    printf("Called do_clean(%d)\n", argc);
}


int main(int argc, const char *argv[])
{
    int retval;
    int sci_idx = ss_create_invocation(argv[0], version, NULL, &test_package_commands, &retval);
    if (retval != 0) {
        fprintf(stderr, "ss_create_invocation failed\n");
        return 1;
    }
    if (argc < 2) {
        ss_listen(sci_idx);
    } else {
        retval = ss_execute_line(sci_idx, argv[1]);
        if (retval != 0) {
            fprintf("ss_execute_line failed with %d\n", retval);
            return retval;
        }
    }
    return 0;
}
