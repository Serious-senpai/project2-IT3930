CREATE OR ALTER PROCEDURE respond_refutation
    @Id BIGINT,
    @Response NVARCHAR(MAX)
AS
    UPDATE IT3930_Refutations
    SET response = @Response
    WHERE id = @Id
