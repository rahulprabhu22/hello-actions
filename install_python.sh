PYTHON_FULL_VERSION=$1
echo $PYTHON_FULL_VERSION
MAJOR_VERSION=$(echo $PYTHON_FULL_VERSION | cut -d '.' -f 1)
MINOR_VERSION=$(echo $PYTHON_FULL_VERSION | cut -d '.' -f 2)
PATCH_VERSION=$(echo $PYTHON_FULL_VERSION | cut -d '.' -f 3)
[[ -z "$PATCH_VERSION" ]] && PATCH_VERSION=0
mkdir -p /tools/Python
cd  /tools/Python
curl -s https://raw.githubusercontent.com/actions/python-versions/main/versions-manifest.json > py_versions.json
PY_RELEASE_URL=$(cat py_versions.json | jq -r '.[] | select(.version=="'$PYTHON_FULL_VERSION'") | .files | .[] | select( (.platform=="linux") and .platform_version=="20.04") | .download_url')
[[ -z "$PY_RELEASE_URL" ]] && echo "Python Version $PYTHON_FULL_VERSION NOT FOUND" && exit 1;
echo "Downloading Python Version: $PYTHON_FULL_VERSION"
wget --quiet -O "Python$PYTHON_FULL_VERSION.tar.gz" $PY_RELEASE_URL
cd  /tools/Python
echo "Extracting Python Version: $PYTHON_FULL_VERSION"
tar xzf "Python$PYTHON_FULL_VERSION.tar.gz"
cp "lib/libpython$MAJOR_VERSION.$MINOR_VERSION.so.1.0" /usr/lib
cd bin
ln -s "python$MAJOR_VERSION.$MINOR_VERSION" python
echo "Installing PIP"
./python -m ensurepip
./python -m pip install --ignore-installed pip --disable-pip-version-check --no-warn-script-location
export PATH="$PATH:$(pwd)"
