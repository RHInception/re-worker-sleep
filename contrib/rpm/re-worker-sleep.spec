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
Release: 6%{?dist}

Group: Applications/System
License: AGPLv3
Source0: %{_src_name}-%{version}.tar.gz
Url: https://github.com/rhinception/re-worker-sleep

BuildArch: noarch
BuildRequires: python2-devel, python-setuptools
Requires: re-worker, python-setuptools

%description
A Release Engine Worker Plugin that sleeps for a period of seconds.

%prep
%setup -q -n %{_src_name}-%{version}

%build
%{__python2} setup.py build

%install
%{__python2} setup.py install -O1 --root=$RPM_BUILD_ROOT --record=re-worker-sleep-files.txt

%files -f re-worker-sleep-files.txt
%defattr(-, root, root)
%doc README.md LICENSE AUTHORS
%dir %{python2_sitelib}/%{_pkg_name}
%exclude %{python2_sitelib}/%{_pkg_name}/__init__.py*

%changelog
* Wed Jun 18 2014 Steve Milner <stevem@gnulinux.net> - 0.0.1-6
- Defattr not being used in files section.

* Tue Jun 17 2014 Ryan Cook <rcook@redhat.com> - 0.0.1-5
- Exclude __init__.py*

* Tue Jun 17 2014 Ryan Cook <rcook@redhat.com> - 0.0.1-4
- Exclude __init__.py

* Thu Jun 12 2014 Steve Milner <stevem@gnulinux.et> - 0.0.1-3
- python-setuptools is required.

* Fri Jun  9 2014 Ryan Cook <rcook@redhat.com> - 0.0.1-2
- Requires re-worker rather than reworker

* Thu Jun  5 2014 Steve Milner <stevem@gnulinux.et> - 0.0.1-1
- First release
