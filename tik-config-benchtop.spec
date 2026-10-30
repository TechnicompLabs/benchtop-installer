#
# spec file for package tik-config-benchtop
# Technicomp Benchtop Linux - the configuration and modules of tik, the
# installer of the self-installing USB image.
#
# Built directly from git (OBS scmsync). The files are laid out in this
# repository as a filesystem tree (usr/, etc/) that mirrors their install
# paths; the spec installs that tree verbatim, as tc-benchtop-settings does.
#
Name:           tik-config-benchtop
Version:        0.1.0
Release:        0
Summary:        Technicomp Benchtop Linux configuration and modules for tik
# MIT; pre/15-encrypt and post/15-encrypt are tik's modules (MIT, SUSE LLC and
# Richard Brown), the second with one TCBL change
License:        MIT
URL:            https://github.com/TechnicompLabs/benchtop-installer
BuildArch:      noarch
# tik's configuration, as tik-config-generic and tik-config-Aeon provide it
Provides:       tik-config
Conflicts:      tik-config
# tik's own modules, unchanged
Requires:       tik
Requires:       tik-module-setup-gnome-env
Requires:       tik-module-sicu
Requires:       tik-module-welcome
# this package carries both encryption modules, the post-install one with a
# TCBL change, in place of tik-module-encrypt
Conflicts:      tik-module-encrypt
# the encryption modules: TPM detection and enrollment, the recovery key's QR
# code, the Secure Boot state; 10-welcome: the AC power check
Requires:       mokutil
Requires:       qrencode
Requires:       tpm2.0-tools
Requires:       upower
# TCBL modules: the installer background (gsettings), copy progress (pgrep),
# the optional package sets (zypper)
Requires:       glib2-tools
Requires:       procps
Requires:       zypper
# /usr/lib/tik/config is tik-config-generic's, copied at build time
BuildRequires:  tik-config-generic

%description
The configuration and modules of tik for the Technicomp Benchtop Linux
self-installing USB image: the target disk's layout for systemd-repart
(discard=async, live-session caches left out), a details window and copy
progress during installation, the optional package sets, the host name,
removal of the live USB's accounts and log files from the installed system, an
SELinux relabel at its first boot, its own machine ID, no memtest86+ entry,
and a return to the login screen when the installer is cancelled. It also
carries the live USB's "Create User" helpers.

%prep
# nothing to unpack - the files are a tree in the scm checkout

%build
# nothing to build

%install
treeroot=
for base in "%{_sourcedir}" "%{_sourcedir}/%{name}-%{version}" "%{_topdir}/SOURCES" "%{_builddir}/%{name}-%{version}" "%{_builddir}" "$PWD"; do
    if [ -d "$base/usr" ] && [ -d "$base/etc" ]; then
        treeroot="$base"
        break
    fi
done
if [ -z "$treeroot" ]; then
    echo "ERROR: file tree (usr/ etc/) not found under the build sources" >&2
    exit 1
fi
install -d "%{buildroot}"
( cd "$treeroot" && cp -a --no-preserve=ownership usr etc "%{buildroot}/" )
chmod 0755 %{buildroot}%{_libexecdir}/tcbl/copy-progress \
    %{buildroot}%{_libexecdir}/tcbl/create-user \
    %{buildroot}%{_libexecdir}/tcbl/create-user-dialog
# tik reads /usr/lib/tik/config, then /etc/tik/config; the first is
# tik-config-generic's
install -D -m 0644 %{_prefix}/lib/tik/config %{buildroot}%{_prefix}/lib/tik/config
# the image measures the size of the copy into this directory
install -d %{buildroot}%{_datadir}/tcbl

%files
%dir %{_defaultlicensedir}/%{name}
%license %{_defaultlicensedir}/%{name}/tik.LICENSE
# tik's configuration
%{_prefix}/lib/tik/config
%dir %{_sysconfdir}/tik
%config(noreplace) %{_sysconfdir}/tik/config
# modules that must run before tik's own (tik reads /usr/lib/tik/modules/<phase>
# before /etc/tik/modules/<phase>)
%{_prefix}/lib/tik/modules/pre/01-tcbl-exit
%{_prefix}/lib/tik/modules/pre/06-tcbl-wallpaper
%{_prefix}/lib/tik/modules/pre/15-encrypt
%{_prefix}/lib/tik/modules/post/12-tcbl-machine-id
%{_prefix}/lib/tik/modules/post/13-tcbl-no-memtest
%{_prefix}/lib/tik/modules/post/14-tcbl-package-sets
%{_prefix}/lib/tik/modules/post/15-encrypt
# modules with no ordering need
%dir %{_sysconfdir}/tik/modules
%dir %{_sysconfdir}/tik/modules/pre
%dir %{_sysconfdir}/tik/modules/post
%config %{_sysconfdir}/tik/modules/pre/20-tcbl-package-sets
%config %{_sysconfdir}/tik/modules/pre/22-tcbl-hostname
%config %{_sysconfdir}/tik/modules/pre/90-tcbl-repart-prep
%config %{_sysconfdir}/tik/modules/post/17-tcbl-live-cleanup
%config %{_sysconfdir}/tik/modules/post/18-tcbl-hostname
%config %{_sysconfdir}/tik/modules/post/19-tcbl-autorelabel
# the target disk's layout
%dir %{_prefix}/lib/repart.d
%{_prefix}/lib/repart.d/00-esp.conf
%{_prefix}/lib/repart.d/50-root.conf
# copy progress, and the live USB's "Create User" helpers
%dir %{_libexecdir}/tcbl
%{_libexecdir}/tcbl/copy-progress
%{_libexecdir}/tcbl/create-user
%{_libexecdir}/tcbl/create-user-dialog
%dir %{_datadir}/tcbl

%changelog
