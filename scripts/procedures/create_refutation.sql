CREATE OR ALTER PROCEDURE create_refutation
    @ViolationId BIGINT,
    @UserId BIGINT,
    @Message TEXT
AS
BEGIN
    SET NOCOUNT ON

    DECLARE @Id BIGINT
    EXECUTE generate_id @Id = @Id OUTPUT

    INSERT INTO IT3930_Refutations (id, violation_id, user_id, message, response)
    OUTPUT INSERTED.id
    VALUES (@Id, @ViolationId, @UserId, @Message, NULL)
END
