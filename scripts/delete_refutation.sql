CREATE OR ALTER PROCEDURE delete_refutation
    @Id BIGINT
AS
    DELETE FROM Refutations
    OUTPUT DELETED.id
    WHERE id = @Id
