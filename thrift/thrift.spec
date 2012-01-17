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

# TODO(dreiss): Have a Python build with and without the extension.
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%ifarch (x86_64 || amd64)
  %{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}
%else
  %{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%endif
# TODO(dreiss): Where is this supposed to go?
%{!?thrift_erlang_root: %define thrift_erlang_root /opt/thrift-erl}

Name:       thrift
Version: 	0.8.0
License:    Apache License v2.0
Group:      Development
Summary:    Multi-language RPC and serialization framework
Release:	3%{?release_tag}	
Epoch:      1
Group:      Development/Libraries
URL: 		http://incubator.apache.org/thrift/
Source0: 	%{name}-%{version}.tar.gz
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%if %{!?without_python: 1}
BuildRequires:  python-devel
%endif

%description
Thrift is a software framework for scalable cross-language services
development. It combines a powerful software stack with a code generation
engine to build services that work efficiently and seamlessly between C++,
Java, C#, Python, Ruby, Perl, PHP, Objective C/Cocoa, Smalltalk, Erlang,
Objective Caml, and Haskell.

%files
%defattr(-, root, root, 0755)
%{_bindir}/*
%{_libdir}/libthrift*.so*
#%exclude %{_datadir}/doc/*
#%exclude %{python_prefix}/lib/python*
#%exclude %{java_prefix}/*
#%{java_prefix}/*
#%{_datadir}/doc/*

%package devel
Summary: Development tools for the %{name}-%{version}
Group: Development/Libraries
Requires: %{name}
Requires: pkgconfig
BuildRequires: boost-devel
BuildRequires: libevent

%description devel
This package contains client libraries for %{name}. If you like to develop 
programs using %{name}, you will need to install %{name}-devel.

%files devel
%defattr(-, root, root, 0755)
#%{python_prefix}/lib/python*
#%{java_prefix}/*
#%{_datadir}/doc/*
%{_includedir}/*
%{_libdir}/libthrift*a
%{_libdir}/pkgconfig/*

%define python_prefix /usr
%define java_prefix /usr/java/lib

%package python
Summary:          Python bindings for %{name}
Group:            Development/Libraries
BuildRequires:    python-devel

%description python
Python bindings for %{name}.

%files python
%defattr(-,root,root,-)
%doc LICENSE
%ifarch (x86_64 || amd64)
  %{python_sitearch}/*
%else
  %{python_sitelib}/*
%endif

%prep
%{__rm} -rf %{buildroot}
%setup -q -n %{name}-%{version}
# %patch -p1

%build
#./bootstrap.sh 
#PATH=%{python_prefix}/bin:$PATH %configure PY_PREFIX=%{python_prefix} --prefix=%{_prefix} --exec-prefix=%{_prefix} --bindir=%{_bindir} --libdir=%{_libdir} --disable-static --without-ruby --without-erlang --without-haskell --without-perl --without-csharp --without-java --without-php --with-python 
#./bootstrap.sh %{config_opts}
export CPPFLAGS="-fPIC %{optflags}"
export CFLAGS="-fPIC %{optflags}"
%configure %{config_opts} \
    --prefix=%{_prefix} --exec-prefix=%{_prefix} --bindir=%{_bindir} --libdir=%{_libdir} \
	--without-ruby --without-erlang --without-haskell --without-perl \
	--without-csharp --without-java --without-php \
	--with-python 

# %{__make} %{?_smp_mflags}
# _smp_mflags build error
%{__make}

%if %{!?without_python: 1}
  cd lib/py
  LDFLAGS=-m32 %{__python} setup.py build
  cd ../..
%endif


%install
%{__rm} -rf %{buildroot}
%{__make} install DESTDIR=%{buildroot} INSTALL="%{__install} -p"

%if %{!?without_python: 1}
  cd lib/py
  LDFLAGS=-m32 %{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT 
  cd ../..

  %ifarch (x86_64 || amd64)
    mkdir -p %{buildroot}%{python_sitearch}/thrift %{buildroot}%{python_sitearch}/thrift
    %{__mv}  %{buildroot}%{python_sitelib}/thrift  %{buildroot}%{python_sitearch} || true
  %else
    echo "arch i386 sitearch: %{python_sitearch},  sitelib: %{python_sitelib}"
    if [ -d %{buildroot}/usr/lib64 ]; then
      mkdir -p %{buildroot}%{python_sitelib}/thrift/
      %{__mv} %{buildroot}/usr/lib64/python*/site-packages/thrift/* %{buildroot}%{python_sitelib}/thrift/
    fi
  %endif
%endif


%post
/sbin/ldconfig

%clean
%{__rm} -rf %{buildroot}

%changelog
* Mon Aug 16 2010 - jake farrell
- updated thrift version to 0.5.0
* Fri Jun 4 2010 - jake farrell
- Update thrift version to 0.4.0-dev r951482. 
- Does not build with thrift libs (py, java, php, ..) will have to be built as needed
* Thu May 17 2010 - jake farrell
- Initial rpm, thrift version 0.2.0. Does not build with thrift libs (py, java, php, ..) will have to be built as needed

