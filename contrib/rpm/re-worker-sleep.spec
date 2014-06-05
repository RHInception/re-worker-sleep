%if 0%{?rhel} && 0%{?rhel} <= 6
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

%global _pkg_name replugin
%global _src_name reworkersleep

Name: re-worker-sleep
Summary: RE Worker which sleeps for a number of seconds
Version: 0.0.1
Release: 1%{?dist}

Group: Applications/System
License: AGPLv3
Source0: %{_src_name}-%{version}.tar.gz
Url: https://github.com/rhinception/re-worker-sleep

BuildArch: noarch
BuildRequires: python2-devel, python-setuptools
Requires: reworker

%description
A Release Engine Worker Plugin that sleeps for a period of seconds.

%prep
%setup -q -n %{_src_name}-%{version}

%build
%{__python2} setup.py build

%install
%{__python2} setup.py install -O1 --root=$RPM_BUILD_ROOT --record=re-worker-sleep-files.txt

%files -f re-worker-sleep-files.txt
%doc README.md LICENSE AUTHORS
%dir %{python2_sitelib}/%{_pkg_name}

%changelog
* Thu Jun  5 2014 Steve Milner <stevem@gnulinux.et> - 0.0.1-1
- First release
