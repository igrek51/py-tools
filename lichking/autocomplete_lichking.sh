# put it to: /etc/bash_completion.d/*.sh

# script location (command to invoke)
AUTOCOMPLETE_SCRIPT_COMMAND=lichking
# space delimited application names (command line prefix)
AUTOCOMPLETE_SCRIPT_NAMES=lichking lich king dupa


_autocomplete() {
    COMPREPLY=( $(${AUTOCOMPLETE_SCRIPT_COMMAND} autocomplete "${COMP_LINE}") )
}

complete -F _autocomplete ${AUTOCOMPLETE_SCRIPT_NAMES}
