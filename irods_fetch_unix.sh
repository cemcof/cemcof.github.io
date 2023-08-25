# Invoke: curl -sSfL "https://raw.githubusercontent.com/cemcof/cemcof.github.io/main/irods_fetch_unix.sh" | bash -s --host "{host}" -t "{ticket}" -c {colleciton_path}

# Ensure irods module is installed 
if python3 -c "import irods" >/dev/null 2>&1; then
    echo "iRODS module found."
else
    echo "python-iordsclient is not installed. Installing..."
    python3 -m pip install python-irodsclient
fi


# Execute downloader from url
python_script_url="https://raw.githubusercontent.com/cemcof/cemcof.github.io/main/irods_fetch.py"
temp_file=$(mktemp)
curl -o "$temp_file" "$python_script_url"
python3 "$temp_file" "${args[@]}" # TODO args
rm "$temp_file"
