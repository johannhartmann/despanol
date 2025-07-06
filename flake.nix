{
  description = "Python Tool for Phonetic Transliteration (German to Spanish)";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, uv2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python3;
        
        pythonEnv = python.withPackages (ps: with ps; [
          # Project dependencies
          nltk
          pyphen
          epitran
          pandas
          setuptools
          levenshtein
          appdirs
          
          # QA Tools
          black
          ruff
          mypy
          pytest
          pandas-stubs
          types-requests
        ]);
        
        pyprojectToml = builtins.fromTOML (builtins.readFile ./pyproject.toml);
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            pythonEnv
            uv
            git
          ];

          shellHook = ''
            echo "──────────────────────────────────"
            echo "      Despanol Development"
            echo "──────────────────────────────────"
            echo "QA tools available: black, ruff, mypy, pytest"
          '';

          PYTHONPATH = "./src";
        };
        
        packages.default = python.pkgs.buildPythonPackage {
          pname = "despanol";
          version = pyprojectToml.project.version;
          
          src = ./.;
          
          format = "pyproject";
          
          nativeBuildInputs = with python.pkgs; [
            hatchling
          ];
          
          propagatedBuildInputs = with python.pkgs; [
            nltk
            pyphen
            epitran
            pandas
            setuptools
            levenshtein
            appdirs
          ];
          
          meta = with pkgs.lib; {
            description = pyprojectToml.project.description;
            homepage = pyprojectToml.project.urls.Homepage;
            license = licenses.mit;
            maintainers = [];
          };
        };
      });
}
