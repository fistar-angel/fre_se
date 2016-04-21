-- MySQL dump 10.13  Distrib 5.1.73, for redhat-linux-gnu (x86_64)
--
-- Host: localhost    Database: test
-- ------------------------------------------------------
-- Server version	5.1.73

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `biological_parameters`
--

DROP TABLE IF EXISTS `biological_parameters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `biological_parameters` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `type` varchar(50) DEFAULT NULL,
  `unit` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `biological_parameters`
--

LOCK TABLES `biological_parameters` WRITE;
/*!40000 ALTER TABLE `biological_parameters` DISABLE KEYS */;
INSERT INTO `biological_parameters` VALUES (1,'Body temperature',NULL,'C'),(2,'Systolic blood pressure',NULL,'mmHg'),(3,'Diastolic blood pressure',NULL,'mmHg'),(4,'Blood oxygen',NULL,'%'),(5,'Respiration rate',NULL,'breaths/min'),(6,'Heart rate',NULL,'bpm'),(7,'Blood glucose',NULL,'mg/dl');
/*!40000 ALTER TABLE `biological_parameters` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `comparisons`
--

DROP TABLE IF EXISTS `comparisons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `comparisons` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `measurement_id` bigint(20) unsigned NOT NULL,
  `rule_id` int(10) unsigned NOT NULL,
  `parameter` varchar(150) DEFAULT NULL,
  `status` float DEFAULT '0',
  `timestamp` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  KEY `measurement_id` (`measurement_id`),
  KEY `rule_id` (`rule_id`),
  CONSTRAINT `comparisons_ibfk_1` FOREIGN KEY (`measurement_id`) REFERENCES `measurements` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `comparisons_ibfk_2` FOREIGN KEY (`rule_id`) REFERENCES `rules` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=555 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comparisons`
--

LOCK TABLES `comparisons` WRITE;
/*!40000 ALTER TABLE `comparisons` DISABLE KEYS */;
/*!40000 ALTER TABLE `comparisons` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `doctors`
--

DROP TABLE IF EXISTS `doctors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `doctors` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `surname` varchar(50) NOT NULL,
  `username` varchar(100) NOT NULL,
  `speciality` varchar(100) NOT NULL DEFAULT 'General',
  `birth_date` datetime DEFAULT '0000-00-00 00:00:00',
  `email` varchar(35) NOT NULL,
  `phone` varchar(15) NOT NULL,
  `last_login` datetime NOT NULL,
  `registration` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `doctors`
--

LOCK TABLES `doctors` WRITE;
/*!40000 ALTER TABLE `doctors` DISABLE KEYS */;
INSERT INTO `doctors` VALUES (10,'kostas','papadopoulos','kostas-papad','Generic','1956-01-01 00:00:00','aaaa@bbb.ccc','6764726473647','2015-01-19 18:32:01','2015-01-19 18:32:01');
/*!40000 ALTER TABLE `doctors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `groups`
--

DROP TABLE IF EXISTS `groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `groups` (
  `id` tinyint(3) unsigned NOT NULL AUTO_INCREMENT,
  `role` varchar(30) NOT NULL,
  `permissions` tinyint(3) unsigned NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `groups`
--

LOCK TABLES `groups` WRITE;
/*!40000 ALTER TABLE `groups` DISABLE KEYS */;
INSERT INTO `groups` VALUES (1,'doctor',7),(2,'patient',4);
/*!40000 ALTER TABLE `groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `measurements`
--

DROP TABLE IF EXISTS `measurements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `measurements` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(10) unsigned NOT NULL,
  `biological_parameter_id` int(10) unsigned NOT NULL,
  `timestamp` datetime DEFAULT '0000-00-00 00:00:00',
  `value` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=946 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `measurements`
--

LOCK TABLES `measurements` WRITE;
/*!40000 ALTER TABLE `measurements` DISABLE KEYS */;
/*!40000 ALTER TABLE `measurements` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `profile_treatment`
--

DROP TABLE IF EXISTS `profile_treatment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `profile_treatment` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(10) unsigned NOT NULL,
  `profile_id` int(10) unsigned NOT NULL,
  `treatment_id` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `profile_id` (`profile_id`),
  KEY `treatment_id` (`treatment_id`),
  CONSTRAINT `profile_treatment_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `profile_treatment_ibfk_2` FOREIGN KEY (`profile_id`) REFERENCES `profiles` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `profile_treatment_ibfk_3` FOREIGN KEY (`treatment_id`) REFERENCES `treatments` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `profile_treatment`
--

LOCK TABLES `profile_treatment` WRITE;
/*!40000 ALTER TABLE `profile_treatment` DISABLE KEYS */;
/*!40000 ALTER TABLE `profile_treatment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `profiles`
--

DROP TABLE IF EXISTS `profiles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `profiles` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` varchar(300) DEFAULT NULL,
  `ontime` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `profiles`
--

LOCK TABLES `profiles` WRITE;
/*!40000 ALTER TABLE `profiles` DISABLE KEYS */;
INSERT INTO `profiles` VALUES (2,'Alcoholic','Drinks','2015-01-15 19:38:22'),(3,'Profile-2','dfjgfysdb fy sfhsfhs fvtsd vfsdtvfsvt','2015-01-19 15:16:37'),(4,'Profile-2','mpla mpla','2015-01-19 15:28:18');
/*!40000 ALTER TABLE `profiles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `risk`
--

DROP TABLE IF EXISTS `risk`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `risk` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `comparison_id` bigint(20) unsigned NOT NULL,
  `possibility` float NOT NULL,
  `timestamp` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  KEY `comparison_id` (`comparison_id`),
  CONSTRAINT `risk_ibfk_1` FOREIGN KEY (`comparison_id`) REFERENCES `comparisons` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=545 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `risk`
--

LOCK TABLES `risk` WRITE;
/*!40000 ALTER TABLE `risk` DISABLE KEYS */;
/*!40000 ALTER TABLE `risk` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rules`
--

DROP TABLE IF EXISTS `rules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rules` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `biological_parameter_id` int(10) unsigned NOT NULL,
  `optimal_value` float NOT NULL,
  `critical_low_threshold` float NOT NULL,
  `critical_high_threshold` float NOT NULL,
  `acceptable_low_threshold` float DEFAULT NULL,
  `acceptable_high_threshold` float DEFAULT NULL,
  `time_window` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `biological_parameter_id` (`biological_parameter_id`),
  CONSTRAINT `rules_ibfk_1` FOREIGN KEY (`biological_parameter_id`) REFERENCES `biological_parameters` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rules`
--

LOCK TABLES `rules` WRITE;
/*!40000 ALTER TABLE `rules` DISABLE KEYS */;
INSERT INTO `rules` VALUES (1,1,36.6,30,44,32,38,NULL),(2,2,120,40,350,60,220,NULL),(5,3,80,30,150,NULL,110,NULL),(6,4,100,0,100,95,NULL,NULL),(8,5,12,0,150,NULL,25,NULL),(9,6,70,0,280,50,100,NULL),(10,7,80,0,1000,50,NULL,NULL);
/*!40000 ALTER TABLE `rules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subscription`
--

DROP TABLE IF EXISTS `subscription`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `subscription` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `key` varchar(100) NOT NULL,
  `ontime` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscription`
--

LOCK TABLES `subscription` WRITE;
/*!40000 ALTER TABLE `subscription` DISABLE KEYS */;
INSERT INTO `subscription` VALUES (47,'54bd404ca85dc32430766774','2015-01-19 18:35:08');
/*!40000 ALTER TABLE `subscription` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `treatments`
--

DROP TABLE IF EXISTS `treatments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `treatments` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` varchar(300) DEFAULT NULL,
  `ontime` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `treatments`
--

LOCK TABLES `treatments` WRITE;
/*!40000 ALTER TABLE `treatments` DISABLE KEYS */;
INSERT INTO `treatments` VALUES (2,'test 6',NULL,'2015-01-15 17:48:35'),(3,'test 3','dcsdvsdvs  s  !%&8%*68%8','2015-01-15 17:49:38'),(4,'test 4','a','2015-01-15 18:09:27'),(5,'test 6','a','2015-01-15 18:11:49'),(6,'test 6',NULL,'2015-01-15 18:17:15'),(7,'test 6','a','2015-01-15 18:22:05'),(8,'test 6','a','2015-01-15 18:29:50');
/*!40000 ALTER TABLE `treatments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `group_id` tinyint(3) unsigned NOT NULL,
  `doctor_id` int(10) unsigned NOT NULL,
  `name` varchar(50) NOT NULL,
  `surname` varchar(50) NOT NULL,
  `uid` varchar(50) DEFAULT NULL,
  `birth_date` datetime DEFAULT '0000-00-00 00:00:00',
  `email` varchar(35) NOT NULL,
  `phone` varchar(15) NOT NULL,
  `timezone` varchar(100) NOT NULL,
  `profile` varchar(300) NOT NULL,
  `treatment` varchar(300) NOT NULL,
  `registration_date` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uid` (`uid`),
  KEY `group_id` (`group_id`),
  KEY `doctor_id` (`doctor_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `groups` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `users_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=89 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-01-19 18:47:53
