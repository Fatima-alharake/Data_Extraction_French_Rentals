CREATE DATABASE french_rentals;
USE french_rentals;

CREATE TABLE Studapart(
    AdId INT IDENTITY(1,1) PRIMARY KEY,
    AdUrl NVARCHAR(MAX) NOT NULL,
    AdUrlHash AS CAST(HASHBYTES('SHA2_256', AdUrl) AS BINARY(32)) PERSISTED,
    AdTitle NVARCHAR(255) NOT NULL,
    RentalPrice_EUR INT NULL,
    RentalAddrese NVARCHAR(1000) NULL,
    RentalSize_m2 INT NULL,
    RentalRooms INT NULL,
    RentalFloor NVARCHAR(25) NULL,
    RentalType NVARCHAR(100) NULL,
    Furnished NVARCHAR(25) NULL,

    CONSTRAINT UQ_studapart_AdUrlHash UNIQUE (AdUrlHash)
);

CREATE TABLE LaCarteDesColocs(
    AdId INT IDENTITY(1,1) PRIMARY KEY,
    AdUrl NVARCHAR(MAX) NOT NULL,
    AdUrlHash AS CAST(HASHBYTES('SHA2_256', AdUrl) AS BINARY(32)) PERSISTED,
    AdTitle NVARCHAR(255) NOT NULL,
    RentalPrice_EUR INT NULL,
    RentalAddrese NVARCHAR(1000) NULL,
    RentalSize_m2 INT NULL,
    RentalRooms INT NULL,
    RentalFloor NVARCHAR(25) NULL,
    RentalType NVARCHAR(100) NULL,
    Furnished NVARCHAR(25) NULL,

    CONSTRAINT UQ_laCarteDesColocs_AdUrlHash UNIQUE (AdUrlHash)
);

declare @json_data NVARCHAR(max)
select @json_data = BulkColumn
from openrowset(
    BULK 'I:\m2\data acquistion\studapart_output_all.json', SINGLE_CLOB
) as datasource;

insert into Studapart(AdUrl, AdTitle, RentalPrice_EUR, RentalAddrese, RentalSize_m2, RentalRooms, RentalFloor, RentalType, Furnished)
select AdUrl, AdTitle, 
TRY_CAST(NULLIF(RentalPrice_EUR, N'') AS INT) AS RentalPrice_EUR, 
COALESCE(NULLIF(RentalAddrese, N''), N'-') AS RentalAddrese,
TRY_CAST(NULLIF(RentalSize_m2, N'') AS INT) AS RentalSize_m2,
TRY_CAST(NULLIF(RentalRooms, N'') AS INT) AS RentalRooms,
COALESCE(NULLIF(RentalFloor, N''), N'-') AS RentalFloor,
COALESCE(NULLIF(RentalType, N''), N'-') AS RentalType,
COALESCE(
    NULLIF(
        REPLACE(
            REPLACE(Furnished, N'Meublé', N'True'),
            N'Non meublé', N'False'
        ),
        N''
    ),
    N'-'
) AS Furnished from openjson(@json_data)
WITH (
    AdUrl               VARCHAR(MAX)    '$.AdUrl',
    AdTitle             NVARCHAR(255)   '$.AdTitle',
    RentalPrice_EUR     NVARCHAR(100)   '$.RentalPrice_EUR',
    RentalAddrese       NVARCHAR(1000)  '$.RentalAddrese',
    RentalSize_m2       NVARCHAR(100)   '$.RentalSize_m2',
    RentalRooms         NVARCHAR(100)   '$.RentalRooms',
    RentalFloor         NVARCHAR(25)    '$.RentalFloor',
    RentalType          NVARCHAR(100)   '$.RentalType',
    Furnished           NVARCHAR(25)    '$.Furnished'
);


DECLARE @json_data NVARCHAR(MAX);
SELECT @json_data = BulkColumn
FROM OPENROWSET(
    BULK 'I:\m2\data acquistion\colocs_data_paris.json',
    SINGLE_NCLOB
) AS datasource;

insert into LaCarteDesColocs(AdUrl, AdTitle, RentalPrice_EUR, RentalAddrese, RentalSize_m2, RentalRooms, RentalFloor, RentalType, Furnished)
select AdUrl, AdTitle, 
TRY_CAST(NULLIF(RentalPrice_EUR, N'') AS INT) AS RentalPrice_EUR, 
COALESCE(NULLIF(RentalAddrese, N''), N'-') AS RentalAddrese,
TRY_CAST(NULLIF(RentalSize_m2, N'') AS INT) AS RentalSize_m2,
TRY_CAST(NULLIF(RentalRooms, N'') AS INT)AS RentalRooms,
COALESCE(NULLIF(RentalFloor, N''), N'-') AS RentalFloor,
COALESCE(NULLIF(RentalType, N''), N'-') AS RentalType,
COALESCE(
    NULLIF(
        REPLACE(
            REPLACE(Furnished, N'Meublé', N'True'),
            N'Non meublé', N'False'
        ),
        N''
    ),
    N'-'
) AS Furnished from openjson(@json_data)
WITH (
    AdUrl               VARCHAR(MAX)    '$.AdUrl',
    AdTitle             NVARCHAR(255)   '$.AdTitle',
    RentalPrice_EUR     NVARCHAR(100)   '$.RentalPrice_EUR',
    RentalAddrese       NVARCHAR(1000)  '$.RentalAddrese',
    RentalSize_m2       NVARCHAR(100)   '$.RentalSize_m2',
    RentalRooms         NVARCHAR(100)   '$.RentalRooms',
    RentalFloor         NVARCHAR(25)    '$.RentalFloor',
    RentalType          NVARCHAR(100)   '$.RentalType',
    Furnished           NVARCHAR(25)    '$.Furnished'
);

select * from Studapart
select * from LaCarteDesColocs