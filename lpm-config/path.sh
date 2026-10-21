# LPM Linux: use administrator-installed commands when present.
case ":$PATH:" in
    *:/usr/local/bin:*) ;;
    *) PATH="/usr/local/bin:$PATH" ;;
esac
export PATH
