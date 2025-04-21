CREATE OR ALTER PROCEDURE delete_violation
    @Id BIGINT
AS
BEGIN
    SET NOCOUNT ON

    BEGIN TRANSACTION
        DELETE FROM Transactions
        WHERE violation_id = @Id

        DELETE FROM Refutations
        WHERE violation_id = @Id

        DELETE FROM Violations
        OUTPUT DELETED.id
        WHERE id = @Id
    COMMIT TRANSACTION
END
