--- lib/et/compile_et.sh.in
+++ lib/et/compile_et.sh.in
@@ -3,7 +3,7 @@
 #

 AWK=@AWK@
-DIR=@datadir@/et
+DIR="#E2FSPROGS_CONAN_DATADIR/et"

 if test "$1" = "--build-tree" ; then
     shift;
--- lib/ss/mk_cmds.sh.in
+++ lib/ss/mk_cmds.sh.in
@@ -2,7 +2,7 @@
 #
 #

-DIR=@datadir@/ss
+DIR="$E2FSPROGS_CONAN_DATADIR/ss"
 AWK=@AWK@
 SED=sed

