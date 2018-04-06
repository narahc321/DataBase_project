CREATE DATABASE MobileVoting;
USE MobileVoting;

CREATE TABLE Voter(
	Name VARCHAR(100),
	Gender VARCHAR(20),
	DateOfBirth DATE,
	AadhaarNumber VARCHAR(20),
	FatherName VARCHAR(70),
	Address VARCHAR(150),
	PinCode VARCHAR(50),
	MobileNumber VARCHAR(50),
	EmailId VARCHAR(50),
	Password VARCHAR(255),
	PRIMARY KEY (AadhaarNumber)
);

CREATE TABLE City(
	PinCode VARCHAR(50),
	city VARCHAR(50),
	ConstituencyId INT(50),
	PRIMARY KEY (PinCode)
);

CREATE TABLE Candidate(
	AadhaarNumber VARCHAR(50),
	PhotoLink VARCHAR(50),
	SignatureLink VARCHAR(50),
	EduQua VARCHAR(50),
	ConstituencyId INT(50),
	PRIMARY KEY (AadhaarNumber),
	FOREIGN KEY (AadhaarNumber) REFERENCES Voter (AadhaarNumber) 
);

CREATE TABLE ElectionOfficer(
	AadhaarNumber VARCHAR(50),
	Constituency VARCHAR(50),
	PRIMARY KEY (AadhaarNumber)
);

CREATE TABLE Constituency(
	State VARCHAR(50),
	Id INT(50) NOT NULL AUTO_INCREMENT,
	PRIMARY KEY (Id)
);

INSERT INTO Constituency (STATE) VALUES("Andhra Pradesh");
INSERT INTO Constituency (STATE) VALUES("Arunachal Pradesh");
INSERT INTO Constituency (STATE) VALUES("Assam");
INSERT INTO Constituency (STATE) VALUES("Bihar");
INSERT INTO Constituency (STATE) VALUES("Chhattisgarh");
INSERT INTO Constituency (STATE) VALUES("Goa");
INSERT INTO Constituency (STATE) VALUES("Gujarat");
INSERT INTO Constituency (STATE) VALUES("Haryana");
INSERT INTO Constituency (STATE) VALUES("Himachal Pradesh");
INSERT INTO Constituency (STATE) VALUES("Jammu And Kashmir");
INSERT INTO Constituency (STATE) VALUES("Jharkhand");
INSERT INTO Constituency (STATE) VALUES("Karnataka");
INSERT INTO Constituency (STATE) VALUES("Kerala");
INSERT INTO Constituency (STATE) VALUES("Madhya Pradesh");
INSERT INTO Constituency (STATE) VALUES("Maharashtra");
INSERT INTO Constituency (STATE) VALUES("Manipur");
INSERT INTO Constituency (STATE) VALUES("Meghalaya");
INSERT INTO Constituency (STATE) VALUES("Mizoram");
INSERT INTO Constituency (STATE) VALUES("Nagaland");
INSERT INTO Constituency (STATE) VALUES("Odisha");
INSERT INTO Constituency (STATE) VALUES("Punjab");
INSERT INTO Constituency (STATE) VALUES("Rajasthan");
INSERT INTO Constituency (STATE) VALUES("Sikkim");
INSERT INTO Constituency (STATE) VALUES("Tamil Nadu");
INSERT INTO Constituency (STATE) VALUES("Telangana");
INSERT INTO Constituency (STATE) VALUES("Tripura");
INSERT INTO Constituency (STATE) VALUES("Uttarakhand");
INSERT INTO Constituency (STATE) VALUES("Uttar Pradesh");
INSERT INTO Constituency (STATE) VALUES("West Bengal");


ALTER TABLE `MobileVoting`.`Voter` 
ADD COLUMN `VotingStatus` INT NULL DEFAULT 0 AFTER `Password`;

ALTER TABLE `MobileVoting`.`Candidate` 
ADD COLUMN `NumberOfVotes` INT NULL DEFAULT 0 AFTER `ConstituencyId`;

ALTER TABLE `MobileVoting`.`Candidate` 
ADD COLUMN `Validate` INT NULL DEFAULT 0 AFTER `NumberOfVotes`;

ALTER TABLE `MobileVoting`.`Constituency` 
ADD COLUMN `StartStop` INT NULL DEFAULT 0 AFTER `Id`;

ALTER TABLE `MobileVoting`.`ElectionOfficer` 
ADD COLUMN `Password` VARCHAR(45) NULL AFTER `Constituency`;

ALTER TABLE `MobileVoting`.`Voter` 
ADD INDEX `FK_pincode_idx` (`PinCode` ASC);
ALTER TABLE `MobileVoting`.`Voter` 
ADD CONSTRAINT `FK_pincode`
  FOREIGN KEY (`PinCode`)
  REFERENCES `MobileVoting`.`City` (`PinCode`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION;


SELECT * FROM Candidate where ConstituencyId = 23 order by NumberOfVotes DESC;

ALTER TABLE `MobileVoting`.`City` 
DROP COLUMN `ConstituencyId`,
ADD COLUMN `State` VARCHAR(45) NULL AFTER `city`;

ALTER TABLE `MobileVoting`.`City` 
CHANGE COLUMN `city` `city` VARCHAR(255) NULL DEFAULT NULL ,
CHANGE COLUMN `State` `State` VARCHAR(255) NULL DEFAULT NULL ;

Drop table City;
CREATE TABLE `MobileVoting`.`City` (
  `PinCode` INT NOT NULL,
  `City` VARCHAR(100) NULL,
  `State` VARCHAR(100) NULL,
  PRIMARY KEY (`PinCode`));

LOAD DATA LOCAL INFILE "/home/charan/project/pincode.txt" INTO TABLE City;

CREATE TABLE `MobileVoting`.`Constituency` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `State` VARCHAR(100) NULL,
  `StartStop` INT NULL,
  PRIMARY KEY (`ID`));

LOAD DATA LOCAL INFILE "/home/charan/project/states.txt" INTO TABLE Constituency;

ALTER TABLE `MobileVoting`.`Constituency` 
CHANGE COLUMN `StartStop` `StartStop` INT NULL DEFAULT 0 ;

INSERT INTO Constituency (STATE) VALUES("ANDAMAN & NICOBAR ISLANDS");
INSERT INTO Constituency (STATE) VALUES("ANDHRA PRADESH");
INSERT INTO Constituency (STATE) VALUES("ARUNACHAL PRADESH");
INSERT INTO Constituency (STATE) VALUES("ASSAM");
INSERT INTO Constituency (STATE) VALUES("BIHAR");
INSERT INTO Constituency (STATE) VALUES("CHANDIGARH");
INSERT INTO Constituency (STATE) VALUES("CHATTISGARH");
INSERT INTO Constituency (STATE) VALUES("DADRA & NAGAR HAVELI");
INSERT INTO Constituency (STATE) VALUES("DAMAN & DIU");
INSERT INTO Constituency (STATE) VALUES("DELHI");
INSERT INTO Constituency (STATE) VALUES("GOA");
INSERT INTO Constituency (STATE) VALUES("GUJARAT");
INSERT INTO Constituency (STATE) VALUES("HARYANA");
INSERT INTO Constituency (STATE) VALUES("HIMACHAL PRADESH");
INSERT INTO Constituency (STATE) VALUES("JAMMU & KASHMIR");
INSERT INTO Constituency (STATE) VALUES("JHARKHAND");
INSERT INTO Constituency (STATE) VALUES("KARNATAKA");
INSERT INTO Constituency (STATE) VALUES("KERALA");
INSERT INTO Constituency (STATE) VALUES("LAKSHADWEEP");
INSERT INTO Constituency (STATE) VALUES("MADHYA PRADESH");
INSERT INTO Constituency (STATE) VALUES("MAHARASHTRA");
INSERT INTO Constituency (STATE) VALUES("MANIPUR");
INSERT INTO Constituency (STATE) VALUES("MEGHALAYA");
INSERT INTO Constituency (STATE) VALUES("MIZORAM");
INSERT INTO Constituency (STATE) VALUES("NAGALAND");
INSERT INTO Constituency (STATE) VALUES("ODISHA");
INSERT INTO Constituency (STATE) VALUES("PONDICHERRY");
INSERT INTO Constituency (STATE) VALUES("PUNJAB");
INSERT INTO Constituency (STATE) VALUES("RAJASTHAN");
INSERT INTO Constituency (STATE) VALUES("SIKKIM");
INSERT INTO Constituency (STATE) VALUES("TAMIL NADU");
INSERT INTO Constituency (STATE) VALUES("TELANGANA");
INSERT INTO Constituency (STATE) VALUES("TRIPURA");
INSERT INTO Constituency (STATE) VALUES("UTTAR PRADESH");
INSERT INTO Constituency (STATE) VALUES("UTTARAKHAND");
INSERT INTO Constituency (STATE) VALUES("WEST BENGAL");

ALTER TABLE `MobileVoting`.`Voter` 
CHANGE COLUMN `PinCode` `PinCode` INT NULL DEFAULT NULL ;

ALTER TABLE `MobileVoting`.`ElectionOfficer` 
CHANGE COLUMN `AadhaarNumber` `UserID` VARCHAR(50) NOT NULL ;

ALTER TABLE `MobileVoting`.`ElectionOfficer` 
CHANGE COLUMN `Password` `Password` VARCHAR(255) NULL DEFAULT NULL ;

ALTER TABLE `MobileVoting`.`Candidate` 
CHANGE COLUMN `ConstituencyId` `Constituency` VARCHAR(100) NULL DEFAULT NULL ;
