#include "util.h"
#include "cudd.h"

int main (int argc, const char *argv[])
{
    DdManager *gbm;
    char filename[30];
    gbm = Cudd_Init(0, 0, CUDD_UNIQUE_SLOTS, CUDD_CACHE_SLOTS, 0);
    DdNode *bdd = Cudd_bddNewVar(gbm);
    Cudd_Ref(bdd);
    Cudd_Quit(gbm);
    return 0;
}
