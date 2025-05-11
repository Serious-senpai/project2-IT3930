CREATE OR ALTER PROCEDURE create_user
    @Fullname NVARCHAR(255),
    @Phone VARCHAR(15),
    @HashedPassword VARCHAR(136)
AS
BEGIN
    SET NOCOUNT ON

    DECLARE @Id BIGINT
    EXECUTE generate_id @Id = @Id OUTPUT

    INSERT INTO IT3930_Users (id, fullname, phone, permissions, hashed_password)
    OUTPUT INSERTED.id
    VALUES (@Id, @Fullname, @Phone, 0, @HashedPassword)
END
