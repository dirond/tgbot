#!/bin/sh
rm -r /var/lib/postgresql/data/*
#pg_basebackup -R -h db -U postgres -D /var/lib/postgresql/data
pg_basebackup --host=db --username=postgres --pgdata=/var/lib/postgresql/data --wal-method=stream --write-recovery-conf
