
SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';



CREATE DATABASE ###DBNAME###;

DROP TABLE IF EXISTS `dntmacs`;
CREATE TABLE `dntmacs` (
                           `id` int(11) NOT NULL AUTO_INCREMENT,
                           `datetime` datetime NOT NULL DEFAULT '0000-00-00 00:00:00' ON UPDATE current_timestamp(),
                           `machash` char(64) COLLATE utf8_unicode_ci NOT NULL,
                           `status` int(1) NOT NULL,
                           `statusmsg` char(200) COLLATE utf8_unicode_ci NOT NULL,
                           PRIMARY KEY (`id`),
                           UNIQUE KEY `uniquemac` (`machash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


DROP TABLE IF EXISTS `optout`;
CREATE TABLE `optout` (
                          `id` int(11) NOT NULL AUTO_INCREMENT,
                          `datetime` datetime NOT NULL DEFAULT '0000-00-00 00:00:00' ON UPDATE current_timestamp(),
                          `machash` char(64) COLLATE utf8_unicode_ci NOT NULL,
                          PRIMARY KEY (`id`),
                          UNIQUE KEY `uniquemac` (`machash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
