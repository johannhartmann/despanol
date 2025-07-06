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
            echo "──────────────��───────────────────"
            echo "Despanol Development Environment"
            echo "──────────────────────────────────"
            echo "Python: ${python.version}"
            echo ""
          '';

          PYTHONPATH = ".";
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