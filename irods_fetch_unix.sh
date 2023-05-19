

if python3 -c "import irods" >/dev/null 2>&1; then
    echo "iRODS module found."
else
    echo "python-iordsclient is not installed. Installing..."
    pip3 install python-irodsclient
fi

python3 --host kkk -c kk <(curl -s https://raw.githubusercontent.com/cemcof/cemcof.github.io/main/irods_fetch.py)

# Exec from url: https://raw.githubusercontent.com/cemcof/cemcof.github.io/main/irods_fetch_unix.sh