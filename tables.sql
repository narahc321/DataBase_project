CREATE DATABASE MobileVoting;
USE MobileVoting;

CREATE TABLE Voter(
	Name VARCHAR(100),
	Gender VARCHAR(20),
	DateOfBirth DATE,
	AadhaarNumber VARCHAR(20),
	PinCode VARCHAR(50),
	MobileNumber VARCHAR(50),
	EmailId VARCHAR(50),
	Password VARCHAR(255),
	VotingStatus VARCHAR(50),
	PRIMARY KEY (AadhaarNumber)
);

CREATE TABLE City(
	PinCode INT(50),
	City VARCHAR(50),
	State VARCHAR(50),
	PRIMARY KEY (PinCode)
);

CREATE TABLE Candidate(
	AadhaarNumber VARCHAR(50),
	PhotoLink VARCHAR(50),
	SignatureLink VARCHAR(50),
	EduQua VARCHAR(50),
	Constituency INT(50),
	NumberOfVotes INT(11),
	Validate INT(11),
	PRIMARY KEY (AadhaarNumber),
	FOREIGN KEY (AadhaarNumber) REFERENCES Voter (AadhaarNumber) 
);

CREATE TABLE ElectionOfficer(
	UserID VARCHAR(50),
	Constituency VARCHAR(50),
	Password VARCHAR(225),
	PRIMARY KEY (UserID)
);

CREATE TABLE Constituency(
	State VARCHAR(50),
	Id INT(50) NOT NULL AUTO_INCREMENT,
	StartStopElection INT(11),
	StartStopNomination INT(11),
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


LOAD DATA LOCAL INFILE "/home/anagh/states.txt" INTO TABLE Constituency;
LOAD DATA LOCAL INFILE "/home/anagh/pincode.txt" INTO TABLE City;


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

