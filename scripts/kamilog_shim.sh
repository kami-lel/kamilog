################################################################################
# kamilog_shim
# shipped with kamilog v2.10.0
#
# lets scripts call `kamilog` safely even when it is not installed
# Q.v. https://github.com/kami-lel/kamilog
################################################################################
_KAMILOG_BIN="$(type -P kamilog 2>/dev/null || true)"

kamilog() {
    [ -n "$_KAMILOG_BIN" ] && { "$_KAMILOG_BIN" "$@"; return; }
    [ "$1" = logger ] && { printf '%s:\t' "$2"; cat; return; }
    cat  # no bin found, pass stdin through as-is, skip cb formatting
}
# END of kamilog_shim  #########################################################