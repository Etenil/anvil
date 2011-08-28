-- MySQL dump 10.13  Distrib 5.1.58, for debian-linux-gnu (i486)
--
-- Host: localhost    Database: anvil
-- ------------------------------------------------------
-- Server version	5.1.58-1

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
-- Table structure for table `actionqueue`
--

DROP TABLE IF EXISTS `actionqueue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `actionqueue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action` varchar(128) NOT NULL,
  `item` varchar(128) DEFAULT NULL,
  `args` text DEFAULT NULL,
  `state` tinyint(4) NOT NULL DEFAULT 0,
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `action_ind` (`action`),
  KEY `item_ind` (`item`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `bug_comments`
--

DROP TABLE IF EXISTS `bug_comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bug_comments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `bug` int(11) DEFAULT NULL,
  `author` varchar(64) DEFAULT NULL,
  `author_email` varchar(128) DEFAULT NULL,
  `is_extern` tinyint(1) NOT NULL DEFAULT '0',
  `message` text,
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `bug_ind` (`bug`),
  KEY `author_ind` (`author`),
  CONSTRAINT `bug_comments_ibfk_1` FOREIGN KEY (`bug`) REFERENCES `bugs` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bug_comments`
--

LOCK TABLES `bug_comments` WRITE;
/*!40000 ALTER TABLE `bug_comments` DISABLE KEYS */;
/*!40000 ALTER TABLE `bug_comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bug_template`
--

DROP TABLE IF EXISTS `bug_template`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bug_template` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project` int(11) DEFAULT NULL,
  `template` text,
  PRIMARY KEY (`id`),
  KEY `project_ind` (`project`),
  CONSTRAINT `bug_template_ibfk_1` FOREIGN KEY (`project`) REFERENCES `project` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bug_template`
--

LOCK TABLES `bug_template` WRITE;
/*!40000 ALTER TABLE `bug_template` DISABLE KEYS */;
/*!40000 ALTER TABLE `bug_template` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bugs`
--

DROP TABLE IF EXISTS `bugs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bugs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `subject` text,
  `description` text,
  `guest` tinyint(1) NOT NULL DEFAULT '0',
  `author_extern` text,
  `author_extern_email` text,
  `author_intern` int(11) DEFAULT NULL,
  `project` int(11) DEFAULT NULL,
  `status` int(11) NOT NULL DEFAULT '0',
  `assigned_to` int(11) DEFAULT NULL,
  `version` varchar(16) DEFAULT NULL,
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `modified` timestamp NOT NULL,
  PRIMARY KEY (`id`),
  KEY `author_ind` (`author_intern`),
  KEY `project_ind` (`project`),
  KEY `status_ind` (`status`),
  KEY `version_ind` (`version`),
  KEY `assigned_ind` (`assigned_to`),
  CONSTRAINT `bugs_ibfk_1` FOREIGN KEY (`project`) REFERENCES `project` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bugs`
--

LOCK TABLES `bugs` WRITE;
/*!40000 ALTER TABLE `bugs` DISABLE KEYS */;
/*!40000 ALTER TABLE `bugs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `doc_history`
--

DROP TABLE IF EXISTS `doc_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `doc_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `document` int(11) DEFAULT NULL,
  `modified` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `author` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `document_ind` (`document`),
  CONSTRAINT `doc_history_ibfk_1` FOREIGN KEY (`document`) REFERENCES `document` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `doc_history`
--

LOCK TABLES `doc_history` WRITE;
/*!40000 ALTER TABLE `doc_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `doc_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `document`
--

DROP TABLE IF EXISTS `document`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `document` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project` int(11) NOT NULL,
  `name` varchar(128) NOT NULL,
  `title` varchar(128) NOT NULL,
  `content` text,
  `deleted` tinyint(1) NOT NULL DEFAULT '0',
  `author` int(11) NOT NULL,
  `mtime` timestamp NOT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `project_ind` (`project`),
  KEY `author_ind` (`author`),
  CONSTRAINT `document_ibfk_1` FOREIGN KEY (`project`) REFERENCES `project` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `document`
--

LOCK TABLES `document` WRITE;
/*!40000 ALTER TABLE `document` DISABLE KEYS */;
/*!40000 ALTER TABLE `document` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `messages`
--

DROP TABLE IF EXISTS `messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `messages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `author` int(11) DEFAULT NULL,
  `destination` int(11) DEFAULT NULL,
  `subject` text,
  `content` text,
  `is_read` tinyint(1) NOT NULL DEFAULT '0',
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `par_ind1` (`author`),
  KEY `par_ind2` (`destination`),
  CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`author`) REFERENCES `user` (`id`),
  CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`destination`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `messages`
--

LOCK TABLES `messages` WRITE;
/*!40000 ALTER TABLE `messages` DISABLE KEYS */;
/*!40000 ALTER TABLE `messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project`
--

DROP TABLE IF EXISTS `project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) DEFAULT NULL,
  `owned_by_team` tinyint(1) NOT NULL DEFAULT '0',
  `owner` int(11) DEFAULT NULL,
  `homepage` text,
  `description` text,
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `name_ind` (`name`),
  KEY `par_ind1` (`owner`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project`
--

LOCK TABLES `project` WRITE;
/*!40000 ALTER TABLE `project` DISABLE KEYS */;
/*!40000 ALTER TABLE `project` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sessions`
--

DROP TABLE IF EXISTS `sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sessions` (
  `session_id` varchar(128) NOT NULL,
  `atime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `data` text,
  UNIQUE KEY `session_id` (`session_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sessions`
--

LOCK TABLES `sessions` WRITE;
/*!40000 ALTER TABLE `sessions` DISABLE KEYS */;
/*!40000 ALTER TABLE `sessions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ssh_keys`
--

DROP TABLE IF EXISTS `ssh_keys`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ssh_keys` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` int(11) NOT NULL,
  `pubkey` text,
  PRIMARY KEY (`id`),
  KEY `par_ind` (`user`),
  CONSTRAINT `ssh_keys_ibfk_1` FOREIGN KEY (`user`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ssh_keys`
--

LOCK TABLES `ssh_keys` WRITE;
/*!40000 ALTER TABLE `ssh_keys` DISABLE KEYS */;
/*!40000 ALTER TABLE `ssh_keys` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `team`
--

DROP TABLE IF EXISTS `team`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `team` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `team`
--

LOCK TABLES `team` WRITE;
/*!40000 ALTER TABLE `team` DISABLE KEYS */;
/*!40000 ALTER TABLE `team` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `team_link`
--

DROP TABLE IF EXISTS `team_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `team_link` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` int(11) DEFAULT NULL,
  `team` int(11) DEFAULT NULL,
  `committer` tinyint(1) NOT NULL DEFAULT '0',
  `manager` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `par_ind1` (`user`),
  KEY `par_ind2` (`team`),
  CONSTRAINT `team_link_ibfk_1` FOREIGN KEY (`user`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `team_link_ibfk_2` FOREIGN KEY (`team`) REFERENCES `team` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `team_link`
--

LOCK TABLES `team_link` WRITE;
/*!40000 ALTER TABLE `team_link` DISABLE KEYS */;
/*!40000 ALTER TABLE `team_link` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `translation`
--

DROP TABLE IF EXISTS `translation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `translation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project` int(11) DEFAULT NULL,
  `lang` varchar(8) NOT NULL,
  `original` text,
  `translation` text,
  PRIMARY KEY (`id`),
  KEY `project_ind` (`project`),
  CONSTRAINT `translation_ibfk_1` FOREIGN KEY (`project`) REFERENCES `project` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `translation`
--

LOCK TABLES `translation` WRITE;
/*!40000 ALTER TABLE `translation` DISABLE KEYS */;
/*!40000 ALTER TABLE `translation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `email` varchar(128) DEFAULT NULL,
  `password` varchar(64) DEFAULT NULL,
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `homepage` text,
  `description` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2011-08-22 18:36:37
