#%define _with_server 1
#%define _with_agent 0

%define server %{?_with_server:1}%{!?_with_server:0}
%define agent %{?_with_agent:1}%{!?_with_agent:0}

%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%ifarch x86_64
  %{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}
%else
  %{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%endif

#%global config_opts --disable-static --with-thriftpath=%{_prefix} --with-fb303path=%{_prefix} --with-boost-system=boost_system --with-boost-filesystem=boost_filesystem
%global config_opts  --prefix=%{_prefix} --exec-prefix=%{_prefix} --bindir=%{_bindir} --libdir=%{_libdir} --with-thriftpath=%{_prefix} --with-fb303path=%{_prefix} --with-boost-system=boost_system --with-boost-filesystem=boost_filesystem

Name:             scribe
Version:          2.2.0
Release:          7%{?dist}
Summary:          A server for aggregating log data streamed in real time
Group:            Development/Libraries
License:          ASL 2.0
URL:              https://github.com/facebook/scribe
Source0:          https://github.com/downloads/facebook/%{name}/%{name}-%{version}.tar.gz
Source1:          scribed.init
Source2:          scribed.sysconfig
Source3:          logrotate
Source4:          scribea.init
# make scribe 2.2 work with boost 1.33
#Patch0:           boost-1.33.patch
# Patch below is from: http://github.com/bterm/sandbox.git
# make scribe 2.2 work with thrift 0.5.0
#Patch1:           thrift-0.5.0.patch
# Patch below is from: http://github.com/zxvdr/scribe.git
# it fixes the initial filename for hourly rolled logs
#Patch2:           hourly_roll_period_initial_filename.patch
BuildRoot:        %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:    automake
BuildRequires:    boost-devel >= 1.36
BuildRequires:    libfb303-devel
BuildRequires:    libevent-devel
BuildRequires:    thrift >= 0.8.0
BuildRequires:    thrift-devel

Requires:         boost >= 1.36
Requires:         libevent
Requires:         thrift-python >= 0.8.0
Requires:         libfb303-python
Requires(pre):    shadow-utils
Requires(post):   chkconfig

%description
Scribe is a server for aggregating log data streamed in real time from a large
number of servers. It is designed to be scalable, extensible without
client-side modification, and robust to failure of the network or any specific
machine.

%package agent
Summary:          A server for aggregating log data streamed in real time
Group:            Development/Libraries
License:          ASL 2.0
Requires:         scribe-python
Requires:         thrift-python >= 0.8.0
Requires:         libfb303-python

%description agent
Scribe is a agent for aggregating log data streamed in real time from a large
number of servers. It is designed to be scalable, extensible without
client-side modification, and robust to failure of the network or any specific
machine.

%package devel
Summary:          Devel bindings for %{name}
Group:            Development/Libraries

%description devel
Devel bindings for %{name}.

%package python
Summary:          Python bindings for %{name}
Group:            Development/Libraries
BuildRequires:    python-devel
Requires:         thrift-python >= 0.8.0
Requires:         libfb303-python

%description python
Python bindings for %{name}.

%prep
%{__rm} -rf %{buildroot}
%setup -q -n %{name}-%{version}
#%patch0 -p1
#%patch1 -p1
#%patch2 -p1

%build
#export CPPFLAGS="-static -O0 -DHAVE_NETDB_H=1 -fpermissive"
export CPPFLAGS="-fPIC -O3 -DHAVE_NETDB_H=1 -fpermissive"
#export LDFLAGS="-lrt -lc -lpthread -lboost_filesystem"
export CFLAGS="%{optflags}"
./bootstrap.sh --enable-static --enable-hdfs --enable-lzo --enable-zookeeper %{config_opts}

%{__make} %{?_smp_mflags}

%ifarch x86_64
  mkdir -p %{buildroot}%{python_sitearch}/%{name}
  %{__mv}  %{buildroot}%{python_sitelib}/%{name} %{buildroot}%{python_sitearch} || true
%else 
  echo "i386"
%endif


%install
%{__rm} -rf %{buildroot}
%{__make} DESTDIR=%{buildroot} install

# Install manually
mkdir -p %{buildroot}%{_includedir}/%{name}
%{__install} -D -m 755 ./examples/scribe_cat %{buildroot}%{_bindir}/scribe_cat
%{__install} -D -m 755 ./examples/scribe_ctrl %{buildroot}%{_bindir}/scribe_ctrl
%{__install} -D -m 755 ./src/libscribe.so %{buildroot}%{_libdir}/libscribe.so
%{__install} -D -m 755 ./src/libscribe.a %{buildroot}%{_libdir}/libscribe.a
#%{__install} -D -m 755 ./src/libdynamicbucketupdater.a %{buildroot}%{_libdir}/libdynamicbucketupdater.a
%{__install} -D -m 644 ./examples/example1.conf %{buildroot}%{_sysconfdir}/scribed/default.conf
%{__install} -D -m 755 %{SOURCE1} %{buildroot}%{_sysconfdir}/rc.d/init.d/scribed
%{__install} -D -m 755 %{SOURCE4} %{buildroot}%{_sysconfdir}/rc.d/init.d/scribea
%{__install} -D -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/scribed
%{__install} -D -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/scribe
%{__install} -d -m 755 %{buildroot}%{_localstatedir}/spool/scribed
%{__install} -d -m 755 %{buildroot}%{_localstatedir}/run/scribed
%{__install} -D -m 755 ./src/gen-cpp/scribe_types.h 			%{buildroot}%{_includedir}/scribe/scribe_types.h
%{__install} -D -m 755 ./src/gen-cpp/scribe_constants.h 		%{buildroot}%{_includedir}/scribe/scribe_constants.h 		
%{__install} -D -m 755 ./src/gen-cpp/scribe.h 					%{buildroot}%{_includedir}/scribe/scribe.h 					
%{__install} -D -m 755 ./src/gen-cpp/bucketupdater_types.h 		%{buildroot}%{_includedir}/scribe/bucketupdater_types.h 		
%{__install} -D -m 755 ./src/gen-cpp/bucketupdater_constants.h 	%{buildroot}%{_includedir}/scribe/bucketupdater_constants.h 	
%{__install} -D -m 755 ./src/gen-cpp/BucketStoreMapping.h 		%{buildroot}%{_includedir}/scribe/BucketStoreMapping.h 		

%ifarch x86_64
  mkdir -p %{buildroot}%{python_sitearch}/%{name}
  %{__mv}  %{buildroot}%{python_sitelib}/%{name}            %{buildroot}%{python_sitearch} || true
%else
  echo "arch i386 sitearch: %{python_sitearch},  sitelib: %{python_sitelib}"
  if [ -d %{buildroot}/usr/lib64 ]; then
    mkdir -p %{buildroot}%{python_sitelib}/%{name}
    %{__mv} %{buildroot}/usr/lib64/python*/site-packages/%{name}/* %{buildroot}%{python_sitelib}/%{name}/
  fi
%endif

# Remove scripts
#%{__rm} ./examples/scribe_*

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc LICENSE examples/
%config(noreplace) %{_sysconfdir}/scribed/default.conf
%config(noreplace) %{_sysconfdir}/sysconfig/scribed
%config(noreplace) %{_sysconfdir}/logrotate.d/scribe
%{_bindir}/scribed
%{_libdir}/libscribe.so
%{_sysconfdir}/rc.d/init.d/scribed
%{_bindir}/scribe_ctrl
%attr(0750,scribe,scribe) %{_localstatedir}/spool/scribed
%attr(-,scribe,scribe) %{_localstatedir}/run/scribed

%files agent
%defattr(-,root,root,-)
%doc LICENSE examples/
%config(noreplace) %{_sysconfdir}/scribed/default.conf
%config(noreplace) %{_sysconfdir}/sysconfig/scribed
%config(noreplace) %{_sysconfdir}/logrotate.d/scribe
%{_bindir}/scribea
#%{_libdir}/libscribe.so
%{_sysconfdir}/rc.d/init.d/scribea
%{_bindir}/scribe_ctrl
%attr(0750,scribe,scribe) %{_localstatedir}/spool/scribed
%attr(-,scribe,scribe) %{_localstatedir}/run/scribed

%files devel
%defattr(-,root,root,-)
%{_includedir}/scribe
%{_libdir}/libscribe.a
#%{_libdir}/libdynamicbucketupdater.a

%files python
%defattr(-,root,root,-)
%doc LICENSE

%ifarch x86_64
  %{python_sitearch}/%{name}
%else
  %{python_sitelib}/%{name}
%endif

%if (0%{?fedora} > 9 || 0%{?rhel} > 5)
  %{python_sitelib}/%{name}-*.egg-info
%endif

%{_bindir}/scribe_cat

%pre
getent group scribe >/dev/null || groupadd -r scribe
getent passwd scribe >/dev/null || \
    useradd -r -g scribe -d /var/log -s /sbin/nologin \
    -c "Scribe pseudo-user" scribe
exit 0

%post
/sbin/chkconfig --add scribed

%post agent
/sbin/chkconfig --add scribea

%preun
if [ $1 = 0 ]; then
  /sbin/service scribed stop > /dev/null 2>&1
  /sbin/chkconfig --del scribed
fi

%preun agent
if [ $1 = 0 ]; then
  /sbin/service scribea stop > /dev/null 2>&1
  /sbin/chkconfig --del scribea
fi

%changelog
* Fri May 13 2011 David Robinson <zxvdr.au@gmail.com> - 2.2-4
- fixed hourly roll period initial filename

* Wed May 11 2011 David Robinson <zxvdr.au@gmail.com> - 2.2-3
- added logrotate config

* Thu May 05 2011 David Robinson <zxvdr.au@gmail.com> - 2.2-2
- added scribe user
- run scribed as non-root user

* Wed Apr 20 2011 David Robinson <zxvdr.au@gmail.com> - 2.2-1
- rebuilt for RHEL 6
- rebuilt for thrift 2.2
- Update to 2.2

* Mon Dec 07 2009 Silas Sewell <silas@sewell.ch> - 2.1-1
- Update to 2.1

* Fri May 01 2009 Silas Sewell <silas@sewell.ch> - 2.0.1-1
- Initial build
