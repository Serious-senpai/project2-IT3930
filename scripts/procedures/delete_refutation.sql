CREATE OR ALTER PROCEDURE delete_refutation
    @Id BIGINT
AS
    DELETE FROM IT3930_Refutations
    OUTPUT DELETED.id
    WHERE id = @Id
