-- Some params are required for substitution:
DECLARE
    @SessionSecretKey NVARCHAR(MAX) = ?,
    @Epoch DATETIME2 = ?

IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE name = 'Config' AND type = 'U')
BEGIN
    CREATE TABLE Config (
        name NVARCHAR(255) PRIMARY KEY,
        value NVARCHAR(MAX) NOT NULL
    )
    INSERT INTO Config VALUES ('session_secret_key', @SessionSecretKey)
END
ELSE
    UPDATE Config SET value = @SessionSecretKey WHERE name = 'session_secret_key'

IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE name = 'ConfigBigInt' AND type = 'U')
BEGIN
    CREATE TABLE ConfigBigInt (
        name NVARCHAR(255) PRIMARY KEY,
        value BIGINT NOT NULL
    )
    INSERT INTO ConfigBigInt VALUES ('id_counter', 0)
END

IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE name = 'ConfigDateTime2' AND type = 'U')
BEGIN
    CREATE TABLE ConfigDateTime2 (
        name NVARCHAR(255) PRIMARY KEY,
        value DATETIME2 NOT NULL
    )
    INSERT INTO ConfigDateTime2 VALUES ('epoch', @Epoch)
END

IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE name = 'Violations' AND type = 'U')
    CREATE TABLE Violations (
        id BIGINT PRIMARY KEY,
        category TINYINT NOT NULL CHECK (category IN (0, 1, 2)),
        plate NVARCHAR(12) NOT NULL,
        fine_vnd BIGINT NOT NULL,
        video_url NVARCHAR(2048) NOT NULL
    )

IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE name = 'Refutations' AND type = 'U')
    CREATE TABLE Refutations (
        id BIGINT PRIMARY KEY,
        violation_id BIGINT NOT NULL,
        message NVARCHAR(MAX) NOT NULL,
        response NVARCHAR(MAX),
        CONSTRAINT FK_Refutations_Violations FOREIGN KEY (violation_id) REFERENCES Violations(id)
    )

IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE name = 'Transactions' AND type = 'U')
    CREATE TABLE Transactions (
        id BIGINT PRIMARY KEY,
        violation_id BIGINT NOT NULL,
        CONSTRAINT FK_Transactions_Violations FOREIGN KEY (violation_id) REFERENCES Violations(id)
    )

IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE name = 'Authorities' AND type = 'U')
    CREATE TABLE Authorities (
        id BIGINT PRIMARY KEY,
        username NVARCHAR(50) UNIQUE NOT NULL,
        hashed_password NVARCHAR(255) NOT NULL
    )
