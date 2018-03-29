CREATE DATABASE MobileVoting;
USE MobileVoting;

CREATE TABLE Voter(
	Name VARCHAR(50),
	Gender VARCHAR(20),
	DateOfBirth DATE,
	AadhaarNumber VARCHAR(20),
	FatherName VARCHAR(50),
	Address VARCHAR(50),
	PinCode VARCHAR(50),
	MobileNumber VARCHAR(50),
	EmailId VARCHAR(50),
	Password VARCHAR(50),
	PRIMARY KEY (AadhaarNumber)
);

CREATE TABLE City(
	PinCode VARCHAR(50),
	City VARCHAR(50),
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
	Id INT(50) NOT NULL AUTO_INCREMENT
	PRIMARY KEY (Id)
);

INSERT INTO Constituency VALUES("Andhra Pradesh");
INSERT INTO Constituency VALUES("Arunachal Pradesh");
INSERT INTO Constituency VALUES("Assam");
INSERT INTO Constituency VALUES("Bihar");
INSERT INTO Constituency VALUES("Chhattisgarh");
INSERT INTO Constituency VALUES("Goa");
INSERT INTO Constituency VALUES("Gujarat");
INSERT INTO Constituency VALUES("Haryana");
INSERT INTO Constituency VALUES("Himachal Pradesh");
INSERT INTO Constituency VALUES("Jammu And Kashmir");
INSERT INTO Constituency VALUES("Jharkhand");
INSERT INTO Constituency VALUES("Karnataka");
INSERT INTO Constituency VALUES("Kerala");
INSERT INTO Constituency VALUES("Madhya Pradesh");
INSERT INTO Constituency VALUES("Maharashtra");
INSERT INTO Constituency VALUES("Manipur");
INSERT INTO Constituency VALUES("Meghalaya");
INSERT INTO Constituency VALUES("Mizoram");
INSERT INTO Constituency VALUES("Nagaland");
INSERT INTO Constituency VALUES("Odisha");
INSERT INTO Constituency VALUES("Punjab");
INSERT INTO Constituency VALUES("Rajasthan");
INSERT INTO Constituency VALUES("Sikkim");
INSERT INTO Constituency VALUES("Tamil Nadu");
INSERT INTO Constituency VALUES("Telangana");
INSERT INTO Constituency VALUES("Tripura");
INSERT INTO Constituency VALUES("Uttarakhand");
INSERT INTO Constituency VALUES("Uttar Pradesh");
INSERT INTO Constituency VALUES("West Bengal");
