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

alter table City 
ADD column city varchar(30) after PinCode;