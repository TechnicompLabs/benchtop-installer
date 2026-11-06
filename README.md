# benchtop-installer

`tik-config-benchtop`: the configuration and modules of [tik](https://github.com/sysrich/tik), the installer of the Technicomp Benchtop Linux self-installing USB image ([benchtop-image](https://github.com/TechnicompLabs/benchtop-image)). Built on OBS (home:technicomp:benchtop) from this repository through scmsync. It takes the place of `tik-config-generic`, as `tik-config-Aeon` does for Aeon, and the image installs it in place of the files its `config.sh` used to write. tik's own modules (`tik-module-encrypt`, `tik-module-setup-gnome-env`, `tik-module-welcome`, `tik-module-sicu`) are required unchanged.

The files are a filesystem tree (`usr/`, `etc/`) that mirrors their install paths; the spec installs the tree verbatim.

## Contents

- `etc/tik/config` - tik's settings: the system's name, the bug-report address and the name of the unlocked root device (`benchtop_root`, also the root partition's label, so the text password prompt at boot names the disk once). tik reads `/usr/lib/tik/config` first and this file second; the first is `tik-config-generic`'s, copied at build time.
- `usr/lib/repart.d/` - the target disk's layout for systemd-repart, from Aeon's `systemd-repart-branding-Aeon`: a new ESP, and a new Btrfs root whose subvolumes and first snapshot repart creates and then fills file by file from the running USB (`CopyFiles=`), then encrypts. `ExcludeFiles=` leaves out the installer's own files (the tik account, its sudo and polkit rules, `/ignition`), and the live session's zypper and man caches and journal. TCBL changes: `Label=benchtop_root`, and `discard=async` on every `MountPoint=`, because systemd-repart's generated fstab puts a plain `discard` first, which on Btrfs is synchronous discard and made an installed system stall ([systemd issue 38829](https://github.com/systemd/systemd/issues/38829)); Btrfs applies the later `discard=async`.
- `usr/lib/tik/modules/` - modules that must run before particular tik modules, since tik reads `/usr/lib/tik/modules/<phase>` before `/etc/tik/modules/<phase>`:
  - `pre/01-tcbl-exit` - back to the login screen when the installer is cancelled or fails
  - `pre/06-tcbl-wallpaper` - the navy board background in the installer's session
  - `post/12-tcbl-machine-id` - the installed system gets its own machine ID
  - `post/13-tcbl-no-memtest` - no memtest86+ boot entry on the installed system
  - `post/14-tcbl-package-sets` - installs the optional package sets chosen before the copy
- `etc/tik/modules/` - modules with no ordering need:
  - `pre/20-tcbl-package-sets` - offers the optional package sets and resolves them before the disk is erased
  - `pre/22-tcbl-hostname`, `post/18-tcbl-hostname` - asks for the host name and writes it
  - `pre/90-tcbl-repart-prep` - shows the details window and the copy's progress, and has mkfs.btrfs skip its own discard (systemd-repart has already discarded the disk)
  - `post/16-tcbl-passphrase` - with the TPM in use, offers a disk password of the user's own, alongside the recovery key
  - `post/17-tcbl-live-cleanup` - removes the "Create User" account, its sudo rule, the passwordless GDM rule and the live session's log files from the installed system
  - `post/19-tcbl-autorelabel` - the installed system relabels its files for SELinux at its first boot
- `usr/libexec/tcbl/` - `copy-progress`, which reports the copy's progress from the bytes mkfs.btrfs has read against the size the image records in `/usr/share/tcbl/copy-bytes`; `create-user` and `create-user-dialog`, the live USB's "Create User" session
- `usr/share/licenses/tik-config-benchtop/tik.LICENSE` - tik's license, for the two functions copied from tik

The live USB's accounts ("Install Benchtop" and "Create User"), their sudo, polkit and GDM rules, and the size of the copy stay in the image's `config.sh`, because they belong to that image alone.

## License

MIT. The functions copied from tik are tik's (MIT, SUSE LLC and Richard Brown).

## Copies of upstream files

`90-tcbl-repart-prep` and `01-tcbl-exit` replace tik's `dump_image_repart_self` and `cleanup` with changed copies, and `usr/lib/repart.d/` is a changed copy of Aeon's layout (`systemd-repart-branding-Aeon`). The spec's `%check` compares the upstream originals with the checksums of the versions the copies are based on and stops the build when one changes, so that the copy is re-synced. OBS rebuilds the package when tik or `systemd-repart-branding-Aeon` changes.
