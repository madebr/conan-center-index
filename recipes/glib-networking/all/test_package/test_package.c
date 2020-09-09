#include "gio/gio.h"

#include <stdio.h>
#include <stdlib.h>

#if defined(STATIC_BACKEND)
# define DECLARE_BACKEND(backend) extern void G_PASTE(g_io_, G_PASTE(backend, _load))(void *)
# define LOAD_BACKEND(backend) G_PASTE(g_io_, G_PASTE(backend, _load))(NULL)
#else
# define DECLARE_BACKEND
# define LOAD_BACKEND (void)
#endif

DECLARE_BACKEND(BACKEND);

int main() {
#ifdef STATIC_BACKEND
    printf("Loading backend " BACKEND_STRING "...\n");
    fflush(stdout);
    LOAD_BACKEND(BACKEND);
    printf("Backend loaded.\n");
    fflush(stdout);
#endif

    g_setenv ("GSETTINGS_BACKEND", "memory", TRUE);
    g_setenv ("GIO_USE_TLS", BACKEND_STRING, TRUE);

    GTlsBackend *backend;
    GTlsDatabase *database;
    GTlsDatabase *check;

    backend = g_tls_backend_get_default ();
    g_assert_true (G_IS_TLS_BACKEND (backend));
    database = g_tls_backend_get_default_database (backend);
    g_assert_true (G_IS_TLS_DATABASE (database));
    check = g_tls_backend_get_default_database (backend);
    g_assert_true (database == check);
    g_object_unref (database);
    g_object_unref (check);
    return 0;
}
