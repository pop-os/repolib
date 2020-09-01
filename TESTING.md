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
sudo apt-manage -b deb http://example.com ubuntu main
```
Verify that the added repository matches the given input, and that there is a
commented-out `deb-src` repository with it. 

3. Test adding URLs

```
sudo apt-manage -b add http://example.com/ubuntu
```
Verify that the repository is correctly expanded to include the `deb` at the 
beginning, and the correct `{RELEASE} main` suites and components, where 
{RELEASE} matches the current version codename. Verify that a matching `deb-src`
entry is added as well in the command output. 