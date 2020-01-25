Summary:	N2RRD/RRD2GRAPH Performance data collector and Graph generator
Name:		nagios-n2rrd
Version:	1.4.2
Release:	0.1
License:	GPL v2
Group:		Applications
Source0:	http://n2rrd.diglinks.com/download/n2rrd-%{version}.tar.gz
# Source0-md5:	6cf8b756272b3243fb9d8feae3ff7d72
URL:		http://n2rrd.diglinks.com/
BuildRequires:	rpm-perlprov >= 4.1-13
BuildRequires:	sed >= 4.0
Requires:	nagios-common
Requires:	perl-RRD-Simple
Requires:	perl-rrdtool
Requires:	rrdtool
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir		/etc/nagios/n2rrd
%define		nagiosconfdir	/etc/nagios
%define		nagiosdatadir	/usr/share/nagios
# argh XXX lib64?
%define		nagioslibdir	/usr/lib/nagios
%define		nagioscgidir	%{nagioslibdir}/cgi
%define		nagios_status_file	/var/lib/nagios/status.dat

%description
Nagios to RRD = n2rrd, is a small perl script, which analyzes
perf-data string for one or more name=value pairs and creates/updates
RRA (Round Robin Archives).

The archive can later be viewed by any RRD database graph frontend
e.g. rrd2graph, Cacti, Drraw, etc.

%prep
%setup -q -n n2rrd-%{version}

find -name 'dist-*' -exec rename 'dist-' '' {} ';'

%{__sed} -i -e '
	s|@BIN_PERL@|%{__perl} -w|
	s|@VERSION@|%{version}|
	s|@CONF_DIR@|%{_sysconfdir}|
	s|@RRA_DIR@|/var/lib/nagios/rra|
	s|@TEMPLATES_DIR@|%{_sysconfdir}/templates|
	s|@SERVICE_NAME_MAPS@|templates/maps/service_name_maps|
	s|@LOGFILE@|/var/log/nagios/n2rrd.log|
	s|@DOCUMENT_ROOT@|/var/cache/n2rrd|
	s|@CACHE_DIR@|tmp|
	s|@TMPDIR@|/tmp|
	s|@RRDTOOL@|%{_bindir}/rrdtool|
	s|@CGIBIN@|/nagios/cgi-bin|
	s|@NAGIOS_STATUS_FILE@|%{nagios_status_file}|
' n2rrd.pl rrd2graph.cgi n2rrd.conf

%{__sed} -i -e 's,@CGIBIN@,%{nagioscgidir},' js/zoom.js

cat > README.PLD <<'EOF'
Edit %{nagiosconfdir}/nagios.cfg to reflect the following variables

process_performance_data=1
host_perfdata_command=n2rrd-process-host-perfdata
service_perfdata_command=n2rrd-process-service-perfdata

Read more about how to integrate from:
<http://n2rrd.diglinks.com/cgi-bin/trac.fcgi/wiki/InstallationGuide140>
EOF

cat > n2rrd.cfg <<'EOF'
define command {
	command_name    n2rrd-process-host-perfdata
	command_line    %{nagioslibdir}/n2rrd -c %{_sysconfdir}/n2rrd.conf -D "HOST" -N "%{nagios_status_file}" -C '$HOSTCHECKCOMMAND$' -T $LASTHOSTCHECK$ -H $HOSTNAME$ -s "check_fping" -o "$HOSTPERFDATA$"
}

define command {
	command_name    n2rrd-process-service-perfdata
	command_line    %{nagioslibdir}/n2rrd -c %{_sysconfdir}/n2rrd.conf -N "%{nagios_status_file}" -C '$SERVICECHECKCOMMAND$' -e $SERVICEEXECUTIONTIME$ -l $SERVICELATENCY$ -T $LASTSERVICECHECK$ -H $HOSTNAME$ -s "$SERVICEDESC$" -o "$SERVICEPERFDATA$"
}
EOF

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},/var/lib/nagios/rra}
install -d $RPM_BUILD_ROOT{%{nagioslibdir},%{nagiosconfdir}/plugins,%{nagioscgidir},%{nagiosdatadir}/js}
install n2rrd.pl $RPM_BUILD_ROOT%{nagioslibdir}/n2rrd
cp -a n2rrd.conf $RPM_BUILD_ROOT%{_sysconfdir}
cp -a n2rrd.cfg $RPM_BUILD_ROOT%{nagiosconfdir}/plugins

# rrd2graph
install -d $RPM_BUILD_ROOT{/var/cache/n2rrd,%{_examplesdir}/%{name}-%{version}}
install rrd2graph.cgi $RPM_BUILD_ROOT%{nagioscgidir}
cp -a js/zoom.js $RPM_BUILD_ROOT%{nagiosdatadir}/js
# as default templates are too intrusive, we provide them as examples and
# package only essential.
install -d $RPM_BUILD_ROOT%{_sysconfdir}/templates/{maps,graph,rewrite,rra,code}
cp -a templates/environment.t $RPM_BUILD_ROOT%{_sysconfdir}/templates
cp -a templates/maps $RPM_BUILD_ROOT%{_sysconfdir}/templates
cp -a templates $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc CHANGELOG UPGRADE README.PLD
%dir %{_sysconfdir}
%dir %{_sysconfdir}/templates
%dir %{_sysconfdir}/templates/code
%dir %{_sysconfdir}/templates/graph
%dir %{_sysconfdir}/templates/maps
%dir %{_sysconfdir}/templates/rewrite
%dir %{_sysconfdir}/templates/rra
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/n2rrd.conf
%config(noreplace) %verify(not md5 mtime size) %{nagiosconfdir}/plugins/n2rrd.cfg
%attr(755,root,root) %{nagioslibdir}/n2rrd

%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/templates/environment.t
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/templates/maps/rgb.txt
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/templates/maps/rra_plugin_maps
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/templates/maps/service_name_maps

# rrd2graph
%attr(769,root,http) /var/cache/n2rrd
%attr(755,root,root) %{nagioscgidir}/rrd2graph.cgi
%dir %{nagiosdatadir}/js
%{nagiosdatadir}/js/zoom.js
%{_examplesdir}/%{name}-%{version}
