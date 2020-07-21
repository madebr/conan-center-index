#include "graphviz/gvc.h"

#include <stdio.h>
#include <stdlib.h>

int main() {
    const char **s = NULL;
    GVC_t *context = gvNEWcontext(NULL, 0);
    printf("gvc version: %s\n", gvcVersion(context));
    printf("gvc build date: %s\n", gvcBuildDate(context));
    for(s = gvcInfo(context); s; ++s) {
        printf("gvcInfo: %s\n", *s);
    }
    return 0;
}
