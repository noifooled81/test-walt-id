{ pkgs, ... }:

{
  packages = with pkgs; [
    dotnet-sdk_10
    csharp-ls
    netcoredbg
  ];
}
