## Testing

The following components of RepoLib should be tested with each revision:

### CLI - apt-manage command

The `apt-manage` command should be tested every single revision to ensure that 
it is working correctly. This will also generally test that changes to the 
underlying library have not affected anything. 

#### Adding repositories

Adding repositories should be tested. 

1. Test Adding PPAs

```
sudo apt-manage -b add ppa:system76/proposed
```
Verify that the information output and the resulting deb lines (at the end of
the output) appear correct for the given PPA.

```
sudo apt-manage add -s ppa:system76/proposed
```
Verify that the `deb-src` is included in the `Types` field, then remove the 
repository: `sudo apt-manage remove ppa-system76-proposed`

```
sudo apt-manage add -d ppa:system76/proposed
```
Verify that the `Enabled` field is set to `no`, then remove the 
repository: `sudo apt-manage remove ppa-system76-proposed`

```
sudo apt-manage add ppa:system76/proposed
```
Verify that the command asks for verification before completing and displays
information about the PPA (similar to `add-apt-repository`). Verify that the 
command fetches the signing key and adds it to the system. Verify that the 
the correct `.list` file is added to `/etc/apt/sources.list.d`, then remove the 
repository: `sudo apt-manage remove ppa-system76-proposed`


2. Test adding deb repositories 

```
sudo apt-manage add --format list deb http://example.com/ubuntu focal main
```
Verify that the added repository matches the given input, and that there is a
commented-out `deb-src` repository with it. Ensure that the added repository 
file ends in `.list` and that the contents match legacy Deb format.

Remove the repository with `sudo apt-manage remove 

3. Test adding URLs

```
sudo apt-manage add --format list http://example.com/ubuntu
```
Verify that the repository is correctly expanded to include the `deb` at the 
beginning, and the correct `{RELEASE} main` suites and components, where 
{RELEASE} matches the current version codename. Verify that a matching `deb-src`
entry is added as well in the command output. 

4. Test adding Pop Development repositories

```
sudo apt-manage add popdev:master
```

Verify that the repository details are correct, that the `Signed-by` field 
points to `/etc/apt/keyrings/popdev-archive-keyring.gpg`, that the key file 
exists at that path. Then, delete the repostiory: 
```
sudo apt-manage remove popdev-master
```

#### Test Listing Details

1. Test that all repos are listed

```
apt-manage list
```
Verify that all configured repositories added to `/etc/apt/sources.list.d` are 
printed in the command output.

2. Test that details for all repositories are listed

```
apt-manage list -a
```

Verify that the specific configuration for each repository listed in step 1 is
presented in the output.

3. Test that details for a specific repository are listed

```
apt-manage list system
```

Verify that the detailed configuration for only the specified repository is 
listed in the output.


#### Removing repositories

1. Test cancelling removal

```
sudo apt-manage remove example-com-ubuntu
sudo apt-manage remove example-com-ubuntu
sudo apt-manage remove example-com-ubuntu
```

On the first run, enter 'n' and press enter. Verify that the source is not 
removed using `apt-manage list`.

On the second run, simply press enter. Verify that the source is not removed by
using `apt-manage list`.

On the third run, enter 'v' and press enter. Verify that the source is not removed by
using `apt-manage list`.

2. Test removing sources

```
sudo apt-manage remove example-com-ubuntu
```

Enter 'y'. Verify that the source is removed using `apt-manage list`.

3. Verify protection of system sources

```
sudo apt-manage remove system
```

Verify that the command returns an error and that no action is taken (even if a
system.sources file does not exist) using `apt-manage list`


#### Modifying a repository

##### Setup

Add a testing repository:

```
sudo apt-manage add popdev:master
apt-manage list popdev-master
```
Verify that the details are correct in the output.

1. Change Repository Name

```
sudo apt-manage modify popdev-master --name 'Testing Repo'
apt-manage list popdev-master
```

Verify that the name was updated in the final output to match the given input
`Testing Repo`

2. Disable Repository

```
sudo apt-manage modify popdev-master --disable
apt-manage list popdev-master
```
Ensure that the repository is now listed as `Enabled: no`.

3. Add/Remove URI

```
sudo apt-manage modify popdev-master --add-uri http://example.com/
apt-manage list popdev-master
```
Ensure that the `http://example.com` URI was added to the source.

```
sudo apt-manage modify popdev-master --remove-uri http://example.com
apt-manage list popdev-master
```
Ensure that the `http://example.com` URI was removed.

4. Add/Remove Suite

```
sudo apt-manage modify popdev-master --add-suite xenial
apt-manage list popdev-master
```
Ensure that the suite `xenial` was added to the source.

```
sudo apt-manage modify popdev-master --remove-suite xenial
apt-manage list popdev-master
```

Ensure that the suite `xenial` was removed from the source.

5. Add/Remove Components

```
sudo apt-manage modify popdev-master --add-component 'universe multiverse'
apt-manage list popdev-master
```
Ensure that the components `universe` and `multiverse` were added to the source.

```
sudo apt-manage modify popdev-master --remove-component 'main multiverse'
apt-manage list popdev-master
```
Ensure that the components `main` and `multiverse` were removed from the source.


#### Enabling/Disabling Source Code

##### Setup

Add a testing repository:

```
apt-manage list popdev-master
```
Verify that the details are correct in the output and that `Types:` is just 
`deb`.

1. Enable source code for one repo

```
sudo apt-manage modify --source-enable popdev-master
apt-manage list popdev-master
```
Verify that the `Types:` is now `deb deb-src`.

2. Disable source code for one repo

```
sudo apt-manage modify --source-disable popdev-master
apt-manage list popdev-master
```
Verify that the `Types:` is now just `deb`.

Finally, remove the testing repository: 
```
sudo apt-manage remove popdev-master
```

### Installation/upgrading (packaging tests)

_This section is to test the installation behavior of the Debian package,
and doesn't need to be run for changes to repolib itself._

**Confirm add-apt-repository is installed when software-properties-common is not installed:**

- [ ] Make sure `software-properties-common` is not installed.
- [ ] Remove `python3-repolib` with `sudo dpkg -r --force-all python3-repolib`.
- [ ] Ensure `/usr/bin/add-apt-repository` doesn't exist (if it does, remove it.)
- [ ] Install `python3-repolib` (can be done with `sudo apt install -f`).
- [ ] Ensure `/usr/bin/add-apt-repository` exists and is a link to `/usr/lib/repolib/add-apt-repository`.

**Confirm add-apt-repository is not installed when software-properties-common is installed:**

- [ ] Remove `python3-repolib` with `sudo dpkg -r --force-all python3-repolib`.
- [ ] Ensure `/usr/bin/add-apt-repository` doesn't exist (if it does, remove it.)
- [ ] Install `software-properties-common`, confirm `/usr/bin/add-apt-repository` now exists and is not a link.
    - Can be done with `apt download software-properties-common python3-software-properties`
      followed by `dpkg -i` on the downloaded files.
- [ ] Install `python3-repolib` again, confirm `/usr/bin/add-apt-repository` still isn't a link.

**Confirm add-apt-repository is installed when software-properties-common is removed:**

- [ ] Remove `software-properties-common` and confirm that `/usr/bin/add-apt-repository` still exists and is now a link.
