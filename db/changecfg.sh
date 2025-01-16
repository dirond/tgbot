#!/bin/sh
#cp -f /docker-entrypoint-initdb.d/my-postgres.conf /var/lib/postgresql/data/postgresql.conf 
#cp -f /docker-entrypoint-initdb.d/pg_hba.conf /var/lib/postgresql/data/pg_hba.conf 
echo 'host	replication	postgres	172.19.0.0/16	trust' >> /var/lib/postgresql/data/pg_hba.conf

echo "
wal_level = replica
wal_log_hints = on
max_wal_senders = 2
max_replication_slots = 2
hot_standby = on
hot_standby_feedback = on
log_replication_commands = on
log_destination = 'stderr'
logging_collector = on
log_directory = '/logs'
log_filename = 'postgresql.log'
" >> /var/lib/postgresql/data/postgresql.conf
whoami
