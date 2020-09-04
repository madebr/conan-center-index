#include "talloc.h"

#include <stdio.h>
#include <stdlib.h>

struct user {
    unsigned uid;
    char *username;
    unsigned num_groups;
    char **groups;
};


int main()
{
    struct user *user = talloc(NULL, struct user);

    user->uid = 1000;
    user->num_groups = 5;

    user->username = talloc_strdup(user, "Test user");
    user->groups = talloc_array(user, char*, user->num_groups);

    for (unsigned i = 0; i < user->num_groups; ++i) {
        user->groups[i] = talloc_asprintf(user->groups, "Test group %u", i);
    }

    talloc_free(user);
    return 0;
}
