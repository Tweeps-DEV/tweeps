-- Prepare the MySQL server for the Tweeps project
CREATE DATABASE IF NOT EXISTS tweeps_dev_db;
CREATE USER IF NOT EXISTS 'tweeps_dev'@'localhost' IDENTIFIED BY 'tweeps_dev_pwd';
GRANT ALL PRIVILEGES ON tweeps_dev_db.* TO 'tweeps_dev'@'localhost';
GRANT SELECT ON performance_schema.* TO 'tweeps_dev'@'localhost';
FLUSH PRIVILEGES;
