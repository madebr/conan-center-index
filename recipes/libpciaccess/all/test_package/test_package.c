#include "pciaccess.h"

int main() {
    pci_device_vgaarb_init();
    pci_device_vgaarb_fini();
    return 0;
}
