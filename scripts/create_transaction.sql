CREATE OR ALTER PROCEDURE create_transaction
    @ViolationId BIGINT
AS
BEGIN
    SET NOCOUNT ON

    DECLARE @Id BIGINT
    EXECUTE generate_id @Id = @Id OUTPUT

    INSERT INTO Transactions (id, violation_id)
    VALUES (@Id, @ViolationId)
END
