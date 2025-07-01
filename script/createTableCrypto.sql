CREATE TABLE crypto
(
    id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    cryptoName VARCHAR(50),
    cryptoPrice FLOAT,
    cryptoDatetime DATETIME,
    cryptoClassement INTEGER,
    cryptoVolume VARCHAR(50),
    cryptoChange FLOAT
)