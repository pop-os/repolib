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
sudo apt-manage -b add -s ppa:system76/proposed
```
Verify that the `deb-src` repository is uncommented in the command output.

```
sudo apt-manage -b add -d ppa:system76/proposed
```
Verify that both `deb-src` and `deb` repositories are commented out in the 
command output.

After each of the preceeding tests, ensure that no changes are made to the 
system in `/etc/apt/sources.list.d`

```
sudo apt-manage add -e ppa:system76/proposed
```
Verify that the command asks for verification before completing and displays
information about the PPA (similar to `add-apt-repository`). Verify that the 
command fetches the signing key and adds it to the system. Verify that the 
the correct `.list` file is added to `/etc/apt/sources.list.d`


2. Test adding deb repositories 

```
sudo apt-manage add deb http://example.com/ubuntu focal main
```
Verify that the added repository matches the given input, and that there is a
commented-out `deb-src` repository with it. 

3. Test adding URLs

```
sudo apt-manage add http://example.com/ubuntu
```
Verify that the repository is correctly expanded to include the `deb` at the 
beginning, and the correct `{RELEASE} main` suites and components, where 
{RELEASE} matches the current version codename. Verify that a matching `deb-src`
entry is added as well in the command output. 

#### Test Listing Details

1. Test that all repos are listed

```
apt-manage list
```
Verify that all 3rd-party repositories added to `/etc/apt/sources.list.d` are 
printed in the command output.

2. Test that details for all repositories are listed

```
apt-manage list -v
```

Verify that the specific configuration for each repository listed in step 1 is
presented in the output.

3. Test that details for a specific repository are listed

```
apt-manage list example-com-ubuntu
```

Verify that the detailed configuration for only the specified repository is 
listed in the output.

4. Test that contents of `/etc/apt/sources.list` are output

```
apt-manage list -l
cat /etc/apt/sources.list
```

Verify that in addition to the main sources, the repositories in the system-wide
`/etc/apt/sources.list` are presented in the output, and that they match the 
entries in the file.

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

On the third run, enter 'v' and press enter. Verify that the prompt re-appears
and waits for valid input ('y', 'n', or Enter).

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
sudo apt-manage add ppa:system76/proposed
apt-manage list ppa-system76-proposed
```
Verify that the details are correct in the output.

1. Change Repository Name

```
sudo apt-manage modify ppa-system76-proposed --name 'Testing Repo'
apt-manage list ppa-system76-proposed
```

Verify that the name was updated in the final output to match the given input
`Testing Repo`

2. Disable Repository

```
sudo apt-manage modify ppa-system76-proposed --disable
apt-manage list ppa-system76-proposed
```
Ensure that the repository is now listed as `Enabled: no`.

3. Add/Remove URI

```
sudo apt-manage modify ppa-system76-proposed --add-uri http://example.com/
apt-manage list ppa-system76-proposed
```
Ensure that the `http://example.com` URI was added to the source.

```
sudo apt-manage modify ppa-system76-proposed --remove-uri http://example.com
apt-manage list ppa-system76-proposed
```
Ensure that the `http://example.com` URI was removed.

4. Add/Remove Suite

```
sudo apt-manage modify ppa-system76-proposed --add-suite xenial
apt-manage list ppa-system76-proposed
```
Ensure that the suite `xenial` was added to the source.

```
sudo apt-manage modify ppa-system76-proposed --remove-suite xenial
apt-manage list ppa-system76-proposed
```

Ensure that the suite `xenial` was removed from the source.

5. Add/Remove Components

```
sudo apt-manage modify ppa-system76-proposed --add-component 'universe multiverse'
apt-manage list ppa-system76-proposed
```
Ensure that the components `universe` and `multiverse` were added to the source.

```
sudo apt-manage modify ppa-system76-proposed --remove-component 'main multiverse'
apt-manage list ppa-system76-proposed
```
Ensure that the components `main` and `multiverse` were removed from the source.


#### Enabling/Disabling Source Code

##### Setup

Add a testing repository:

```
sudo apt-manage add ppa:system76/proposed
apt-manage list ppa-system76-proposed
```
Verify that the details are correct in the output and that `Types:` is just 
`deb`.

1. Enable source code for one repo

```
sudo apt-manage source -e ppa-system76-proposed
apt-manage list ppa-system76-proposed
```
Verify that the `Types:` is now `deb deb-src`.

2. Disable source code for one repo

```
sudo apt-manage source -d ppa-system76-proposed
apt-manage list ppa-system76-proposed
```
Verify that the `Types:` is now just `deb`.
