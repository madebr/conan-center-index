#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "Incorrect number of arguments\n");
        return EXIT_FAILURE;
    }
    if (!strcmp("--version", argv[1])) {
        printf("GNU %s 3.14\n", argv[0]);
        printf("\n");
        printf("Copyright (C) 2011 Free Software Foundation, Inc.\n");
        printf("This is free software; see the source for copying conditions.  There is NO\n");
        printf("warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.\n");
        printf("\n");
        printf("Written by A. Programmer.\n");
    } else if (!strcmp("--help", argv[1])) {
        printf("GNU `%s' does nothing interesting except serve as an example for\n", argv[0]);
        printf("`%s'.\n", argv[0]);
        printf("\n");
        printf("Usage: test_package [OPTION]...\n");
        printf("\n");
        printf("Options:\n");
        printf("  -a, --option      an option\n");
        printf("  -b, --another-option[=VALUE]\n");
        printf("                    another option\n");
        printf("\n");
        printf("      --help        display this help and exit\n");
        printf("      --version     output version information and exit\n");
        printf("\n");
        printf("Examples:\n");
        printf("  %s               do nothing\n", argv[0]);
        printf("  %s --option      the same thing, giving `--option'\n", argv[0]);
        printf("\n");
        printf("Report bugs to <bug-gnu-utils@gnu.org>.\n");
    } else {
        fprintf(stderr, "Unknown argument\n");
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
