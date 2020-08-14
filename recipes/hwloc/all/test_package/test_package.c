#include "hwloc.h"

#include <stdio.h>

int main() {
    printf("hwloc api version: %u\n", hwloc_get_api_version());

    /* Allocate and initialize topology object. */
    hwloc_topology_t topology;
    hwloc_topology_init(&topology);

    /* ... Optionally, put detection configuration here to ignore
       some objects types, define a synthetic topology, etc....

       The default is to detect all the objects of the machine that
       the caller is allowed to access.  See Configure Topology
       Detection. */

    /* Perform the topology detection. */
    hwloc_topology_load(topology);

    /* Optionally, get some additional topology information
       in case we need the topology depth later. */
    int topodepth = hwloc_topology_get_depth(topology);

    /*****************************************************************
     * First example:
     * Walk the topology with an array style, from level 0 (always
     * the system level) to the lowest level (always the proc level).
     *****************************************************************/
    for (int depth = 0; depth < topodepth; depth++) {
        printf("*** Objects at level %d\n", depth);
        for (unsigned i = 0; i < hwloc_get_nbobjs_by_depth(topology, depth); i++) {
            char string[128];
            hwloc_obj_type_snprintf(string, sizeof(string),
                                    hwloc_get_obj_by_depth(topology, depth, i), 0);
            printf("Index %u: %s\n", i, string);
        }
    }

    return 0;
}
