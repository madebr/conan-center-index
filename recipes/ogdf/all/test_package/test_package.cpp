#include "ogdf/basic/Math.h"

#include <iostream>

int main () {
    for (int n = 0; n < 10; ++n) {
        for(int k = 0; k <= n; ++k) {
            std::cout << ogdf::Math::binomial(n, k) << " ";
        }
        std::cout << "\n";
    }
    return 0;
}
