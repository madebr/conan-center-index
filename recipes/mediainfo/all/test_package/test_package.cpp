#include "MediaInfo/MediaInfo.h"
#include "ZenLib/Ztring.h"

#include <iostream>

int main(int argc, const char *argv[]) {
    if (argc < 2) {
        std::cerr << "Need at least one argument\n";
        return 1;
    }

    MediaInfoLib::MediaInfo mediainfo;
    ZenLib::Ztring videofile(argv[1]);
    size_t opened = mediainfo.Open(videofile.To_Unicode());
    if (!opened) {
        std::cerr << "Open failed\n";
        return 1;
    }
    MediaInfoLib::String info = mediainfo.Inform();
    std::wcout << info;
    return 0;
}
