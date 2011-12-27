#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
#

%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

# TODO(dreiss): Where is this supposed to go?
Name:           thrift
License:        Apache License v2.0
Group:          Development
Summary:        RPC and serialization framework
Version:        0.8.0
Release:        1
URL:            http://developers.facebook.com/thrift
Packager:       David Reiss <dreiss@facebook.com>
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  gcc >= 3.4.6
BuildRequires:  gcc-c++

%if %{!?without_python: 1}
BuildRequires:  python-devel
%endif

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
Thrift is a software framework for scalable cross-language services
development. It combines a powerful software stack with a code generation
engine to build services that work efficiently and seamlessly between C++,
Java, C#, Python, Ruby, Perl, PHP, Objective C/Cocoa, Smalltalk, Erlang,
Objective Caml, and Haskell.

%files
%defattr(-,root,root)
%{_bindir}/thrift


%package lib-cpp
Summary: Thrift C++ library
Group:   Libraries

%description lib-cpp
C++ libraries for Thrift.

%files lib-cpp
%defattr(-,root,root)
%{_libdir}/libthrift*.so*


%package lib-cpp-devel
Summary:   Thrift C++ library development files
Group:     Libraries
Requires:  %{name} = %{version}-%{release}
Requires:  boost-devel
Requires:  libevent-devel
Requires:  zlib-devel

%description lib-cpp-devel
C++ static libraries and headers for Thrift.

%files lib-cpp-devel
%defattr(-,root,root)
%{_includedir}/thrift/
%{_libdir}/libthrift*.*a
%{_libdir}/libthrift*.so
%{_libdir}/pkgconfig/thrift*.pc

%if %{!?without_python: 1}
%package lib-python
Summary: Thrift Python library
Group:   Libraries

%description lib-python
Python libraries for Thrift.

%files lib-python
%defattr(-,root,root)
%{python_sitearch}/*
%endif

%prep
%setup -q

%build
# TODO(dreiss): Implement a single --without-build-kludges.
%configure \
  --with-python \
  --with-cpp \
  --without-java \
  --without-java \
  --without-csharp \
  --without-go \
  --without-ruby \
  --without-perl \
  --without-php \
  --without-php_extension \
  --without-haskell \
  --without-c_glib \
  --without-erlang 

#make
#%{__make} %{?_smp_mflags}
CFLAGS="%{optflags}" %{__make}

%if %{!?without_python: 1}
cd lib/py
CFLAGS="%{optflags}" %{__python} setup.py build
cd ../..
%endif

%install
%makeinstall

%if %{!?without_python: 1}
cd lib/py
CFLAGS="%{optflags}" %{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
cd ../..
%endif

%clean
rm -rf ${RPM_BUILD_ROOT}


%changelog
* Wed May 28 2008 David Reiss <dreiss@facebook.com> - 20080529svn
- Initial build, based on the work of Kevin Smith and Ben Maurer.
