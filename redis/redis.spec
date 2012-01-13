%define pid_dir %{_localstatedir}/run/redis
%define pid_file %{pid_dir}/redis.pid

Summary: redis
Name: redis
Version: 2.4.6
Release: 0
License: BSD
Group: Applications/Multimedia
URL: http://code.google.com/p/redis/

Source0: redis-%{version}.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires: gcc, make
Requires(post): /sbin/chkconfig /usr/sbin/useradd
Requires(preun): /sbin/chkconfig, /sbin/service
Requires(postun): /sbin/service
Provides: redis

Packager: Allan Ralph Hutalla <ahutalla@gmail.com>

%description
Redis is a key-value database. It is similar to memcached but the dataset is
not volatile, and values can be strings, exactly like in memcached, but also
lists and sets with atomic operations to push/pop elements.

In order to be very fast but at the same time persistent the whole dataset is
taken in memory and from time to time and/or when a number of changes to the
dataset are performed it is written asynchronously on disk. You may lose the
last few queries that is acceptable in many applications but it is as fast
as an in memory DB (beta 6 of Redis includes initial support for master-slave
replication in order to solve this problem by redundancy).

Compression and other interesting features are a work in progress. Redis is
written in ANSI C and works in most POSIX systems like Linux, *BSD, Mac OS X,
and so on. Redis is free software released under the very liberal BSD license.

%prep
%setup

%{__cat} <<EOF >redis.logrotate
%{_localstatedir}/log/redis/*log {
    missingok
}
EOF

%{__cat} <<'EOF' >redis.sysv
#!/bin/bash
#
# Init file for redis
#
# chkconfig: - 80 12
# description: A persistent key-value database with network interface
# processname: redis-server
# config: /etc/redis.conf
# pidfile: %{pidfile}

source %{_sysconfdir}/init.d/functions

RETVAL=0
prog="redis-server"

start() {
  echo -n $"Starting $prog: "
  daemon --user redis --pidfile %{pid_file} %{_sbindir}/$prog /etc/redis.conf
  RETVAL=$?
  echo
  [ $RETVAL -eq 0 ] && touch %{_localstatedir}/lock/subsys/$prog
  return $RETVAL
}

stop() {
    PID=`cat %{pid_file} 2>/dev/null`
    if [ -n "$PID" ]; then
        echo "Shutdown may take a while; redis needs to save the entire database";
        echo -n $"Shutting down $prog: "
        /usr/bin/redis-cli shutdown
        if checkpid $PID 2>&1; then
            echo_failure
            RETVAL=1
        else
            rm -f /var/lib/redis/temp*rdb
            rm -f /var/lock/subsys/$prog
            echo_success
            RETVAL=0
        fi
    else
        echo -n $"$prog is not running"
        echo_failure
        RETVAL=1
    fi

    echo
    return $RETVAL
}

restart() {
  stop
  start
}

condrestart() {
    [-e /var/lock/subsys/$prog] && restart || :
}

case "$1" in
  start)
  start
  ;;
  stop)
  stop
  ;;
  status)
  status -p %{pid_file} $prog
  RETVAL=$?
  ;;
  restart)
  restart
  ;;
  condrestart|try-restart)
  condrestart
  ;;
   *)
  echo $"Usage: $0 {start|stop|status|restart|condrestart}"
  RETVAL=1
esac

exit $RETVAL
EOF

%{__cat} <<'EOF' >redis.confv
daemonize yes
pidfile %{pid_file}

port 6379
timeout 300

loglevel notice
logfile %{_localstatedir}/log/redis/redis.log

databases 16

save 900 1
save 300 10
save 60 10000

rdbcompression yes
dbfilename dump.rdb
dir %{_localstatedir}/lib/redis

slave-serve-stale-data yes
appendonly no
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
slowlog-log-slower-than 10000
slowlog-max-len 1024
vm-enabled no

hash-max-zipmap-entries 512
hash-max-zipmap-value 64
list-max-ziplist-entries 512
list-max-ziplist-value 64
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
activerehashing yes
EOF

%build
%{__make}

%install
%{__rm} -rf %{buildroot}
mkdir -p %{buildroot}%{_bindir}
%{__install} -Dp -m 0755 src/redis-server %{buildroot}%{_sbindir}/redis-server
%{__install} -Dp -m 0755 src/redis-benchmark %{buildroot}%{_bindir}/redis-benchmark
%{__install} -Dp -m 0755 src/redis-cli %{buildroot}%{_bindir}/redis-cli

%{__install} -Dp -m 0755 redis.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/redis
%{__install} -Dp -m 0755 redis.sysv %{buildroot}%{_sysconfdir}/init.d/redis
%{__install} -Dp -m 0644 redis.confv %{buildroot}%{_sysconfdir}/redis.conf
%{__install} -p -d -m 0755 %{buildroot}%{_localstatedir}/lib/redis
%{__install} -p -d -m 0755 %{buildroot}%{_localstatedir}/log/redis
%{__install} -p -d -m 0755 %{buildroot}%{_localstatedir}/redis
%{__install} -p -d -m 0755 %{buildroot}%{pid_dir}

%pre
/usr/sbin/useradd -c 'User for Redis key-value store' -u 5001 -s /bin/false -r -d %{_localstatedir}/lib/redis redis 2> /dev/null || :

%preun
if [ $1 = 0 ]; then
    # make sure redis service is not running before uninstalling

    # when the preun section is run, we've got stdin attached.  If we
    # call stop() in the redis init script, it will pass stdin along to
    # the redis-cli script; this will cause redis-cli to read an extraneous
    # argument, and the redis-cli shutdown will fail due to the wrong number
    # of arguments.  So we do this little bit of magic to reconnect stdin
    # to the terminal
    term="/dev/$(ps -p$$ --no-heading | awk '{print $2}')"
    exec < $term

    /sbin/service redis stop > /dev/null 2>&1 || :
    /sbin/chkconfig --del redis
fi

%post
/sbin/chkconfig --add redis

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-, root, root, 0755)
%{_sbindir}/redis-server
%{_bindir}/redis-benchmark
%{_bindir}/redis-cli
%{_sysconfdir}/init.d/redis
%config(noreplace) %{_sysconfdir}/redis.conf
%{_sysconfdir}/logrotate.d/redis
%dir %attr(0770,redis,redis) %{_localstatedir}/lib/redis
%dir %attr(0755,redis,redis) %{_localstatedir}/log/redis
%dir %attr(0755,redis,redis) %{_localstatedir}/run/redis
%dir %attr(0755,redis,redis) %{_localstatedir}/redis
