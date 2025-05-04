CREATE OR ALTER PROCEDURE delete_violation
    @Id BIGINT
AS
BEGIN
    SET NOCOUNT ON

    BEGIN TRANSACTION
        DELETE FROM IT3930_Transactions
        WHERE violation_id = @Id

        DELETE FROM IT3930_Refutations
        WHERE violation_id = @Id

        DELETE FROM IT3930_Violations
        OUTPUT DELETED.id
        WHERE id = @Id
    COMMIT TRANSACTION
END
