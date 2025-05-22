CREATE TABLE crypto
(
    id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    cryptoName VARCHAR(20),
    cryptoPrice FLOAT,
    cryptoDatetime DATETIME,
    cryptoClassement INTEGER,
    cryptoVolume VARCHAR(20),
    cryptoChange FLOAT
)