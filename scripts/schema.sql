-- Some params are required for substitution:
DECLARE
    @SessionSecretKey NVARCHAR(MAX) = ?,
    @Epoch DATETIME2 = ?

IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE name = 'IT3930_Config' AND type = 'U')
BEGIN
    CREATE TABLE IT3930_Config (
        name NVARCHAR(255) PRIMARY KEY,
        value NVARCHAR(MAX) NOT NULL
    )
    INSERT INTO IT3930_Config VALUES ('session_secret_key', @SessionSecretKey)
END
ELSE
    UPDATE IT3930_Config SET value = @SessionSecretKey WHERE name = 'session_secret_key'

IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE name = 'IT3930_ConfigBigInt' AND type = 'U')
BEGIN
    CREATE TABLE IT3930_ConfigBigInt (
        name NVARCHAR(255) PRIMARY KEY,
        value BIGINT NOT NULL
    )
    INSERT INTO IT3930_ConfigBigInt VALUES ('id_counter', 0)
END

IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE name = 'IT3930_ConfigDateTime2' AND type = 'U')
BEGIN
    CREATE TABLE IT3930_ConfigDateTime2 (
        name NVARCHAR(255) PRIMARY KEY,
        value DATETIME2 NOT NULL
    )
    INSERT INTO IT3930_ConfigDateTime2 VALUES ('epoch', @Epoch)
END

IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE name = 'IT3930_Users' AND type = 'U')
BEGIN
    CREATE TABLE IT3930_Users (
        id BIGINT PRIMARY KEY,
        fullname NVARCHAR(255) NOT NULL,
        phone VARCHAR(15) UNIQUE NOT NULL,
        permissions BIGINT NOT NULL,
        hashed_password VARCHAR(136) NOT NULL
    )
    INSERT INTO IT3930_Users
    VALUES (0, N'Nguyễn Thế Nhật Minh', '0856650960', 1, '2d7748e501f6b8aa941a884b8bc03d2825fcc4897b58631f3a0a48ebcda1094a128cf9fedfd3209251a1f3f71f3b45c95ba2bfd63f6badc10ef3dca304f10684D1a3D7AA')
END

IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE name = 'IT3930_Vehicles' AND type = 'U')
BEGIN
    CREATE TABLE IT3930_Vehicles (
        plate VARCHAR(12) PRIMARY KEY,
        user_id BIGINT NOT NULL,
        CONSTRAINT FK_Vehicles_Accounts FOREIGN KEY (user_id) REFERENCES IT3930_Users(id)
    )
    CREATE NONCLUSTERED INDEX IDX_Vehicles_user_id ON IT3930_Vehicles(user_id)
END

IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE name = 'IT3930_Violations' AND type = 'U')
BEGIN
    CREATE TABLE IT3930_Violations (
        id BIGINT PRIMARY KEY,
        creator_id BIGINT NOT NULL,
        category TINYINT NOT NULL CHECK (category IN (0, 1, 2)),
        plate VARCHAR(12) NOT NULL,
        fine_vnd BIGINT NOT NULL,
        video_url NVARCHAR(2048) NOT NULL,
        CONSTRAINT FK_Violations_Users FOREIGN KEY (creator_id) REFERENCES IT3930_Users(id),
        CONSTRAINT FK_Violations_Vehicles FOREIGN KEY (plate) REFERENCES IT3930_Vehicles(plate)
    )
    CREATE NONCLUSTERED INDEX IDX_Violations_plate ON IT3930_Violations(plate)
END

IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE name = 'IT3930_Detected' AND type = 'U')
BEGIN
    CREATE TABLE IT3930_Detected (
        id BIGINT PRIMARY KEY,
        category TINYINT NOT NULL CHECK (category IN (0, 1, 2)),
        plate VARCHAR(12) NOT NULL,
        video_url NVARCHAR(2048) NOT NULL,
        CONSTRAINT FK_Detected_Vehicles FOREIGN KEY (plate) REFERENCES IT3930_Vehicles(plate)
    )
    CREATE NONCLUSTERED INDEX IDX_Detected_plate ON IT3930_Detected(plate)
END

IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE name = 'IT3930_Refutations' AND type = 'U')
BEGIN
    CREATE TABLE IT3930_Refutations (
        id BIGINT PRIMARY KEY,
        violation_id BIGINT NOT NULL,
        user_id BIGINT NOT NULL,
        message NVARCHAR(MAX) NOT NULL,
        response NVARCHAR(MAX),
        CONSTRAINT FK_Refutations_Violations FOREIGN KEY (violation_id) REFERENCES IT3930_Violations(id),
        CONSTRAINT FK_Refutations_Users FOREIGN KEY (user_id) REFERENCES IT3930_Users(id)
    )
    CREATE NONCLUSTERED INDEX IDX_Refutations_violation_id ON IT3930_Refutations(violation_id)
    CREATE NONCLUSTERED INDEX IDX_Refutations_user_id ON IT3930_Refutations(user_id)
END

IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE name = 'IT3930_Transactions' AND type = 'U')
BEGIN
    CREATE TABLE IT3930_Transactions (
        id BIGINT PRIMARY KEY,
        violation_id BIGINT UNIQUE NOT NULL,
        user_id BIGINT NOT NULL,
        CONSTRAINT FK_Transactions_Violations FOREIGN KEY (violation_id) REFERENCES IT3930_Violations(id),
        CONSTRAINT FK_Transactions_Users FOREIGN KEY (user_id) REFERENCES IT3930_Users(id)
    )
    CREATE NONCLUSTERED INDEX IDX_Transactions_user_id ON IT3930_Transactions(user_id)
END
