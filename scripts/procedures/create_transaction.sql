CREATE OR ALTER PROCEDURE create_transaction
    @ViolationId BIGINT,
    @UserId BIGINT
AS
BEGIN
    SET NOCOUNT ON

    DECLARE @Id BIGINT
    EXECUTE generate_id @Id = @Id OUTPUT

    INSERT INTO IT3930_Transactions (id, violation_id, user_id)
    VALUES (@Id, @ViolationId, @UserId)
END
