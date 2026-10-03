################################################################################
# kamilog_shim.sh
# part of kamilog v2.10.0, q.v. https://github.com/kami-lel/kamilog
#
# source, or include as part of, a script
# to call kamilog safely from it whether or not kamilog is installed
################################################################################
_KAMILOG_BIN="$(type -P kamilog 2>/dev/null || true)"

kamilog() {
    [ -n "$_KAMILOG_BIN" ] && { "$_KAMILOG_BIN" "$@"; return; }
    [ "$1" = logger ] && { printf '%s:\t' "$2"; cat; return; }
    { [ "$1" = cb ] || [ "$1" = cb0 ]; } \
        && { printf '# '; cat; printf ' #'; return; }
    cat  # no bin found, pass stdin through as-is, skip cb formatting
}
# END of kamilog_shim  #########################################################
