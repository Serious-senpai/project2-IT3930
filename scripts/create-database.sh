#!/bin/bash
DBSTATUS=1
ERRCODE=1
i=1
sleep $i

while ([[ $DBSTATUS != "0" ]] || [[ $ERRCODE != "0" ]]) && [[ $i -lt 60 ]]  # Note: empty strings are treated as 0 arithmetically
do
	i=$(($i * 2))
	sleep $i
	echo "SQL server is not ready (DBSTATUS=$DBSTATUS, ERRCODE=$ERRCODE). Waiting for $i seconds..."

	DBSTATUS=$(/opt/mssql-tools18/bin/sqlcmd -h -1 -t 1 -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -C -Q "SET NOCOUNT ON; Select SUM(state) from sys.databases" 2> /dev/null | xargs)
	ERRCODE=$?
done

if [[ $DBSTATUS != "0" ]] || [[ $ERRCODE != "0" ]]
then 
	echo "SQL Server took too long to start up or one or more databases are not in an ONLINE state"
	exit 1
fi

echo "DBSTATUS=$DBSTATUS, ERRCODE=$ERRCODE. Creating test database..."
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -C -Q "CREATE DATABASE test"
