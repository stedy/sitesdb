#!/bin/bash
/usr/bin/sqlite3 version1.db << !
.mode csv
.output downloads/isolateresults.csv
select * from isolate where Isolate = "$1";
!
