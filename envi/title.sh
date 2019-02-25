#!/bin/bash
if [[ -z "$ORIG" ]]; then
  export ORIG_PS1=$PS1
fi
export TITLE="\[\e]2;$*\a\]"
export PS1=${ORIG_PS1}${TITLE}
