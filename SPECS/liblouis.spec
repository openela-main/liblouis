%if !( 0%{?rhel} > 0 && 0%{?rhel} <= 7)
# Turn off the brp-python-bytecompile script
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%endif

%if 0%{?rhel} > 7
# Disable python2 build by default
%bcond_with python2
%else
%bcond_without python2
%endif

Name:           liblouis
Version:        2.6.2
Release:        21%{?dist}
Summary:        Braille translation and back-translation library

Group:          System Environment/Libraries
License:        LGPLv3+
URL:            http://liblouis.org
Source0:        https://github.com/%{name}/%{name}/releases/download/v%{version}/%{name}-%{version}.tar.gz
# Backported upstream patch to fix the build with texinfo 6.0
Patch0:         0001-Update-configure.ac-to-reconize-texi2any.patch
# security patch taken from
# https://git.centos.org/raw/rpms/liblouis.git/9f94aa24d3308691c575e2659e42321f4aff1cf3/SOURCES!security-fixes.patch
# fixes CVE-2014-8184, CVE-2017-13738, CVE-2017-13740, CVE-2017-13741, CVE-2017-13742, CVE-2017-13743, CVE-2017-13744
Patch1:         %{name}-security-fixes.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1585906
Patch2:         liblouis-2.6.2-CVE-2018-11577.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1588632
Patch3:         liblouis-2.6.2-CVE-2018-11684.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1588637
Patch4:         liblouis-2.6.2-CVE-2018-11685.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1589942
Patch5:         liblouis-2.6.2-CVE-2018-12085.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1602585
Patch6:         liblouis-2.6.2-coverity-fixes.patch

BuildRequires:  chrpath
BuildRequires:  help2man
BuildRequires:  texinfo
BuildRequires:  texinfo-tex
%if %{with python2}
BuildRequires:  python2-devel
%endif # with python2
BuildRequires:  python3-devel

# For patch0
BuildRequires:  autoconf automake libtool

Requires(post): info
Requires(preun): info

# gnulib is a copylib that has been granted an exception from the no-bundled-libraries policy
# http://fedoraproject.org/wiki/Packaging:No_Bundled_Libraries#Copylibs
Provides: bundled(gnulib) = 20130621

%description
Liblouis is an open-source braille translator and back-translator named in
honor of Louis Braille. It features support for computer and literary braille,
supports contracted and uncontracted translation for many languages and has
support for hyphenation. New languages can easily be added through tables that
support a rule- or dictionary based approach. Liblouis also supports math
braille (Nemeth and Marburg).

Liblouis has features to support screen-reading programs. This has led to its
use in two open-source screen readers, NVDA and Orca. It is also used in some
commercial assistive technology applications for example by ViewPlus.

Liblouis is based on the translation routines in the BRLTTY screen reader for
Linux. It has, however, gone far beyond these routines.

%package        devel
Summary:        Development files for %{name}
Group:          Development/Libraries
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       pkgconfig

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%package        utils
Summary:        Command-line utilities to test %{name}
Group:          Applications/Text
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       python3-louis = %{version}-%{release}
License:        GPLv3+

%description    utils
Six test programs are provided as part of the liblouis package. They
are intended for testing liblouis and for debugging tables. None of
them is suitable for braille transcription.

%if %{with python2}
%package -n python2-louis
Summary:        Python 2 language bindings for %{name}
Group:          Development/Languages
BuildArch:      noarch
Requires:       %{name} = %{version}-%{release}
Obsoletes:      %{name}-python < 2.6.2-3
Provides:       %{name}-python = %{version}-%{release}
%{?python_provide:%python_provide python2-louis}

%description -n python2-louis
This package provides Python 2 language bindings for %{name}.
%endif # with python2

%package -n python3-louis
Summary:        Python 3 language bindings for %{name}
Group:          Development/Languages
BuildArch:      noarch
Requires:       %{name} = %{version}-%{release}
Obsoletes:      %{name}-python3 < 2.6.2-3
Provides:       %{name}-python3 = %{version}-%{release}
%{?python_provide:%python_provide python3-louis}

%description -n python3-louis
This package provides Python 3 language bindings for %{name}.


%package doc
Summary:        Documentation for %{name}
Group:          Documentation
BuildArch:      noarch
Requires:       %{name} = %{version}-%{release}

%description doc
This package provides the documentation for liblouis.


%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1

# For patch0
autoreconf -fi

# Change the shebang of check_doctests to point to python3
pathfix.py -i "%{__python3}" -pn \
tests/check_doctests.py

%build
%configure --disable-static --enable-ucs4
make %{?_smp_mflags}
make -C doc %{name}.pdf


%check
make check


%install
make install DESTDIR=%{buildroot}
rm -f %{buildroot}/%{_infodir}/dir
rm -f %{buildroot}/%{_libdir}/%{name}.la
rm -rf %{buildroot}/%{_defaultdocdir}/%{name}/
cd python/louis

%if %{with python2}
install -d %{buildroot}%{python2_sitelib}/louis
install -pm 0644 __init__.py %{buildroot}%{python2_sitelib}/louis/
%endif # with python2

%if !( 0%{?rhel} > 0 && 0%{?rhel} <= 7)
%if %{with python2}
%py_byte_compile %{__python} %{buildroot}%{python2_sitelib}/louis/
%endif # with python2

install -d %{buildroot}%{python3_sitelib}/louis
install -pm 0644 __init__.py %{buildroot}%{python3_sitelib}/louis/
%py_byte_compile %{__python3} %{buildroot}%{python3_sitelib}/louis/
%endif

# Remove Rpaths from the executables. We must do that in the %%install section
# because, otherwise, the test suite wouldn't build.
for f in `find %{buildroot}%{_bindir} -exec file {} \; | grep 'ELF.*executable' | cut -d: -f1`; do
  chrpath --delete $f
done


%post
/sbin/ldconfig
/sbin/install-info %{_infodir}/%{name}.info %{_infodir}/dir || :


%postun -p /sbin/ldconfig


%preun
if [ $1 = 0 ] ; then
  /sbin/install-info --delete %{_infodir}/%{name}.info %{_infodir}/dir || :
fi


%files
%doc README COPYING.LESSER AUTHORS NEWS ChangeLog TODO
%{_libdir}/%{name}.so.*
%{_datadir}/%{name}/
%{_infodir}/%{name}.info*

%files devel
%doc HACKING
%{_includedir}/%{name}/
%{_libdir}/pkgconfig/%{name}.pc
%{_libdir}/%{name}.so

%files utils
%doc COPYING
%{_bindir}/lou_*
%{_mandir}/man1/lou_*.1*

%if %{with python2}
%files -n python2-louis
%doc python/README
%{python2_sitelib}/louis/
%endif # with python2

%if !( 0%{?rhel} > 0 && 0%{?rhel} <= 7)
%files -n python3-louis
%{python3_sitelib}/louis/
%endif

%files doc
%doc doc/%{name}.{html,txt,pdf}


%changelog
* Mon Mar 02 2020 David King <dking@redhat.com> - 2.6.2-21
- A further Coverity fix (#1602585)

* Thu Dec 19 2019 David King <dking@redhat.com> - 2.6.2-20
- Fix buffer overruns found by Coverity (#1602585)

* Thu Dec 05 2019 David King <dking@redhat.com> - 2.6.2-19
- Fix two issues found by Coverity (#1602585)

* Wed Dec 04 2019 David King <dking@redhat.com> - 2.6.2-18
- Apply patch for CVE-2018-12085 (#1589942)

* Wed Dec 04 2019 David King <dking@redhat.com> - 2.6.2-17
- Fix CVE-2018-11577 (#1585906)
- Fix CVE-2018-11684 (#1588632)
- Fix CVE-2018-11685 (#1588637)
- Fix CVE-2018-12085 (#1589942)

* Thu Jun 07 2018 Charalampos Stratakis <cstratak@redhat.com> - 2.6.2-16
- Conditionalize the python2 subpackage

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.6.2-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Jan 09 2018 Iryna Shcherbina <ishcherb@redhat.com> - 2.6.2-14
- Update Python 2 dependency declarations to new packaging standards
  (See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3)

* Sun Dec 17 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 2.6.2-13
- Python 2 binary package renamed to python2-louis
  See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3

* Fri Nov 03 2017 Martin Gieseking <martin.gieseking@uos.de> - 2.6.2-12
- Applied security fixes from EL 7.4 (CVE-2014-8184, CVE-2017-13738, CVE-2017-13740, CVE-2017-13741, CVE-2017-13742, CVE-2017-13743, CVE-2017-13744)
- Dropped redundant parts of the spec file.
- Updated URL.

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.6.2-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.6.2-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Wed Feb 15 2017 Igor Gnatenko <ignatenko@redhat.com> - 2.6.2-9
- Rebuild for brp-python-bytecompile

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.6.2-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Dec 19 2016 Miro Hrončok <mhroncok@redhat.com> - 2.6.2-7
- Rebuild for Python 3.6

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.6.2-6
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.6.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Nov 10 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.6.2-4
- Rebuilt for https://fedoraproject.org/wiki/Changes/python3.5

* Sun Aug 23 2015 Kalev Lember <klember@redhat.com> - 2.6.2-3
- Rename liblouis-python3 to python3-louis, as per latest packaging guidelines
- Fix the build with texinfo 6.0

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.6.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Apr 08 2015 Martin Gieseking <martin.gieseking@uos.de> 2.6.2-1
- Updated to new upstream release.

* Tue Sep 16 2014 Martin Gieseking <martin.gieseking@uos.de> 2.6.0-1
- Updated to new upstream release.

* Mon Aug 18 2014 Martin Gieseking <martin.gieseking@uos.de> 2.5.4-5
- Fixed check for ELF binaries to prevent chrpath from failing.

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue May 27 2014 Kalev Lember <kalevlember@gmail.com> - 2.5.4-2
- Rebuilt for https://fedoraproject.org/wiki/Changes/Python_3.4

* Tue May 13 2014 Martin Gieseking <martin.gieseking@uos.de> 2.5.4-1
- Updated to new upstream release.
- Activated the bundled test suite which has been adapted to work correctly with the recent release. 
- Remove Rpaths from the utility programs.
- Updated the description according to the upstream website.

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Jul 22 2013 Martin Gieseking <martin.gieseking@uos.de> - 2.5.3-1
- Update to new upstream release.

* Thu Jul 18 2013 Matthias Clasen <mclasen@redhat.com> - 2.5.2-7
- Tighten dependencies between subpackages (pointed out by rpmdiff)

* Tue Apr 16 2013 Martin Gieseking <martin.gieseking@uos.de> 2.5.2-6
- Restrict exclusion of Python 3 packages to RHEL <= 7.

* Mon Apr 15 2013 Martin Gieseking <martin.gieseking@uos.de> 2.5.2-5
- Restrict exclusion of Python 3 packages to RHEL < 7.

* Mon Apr 15 2013 Rui Matos <rmatos@redhat.com> - 2.5.2-4
- Don't depend on python3 in RHEL.

* Tue Feb 26 2013 Martin Gieseking <martin.gieseking@uos.de> 2.5.2-3
- Added Python 3 language bindings.

* Fri Feb 22 2013 Martin Gieseking <martin.gieseking@uos.de> 2.5.2-2
- Moved documentation to doc subpackage.

* Wed Feb 06 2013 Martin Gieseking <martin.gieseking@uos.de> 2.5.2-1
- Updated to new upstream release.

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sat Mar 10 2012 Martin Gieseking <martin.gieseking@uos.de> 2.4.1-1
- Updated to upstream release 2.4.1.
- Made the devel package's dependency on the base package arch specific.

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Dec 12 2011 Martin Gieseking <martin.gieseking@uos.de> 2.4.0-1
- Updated to upstream release 2.4.0.

* Fri May 20 2011 Martin Gieseking <martin.gieseking@uos.de> 2.3.0-1
- Updated to upstream release 2.3.0.

* Mon Feb 28 2011 Martin Gieseking <martin.gieseking@uos.de> - 2.2.0-2
- Added release date of bundled gnulib to Provides.
- Use %%{name} macro consistently.

* Tue Feb 15 2011 Martin Gieseking <martin.gieseking@uos.de> - 2.2.0-1
- Updated to upstream release 2.2.0.
- Added Python bindings.

* Mon Jul 5 2010 Lars Bjørndal <lars.bjorndal@broadpark.no> - 1.9.0-2
- In advice from Martin Gieseking: Removed some garbage from the file section, and added a PDF version of the liblouis documentation. See <https://bugzilla.redhat.com/show_bug.cgi?id=597597>.

* Wed Jun 30 2010 Lars Bjørndal <lars.bjorndal@broadpark.no> - 1.9.0-1
- A new version was up to day. At the same time, fixed a minor spec issue according to a comment from Martin Gieseking, see <https://bugzilla.redhat.com/show_bug.cgi?id=597597>.

* Sun Jun 20 2010 Lars Bjørndal <lars.bjorndal@broadpark.no> - 1.8.0-3
- Fixed some small problems, among them wrong destination directory for documentation. See <https://bugzilla.redhat.com/show_bug.cgi?id=597597> for further details.

* Thu Jun 17 2010 Lars Bjørndal <lars.bjorndal@broadpark.no> 1.8.0-2
- Created the tools sub package and did a lot of clean ups, see <https://bugzilla.redhat.com/show_bug.cgi?id=597597>.

* Sat May 29 2010 Lars Bjørndal <lars.bjorndal@broadpark.no> 1.8.0-1
- Create the RPM for Fedora.
