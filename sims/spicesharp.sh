# SpiceSharpParser: the newest SpiceSharp-Parser and SpiceSharpParser.CustomComponents
# from nuget behind the batch runner in sims/spicesharp/, published self-contained (no
# .NET runtime needed at run time). The SDK is installed into scratch for the build only.
# VERSION=3.4.1 builds against that SpiceSharp-Parser instead of the newest.
. "$(dirname "$0")/common.sh"

# newest stable version of a nuget package
nuget_latest() {
    curl -fsSL "https://api.nuget.org/v3-flatcontainer/$1/index.json" \
        | python3 -c 'import json,sys; print([v for v in json.load(sys.stdin)["versions"] if "-" not in v][-1])'
}

VERSION=${VERSION:-$(nuget_latest spicesharp-parser)}
CC_VERSION=$(nuget_latest spicesharpparser.customcomponents)
log "SpiceSharp-Parser $VERSION, SpiceSharpParser.CustomComponents $CC_VERSION"

PROJ=$REPO/sims/spicesharp
CHANNEL=$(grep -o '<TargetFramework>net[0-9.]*' "$PROJ/runner.csproj" | sed 's/.*>net//')
apt_install libicu-dev
retry curl -fsSL -o "$SRC/dotnet-install.sh" https://dot.net/v1/dotnet-install.sh
bash "$SRC/dotnet-install.sh" --channel "$CHANNEL" --install-dir "$SRC/dotnet" --no-path
export DOTNET_ROOT=$SRC/dotnet DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 \
    NUGET_PACKAGES=$SRC/nuget PATH="$SRC/dotnet:$PATH"
dotnet --version

PREFIX=$(prefix_for spicesharp "$VERSION")
rm -rf "$SRC/spicesharp" && cp -r "$PROJ" "$SRC/spicesharp"
dotnet publish "$SRC/spicesharp/runner.csproj" -c Release -r linux-x64 --self-contained \
    -p:SpiceSharpParserVersion="$VERSION" -p:CustomComponentsVersion="$CC_VERSION" \
    -o "$PREFIX/app"
ln -s ../app/spicesharp-runner "$PREFIX/bin/spicesharp"

{ echo "SpiceSharp-Parser $VERSION, SpiceSharpParser.CustomComponents $CC_VERSION, .NET $(dotnet --version)"
  echo "source: https://www.nuget.org/packages/SpiceSharp-Parser/$VERSION"; } > "$PREFIX/version"
finish spicesharp "$VERSION" "$PREFIX"

export PATH="$PREFIX/bin:$PATH"
smoke spicesharpparser_circuits_cookbook_pure_spice_loaded_voltage spicesharp loaded-voltage-divider.cir
smoke spicesharpparser_circuits_a_devices spicesharp --ltspice clock-divider.cir
d=$(mktemp -d)
printf 'broken netlist\nV1 1 0 1\nR1 1 0 undefined_param_xyz\nQ1 1 0 0 nomodel\n.OP\n.END\n' > "$d/bad.cir"
smoke "$d" spicesharp bad.cir
