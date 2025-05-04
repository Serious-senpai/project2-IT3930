#!/bin/bash
DBSTATUS=1
ERRCODE=1
i=1
sleep $i

while [[ $DBSTATUS -ne 0 ]] || [[ $ERRCODE -ne 0 ]] || [[ $i -lt 60 ]]
do
	DBSTATUS=$(/opt/mssql-tools18/bin/sqlcmd -h -1 -t 1 -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -C -Q "SET NOCOUNT ON; Select SUM(state) from sys.databases" 2> /dev/null)
	ERRCODE=$?
	i=$(($i * 2))
	echo "SQL server is not ready. Waiting for $i seconds..."
	sleep $i
done

if [[ $DBSTATUS -ne 0 ]] || [[ $ERRCODE -ne 0 ]]
then 
	echo "SQL Server took too long to start up or one or more databases are not in an ONLINE state"
	exit 1
fi

# Run the setup script to create the DB and the schema in the DB
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -C -Q "CREATE DATABASE test"
