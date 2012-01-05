#   Licensed to the Apache Software Foundation (ASF) under one or more
#   contributor license agreements.  See the NOTICE file distributed with
#   this work for additional information regarding copyright ownership.
#   The ASF licenses this file to You under the Apache License, Version 2.0
#   (the "License"); you may not use this file except in compliance with
#   the License.  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

#
# RPM Spec file for ZooKeeper version 3.4.2
#

%define name         zookeeper
%define version      3.4.2
%define release      1

# Build time settings
%define _final_name   zookeeper-3.4.2
%define debug_package %{nil}

# RPM searches perl files for dependancies and this breaks for non packaged perl lib
# like thrift so disable this
%define _use_internal_dependency_generator 0

Summary: ZooKeeper is a centralized service for maintaining configuration information, naming, providing distributed synchronization, and providing group services.
License: Apache License, Version 2.0
URL: http://zookeeper.apache.org/
Vendor: Apache Software Foundation
Group: Development/Libraries
Name: %{name}
Version: %{version}
Release: %{release} 
Source0: %{_final_name}.tar.gz
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
AutoReqProv: no
Provides: zookeeper

%description
ZooKeeper is a centralized service for maintaining configuration information, naming, providing distributed synchronization, and providing group services. All of these kinds of services are used in some form or another by distributed applications. Each time they are implemented there is a lot of work that goes into fixing the bugs and race conditions that are inevitable. Because of the difficulty of implementing these kinds of services, applications initially usually skimp on them ,which make them brittle in the presence of change and difficult to manage. Even when done correctly, different implementations of these services lead to management complexity when the applications are deployed.

%package devel
Summary: ZooKeeper C binding library
Group: System/Libraries
#Requires: %{name} == %{version}

%description devel
ZooKeeper C client library for communicating with ZooKeeper Server.

%prep
%{__rm} -rf %{buildroot}
%setup -q -n %{name}-%{version}

%build
cd ./src/c
%configure %{config_opts}

#########################
#### INSTALL SECTION ####
#########################
%install
%{__rm} -rf %{buildroot}
cd ./src/c
%{__make} install DESTDIR=%{buildroot} INSTALL="%{__install} -p"
%{__rm} -rf %{buildroot}/usr/bin

%clean
%{__rm} -rf %{buildroot}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files devel
%defattr(-,root,root)
%{_libdir}/*
%{_includedir}/*

