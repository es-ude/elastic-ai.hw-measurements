{ pkgs, lib, config, inputs, ... }:


let
  pkgs-rosetta = pkgs.pkgsx86_64Darwin;
  pkgs-unstable = import inputs.nixpkgs-unstable { system = pkgs.stdenv.system; };
in {
  packages = [
    pkgs.git
    pkgs.wget
    pkgs.gzip
    pkgs.gnutar
    pkgs.picotool
  ];

  scripts = {
    flash_dirty_jtag = {
      exec = ''
        if [[ -e $DEVENV_ROOT/external/dirtyJtag.uf2 ]]; then
          RELEASE=$(wget -qO- "https://api.github.com/repos/phdussud/pico-dirtyJtag/releases/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
          URL="https://github.com/phdussud/pico-dirtyJtag/releases/download/$RELEASE/dirtyJtag.uf2"
          echo "Downloading DirtyJTAG ($URL) ... "
          cd $DEVENV_ROOT/external && wget -q "$URL"
          echo "Done"
        else
          echo "RP2040 Executable found."
        fi

        picotool load --verify --force --execute dirtyJtag.uf2
      '';
      package = pkgs.bash;
    };
    get_latest_oss_cad_suite_release= {
      exec = ''
        echo $(wget -qO- "https://api.github.com/repos/YosysHQ/oss-cad-suite-build/releases/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
      '';
      package = pkgs.bash;
    };
    check_oss_cad_available = {
      exec = ''
        if [[ -e $DEVENV_ROOT/oss-cad-suite/VERSION ]]; then
            LATEST=$(get_latest_oss_cad_suite_release | tr -d "-")
            CURRENT=$(cat $DEVENV_ROOT/oss-cad-suite/VERSION)
            if [[ "$LATEST" != "$CURRENT" ]]; then
                echo "You have currently Version $CURRENT of the oss-cad-suite installed. A newer version ($LATEST) is available. If you want to update, please enter 'download_build_tools' into terminal."
            fi
        else
            echo "You don't have the oss-cad-suite installed. Please enter 'download_build_tools' into terminal"
        fi
      '';
      package = pkgs.bash;
    };
    download_build_tools = {
      exec = ''
        if [[ "$(uname -m)" == "arm64" ]]; then
          ARCH='arm64'
        elif [[ "$(uname -m)" == "x86_64" ]]; then
          ARCH="x64"
        else
          echo "Architecture not supported!"
          exit 1
        fi
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
           OS="linux"
        elif [[ "$OSTYPE" == "darwin"* ]]; then
          OS="darwin"
        else
          echo "OS not supported!"
          exit 1
        fi

        RELEASE=$(get_latest_oss_cad_suite_release)
        URL="https://github.com/YosysHQ/oss-cad-suite-build/releases/download/$RELEASE/oss-cad-suite-$OS-$ARCH-$(echo "$RELEASE" | tr -d "-").tgz"

        echo "Downloading OSS-CAD-Suite ($URL) ... "
        cd $DEVENV_ROOT && wget -qO- "$URL" | gunzip | tar xf -
        echo "Done"

        if [[ "$OS" == "darwin" ]]; then
          $DEVENV_ROOT/oss-cad-suite/activate
        fi
      '';
      package = pkgs.bash;
    };
  };

  enterShell = ''
    echo
    echo "Welcome Back!"
    echo
    check_oss_cad_available
    if [[ -e $DEVENV_ROOT/oss-cad-suite/environment ]]; then
      echo "Source oss-cad-suite from local project"
      cd $DEVENV_ROOT && source /oss-cad-suite/environment
    elif [[ -e $HOME/oss-cad-suite/environment ]]; then
      echo "Source oss-cad-suite from home directory"
      cd $HOME && source oss-cad-suite/environment
    else
      echo "oss-cad-suite not found"
    fi
    cd $DEVENV_ROOT
  '';
}
