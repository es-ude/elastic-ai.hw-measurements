{
  pkgs,
  lib,
  config,
  inputs,
  ...
}: let
	pkgs-rosetta = pkgs.pkgsx86_64Darwin;
	unstablePkgs = import inputs.nixpkgs-unstable {system = pkgs.stdenv.system;};
in {

  packages = [
    pkgs.git
	pkgs.wget
    pkgs.gzip
    pkgs.gnutar
    pkgs.picotool
	## can only be used with release >0.8
    # pkgs-unstable.yosys
    # pkgs-unstable.nextpnrWithGui
    # pkgs.gtkwave
    # pkgs.iverilog
    # pkgs-unstable.openfpgaloader
  ];

  languages.c.enable = false;
  languages.nix.enable = true;
  languages.python = {
    enable = true;
    package = pkgs.python312;
    uv.enable = true;
    uv.package = unstablePkgs.uv;
    uv.sync.enable = true;
    uv.sync.allExtras = true;
  };

  processes = {
    serve_docs.exec = "serve_docs";
  };

  scripts = {
    serve_docs = {
      exec = "${unstablePkgs.uv}/bin/uv run sphinx-autobuild -j auto docs build/docs/";
    };
	flash_dirty_jtag = {
      exec = ''
        echo "$DEVENV_ROOT"
        if [[ ! -e $DEVENV_ROOT/build/dirtyJtag.uf2 ]]; then
            RELEASE=$(wget -qO- "https://api.github.com/repos/phdussud/pico-dirtyJtag/releases/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
            URL="https://github.com/phdussud/pico-dirtyJtag/releases/download/$RELEASE/dirtyJtag.uf2"
            echo "Downloading DirtyJTAG ($URL) ... "
            cd $DEVENV_ROOT/build && wget -q "$URL"
            echo "Done"
        else
            echo "RP2040 Executable found."
        fi
        picotool load --verify --force --execute $DEVENV_ROOT/build/dirtyJtag.uf2
      '';
      package = pkgs.bash;
    };
    get_latest_oss_cad_suite_release = {
      exec = ''
        echo $(wget -qO- "https://api.github.com/repos/YosysHQ/oss-cad-suite-build/releases/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
      '';
      package = pkgs.bash;
    };
    auto_download_build_tools = {
      exec = ''
        if [[ -e $DEVENV_ROOT/oss-cad-suite/VERSION ]]; then
            LATEST=$(get_latest_oss_cad_suite_release | tr -d "-")
            CURRENT=$(cat $DEVENV_ROOT/oss-cad-suite/VERSION)
            if [[ "$LATEST" != "$CURRENT" ]]; then
                read -p "You have currlenty Version $CURRENT of the oss-cad-suite installed. A newer version ($LATEST) is available. Do you want to update? (y/N)" confirm &&
                if [[ "$confirm" == [yY] ]]; then
                    download_build_tools
                fi
            fi
        else
            read -p "You don't have the oss-cad-suite installed. Do you want to install it? (y/N)" confirm && \
            if [[ "$confirm" == [yY] ]]; then
              download_build_tools
            fi
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

  tasks = let
    uv_run = "${unstablePkgs.uv}/bin/uv run";
  in {
    "check:fast-tests" = {
      exec = ''
        ${uv_run} coverage run
        ${uv_run} coverage xml
      '';
      before = ["check:tests"];
    };

    "package:build" = {
      exec = "${unstablePkgs.uv}/bin/uv build";
    };

    "docs:single-page" = {
      exec = ''
        export LC_ALL=C  # necessary to run in github action
        ${uv_run} sphinx-build -b singlehtml docs build/docs
      '';
    };
    "docs:build" = {
      exec = ''
        export LC_ALL=C  # necessary to run in github action
        ${uv_run} sphinx-build -j auto -b html docs build/docs
        touch build/docs/.nojekyll  # prevent github from trying to build the docs
      '';
    };
    "docs:clean" = {
      exec = ''
        rm -rf build/docs/*
      '';
    };
    "check:tests" = {
    };
  };
  
  enterShell = ''
    echo
    echo "Welcome Back!"
    echo
    auto_download_build_tools
    if [[ -e $DEVENV_ROOT/oss-cad-suite/environment ]]; then
      cd $DEVENV_ROOT && source oss-cad-suite/environment
    fi
  '';
}
