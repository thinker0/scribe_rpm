# To build:
# 
# sudo yum -y install rpmdevtools && rpmdev-setuptree
# 
# wget https://raw.github.com/nmilford/specfiles/master/storm-0.8/storm-0.8.spec -O ~/rpmbuild/SPECS/storm-0.8.spec
# wget https://github.com/downloads/nathanmarz/storm/storm-0.8.0.zip -O ~/rpmbuild/SOURCES/storm-0.8.0.zip
# wget https://raw.github.com/nmilford/specfiles/master/storm-0.8/storm -O ~/rpmbuild/SOURCES/storm
# wget https://raw.github.com/nmilford/specfiles/master/storm-0.8/storm-nimbus.conf -O ~/rpmbuild/SOURCES/storm-nimbus.conf
# wget https://raw.github.com/nmilford/specfiles/master/storm-0.8/storm-supervisor.conf -O ~/rpmbuild/SOURCES/storm-supervisor.conf
# wget https://raw.github.com/nmilford/specfiles/master/storm-0.8/storm-ui.conf -O ~/rpmbuild/SOURCES/storm-ui.conf
# wget https://raw.github.com/nmilford/specfiles/master/storm-0.8/storm.nofiles.conf -O ~/rpmbuild/SOURCES/storm.nofiles.conf
# 
# rpmbuild -bb ~/rpmbuild/SPECS/storm-0.8.spec

%define storm_name storm
%define storm_branch 0.8.1
%define storm_version 0.8.1
%define release_version 1
%define storm_home /opt/%{storm_name}-%{storm_version}
%define etc_storm /etc/%{name}
%define config_storm %{etc_storm}/conf
%define storm_user storm
%define storm_group storm

Name: %{storm_name}
Version: %{storm_version}
Release: %{release_version}
Summary: Storm is a distributed realtime computation system.
License: Eclipse Public License 1.0 
URL: https://github.com/nathanmarz/storm/
Group: Development/Libraries
Source0: %{storm_name}-%{storm_version}.zip
Source1: storm-nimbus.conf
Source2: storm-ui.conf
Source3: storm-supervisor.conf
Source4: storm
Source5: storm.nofiles.conf
Buildroot: %{_tmppath}/%{name}-%{version}-%{release}-%(%{__id_u} -n)
Requires: sh-utils, textutils, /usr/sbin/useradd, /usr/sbin/usermod, /sbin/chkconfig, /sbin/service
Provides: storm
Vendor: Nathan Marz <nathan.marz@gmail.com>
Packager: Nathan Milford <nathan@milford.io>
BuildArch: noarch

%description
Storm is a distributed realtime computation system. Similar to how Hadoop 
provides a set of general primitives for doing batch processing, Storm provides
a set of general primitives for doing realtime computation. 

%package nimbus
Summary: The Storm Nimbus node manages the Storm cluster.
Group: System/Daemons
Requires: %{name} = %{version}-%{release}, jzmq
BuildArch: noarch
%description nimbus
Nimbus is responsible for distributing code around the Storm cluster, assigning
tasks to machines, and monitoring for failures.

%package ui
Summary: The Storm UI exposes metrics for the Storm cluster.
Group: System/Daemons
Requires: %{name} = %{version}-%{release}
BuildArch: noarch
%description ui
The Storm UI exposes metrics on a web interface on port 8080 to give you
a high level view of the cluster.

%package supervisor
Summary: The Storm Supervisor is a worker process of the Storm cluster.
Group: System/Daemons
Requires: %{name} = %{version}-%{release}, jzmq
BuildArch: noarch
%description supervisor
The Supervisor listens for work assigned to its machine and starts and stops
worker processes as necessary based on what Nimbus has assigned to it.

%package drpc
Summary: The Storm DRPC is a worker RPC process of the Storm cluster.
Group: System/Daemons
Requires: %{name} = %{version}-%{release}, jzmq
BuildArch: noarch
%description drpc
The Supervisor listens for work assigned to its machine and starts and stops
worker processes as necessary based on what Nimbus has assigned to it.


%prep
%setup -n %{storm_name}-%{storm_version}

%build
echo 'log4j.rootLogger=INFO, R
log4j.appender.R=org.apache.log4j.RollingFileAppender
log4j.appender.R.File=${storm.home}/logs/${logfile.name}
log4j.appender.R.MaxFileSize=50MB
log4j.appender.R.MaxBackupIndex=10
log4j.appender.R.layout=org.apache.log4j.PatternLayout
log4j.appender.R.layout.ConversionPattern=%d{yyyy-MM-dd HH:mm:ss} %c{1} [%p] %m%n' ./conf/storm.log.properties

%clean
rm -rf %{buildroot}

%install
# Clean out any previous builds not on slash (lol)
[ "%{buildroot}" != "/" ] && %{__rm} -rf %{buildroot}

install -d -m 755 %{buildroot}/%{storm_home}/
install    -m 644 %{_builddir}/%{storm_name}-%{storm_version}/*.jar           %{buildroot}/%{storm_home}/
install    -m 644 %{_builddir}/%{storm_name}-%{storm_version}/RELEASE         %{buildroot}/%{storm_home}/
install    -m 644 %{_builddir}/%{storm_name}-%{storm_version}/LICENSE.html    %{buildroot}/%{storm_home}/
install    -m 644 %{_builddir}/%{storm_name}-%{storm_version}/README.markdown %{buildroot}/%{storm_home}/

install -d -m 755 %{buildroot}/%{storm_home}/bin/
install    -m 755 %{_builddir}/%{storm_name}-%{storm_version}/bin/*           %{buildroot}/%{storm_home}/bin

install -d -m 755 %{buildroot}/%{storm_home}/conf/
install    -m 644 %{_builddir}/%{storm_name}-%{storm_version}/conf/*          %{buildroot}/%{storm_home}/conf

install -d -m 755 %{buildroot}/%{storm_home}/lib/
install    -m 644 %{_builddir}/%{storm_name}-%{storm_version}/lib/*           %{buildroot}/%{storm_home}/lib

install -d -m 755 %{buildroot}/%{storm_home}/log4j/
install    -m 644 %{_builddir}/%{storm_name}-%{storm_version}/log4j/*         %{buildroot}/%{storm_home}/log4j

install -d -m 755 %{buildroot}/%{storm_home}/logs/

install -d -m 755 %{buildroot}/%{storm_home}/public/

install -d -m 755 %{buildroot}/%{storm_home}/public/css/
install    -m 644 %{_builddir}/%{storm_name}-%{storm_version}/public/css/*    %{buildroot}/%{storm_home}/public/css/

install -d -m 755 %{buildroot}/%{storm_home}/public/js/
install    -m 644 %{_builddir}/%{storm_name}-%{storm_version}/public/js/*     %{buildroot}/%{storm_home}/public/js/

cd %{buildroot}/opt/
ln -s %{storm_name}-%{storm_version} %{storm_name}
cd -

install -d -m 755 %{buildroot}/etc/
cd %{buildroot}/etc
ln -s %{storm_home}/conf %{storm_name}
cd -

install -d -m 755 %{buildroot}/%{_sysconfdir}/init
install    -m 644 %_sourcedir/storm-nimbus.conf     %{buildroot}/%{_sysconfdir}/init/storm-nimbus.conf
install    -m 644 %_sourcedir/storm-ui.conf         %{buildroot}/%{_sysconfdir}/init/storm-ui.conf
install    -m 644 %_sourcedir/storm-drpc.conf       %{buildroot}/%{_sysconfdir}/init/storm-drpc.conf
install    -m 644 %_sourcedir/storm-supervisor.conf %{buildroot}/%{_sysconfdir}/init/storm-supervisor.conf
%{__mkdir_p} %{buildroot}/etc/init.d
install    -m 755 %_sourcedir/init.d/storm-nimbus     %{buildroot}/%{_sysconfdir}/init.d/storm-nimbus
install    -m 755 %_sourcedir/init.d/storm-ui         %{buildroot}/%{_sysconfdir}/init.d/storm-ui
install    -m 755 %_sourcedir/init.d/storm-drpc       %{buildroot}/%{_sysconfdir}/init.d/storm-drpc
install    -m 755 %_sourcedir/init.d/storm-supervisor %{buildroot}/%{_sysconfdir}/init.d/storm-supervisor
install -d -m 755 %{buildroot}/%{_sysconfdir}/sysconfig
install -d -m 755 %{buildroot}/%{_sysconfdir}/sysconfig
install    -m 644 %_sourcedir/storm            %{buildroot}/%{_sysconfdir}/sysconfig/storm
install -d -m 755 %{buildroot}/%{_sysconfdir}/security/limits.d/
install    -m 644 %_sourcedir/storm.nofiles.conf %{buildroot}/%{_sysconfdir}/security/limits.d/storm.nofiles.conf

install -d -m 755 %{buildroot}/usr/bin/
cd %{buildroot}/usr/bin
ln -s %{storm_home}/bin/%{storm_name} %{storm_name}
cd -

install -d -m 755 %{buildroot}/var/log/
cd %{buildroot}/var/log/
ln -s %{storm_home}/logs %{storm_name}
cd -

install -d -m 755 %{buildroot}/var/run/storm/

install -d -m 755 %{buildroot}/%{storm_home}/local/
echo 'storm.local.dir: "/opt/storm/local/"' >> %{buildroot}/%{storm_home}/conf/storm.yaml.example

%pre
getent group %{storm_group} >/dev/null || groupadd -r %{storm_group}
getent passwd %{storm_user} >/dev/null || /usr/sbin/useradd --comment "Storm Daemon User" --shell /bin/bash -M -r -g %{storm_group} --home %{storm_home} %{storm_user}

%files
%defattr(-,%{storm_user},%{storm_group})

/opt/%{storm_name}
%{storm_home}
%{storm_home}/*
%attr(755,%{storm_user},%{storm_group}) %{storm_home}/bin/*
/etc/storm 
/var/log/*
/var/run/storm/
/usr/bin/storm
/etc/init.d/
/etc/sysconfig/storm
/etc/security/limits.d/storm.nofiles.conf


%define service_macro() \
%files %1 \
%defattr(-,root,root) \
%{_sysconfdir}/init/%{storm_name}-%1.conf \
%preun %1 \
if [ $1 = 0 ]; then \
  stop %{storm_name}-%1 \
  rm %{_sysconfdir}/init/%{storm_name}-%1.conf \
fi \
%postun %1 \
if [ $1 -ge 1 ]; then \
  status %{storm_name}-%1 && \
  restart %{storm_name}-%1 \
fi

%service_macro nimbus
%service_macro ui
%service_macro drpc
%service_macro supervisor

%changelog
* Wed Aug 08 2012 Nathan Milford <nathan@milford.io> - 0.8.0
- Storm 0.8.0
