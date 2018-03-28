# DataBase_project

# CREATE TABLE `voter`.`voter_infor` (
  `Name` CHAR(255) NULL,
  `gender` CHAR(3) NULL,
  `DOB` DATE NULL,
  `aadhaar_no` VARCHAR(30) NOT NULL,
  `father_name` CHAR(255) NULL,
  `Address` VARCHAR(255) NULL,
  `city` VARCHAR(255) NULL,
  `pincode` VARCHAR(10) NULL,
  `state` VARCHAR(255) NULL,
  `phone` VARCHAR(15) NULL,
  `email_id` VARCHAR(255) NULL,
  `password` VARCHAR(255) NULL,
  PRIMARY KEY (`aadhaar_no`));
