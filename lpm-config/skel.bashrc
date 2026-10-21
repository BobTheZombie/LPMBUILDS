# LPM Linux default interactive Bash configuration.
case $- in *i*) ;; *) return ;; esac
HISTSIZE=2000
HISTFILESIZE=5000
HISTCONTROL=ignoreboth
alias ll='ls -lah'
alias la='ls -A'
PS1='\u@\h:\w\$ '
