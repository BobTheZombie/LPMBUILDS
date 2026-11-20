# LPM Linux: ~/.bashrc (installed into /etc/skel for new accounts)
[[ $- != *i* ]] && return

alias ls='ls --color=auto'
alias grep='grep --color=auto'

# Escape sequences are single-backslash Bash PS1 syntax. Do not double them.
if [[ ${TERM:-dumb} == dumb ]]; then
    PS1='\u@\h:\w\$ '
else
    PS1='\[\e[1;35m\]\u@\h\[\e[0m\]:\[\e[1;34m\]\w\[\e[0m\]\$ '
fi
