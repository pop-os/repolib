from pathlib import Path
import subprocess
import tempfile

import dbus

GPG_KEYBOX_CMD = [
    'gpg',
    '-q',
    '--no-options',
    '--no-default-keyring',
    '--batch'
]

GPG_KEYRING_CMD = [
    'gpg',
    '-q',
    '--no-options',
    '--no-default-keyring'
]

def add_key(key_file_path, key_data):
    import_dest = Path('/tmp', key_file_path.name)

    with tempfile.TemporaryDirectory() as tempdir:
        import_cmd = GPG_KEYBOX_CMD.copy()
        import_cmd += [f'--keyring={import_dest}', '--homedir', tempdir, '--import']
        export_cmd = GPG_KEYRING_CMD.copy()
        export_cmd += [f'--keyring={import_dest}', '--export']

        try:
            with open(key_file_path, mode='wb') as key_file:
                subprocess.run(import_cmd, check=True, input=key_data.encode())
                subprocess.run(export_cmd, check=True, stdout=key_file)
        except PermissionError:
            subprocess.run(import_cmd, check=True, input=key_data.encode())
            bus = dbus.SystemBus()
            privileged_object = bus.get_object('org.pop_os.repolib', '/Repo')
            export_cmd += [str(key_file_path)]
            privileged_object.add_apt_signing_key(export_cmd)
