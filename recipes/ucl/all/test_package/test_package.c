#include "ucl/ucl.h"

#include <stdio.h>
#include <string.h>

int main()
{
    printf("version: %s\n", ucl_version_string());
    return 0;
}
