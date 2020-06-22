#include "svn_version.h"

#include "apr_general.h"

#include <stdio.h>
#include <stdlib.h>

int main(int argc, const char *const*argv, const char *const*env) {
    apr_app_initialize(&argc, &argv, &env);
    apr_pool_initialize();

    apr_pool_t *pool;
    apr_pool_create(&pool, NULL);

    const svn_version_t *version = svn_subr_version();
    const svn_version_extended_t *ext_version = svn_version_extended(1, pool);

    printf("subversion version %d.%d.%d\n", version->major, version->minor, version->patch);
    printf("build date: %s\n", svn_version_ext_build_date(ext_version));
    printf("build time: %s\n", svn_version_ext_build_time(ext_version));

    apr_pool_destroy(pool);
    apr_pool_terminate();
    apr_terminate2();
    return 0;
}

