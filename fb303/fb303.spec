%global with_php 0

%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

Name:             fb303
Version:          0.8.0
Release:          5%{?dist}
Summary:          Facebook Bassline

Group:            Development/Libraries
License:          ASL 2.0
URL:              http://incubator.apache.org/thrift
Source0:          http://www.apache.org/dist/thrift/%{version}/thrift-%{version}.tar.gz
BuildRoot:        %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:    automake
BuildRequires:    byacc
BuildRequires:    boost-devel >= 1.33.1
BuildRequires:    flex
BuildRequires:    libevent-devel
BuildRequires:    libtool
BuildRequires:    thrift
BuildRequires:    thrift-devel
BuildRequires:    zlib-devel

%description
Facebook Baseline is a standard interface to monitoring, dynamic options and
configuration, uptime reports, activity, and more.

%package devel
Summary:          Development files for %{name}
Group:            Development/Libraries
Requires:         %{name} = %{version}

%description devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%package python
Summary:          Python bindings for %{name}
Group:            Development/Libraries
BuildRequires:    python-devel
Requires:         thrift-devel

%description python
Python bindings for %{name}.

%if %{with_php}
%package php
Summary:          PHP bindings for %{name}
Group:            Development/Libraries
BuildRequires:    php-devel
Requires:         thrift-php = %{version}

%description php
PHP bindings for %{name}.
%endif

%prep
%{__rm} -rf %{buildroot}
%setup -q -n thrift-%{version}
cd ./contrib/fb303

# Fix non-executable-script error
sed -i '/^#!\/usr\/bin\/env python/,+1 d' \
  py/fb303_scripts/*.py \
  py/fb303/FacebookBase.py

%build
cd ./contrib/fb303
export CPPFLAGS="-fPIC -fpermissive" 
./bootstrap.sh --with-thriftpath=%{_prefix}
#%configure %{config_opts} --enable-static --enable-shared --with-thriftpath=%{_prefix}
#%configure --with-thriftpath=%{_prefix}
%{__make} %{?_smp_mflags}

%install
%{__rm} -rf %{buildroot}
cd ./contrib/fb303

# Fix install path
#sed -i 's/shareddir = lib/shareddir = ${prefix}\/lib/g' cpp/Makefile
sed -i 's/shareddir = lib/shareddir = ${_libdir}/g' cpp/Makefile

#%{__make} DESTDIR=%{buildroot} install
%{__make} install DESTDIR=%{buildroot} INSTALL="%{__install} -p"

# Install PHP
%if %{with_php}
%{__mkdir_p} %{buildroot}%{_datadir}/php/%{name}
%{__cp} -r php/FacebookBase.php %{buildroot}%{_datadir}/php/%{name}/
%endif

%ifarch x86_64
# Fix lib install path on x86_64
%{__mv} %{buildroot}/usr/lib/libfb303.so %{buildroot}%{_libdir}/libfb303.so || true
%endif

%if %{!?without_python: 1}

#%if %{?python_sitearch == '/usr/lib64/python2.4/site-packages'}
%ifarch x86_64
mkdir -p %{buildroot}%{python_sitearch}/fb303 			%{buildroot}%{python_sitearch}/fb303_scripts
mv       %{buildroot}%{python_sitelib}/fb303 			%{buildroot}%{python_sitearch} || true
mv       %{buildroot}%{python_sitelib}/fb303_scripts 	%{buildroot}%{python_sitearch} || true
%endif

#cd py
#%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
#cd ..

%endif


%clean
%{__rm} -rf %{buildroot}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc README
%{_datadir}/fb303
%{_libdir}/*.so*

%files devel
%defattr(-,root,root,-)
%doc README
%{_includedir}/thrift/fb303
#%{_libdir}/*.so
%{_libdir}/*.a

%if %{with_php}
%files php
%defattr(-,root,root,-)
%doc README
%{_datadir}/php/%{name}
%endif

%files python
%defattr(-,root,root,-)
%doc README
%if (0%{?fedora} > 9 || 0%{?rhel} > 5)
%ifarch x86_64
%{python_sitearch}/%{name}-*.egg-info
%else
%{python_sitelib}/%{name}-*.egg-info
%endif
%endif

%ifarch x86_64
%{python_sitearch}/*
%else
%{python_sitelib}/*
%endif

%changelog
* Mon May 16 2011 David Robinson <zxvdr.au@gmail.com> - 0.6.0-2
- fix THRIFT-925

* Fri May 13 2011 David Robinson <zxvdr.au@gmail.com> - 0.6.0-1
- Update to 0.6.0

* Wed Mar 03 2010 Silas Sewell <silas@sewell.ch> - 0.2.0-1
- Update to non-snapshot release

* Wed Dec 09 2009 Silas Sewell <silas@sewell.ch> - 0.2-0.4.20091117svn835538
- Tweaks for EL compatibility

* Tue Nov 17 2009 Silas Sewell <silas@sewell.ch> - 0.2-0.3.20091117svn835538
- Update to thrift snapshot

* Tue Jul 21 2009 Silas Sewell <silas@sewell.ch> - 0.2-0.2.20090721svn795861
- Update to latest snapshot

* Fri May 01 2009 Silas Sewell <silas@sewell.ch> - 0.2-0.1.20090501svn770888
- Initial build

