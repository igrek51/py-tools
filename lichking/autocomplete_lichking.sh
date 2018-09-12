# put it to /etc/bash_completion.d/autocomplete_liching.sh

_lichking() {
    # COMPREPLY=()
    # lich test duPa 51
    # echo ""
    # echo "COMP_WORDS : ${COMP_WORDS}" # lich
    # echo "COMP_CWORD : ${COMP_CWORD}" # 2
    # echo "COMP_WORDS[COMP_CWORD] : ${COMP_WORDS[COMP_CWORD]}" # duPa
    # echo "COMP_LINE : ${COMP_LINE}" # lich test duPa 51
    # echo "COMP_POINT : ${COMP_POINT}" # 12
    # echo "COMP_KEY : ${COMP_KEY}" # 9
    # echo "COMP_TYPE : ${COMP_TYPE}" # 9
    # echo "args : $@" # lich du test
    # echo "reply : ${COMPREPLY}" #
    COMPREPLY=( $(lichking autocomplete "${COMP_LINE}") )
}

complete -F _lichking lichking lich king dupa
