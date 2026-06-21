{
  description = "Thunder build environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
  };

  outputs = { self, nixpkgs }:
    let
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
    in {
      devShells.x86_64-linux.default = pkgs.mkShell {
        buildInputs = with pkgs; [
          go
          pkg-config
          gtk3
          webkitgtk_4_0
          gobject-introspection
        ];

        shellHook = ''
          export PATH=$HOME/go/bin:$PATH
        '';
      };
    };
}
