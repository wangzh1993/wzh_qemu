# Build time setting
%define rhev 0

#%bcond_with     guest_agent     # disabled
%bcond_without     guest_agent     # disabled

%global SLOF_gittagdate 20120731

%global have_usbredir 1

%ifarch %{ix86} x86_64
    %global have_seccomp 1
    %global have_spice   1
%else
    %global have_usbredir 0
%endif

%ifnarch s390 s390x
    %global have_librdma 1
    %global have_tcmalloc 1
%endif

%ifnarch x86_64
    %global build_only_sub 1
%endif

%ifarch %{ix86}
    %global kvm_target    i386
%endif
%ifarch x86_64
    %global kvm_target    x86_64
%endif
%ifarch %{power64}
    %global kvm_target    ppc64
%endif
%ifarch s390x s390
    %global kvm_target    s390x
%endif
%ifarch ppc
    %global kvm_target    ppc
%endif
%ifarch aarch64
    %global kvm_target    aarch64
%endif

#Versions of various parts:

%define pkgname qemu-kvm
%define rhel_suffix -rhel
%define rhev_suffix -rhev

# Setup for RHEL/RHEV package handling
# We need to define tree suffixes:
# - pkgsuffix:             used for package name
# - extra_provides_suffix: used for dependency checking of other packages
# - conflicts_suffix:      used to prevent installation of both RHEL and RHEV

%if %{rhev}
    %global pkgsuffix %{rhev_suffix}
    %global extra_provides_suffix %{nil}
    %global conflicts_suffix %{rhel_suffix}
    %global obsoletes_version 15:0-0
%else
    %global pkgsuffix %{nil}
    %global extra_provides_suffix %{rhel_suffix}
    %global conflicts_suffix %{rhev_suffix}
%endif

# Macro to properly setup RHEL/RHEV conflict handling
%define rhel_rhev_conflicts()                                         \
Conflicts: %1%{conflicts_suffix}                                      \
Provides: %1%{extra_provides_suffix} = %{epoch}:%{version}-%{release} \
    %if 0%{?obsoletes_version:1}                                          \
Obsoletes: %1 < %{obsoletes_version}                                      \
    %endif

Summary: QEMU is a machine emulator and virtualizer
Name: %{pkgname}%{?pkgsuffix}
Version: 2.5.1
Release: 141%{?dist}.1
# Epoch because we pushed a qemu-1.0 package. AIUI this can't ever be dropped
Epoch: 10
License: GPLv2+ and LGPLv2+ and BSD
Group: Development/Tools
URL: http://www.qemu.org/
ExclusiveArch: x86_64 %{power64} aarch64 s390x
Requires: seabios-bin >= 1.7.2.2-5
Requires: sgabios-bin
Requires: seavgabios-bin
Requires: ipxe-roms-qemu
Requires: %{pkgname}-common%{?pkgsuffix} = %{epoch}:%{version}-%{release}
        %if 0%{?have_seccomp:1}
Requires: libseccomp >= 1.0.0
        %endif
%if 0%{!?build_only_sub:1}
Requires: glusterfs-api >= 3.6.0
%endif
Requires: libusbx >= 1.0.19
# OOM killer breaks builds with parallel make on s390(x)
%ifarch s390 s390x
    %define _smp_mflags %{nil}
%endif

Source0: /root/rpmbuild/SOURCES/qemu-2.5.1.tar.xz

Source1: qemu.binfmt
# Loads kvm kernel modules at boot
# Not needed anymore - required only for kvm on non i86 archs 
# where we do not ubuild kvm
# Source2: kvm.modules
# Creates /dev/kvm
Source3: 80-kvm.rules
# KSM control scripts
Source4: ksm.service
Source5: ksm.sysconfig
Source6: ksmctl.c
Source7: ksmtuned.service
Source8: ksmtuned
Source9: ksmtuned.conf
Source10: qemu-guest-agent.service
Source11: 99-qemu-guest-agent.rules
Source12: bridge.conf
Source13: qemu-ga.sysconfig
#Source14: efi-virtio.rom
#Source15: efi-pcnet.rom
#Source16: efi-rtl8139.rom
#Source17: efi-ne2k_pci.rom
#Source18: bios-256k.bin
Source19: README.rhel6-gpxe-source
#Source20: efi-e1000.rom
#Source21: sample_images.tar
#Source22: efi-eepro100.rom

# libcacard build fixes (heading upstream)
# Patch1: 0000-libcacard-fix-missing-symbols-in-libcacard.so.patch

# Fix migration from qemu-kvm 1.2 to qemu 1.3
#Patch3: 0002-Fix-migration-from-qemu-kvm-1.2.patch

# Flow control series
#Patch4: 0100-char-Split-out-tcp-socket-close-code-in-a-separate-f.patch
#Patch5: 0101-char-Add-a-QemuChrHandlers-struct-to-initialise-char.patch
#Patch6: 0102-iohandlers-Add-enable-disable_write_fd_handler-funct.patch
#Patch7: 0103-char-Add-framework-for-a-write-unblocked-callback.patch
#Patch8: 0104-char-Update-send_all-to-handle-nonblocking-chardev-w.patch
#Patch9: 0105-char-Equip-the-unix-tcp-backend-to-handle-nonblockin.patch
#Patch10: 0106-char-Throttle-when-host-connection-is-down.patch
#Patch11: 0107-virtio-console-Enable-port-throttling-when-chardev-i.patch
#Patch12: 0108-spice-qemu-char.c-add-throttling.patch
#Patch13: 0109-spice-qemu-char.c-remove-intermediate-buffer.patch
#Patch14: 0110-usb-redir-Add-flow-control-support.patch
#Patch15: 0111-char-Disable-write-callback-if-throttled-chardev-is-.patch
#Patch16: 0112-hw-virtio-serial-bus-replay-guest-open-on-destinatio.patch

# Migration compatibility
#Patch17: configure-add-enable-migration-from-qemu-kvm.patch
#Patch18: acpi_piix4-condition-on-minimum_version_id.patch
#Patch19: i8254-fix-migration-from-qemu-kvm-1.1.patch
#Patch20: pc_piix-add-compat-handling-for-qemu-kvm-vga-mem-size.patch
#Patch21: qxl-add-rom_size-compat-property.patch
#Patch22: docs-fix-generating-qemu-doc.html-with-texinfo5.patch
#Patch23: rtc-test-Fix-test-failures-with-recent-glib.patch
#Patch24: iscsi-look-for-pkg-config-file-too.patch
#Patch25: tcg-fix-occcasional-tcg-broken-problem.patch
#Patch26: qxl-better-vga-init-in-enter_vga_mode.patch

# Enable/disable supported features
#Patch27: make-usb-devices-configurable.patch
#Patch28: fix-scripts-make_device_config-sh.patch


BuildRequires: zlib-devel
BuildRequires: SDL-devel
BuildRequires: which
BuildRequires: gnutls-devel
BuildRequires: cyrus-sasl-devel
BuildRequires: libtool
BuildRequires: libaio-devel
BuildRequires: rsync
BuildRequires: python
BuildRequires: pciutils-devel
BuildRequires: pulseaudio-libs-devel
BuildRequires: libiscsi-devel
BuildRequires: ncurses-devel
BuildRequires: libattr-devel
BuildRequires: libusbx-devel
%if 0%{?have_usbredir:1}
BuildRequires: usbredir-devel >= 0.6
%endif
BuildRequires: texinfo
%if 0%{!?build_only_sub:1}
    %if 0%{?have_spice:1}
BuildRequires: spice-protocol >= 0.12.2
BuildRequires: spice-server-devel >= 0.12.0
    %endif
%endif
%if 0%{?have_seccomp:1}
BuildRequires: libseccomp-devel >= 1.0.0
%endif
%if 0%{?have_tcmalloc:1}
BuildRequires: gperftools-devel
%endif
# For network block driver
BuildRequires: libcurl-devel
%ifarch x86_64
BuildRequires: librados2-devel
BuildRequires: librbd1-devel
%endif
%if 0%{!?build_only_sub:1}
# For gluster block driver
BuildRequires: glusterfs-api-devel >= 3.6.0
BuildRequires: glusterfs-devel
%endif
# We need both because the 'stap' binary is probed for by configure
BuildRequires: systemtap
BuildRequires: systemtap-sdt-devel
# For smartcard NSS support
BuildRequires: nss-devel
# For XFS discard support in raw-posix.c
# For VNC JPEG support
BuildRequires: libjpeg-devel
# For VNC PNG support
BuildRequires: libpng-devel
# For uuid generation
BuildRequires: libuuid-devel
# For BlueZ device support
BuildRequires: bluez-libs-devel
# For Braille device support
BuildRequires: brlapi-devel
# For test suite
BuildRequires: check-devel
# For virtfs
BuildRequires: libcap-devel
# Hard requirement for version >= 1.3
BuildRequires: pixman-devel
# Documentation requirement
BuildRequires: perl-podlators
BuildRequires: texinfo
# For rdma
%if 0%{?have_librdma:1}
# BuildRequires: rdma-core-devel
BuildRequires: libibverbs-devel
%endif
# cpp for preprocessing option ROM assembly files
%ifarch %{ix86} x86_64
BuildRequires: cpp
%endif
%if 0%{!?build_only_sub:1}
# For compressed guest memory dumps
BuildRequires: lzo-devel snappy-devel
%endif
BuildRequires: libssh2-devel
BuildRequires: libcurl-devel


%if 0%{!?build_only_sub:1}
Requires: qemu-img = %{epoch}:%{version}-%{release}
%endif

# RHEV-specific changes:
# We provide special suffix for qemu-kvm so the conflit is easy
# In addition, RHEV version should obsolete all RHEL version in case both
# RHEL and RHEV channels are used
%rhel_rhev_conflicts qemu-kvm


%define qemudocdir %{_docdir}/%{pkgname}

%description
qemu-kvm%{?pkgsuffix} is an open source virtualizer that provides hardware
emulation for the KVM hypervisor. qemu-kvm%{?pkgsuffix} acts as a virtual
machine monitor together with the KVM kernel modules, and emulates the
hardware for a full system such as a PC and its associated peripherals.

%package -n qemu-img%{?pkgsuffix}
Summary: QEMU command line tool for manipulating disk images
Group: Development/Tools

%rhel_rhev_conflicts qemu-img

%description -n qemu-img%{?pkgsuffix}
This package provides a command line tool for manipulating disk images.

%if 0%{!?build_only_sub:1}
%package -n qemu-kvm-common%{?pkgsuffix}
Summary: QEMU common files needed by all QEMU targets
Group: Development/Tools
Requires(post): /usr/bin/getent
Requires(post): /usr/sbin/groupadd
Requires(post): /usr/sbin/useradd
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

%rhel_rhev_conflicts qemu-kvm-common

%description -n qemu-kvm-common%{?pkgsuffix}
qemu-kvm is an open source virtualizer that provides hardware emulation for
the KVM hypervisor. 

This package provides documentation and auxiliary programs used with qemu-kvm.

%endif

%if %{with guest_agent}
%package -n qemu-guest-agent
Summary: QEMU guest agent
Group: System Environment/Daemons
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

%description -n qemu-guest-agent
qemu-kvm is an open source virtualizer that provides hardware emulation for
the KVM hypervisor. 

This package provides an agent to run inside guests, which communicates
with the host over a virtio-serial channel named "org.qemu.guest_agent.0"

This package does not need to be installed on the host OS.

%post -n qemu-guest-agent
%systemd_post qemu-guest-agent.service

%preun -n qemu-guest-agent
%systemd_preun qemu-guest-agent.service

%postun -n qemu-guest-agent
%systemd_postun_with_restart qemu-guest-agent.service

%endif

%if 0%{!?build_only_sub:1}
%package -n qemu-kvm-tools%{?pkgsuffix}
Summary: KVM debugging and diagnostics tools
Group: Development/Tools

%rhel_rhev_conflicts qemu-kvm-tools

%description -n qemu-kvm-tools%{?pkgsuffix}
This package contains some diagnostics and debugging tools for KVM,
such as kvm_stat.
%endif

%prep
%setup -q -n qemu-%{version}
# cp %{SOURCE18} pc-bios # keep "make check" happy
# tar -xf %{SOURCE21}
#%patch1 -p1
#%%patch2 -p1
#%%patch3 -p1
#%%patch4 -p1
#%%patch5 -p1
#%%patch6 -p1
#%%patch7 -p1
#%%patch8 -p1
#%%patch9 -p1
#%%patch10 -p1
#%%patch11 -p1
#%%patch12 -p1
#%%patch13 -p1
#%%patch14 -p1
#%%patch15 -p1
#%%patch16 -p1
#%%patch17 -p1
#%%patch18 -p1
#%%patch19 -p1
#%%patch20 -p1
#%%patch21 -p1
#%%patch22 -p1
#%%patch23 -p1
#%%patch24 -p1
#%%patch25 -p1
#%%patch26 -p1
#%%patch27 -p1
#%%patch28 -p1

%build
buildarch="%{kvm_target}-softmmu"

# --build-id option is used for giving info to the debug packages.
extraldflags="-Wl,--build-id";
buildldflags="VL_LDFLAGS=-Wl,--build-id"

# QEMU already knows how to set _FORTIFY_SOURCE
%global optflags %(echo %{optflags} | sed 's/-Wp,-D_FORTIFY_SOURCE=2//')

%ifarch s390
    # drop -g flag to prevent memory exhaustion by linker
    %global optflags %(echo %{optflags} | sed 's/-g//')
    sed -i.debug 's/"-g $CFLAGS"/"$CFLAGS"/g' configure
%endif

dobuild() {
%if 0%{!?build_only_sub:1}
    ./configure \
        --prefix=%{_prefix} \
        --libdir=%{_libdir} \
        --sysconfdir=%{_sysconfdir} \
        --interp-prefix=%{_prefix}/qemu-%%M \
        --audio-drv-list=pa,alsa \
        --with-confsuffix=/%{pkgname} \
        --localstatedir=%{_localstatedir} \
        --libexecdir=%{_libexecdir} \
        --with-pkgversion=%{pkgname}-%{version}-%{release} \
        --disable-strip \
        --disable-qom-cast-debug \
        --extra-ldflags="$extraldflags -pie -Wl,-z,relro -Wl,-z,now" \
        --extra-cflags="%{optflags} -fPIE -DPIE" \
        --enable-trace-backend=dtrace \
        --enable-werror \
        --disable-xen \
        --disable-virtfs \
        --enable-kvm \
        --enable-libusb \
        --enable-spice \
        --enable-seccomp \
        --enable-docs \
        --disable-sdl \
        --disable-debug-tcg \
        --disable-sparse \
        --disable-brlapi \
        --disable-bluez \
        --disable-vde \
        --disable-curses \
        --enable-curl \
        --enable-libssh2 \
        --enable-vnc \
        --enable-vnc-sasl \
        --enable-linux-aio \
        --enable-lzo \
        --enable-snappy \
        --enable-usb-redir \
        --enable-vnc-png \
        --disable-vnc-jpeg \
        --enable-uuid \
        --disable-vhost-scsi \
%if %{with guest_agent}
        --enable-guest-agent \
%else
        --disable-guest-agent \
%endif
%ifarch x86_64
        --enable-rbd \
%endif
        --enable-glusterfs \
%if 0%{?have_tcmalloc:1}
        --enable-tcmalloc \
%endif
        --block-drv-rw-whitelist=qcow2,raw,file,host_device,blkdebug,nbd,iscsi,gluster,rbd,null-co \
        --block-drv-ro-whitelist=vmdk,vhdx,vpc,ssh,https \
        --iasl=/bin/false \
        "$@"

    echo "config-host.mak contents:"
    echo "==="
    cat config-host.mak
    echo "==="

    make V=1 %{?_smp_mflags} $buildldflags
%else
   ./configure --prefix=%{_prefix} \
               --libdir=%{_libdir} \
               --with-pkgversion=%{pkgname}-%{version}-%{release} \
               --disable-guest-agent \
               "$@"

   make qemu-img %{?_smp_mflags} $buildldflags
   make qemu-io %{?_smp_mflags} $buildldflags
   make qemu-nbd %{?_smp_mflags} $buildldflags
   make qemu-img.1 %{?_smp_mflags} $buildldflags
   make qemu-nbd.8 %{?_smp_mflags} $buildldflags
   %if %{with guest_agent}
      make qemu-ga %{?_smp_mflags} $buildldflags
   %endif
%endif
}

echo "wangzh flag"
echo %{with guest_agent}

dobuild --target-list="$buildarch"

%if 0%{!?build_only_sub:1}
        # Setup back compat qemu-kvm binary
        ./scripts/tracetool.py --backend dtrace --format stap \
          --binary %{_libexecdir}/qemu-kvm \
          --target-type system --probe-prefix \
          qemu.kvm < ./trace-events > qemu-kvm.stp

        ./scripts/tracetool.py --backend dtrace --format simpletrace-stap \
          --binary %{_libexecdir}/qemu-kvm \
          --target-type system --probe-prefix \
          qemu.kvm < ./trace-events > qemu-kvm-simpletrace.stp

        cp -a %{kvm_target}-softmmu/qemu-system-%{kvm_target} qemu-kvm


    gcc %{SOURCE6} -O2 -g -o ksmctl
%endif

%install
%define _udevdir %(pkg-config --variable=udevdir udev)/rules.d

%if 0%{!?build_only_sub:1}
    install -D -p -m 0644 %{SOURCE4} $RPM_BUILD_ROOT%{_unitdir}/ksm.service
    install -D -p -m 0644 %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/ksm
    install -D -p -m 0755 ksmctl $RPM_BUILD_ROOT%{_libexecdir}/ksmctl

    install -D -p -m 0644 %{SOURCE7} $RPM_BUILD_ROOT%{_unitdir}/ksmtuned.service
    install -D -p -m 0755 %{SOURCE8} $RPM_BUILD_ROOT%{_sbindir}/ksmtuned
    install -D -p -m 0644 %{SOURCE9} $RPM_BUILD_ROOT%{_sysconfdir}/ksmtuned.conf

    mkdir -p $RPM_BUILD_ROOT%{_bindir}/
    mkdir -p $RPM_BUILD_ROOT%{_udevdir}
    mkdir -p $RPM_BUILD_ROOT%{_datadir}/%{pkgname}

    install -m 0755 scripts/kvm/kvm_stat $RPM_BUILD_ROOT%{_bindir}/
    install -m 0644 %{SOURCE3} $RPM_BUILD_ROOT%{_udevdir}
    install -m 0644 scripts/dump-guest-memory.py \
                    $RPM_BUILD_ROOT%{_datadir}/%{pkgname}

    make DESTDIR=$RPM_BUILD_ROOT \
        sharedir="%{_datadir}/%{pkgname}" \
        datadir="%{_datadir}/%{pkgname}" \
        install

    mkdir -p $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset

    # Install compatibility roms
    #install %{SOURCE14} $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/
    #install %{SOURCE15} $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/
    #install %{SOURCE16} $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/
    #install %{SOURCE17} $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/
    #install %{SOURCE20} $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/
    #install %{SOURCE22} $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/
    install pc-bios/*.rom $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/

    install -m 0755 qemu-kvm $RPM_BUILD_ROOT%{_libexecdir}/
    install -m 0644 qemu-kvm.stp $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/
    install -m 0644 qemu-kvm-simpletrace.stp $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/

    rm $RPM_BUILD_ROOT%{_bindir}/qemu-system-%{kvm_target}
    rm $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/qemu-system-%{kvm_target}.stp
    rm $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/qemu-system-%{kvm_target}-simpletrace.stp

    # Install simpletrace
    install -m 0755 scripts/simpletrace.py $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/simpletrace.py
    mkdir -p $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/tracetool
    install -m 0644 -t $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/tracetool scripts/tracetool/*.py
    mkdir -p $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/tracetool/backend
    install -m 0644 -t $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/tracetool/backend scripts/tracetool/backend/*.py
    mkdir -p $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/tracetool/format
    install -m 0644 -t $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/tracetool/format scripts/tracetool/format/*.py

    mkdir -p $RPM_BUILD_ROOT%{qemudocdir}
    install -p -m 0644 -t ${RPM_BUILD_ROOT}%{qemudocdir} Changelog README COPYING COPYING.LIB LICENSE %{SOURCE19} docs/qmp-spec.txt docs/qmp-events.txt
    mv ${RPM_BUILD_ROOT}%{_docdir}/qemu/qemu-doc.html $RPM_BUILD_ROOT%{qemudocdir}
    mv ${RPM_BUILD_ROOT}%{_docdir}/qemu/qemu-tech.html $RPM_BUILD_ROOT%{qemudocdir}
    mv ${RPM_BUILD_ROOT}%{_docdir}/qemu/qmp-commands.txt $RPM_BUILD_ROOT%{qemudocdir}
    chmod -x ${RPM_BUILD_ROOT}%{_mandir}/man1/*
    chmod -x ${RPM_BUILD_ROOT}%{_mandir}/man8/*

    install -D -p -m 0644 qemu.sasl $RPM_BUILD_ROOT%{_sysconfdir}/sasl2/qemu-kvm.conf

    # Provided by package openbios
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/openbios-ppc
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/openbios-sparc32
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/openbios-sparc64
    # Provided by package SLOF
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/slof.bin

    # Remove unpackaged files.
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/palcode-clipper
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/petalogix*.dtb
    rm -f ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/bamboo.dtb
    rm -f ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/ppc_rom.bin
    rm -f ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/spapr-rtas.bin
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/s390-zipl.rom
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/s390-ccw.img

    # Remove efi roms
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/efi*.rom

    # Provided by package ipxe
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/pxe*rom
    # Provided by package vgabios
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/vgabios*bin
    # Provided by package seabios
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/bios*.bin
    # Provided by package sgabios
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/sgabios.bin

    # the pxe gpxe images will be symlinks to the images on
    # /usr/share/ipxe, as QEMU doesn't know how to look
    # for other paths, yet.
    #pxe_link() {
    #    ln -s ../ipxe/$2.rom %{buildroot}%{_datadir}/%{pkgname}/pxe-$1.rom
    #}

    pxe_link() {
        ln -s ../pc-bios/$1 %{buildroot}%{_datadir}/%{pkgname}/$1
    }

    pxe_link pxe-e1000.rom
    pxe_link pxe-ne2k_pci.rom
    pxe_link pxe-pcnet.rom
    pxe_link pxe-rtl8139.rom 
    pxe_link pxe-virtio.rom
    pxe_link pxe-eepro100.rom

    rom_link() {
        ln -s $1 %{buildroot}%{_datadir}/%{pkgname}/$2
    }

    #rom_link ../seavgabios/vgabios-isavga.bin vgabios.bin
    #rom_link ../seavgabios/vgabios-cirrus.bin vgabios-cirrus.bin
    #rom_link ../seavgabios/vgabios-qxl.bin vgabios-qxl.bin
    #rom_link ../seavgabios/vgabios-stdvga.bin vgabios-stdvga.bin
    #rom_link ../seavgabios/vgabios-vmware.bin vgabios-vmware.bin
    #rom_link ../seabios/bios.bin bios.bin
    #rom_link ../seabios/bios-256k.bin bios-256k.bin
    #rom_link ../sgabios/sgabios.bin sgabios.bin

    rom_link ../pc-bios/vgabios-isavga.bin vgabios.bin
    rom_link ../pc-bios/vgabios-cirrus.bin vgabios-cirrus.bin
    rom_link ../pc-bios/vgabios-qxl.bin vgabios-qxl.bin
    rom_link ../pc-bios/vgabios-stdvga.bin vgabios-stdvga.bin
    rom_link ../pc-bios/vgabios-vmware.bin vgabios-vmware.bin
    rom_link ../pc-bios/bios.bin bios.bin
    rom_link ../pc-bios/bios-256k.bin bios-256k.bin
    rom_link ../pc-bios/sgabios.bin sgabios.bin
%endif

# Remove libcacard
rm -rf $RPM_BUILD_ROOT%{_bindir}/vscclient
rm -rf $RPM_BUILD_ROOT%{_includedir}/cacard
rm -rf $RPM_BUILD_ROOT%{_libdir}/libcacard.so*
rm -rf $RPM_BUILD_ROOT%{_libdir}/pkgconfig/libcacard.pc

%if %{with guest_agent}
    # For the qemu-guest-agent subpackage, install:
    # - the systemd service file and the udev rules:
    mkdir -p $RPM_BUILD_ROOT%{_unitdir}
    mkdir -p $RPM_BUILD_ROOT%{_udevdir}
    install -m 0644 %{SOURCE10} $RPM_BUILD_ROOT%{_unitdir}
    install -m 0644 %{SOURCE11} $RPM_BUILD_ROOT%{_udevdir}

    # - the environment file for the systemd service:
    install -D -p -m 0644 %{SOURCE13} \
      $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/qemu-ga

    # - the fsfreeze hook script:
    install -D --preserve-timestamps \
      scripts/qemu-guest-agent/fsfreeze-hook \
      $RPM_BUILD_ROOT%{_sysconfdir}/qemu-ga/fsfreeze-hook

    # - the directory for user scripts:
    mkdir $RPM_BUILD_ROOT%{_sysconfdir}/qemu-ga/fsfreeze-hook.d

    # - and the fsfreeze script samples:
    mkdir --parents $RPM_BUILD_ROOT%{_datadir}/%{name}/qemu-ga/fsfreeze-hook.d/
    install --preserve-timestamps --mode=0644 \
      scripts/qemu-guest-agent/fsfreeze-hook.d/*.sample \
      $RPM_BUILD_ROOT%{_datadir}/%{name}/qemu-ga/fsfreeze-hook.d/

    # - Install dedicated log directory:
    mkdir -p -v $RPM_BUILD_ROOT%{_localstatedir}/log/qemu-ga/
%endif

%if 0%{!?build_only_sub:1}
    # Install rules to use the bridge helper with libvirt's virbr0
    install -m 0644 %{SOURCE12} $RPM_BUILD_ROOT%{_sysconfdir}/%{pkgname}
%endif


find $RPM_BUILD_ROOT -name '*.la' -or -name '*.a' | xargs rm -f

%if 0%{?build_only_sub}
    mkdir -p $RPM_BUILD_ROOT%{_bindir}
    mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1/*
    mkdir -p $RPM_BUILD_ROOT%{_mandir}/man8/*
    install -m 0755 qemu-img $RPM_BUILD_ROOT%{_bindir}/qemu-img
    install -m 0755 qemu-io $RPM_BUILD_ROOT%{_bindir}/qemu-io
    install -m 0755 qemu-nbd $RPM_BUILD_ROOT%{_bindir}/qemu-nbd
    install -c -m 0644 qemu-img.1 ${RPM_BUILD_ROOT}%{_mandir}/man1/qemu-img.1
    install -c -m 0644 qemu-nbd.8 ${RPM_BUILD_ROOT}%{_mandir}/man8/qemu-nbd.8
    %if %{with guest_agent}
        install -c -m 0755  qemu-ga ${RPM_BUILD_ROOT}%{_bindir}/qemu-ga
    %endif
    chmod -x ${RPM_BUILD_ROOT}%{_mandir}/man1/*
    chmod -x ${RPM_BUILD_ROOT}%{_mandir}/man8/*
%endif


%if 0%{!?build_only_sub:1}
%check
    make check
%endif
%post
# load kvm modules now, so we can make sure no reboot is needed.
# If there's already a kvm module installed, we don't mess with it
%udev_rules_update
sh %{_sysconfdir}/sysconfig/modules/kvm.modules &> /dev/null || :
    udevadm trigger --subsystem-match=misc --sysname-match=kvm --action=add || :

%if 0%{!?build_only_sub:1}
%post -n qemu-kvm-common%{?pkgsuffix}
    %systemd_post ksm.service
    %systemd_post ksmtuned.service

    getent group kvm >/dev/null || groupadd -g 36 -r kvm
    getent group qemu >/dev/null || groupadd -g 107 -r qemu
    getent passwd qemu >/dev/null || \
       useradd -r -u 107 -g qemu -G kvm -d / -s /sbin/nologin \
       -c "qemu user" qemu

%preun -n qemu-kvm-common%{?pkgsuffix}
    %systemd_preun ksm.service
    %systemd_preun ksmtuned.service

%postun -n qemu-kvm-common%{?pkgsuffix}
    %systemd_postun_with_restart ksm.service
    %systemd_postun_with_restart ksmtuned.service
%endif

%global kvm_files \
%{_udevdir}/80-kvm.rules

%global qemu_kvm_files \
%{_libexecdir}/qemu-kvm \
%{_sysconfdir}/qemu-kvm \
#%{_datadir}/systemtap/tapset/qemu-kvm.stp \
%{_datadir}/systemtap/tapset/qemu-kvm-simpletrace.stp \
%{_datadir}/%{pkgname}/trace-events \
#%{_datadir}/%{pkgname}/systemtap/script.d/qemu_kvm.stp \
#%{_datadir}/%{pkgname}/systemtap/conf.d/qemu_kvm.conf

%if 0%{!?build_only_sub:1}
%files -n qemu-kvm-common%{?pkgsuffix}
    %defattr(-,root,root)
    %dir %{qemudocdir}
    %doc %{qemudocdir}/Changelog
    %doc %{qemudocdir}/README
    %doc %{qemudocdir}/qemu-doc.html
    %doc %{qemudocdir}/qemu-tech.html
    %doc %{qemudocdir}/qmp-commands.txt
    %doc %{qemudocdir}/COPYING
    %doc %{qemudocdir}/COPYING.LIB
    %doc %{qemudocdir}/LICENSE
    %doc %{qemudocdir}/README.rhel6-gpxe-source
    #%doc %{qemudocdir}/README.systemtap
    %doc %{qemudocdir}/qmp-spec.txt
    %doc %{qemudocdir}/qmp-events.txt
    %dir %{_datadir}/%{pkgname}/
    %doc %{_datadir}/locale/*
    %{_datadir}/%{pkgname}/keymaps/
    %{_mandir}/man1/qemu.1.gz
    %attr(4755, -, -) %{_libexecdir}/qemu-bridge-helper
    %config(noreplace) %{_sysconfdir}/sasl2/%{pkgname}.conf
    %{_unitdir}/ksm.service
    %{_libexecdir}/ksmctl
    %config(noreplace) %{_sysconfdir}/sysconfig/ksm
    %{_unitdir}/ksmtuned.service
    %{_sbindir}/ksmtuned
    %config(noreplace) %{_sysconfdir}/ksmtuned.conf
    #%dir %{_sysconfdir}/%{pkgname}
    #%config(noreplace) %{_sysconfdir}/%{pkgname}/bridge.conf
    %{_datadir}/%{pkgname}/simpletrace.py*
    %{_datadir}/%{pkgname}/tracetool/*.py*
    %{_datadir}/%{pkgname}/tracetool/backend/*.py*
    %{_datadir}/%{pkgname}/tracetool/format/*.py*
%endif

%if %{with guest_agent}
%files -n qemu-guest-agent
    %defattr(-,root,root,-)
    %doc COPYING README
    %{_bindir}/qemu-ga
    %{_unitdir}/qemu-guest-agent.service
    %{_udevdir}/99-qemu-guest-agent.rules
    %{_sysconfdir}/sysconfig/qemu-ga
    %{_sysconfdir}/qemu-ga
    %{_datadir}/%{name}/qemu-ga
    %dir %{_localstatedir}/log/qemu-ga
    %{_mandir}/man8/qemu-ga.8*
%endif

%if 0%{!?build_only_sub:1}
%files
    %defattr(-,root,root)
    %{_datadir}/%{pkgname}/acpi-dsdt.aml
    %{_datadir}/%{pkgname}/q35-acpi-dsdt.aml
    %{_datadir}/%{pkgname}/bios.bin
    %{_datadir}/%{pkgname}/bios-256k.bin
    %{_datadir}/%{pkgname}/sgabios.bin
    %{_datadir}/%{pkgname}/linuxboot.bin
    %{_datadir}/%{pkgname}/multiboot.bin
    %{_datadir}/%{pkgname}/kvmvapic.bin
    %{_datadir}/%{pkgname}/vgabios.bin
    %{_datadir}/%{pkgname}/vgabios-cirrus.bin
    %{_datadir}/%{pkgname}/vgabios-qxl.bin
    %{_datadir}/%{pkgname}/vgabios-stdvga.bin
    %{_datadir}/%{pkgname}/vgabios-vmware.bin
    %{_datadir}/%{pkgname}/pxe-e1000.rom
    %{_datadir}/%{pkgname}/pxe-virtio.rom
    %{_datadir}/%{pkgname}/pxe-pcnet.rom
    %{_datadir}/%{pkgname}/pxe-rtl8139.rom
    %{_datadir}/%{pkgname}/pxe-ne2k_pci.rom
    %{_datadir}/%{pkgname}/pxe-eepro100.rom
    %{_datadir}/%{pkgname}/qemu-icon.bmp
    %{_datadir}/qemu-kvm/QEMU,cgthree.bin
    %{_datadir}/qemu-kvm/QEMU,tcx.bin
    %{_datadir}/qemu-kvm/qemu_logo_no_text.svg
    %{_datadir}/qemu-kvm/u-boot.e500
    %{_datadir}/systemtap/tapset/qemu-kvm.stp


    #%{_datadir}/%{pkgname}/efi-virtio.rom
    #%{_datadir}/%{pkgname}/efi-pcnet.rom
    #%{_datadir}/%{pkgname}/efi-rtl8139.rom
    #%{_datadir}/%{pkgname}/efi-ne2k_pci.rom
    #%{_datadir}/%{pkgname}/efi-e1000.rom
    #%{_datadir}/%{pkgname}/efi-eepro100.rom
    %{_datadir}/%{pkgname}/dump-guest-memory.py*
    #%config(noreplace) %{_sysconfdir}/%{pkgname}/target-x86_64.conf
    %{?kvm_files:}
    %{?qemu_kvm_files:}

%files -n qemu-kvm-tools%{?pkgsuffix}
    %defattr(-,root,root,-)
    %{_bindir}/kvm_stat
    %{_bindir}/ivshmem-client
    %{_bindir}/ivshmem-server
%endif

%files -n qemu-img%{?pkgsuffix}
%defattr(-,root,root)
%{_bindir}/qemu-img
%{_bindir}/qemu-io
%{_bindir}/qemu-nbd
%{_mandir}/man1/qemu-img.1*
%{_mandir}/man8/qemu-nbd.8*

%changelog
* Tue Aug 15 2017 Xu Wang <wangxu19@lenovo.com> - 2.5.1.el7_4.1
- Build qemu rpm package for ThinkCloud
