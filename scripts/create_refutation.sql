CREATE OR ALTER PROCEDURE create_refutation
    @ViolationId BIGINT,
    @Message TEXT
AS
BEGIN
    SET NOCOUNT ON

    DECLARE @Id BIGINT
    EXECUTE generate_id @Id = @Id OUTPUT

    INSERT INTO Refutations (id, violation_id, message, response)
    OUTPUT INSERTED.id
    VALUES (@Id, @ViolationId, @Message, NULL)
END
