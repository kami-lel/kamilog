# FIXME simplify

################################################################################
# kamilog_shim
# shipped with kamilog v2.10.0
#
# lets scripts call `kamilog` safely even when it is not installed
# Q.v. https://github.com/kami-lel/kamilog
################################################################################
_KAMILOG_BIN="$(type -P kamilog 2>/dev/null || true)"

kamilog() {
    if [ -n "$_KAMILOG_BIN" ]; then
        "$_KAMILOG_BIN" "$@"
        return
    fi
    input="$(cat; printf x)";
    input="${input%x}"   # keep trailing \n from being stripped
    case "$1" in
        cb|cb0)
            printf '# %s' "$input"
            ;;
        logger)
            printf '%s:\t%s' "$2" "$input"
            ;;
        *)
            printf '%s' "$input"  # no bin found, pass stdin through as-is
            ;;
    esac
}
# END of kamilog_shim  #########################################################