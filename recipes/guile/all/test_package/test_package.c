#include <libguile.h>

#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>


static SCM
tp_secret_function(SCM arg_in)
{
    const int input = scm_to_int (arg_in);
    if (input == 1337) {
        fprintf(stdout, "SECRET VALUE DETECTED\n");
        fflush(stdout);
    }
    const int result = input * 2;
    return scm_from_int (result);

}

static void
inner_main(void *data, int argc, char **argv)
{
    scm_c_define_gsubr("tp-secret-function", 1, 0, 0, &tp_secret_function);
    scm_shell(argc, argv);
}

int main(int argc, char **argv) {
    scm_boot_guile (argc, argv, inner_main, NULL);
    return EXIT_FAILURE;
}
