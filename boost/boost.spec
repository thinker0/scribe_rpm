Name: 		boost
Version: 	1.48.0
Release:	2%{?release_tag}	
License: 	Boost
Summary:    The free peer-reviewed portable C++ source libraries
Group:      Development/Libraries
URL: 		http://www.boost.org/
Source0: 	boost-%{version}.tar.gz

BuildRoot: 	%{_tmppath}/%{name}-%{version}

%description
Boost provides free peer-reviewed portable C++ source libraries. The
emphasis is on libraries which work well with the C++ Standard
Library, in the hopes of establishing "existing practice" for
extensions and providing reference implementations so that the Boost
libraries are suitable for eventual standardization. (Some of the
libraries have already been proposed for inclusion in the C++
Standards Committee's upcoming C++ Standard Library Technical Report.)

%files
%defattr(-, root, root, 0755)
%{_libdir}/*.so
%{_libdir}/libboost*.so*

%package devel
Summary: Development tools for the %{name}-%{version}
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}

%description devel
This package contains client libraries for %{name}. If you like to develop
programs using %{name}, you will need to install %{name}-devel.

%files devel 
%defattr(-, root, root, 0755)
%{_includedir}/*
%{_libdir}/*.a

%prep
%setup -q -n %{name}-%{version}

%build
export CPPFLAGS="%{optflags}"
export CFLAGS="%{optflags}"
export LDLAGS="%{optflags}"
./bootstrap.sh --prefix=%{_prefix} --exec-prefix=%{_prefix} --libdir=%{_libdir}
./bjam

%install
%{__rm} -rf %{buildroot}
export CPPFLAGS="%{optflags}"
export CFLAGS="%{optflags}"
export LDLAGS="%{optflags}"
./bjam --prefix=%{buildroot} --libdir=%{buildroot}%{_libdir} --includedir=%{buildroot}%{_includedir} install

%post
/sbin/ldconfig

%clean
%{__rm} -rf %{buildroot}

%changelog
* Thu Jan 3 2012 thinker0
- boost version 1.48.0
* Thu Apr 1 2010 - jake farrell
- Initial rpm, boost version 1.42.0
