# LPM Linux: /etc/bash.bashrc
# This file is evaluated by interactive Bash shells (including Konsole).
[[ $- != *i* ]] && return

# Legacy LPM startup files could put two literal backslashes into PS1. Bash
# then printed prompt syntax such as \[\e[1;35m\]\u@\h instead of formatting it.
# Repair ONLY that recognizable broken form; leave custom valid prompts alone.
__lpm_repair_prompt() {
    if [[ ${PS1-} == *'\\['* && ${PS1-} == *'\\u'* ]]; then
        if [[ ${TERM:-dumb} == dumb ]]; then
            PS1='\u@\h:\w\$ '
        else
            PS1='\[\e[1;35m\]\u@\h\[\e[0m\]:\[\e[1;34m\]\w\[\e[0m\]\$ '
        fi
    fi
}

if [[ -z ${BASHRCSOURCED:-} ]]; then
    BASHRCSOURCED=Y

    # Bash's builtin default prompt is safe to replace; never override a
    # correctly formatted customized PS1.
    if [[ ${PS1-} == '\s-\v\$ ' ]]; then
        if [[ ${TERM:-dumb} == dumb ]]; then
            PS1='\u@\h:\w\$ '
        else
            PS1='\[\e[1;35m\]\u@\h\[\e[0m\]:\[\e[1;34m\]\w\[\e[0m\]\$ '
        fi
    fi

    # This runs after ~/.bashrc has been read, so it also fixes an older
    # user-level PS1 assignment without editing or overwriting $HOME files.
    PROMPT_COMMAND+=(__lpm_repair_prompt)

    case ${TERM-} in
        Eterm*|alacritty*|aterm*|foot*|gnome*|konsole*|kterm*|putty*|rxvt*|tmux*|xterm*)
            PROMPT_COMMAND+=('printf "\033]0;%s@%s:%s\007" "${USER}" "${HOSTNAME%%.*}" "${PWD/#$HOME/\~}"')
            ;;
        screen*)
            PROMPT_COMMAND+=('printf "\033_%s@%s:%s\033\\" "${USER}" "${HOSTNAME%%.*}" "${PWD/#$HOME/\~}"')
            ;;
    esac
fi

# Also normalize malformed prompts when this file was loaded AFTER ~/.bashrc.
__lpm_repair_prompt

if [[ -r /usr/share/bash-completion/bash_completion ]]; then
    . /usr/share/bash-completion/bash_completion
fi
