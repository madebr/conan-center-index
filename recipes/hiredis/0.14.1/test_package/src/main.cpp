#include <stdlib.h>
#include <iostream>

#include <hiredis/hiredis.h>

int main()
{
    std::cout << "hiredis version: " << HIREDIS_MAJOR << "."
              << HIREDIS_MINOR << "."
              << HIREDIS_PATCH << std::endl;

    const char *hostname = "127.0.0.1";
    int port = 6379;

    redisContext *c = redisConnect(hostname, port);
    if (c == NULL)
    {
        printf("Error: Can't allocate redis context\n");
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
