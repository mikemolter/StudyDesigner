# Change command prompt
if [ -f $(brew --prefix)/etc/bash_completion/ ]; then
    . $(brew --prefix)/etc/bash_completion
fi

# colors!
green="\[\033[0;32m\]"
blue="\[\033[0;34m\]"
purple="\[\033[0;35m\]"
reset="\[\033[0m\]"


export GIT_PS1_SHOWDIRTYSTATE=1
# '\u' adds the name of the current user to the prompt
# '\$(__git_ps1)' adds git-related stuff
# '\W' adds the name of the current directory
export PS1="$purple\u$green\$(__git_ps1)$blue \W $ $reset"


alias subl="/Applications/Sublime\ Text.app/Contents/SharedSupport/bin/subl"
alias V="cd ~/Vagrants"
alias SD="cd ~/Vagrants/apache/StudyDesigner"


if which rbenv > /dev/null; then eval "$(rbenv init -)"; fi

export WORKON_HOME=$HOME/.virtualenvs
export PROJECT_HOME=$HOME/projects
export VIRTUALENVWRAPPER_PYTHON=/usr/local/bin/python
export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv
export VIRTUALENVWRAPPER_VIRTUALENV_ARGS='--no-site-packages'
export VIRTUALENVWRAPPER_LOG_DIR="$WORKON_HOME"
export VIRTUALENVWRAPPER_HOOK_DIR="$WORKON_HOME"

source /usr/local/bin/virtualenvwrapper.sh



