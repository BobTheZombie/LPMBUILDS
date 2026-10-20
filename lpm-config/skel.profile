# LPM Linux default POSIX user profile.
if [ -d "$HOME/.local/bin" ]; then
    case ":$PATH:" in
        *:"$HOME/.local/bin":*) ;;
        *) PATH="$HOME/.local/bin:$PATH" ;;
    esac
    export PATH
fi
