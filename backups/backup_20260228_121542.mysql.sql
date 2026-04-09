-- MySQL dump 10.13  Distrib 8.0.45, for Linux (x86_64)
--
-- Host: localhost    Database: Rays_machda
-- ------------------------------------------------------
-- Server version	8.0.45-0ubuntu0.22.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('902c2146adec');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `announcements`
--

DROP TABLE IF EXISTS `announcements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `announcements` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `content` text NOT NULL,
  `target_audience` varchar(50) DEFAULT NULL,
  `priority` varchar(20) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `expires_at` datetime DEFAULT NULL,
  `created_by_id` int DEFAULT NULL,
  `school_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `created_by_id` (`created_by_id`),
  KEY `school_id` (`school_id`),
  CONSTRAINT `announcements_ibfk_1` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `announcements`
--

LOCK TABLES `announcements` WRITE;
/*!40000 ALTER TABLE `announcements` DISABLE KEYS */;
INSERT INTO `announcements` VALUES (1,'eid','asc','All','Normal','2026-02-05 12:19:07','2026-02-05 15:19:00',1,NULL),(2,'Wargalin','WCdhskjdenpdwnldcbcbwpdbfb','Parents','Normal','2026-02-05 14:21:55',NULL,6,NULL);
/*!40000 ALTER TABLE `announcements` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attendance`
--

DROP TABLE IF EXISTS `attendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attendance` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `teacher_id` int DEFAULT NULL,
  `class_id` int DEFAULT NULL,
  `attendance_date` date DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `remarks` text,
  `created_at` datetime DEFAULT NULL,
  `school_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `student_id` (`student_id`),
  KEY `teacher_id` (`teacher_id`),
  KEY `class_id` (`class_id`),
  KEY `school_id` (`school_id`),
  CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`),
  CONSTRAINT `attendance_ibfk_2` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`),
  CONSTRAINT `attendance_ibfk_3` FOREIGN KEY (`class_id`) REFERENCES `class_schedules` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendance`
--

LOCK TABLES `attendance` WRITE;
/*!40000 ALTER TABLE `attendance` DISABLE KEYS */;
INSERT INTO `attendance` VALUES (1,1,1,1,'2026-02-01','Present','','2026-02-02 09:22:12',NULL),(2,1,1,1,'2026-02-02','Present','','2026-02-02 09:22:23',NULL),(3,1,1,1,'2026-01-31','Late','','2026-02-02 09:22:34',NULL),(4,1,1,1,'2026-01-29','Absent','','2026-02-02 09:22:44',NULL),(5,1,1,1,'2026-01-28','Present','','2026-02-02 09:22:52',NULL),(7,1,1,1,'2026-02-09','Present','','2026-02-09 13:15:07',NULL),(10,1,1,1,'2026-02-21','Present','','2026-02-21 05:57:51',NULL);
/*!40000 ALTER TABLE `attendance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `type` varchar(20) NOT NULL,
  `description` text,
  `created_at` datetime DEFAULT NULL,
  `school_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uix_name_type` (`name`,`type`),
  KEY `school_id` (`school_id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (4,'Salary','Expense','Staff salary payments','2026-02-09 13:39:50',NULL),(5,'Rent','Expense','Facility rent','2026-02-09 13:39:50',NULL),(6,'Utilities','Expense','Electricity, water, etc.','2026-02-09 13:39:50',NULL),(9,'Quranic Sciences','Subject','Focused on Quranic memorization, recitation, and understanding.',NULL,NULL),(10,'Islamic Jurisprudence','Subject','Study of Sharia, Fiqh, and Islamic law.',NULL,NULL),(11,'Theology & Creed','Subject','Study of Aqeedah and Islamic beliefs.',NULL,NULL),(12,'Prophetic Traditions','Subject','Focus on Hadith and Seerah.',NULL,NULL),(13,'Languages','Subject','Arabic, Somali, English and other linguistic studies.',NULL,NULL),(14,'Ethics & Manners','Subject','Training in Islamic Akhlaq and Tarbiyah.',NULL,NULL);
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `class_schedules`
--

DROP TABLE IF EXISTS `class_schedules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `class_schedules` (
  `id` int NOT NULL AUTO_INCREMENT,
  `class_name` varchar(100) NOT NULL,
  `description` text,
  `teacher_id` int DEFAULT NULL,
  `tuition_fee` decimal(10,2) DEFAULT NULL,
  `admission_fee` decimal(10,2) DEFAULT NULL,
  `exam_fee` decimal(10,2) DEFAULT NULL,
  `uniform_fee` decimal(10,2) DEFAULT NULL,
  `books_fee` decimal(10,2) DEFAULT NULL,
  `bus_fee` decimal(10,2) DEFAULT NULL,
  `activity_fee` decimal(10,2) DEFAULT NULL,
  `library_fee` decimal(10,2) DEFAULT NULL,
  `other_fee` decimal(10,2) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `school_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `teacher_id` (`teacher_id`),
  KEY `school_id` (`school_id`),
  CONSTRAINT `class_schedules_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`),
  CONSTRAINT `class_schedules_ibfk_2` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `class_schedules`
--

LOCK TABLES `class_schedules` WRITE;
/*!40000 ALTER TABLE `class_schedules` DISABLE KEYS */;
INSERT INTO `class_schedules` VALUES (1,'class 1','Class one',1,20.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,'2026-02-02 09:19:45',1);
/*!40000 ALTER TABLE `class_schedules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `class_sessions`
--

DROP TABLE IF EXISTS `class_sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `class_sessions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `class_id` int NOT NULL,
  `day_of_week` varchar(20) NOT NULL,
  `start_time` time NOT NULL,
  `end_time` time NOT NULL,
  `room` varchar(50) DEFAULT NULL,
  `school_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `class_id` (`class_id`),
  KEY `school_id` (`school_id`),
  CONSTRAINT `class_sessions_ibfk_1` FOREIGN KEY (`class_id`) REFERENCES `class_schedules` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `class_sessions`
--

LOCK TABLES `class_sessions` WRITE;
/*!40000 ALTER TABLE `class_sessions` DISABLE KEYS */;
/*!40000 ALTER TABLE `class_sessions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exam_results`
--

DROP TABLE IF EXISTS `exam_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exam_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `exam_id` int NOT NULL,
  `student_id` int NOT NULL,
  `marks_obtained` float DEFAULT NULL,
  `grade` varchar(10) DEFAULT NULL,
  `memorization_accuracy` int DEFAULT NULL,
  `tajweed_score` int DEFAULT NULL,
  `fluency_score` int DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `remarks` text,
  `evaluated_by` int DEFAULT NULL,
  `evaluated_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `school_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `exam_id` (`exam_id`),
  KEY `student_id` (`student_id`),
  KEY `evaluated_by` (`evaluated_by`),
  KEY `school_id` (`school_id`),
  CONSTRAINT `exam_results_ibfk_1` FOREIGN KEY (`exam_id`) REFERENCES `exams` (`id`),
  CONSTRAINT `exam_results_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`),
  CONSTRAINT `exam_results_ibfk_3` FOREIGN KEY (`evaluated_by`) REFERENCES `teachers` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exam_results`
--

LOCK TABLES `exam_results` WRITE;
/*!40000 ALTER TABLE `exam_results` DISABLE KEYS */;
INSERT INTO `exam_results` VALUES (1,1,1,80,'A',90,80,70,'Very Good','',NULL,'2026-02-02 09:26:44','2026-02-02 09:26:44','2026-02-02 09:26:44',NULL);
/*!40000 ALTER TABLE `exam_results` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `exams`
--

DROP TABLE IF EXISTS `exams`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `exams` (
  `id` int NOT NULL AUTO_INCREMENT,
  `exam_name` varchar(200) NOT NULL,
  `exam_type` varchar(50) NOT NULL,
  `class_id` int DEFAULT NULL,
  `teacher_id` int NOT NULL,
  `exam_date` date NOT NULL,
  `total_marks` int DEFAULT NULL,
  `passing_marks` int DEFAULT NULL,
  `surah_from` varchar(100) DEFAULT NULL,
  `surah_to` varchar(100) DEFAULT NULL,
  `juz_number` int DEFAULT NULL,
  `description` text,
  `status` varchar(20) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `school_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `class_id` (`class_id`),
  KEY `teacher_id` (`teacher_id`),
  KEY `school_id` (`school_id`),
  CONSTRAINT `exams_ibfk_1` FOREIGN KEY (`class_id`) REFERENCES `class_schedules` (`id`),
  CONSTRAINT `exams_ibfk_2` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `exams`
--

LOCK TABLES `exams` WRITE;
/*!40000 ALTER TABLE `exams` DISABLE KEYS */;
INSERT INTO `exams` VALUES (1,'Juz 4','Hifz',NULL,1,'2026-01-31',100,50,'qulhuwale','idaa jaa',4,'','Completed','2026-02-02 09:24:02','2026-02-02 09:24:02',NULL),(2,'Juz 4','Arabic Morphology (Sarf)',1,1,'2026-02-10',100,60,'','',NULL,'','Ongoing','2026-02-11 05:08:36','2026-02-11 05:08:36',NULL);
/*!40000 ALTER TABLE `exams` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `expenses`
--

DROP TABLE IF EXISTS `expenses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `expenses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(100) NOT NULL,
  `category` varchar(50) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `expense_date` date DEFAULT NULL,
  `payment_method` varchar(50) DEFAULT NULL,
  `status` varchar(20) DEFAULT 'Paid',
  `transaction_id` varchar(100) DEFAULT NULL,
  `expense_month` varchar(20) DEFAULT NULL,
  `description` text,
  `teacher_id` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `school_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `teacher_id` (`teacher_id`),
  KEY `school_id` (`school_id`),
  CONSTRAINT `expenses_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `expenses`
--

LOCK TABLES `expenses` WRITE;
/*!40000 ALTER TABLE `expenses` DISABLE KEYS */;
/*!40000 ALTER TABLE `expenses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fees`
--

DROP TABLE IF EXISTS `fees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fees` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `paid_amount` decimal(10,2) DEFAULT NULL,
  `balance` decimal(10,2) NOT NULL,
  `fee_type` varchar(50) NOT NULL,
  `fee_month` varchar(20) DEFAULT NULL,
  `due_date` date NOT NULL,
  `payment_date` datetime DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `payment_method` varchar(50) DEFAULT NULL,
  `transaction_id` varchar(100) DEFAULT NULL,
  `remarks` text,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `school_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `student_id` (`student_id`),
  KEY `school_id` (`school_id`),
  CONSTRAINT `fees_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fees`
--

LOCK TABLES `fees` WRITE;
/*!40000 ALTER TABLE `fees` DISABLE KEYS */;
/*!40000 ALTER TABLE `fees` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `login_logs`
--

DROP TABLE IF EXISTS `login_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `login_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `email` varchar(120) NOT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` varchar(255) DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `timestamp` datetime DEFAULT NULL,
  `school_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `idx_ll_school` (`school_id`),
  CONSTRAINT `login_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=168 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `login_logs`
--

LOCK TABLES `login_logs` WRITE;
/*!40000 ALTER TABLE `login_logs` DISABLE KEYS */;
INSERT INTO `login_logs` VALUES (62,1,'nor.jws@gmail.com','192.145.171.30','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-07 11:35:56',NULL),(63,1,'nor.jws@gmail.com','192.145.171.30','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-07 11:47:20',NULL),(69,1,'nor.jws@gmail.com','192.145.171.30','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-07 12:37:31',NULL),(70,1,'nor.jws@gmail.com','192.145.171.16','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-07 14:10:04',NULL),(71,1,'nor.jws@gmail.com','192.145.171.16','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-07 14:11:24',NULL),(72,1,'nor.jws@gmail.com','192.145.171.16','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-08 06:38:45',NULL),(73,1,'nor.jws@gmail.com','192.145.171.4','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-09 07:16:56',NULL),(74,1,'nor.jws@gmail.com','192.145.171.4','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-09 09:18:53',NULL),(75,1,'nor.jws@gmail.com','192.145.171.4','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-09 10:34:39',NULL),(76,1,'nor.jws@gmail.com','192.145.171.4','Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36','Success','2026-02-09 11:40:04',NULL),(77,1,'nor.jws@gmail.com','192.145.171.4','Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36','Success','2026-02-09 11:42:17',NULL),(78,1,'nor.jws@gmail.com','192.145.171.4','Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1 Edg/144.0.0.0','Success','2026-02-09 11:52:41',NULL),(79,1,'nor.jws@gmail.com','192.145.171.4','Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36','Success','2026-02-09 13:07:29',NULL),(80,1,'nor.jws@gmail.com','192.145.171.4','Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36','Success','2026-02-09 13:46:01',NULL),(81,1,'nor.jws@gmail.com','192.145.171.4','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-09 14:11:12',NULL),(82,1,'nor.jws@gmail.com','192.145.171.4','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-09 14:18:46',NULL),(83,1,'nor.jws@gmail.com','192.145.171.32','Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36','Success','2026-02-09 15:05:15',NULL),(84,1,'nor.jws@gmail.com','192.145.171.32','Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36','Success','2026-02-09 15:08:16',NULL),(85,1,'nor.jws@gmail.com','192.145.171.10','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-10 04:53:42',NULL),(86,1,'nor.jws@gmail.com','192.145.171.10','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-10 05:03:26',NULL),(87,1,'nor.jws@gmail.com','192.145.171.10','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-10 05:15:24',NULL),(88,1,'nor.jws@gmail.com','192.145.171.10','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-10 06:26:34',NULL),(89,1,'nor.jws@gmail.com','192.145.171.10','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-10 08:10:11',NULL),(90,1,'nor.jws@gmail.com','192.145.171.10','Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36','Success','2026-02-10 08:28:39',NULL),(91,1,'nor.jws@gmail.com','192.145.171.10','Mozilla/5.0 (Linux; Android 8.0.0; SM-G955U Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36 Edg/144.0.0.0','Success','2026-02-10 09:06:27',NULL),(92,1,'nor.jws@gmail.com','192.145.171.10','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-10 12:02:12',NULL),(93,1,'nor.jws@gmail.com','192.145.171.10','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-10 12:08:22',NULL),(94,1,'nor.jws@gmail.com','192.145.171.35','Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36','Success','2026-02-10 16:57:32',NULL),(95,2,'cabaas@gmail.com','192.145.171.30','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-11 05:04:57',NULL),(96,1,'nor.jws@gmail.com','192.145.171.30','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-11 05:06:57',NULL),(97,1,'nor.jws@gmail.com','192.145.171.30','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-11 05:07:01',NULL),(99,1,'nor.jws@gmail.com','192.145.171.30','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-11 05:24:05',NULL),(100,1,'nor.jws@gmail.com','192.145.171.30','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-11 06:00:18',NULL),(101,1,'nor.jws@gmail.com','192.145.171.30','Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36','Success','2026-02-11 06:09:20',NULL),(102,1,'nor.jws@gmail.com','192.145.171.24','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-11 06:40:42',NULL),(104,2,'cabaas@gmail.com','192.145.171.24','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-11 06:55:24',NULL),(105,1,'nor.jws@gmail.com','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-11 07:05:58',NULL),(106,1,'nor.jws@gmail.com','192.145.171.24','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-11 08:35:23',NULL),(107,1,'nor.jws@gmail.com','192.145.171.24','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-11 09:10:50',NULL),(108,1,'nor.jws@gmail.com','192.145.171.24','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-11 09:35:09',NULL),(109,1,'nor.jws@gmail.com','192.145.171.24','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-11 10:51:18',NULL),(110,1,'nor.jws@gmail.com','192.145.171.14','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-12 08:03:25',NULL),(111,1,'nor.jws@gmail.com','192.145.171.14','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-12 11:03:20',NULL),(112,1,'nor.jws@gmail.com','192.145.171.14','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-12 11:17:13',NULL),(114,2,'cabaas@gmail.com','192.145.171.31','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-12 11:27:43',NULL),(115,1,'nor.jws@gmail.com','192.145.171.31','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-12 11:34:31',NULL),(116,1,'nor.jws@gmail.com','192.145.171.69','Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36','Success','2026-02-12 18:12:26',NULL),(117,1,'nor.jws@gmail.com','192.145.171.79','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-13 06:07:03',NULL),(118,1,'nor.jws@gmail.com','192.145.171.14','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-14 05:07:55',NULL),(119,1,'nor.jws@gmail.com','192.145.171.20','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-15 09:59:30',NULL),(120,1,'nor.jws@gmail.com','192.145.171.20','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-15 11:53:52',NULL),(121,1,'nor.jws@gmail.com','192.145.171.20','Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36','Success','2026-02-15 13:13:54',NULL),(122,1,'nor.jws@gmail.com','192.145.171.17','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-17 07:20:26',NULL),(123,1,'nor.jws@gmail.com','192.145.171.17','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-17 08:57:34',NULL),(124,1,'nor.jws@gmail.com','192.145.171.17','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-17 08:59:19',NULL),(125,1,'nor.jws@gmail.com','192.145.171.17','Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36','Success','2026-02-17 09:06:43',NULL),(126,1,'nor.jws@gmail.com','192.145.171.17','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-17 10:28:34',NULL),(127,1,'nor.jws@gmail.com','192.145.171.17','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-17 10:31:06',NULL),(128,1,'nor.jws@gmail.com','192.145.171.17','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-17 10:32:17',NULL),(130,1,'nor.jws@gmail.com','192.145.171.31','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0','Success','2026-02-17 12:23:31',NULL),(131,1,'nor.jws@gmail.com','192.145.171.24','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Success','2026-02-21 08:26:14',NULL),(132,1,'nor.jws@gmail.com','192.145.171.24','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Success','2026-02-21 08:51:12',NULL),(133,1,'nor.jws@gmail.com','192.145.171.15','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Success','2026-02-21 09:39:55',NULL),(134,1,'nor.jws@gmail.com','192.145.171.24','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Success','2026-02-21 10:32:14',NULL),(135,1,'nor.jws@gmail.com','192.145.171.24','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Success','2026-02-21 11:02:39',NULL),(136,1,'nor.jws@gmail.com','192.145.171.24','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Success','2026-02-21 11:07:24',NULL),(137,1,'nor.jws@gmail.com','192.145.171.24','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Success','2026-02-21 11:18:59',NULL),(138,1,'nor.jws@gmail.com','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Failed','2026-02-21 11:51:51',NULL),(139,1,'nor.jws@gmail.com','127.0.0.1','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Success','2026-02-21 11:52:01',NULL),(140,1,'nor.jws@gmail.com','192.145.171.24','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Success','2026-02-21 12:11:51',NULL),(144,1,'nor.jws@gmail.com','192.145.171.24','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Success','2026-02-21 12:18:57',NULL),(146,1,'nor.jws@gmail.com','192.145.171.24','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Success','2026-02-21 12:22:59',NULL),(148,1,'nor.jws@gmail.com','192.145.171.24','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Success','2026-02-21 12:28:39',NULL),(150,1,'nor.jws@gmail.com','192.145.171.24','Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36','Success','2026-02-21 13:20:40',NULL),(152,1,'nor.jws@gmail.com','192.145.171.4','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Success','2026-02-22 09:00:32',NULL),(153,NULL,'raystechcenter@gmail.com','192.145.171.4','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Failed','2026-02-22 09:28:05',NULL),(154,NULL,'raystechcenter@gmail.com','192.145.171.4','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Failed','2026-02-22 09:29:43',NULL),(155,NULL,'raystechcenter@gmail.com','192.145.171.4','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Failed','2026-02-22 09:31:40',NULL),(156,NULL,'raystechcenter@gmail.com','192.145.171.4','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Failed','2026-02-22 09:31:45',NULL),(157,1,'nor.jws@gmail.com','192.145.171.6','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Success','2026-02-22 11:11:14',1),(158,1,'nor.jws@gmail.com','192.145.171.6','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Success','2026-02-22 11:29:59',1),(159,16,'raystechcenter@gmail.com','192.145.171.6','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Failed','2026-02-22 11:40:53',12),(160,16,'raystechcenter@gmail.com','192.145.171.6','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Success','2026-02-22 11:41:45',12),(161,1,'nor.jws@gmail.com','192.145.171.28','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Failed','2026-02-23 08:40:47',1),(162,1,'nor.jws@gmail.com','192.145.171.28','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Success','2026-02-23 08:40:56',1),(163,1,'nor.jws@gmail.com','192.145.171.21','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Success','2026-02-28 07:08:19',1),(164,16,'raystechcenter@gmail.com','192.145.171.21','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Success','2026-02-28 09:33:56',12),(165,16,'raystechcenter@gmail.com','192.145.171.21','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Failed','2026-02-28 10:29:16',12),(166,16,'raystechcenter@gmail.com','192.145.171.21','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Success','2026-02-28 10:30:35',12),(167,1,'nor.jws@gmail.com','192.145.171.21','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0','Success','2026-02-28 10:41:16',1);
/*!40000 ALTER TABLE `login_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `message_logs`
--

DROP TABLE IF EXISTS `message_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `message_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `recipient` varchar(20) NOT NULL,
  `message_body` text NOT NULL,
  `status` varchar(20) DEFAULT NULL,
  `error_message` text,
  `sent_at` datetime DEFAULT NULL,
  `message_type` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `message_logs`
--

LOCK TABLES `message_logs` WRITE;
/*!40000 ALTER TABLE `message_logs` DISABLE KEYS */;
INSERT INTO `message_logs` VALUES (1,'252617220603','*OGAYSIIS MUHIIM AH*\n\nEID\n\nasc','sent (mock)',NULL,'2026-02-05 12:19:14','announcement'),(2,'252627220603','*OGAYSIIS MUHIIM AH*\n\nEID\n\nasc','sent (mock)',NULL,'2026-02-05 12:19:14','announcement'),(3,'252617220603','*OGAYSIIS MUHIIM AH*\n\nEID\n\nasc','sent (mock)',NULL,'2026-02-05 12:20:07','announcement'),(4,'252627220603','*OGAYSIIS MUHIIM AH*\n\nEID\n\nasc','sent (mock)',NULL,'2026-02-05 12:20:07','announcement'),(5,'252617220603','*OGAYSIIS MUHIIM AH*\n\nEID\n\nasc','sent (mock)',NULL,'2026-02-05 14:22:16','announcement'),(6,'252627220603','*OGAYSIIS MUHIIM AH*\n\nEID\n\nasc','sent (mock)',NULL,'2026-02-05 14:22:16','announcement'),(7,'252627220603','*OGAYSIIS WAALIDIINTA*\n\nWARGALIN\n\nWCdhskjdenpdwnldcbcbwpdbfb','sent (mock)',NULL,'2026-02-05 17:13:18','announcement'),(8,'252627220603','*OGAYSIIS WAALIDIINTA*\n\nWARGALIN\n\nWCdhskjdenpdwnldcbcbwpdbfb','sent (mock)',NULL,'2026-02-07 12:37:44','announcement'),(9,'252617220603','*OGAYSIIS MUHIIM AH*\n\nEID\n\nasc','sent (mock)',NULL,'2026-02-07 12:38:23','announcement'),(10,'252627220603','*OGAYSIIS MUHIIM AH*\n\nEID\n\nasc','sent (mock)',NULL,'2026-02-07 12:38:23','announcement'),(11,'+1234567890','Hello from Webhook Test!','received',NULL,'2026-02-07 13:06:50','sms_inbound'),(12,'252627220603','*OGAYSIIS WAALIDIINTA*\n\nWARGALIN\n\nWCdhskjdenpdwnldcbcbwpdbfb','sent (mock)',NULL,'2026-02-07 14:10:13','announcement'),(13,'252627220603','Assalamu Alaykum Ali Muse Omer, here is the monthly report for February 2026 for student Bashir Ali Muse.\n- Attendance: 100.0%\n- Hifz Progress: Juz 5 (N/A)\n- Financial Status: Paid (Balance: $0.0)\nThank you, Rays Tech Center.','sent (mock)',NULL,'2026-02-07 14:10:34','monthly_report'),(14,'252627220603','*OGAYSIIS WAALIDIINTA*\n\nWARGALIN\n\nWCdhskjdenpdwnldcbcbwpdbfb','sent (mock)',NULL,'2026-02-09 07:17:03','announcement'),(15,'252617220603','*OGAYSIIS WAALIDIINTA*\n\nWARGALIN\n\nWCdhskjdenpdwnldcbcbwpdbfb','sent',NULL,'2026-02-09 09:20:17','announcement'),(16,'252617220603','*OGAYSIIS WAALIDIINTA*\n\nWARGALIN\n\nWCdhskjdenpdwnldcbcbwpdbfb','failed','{\"error\":{\"message\":\"Error validating application. Application has been deleted.\",\"type\":\"OAuthException\",\"code\":190,\"fbtrace_id\":\"A6fcAPU9gYsmT8W0yL9zUvp\"}}','2026-02-09 10:34:56','announcement'),(17,'252617220603','Assalamu Alaykum Ali Muse Omer, here is the monthly report for February 2026 for student Bashir Ali Muse.\n- Attendance: 100.0%\n- Hifz Progress: Juz 5 (N/A)\n- Financial Status: Paid (Balance: $0.0)\nThank you, Rays Tech Center.','failed','{\"error\":{\"message\":\"Error validating application. Application has been deleted.\",\"type\":\"OAuthException\",\"code\":190,\"fbtrace_id\":\"AQt_oYWNztxNmyHtHTTnfM6\"}}','2026-02-09 10:36:08','monthly_report'),(18,'+252617220603','Assalamu Alaykum Ali Muse Omer, here is the monthly report for February 2026 for student Bashir Ali Muse.\n- Attendance: 100.0%\n- Hifz Progress: Juz 5 (N/A)\n- Financial Status: Paid (Balance: $0.0)\nThank you, Rays Tech Center.','failed','WA: {\"error\":{\"message\":\"Error validating application. Application has been deleted.\",\"type\":\"OAuthException\",\"code\":190,\"fbtrace_id\":\"AQt_oYWNztxNmyHtHTTnfM6\"}} | SMS: TextBee Error: {\"error\":\"Invalid device id\"}','2026-02-09 10:36:09','monthly_report'),(19,'252617220603','Assalamu Alaykum Ali Muse Omer, here is the monthly report for February 2026 for student Bashir Ali Muse.\n- Attendance: 100.0%\n- Hifz Progress: Juz 5 (N/A)\n- Financial Status: Paid (Balance: $0.0)\nThank you, Rays Tech Center.','failed','{\"error\":{\"message\":\"Error validating application. Application has been deleted.\",\"type\":\"OAuthException\",\"code\":190,\"fbtrace_id\":\"A1ti0uFn3YG2ucorRuZkJYO\"}}','2026-02-09 11:29:51','monthly_report'),(20,'+252617220603','Assalamu Alaykum Ali Muse Omer, here is the monthly report for February 2026 for student Bashir Ali Muse.\n- Attendance: 100.0%\n- Hifz Progress: Juz 5 (N/A)\n- Financial Status: Paid (Balance: $0.0)\nThank you, Rays Tech Center.','failed','WA: {\"error\":{\"message\":\"Error validating application. Application has been deleted.\",\"type\":\"OAuthException\",\"code\":190,\"fbtrace_id\":\"A1ti0uFn3YG2ucorRuZkJYO\"}} | SMS: TextBee Error: {\"error\":\"Invalid device id\"}','2026-02-09 11:29:52','monthly_report'),(21,'252617220603','*OGAYSIIS MUHIIM AH*\n\nEID\n\nasc','failed','{\"error\":{\"message\":\"Error validating application. Application has been deleted.\",\"type\":\"OAuthException\",\"code\":190,\"fbtrace_id\":\"AqRx2lBF-Q96EstJ_A82IVm\"}}','2026-02-09 11:32:38','announcement');
/*!40000 ALTER TABLE `message_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `otps`
--

DROP TABLE IF EXISTS `otps`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `otps` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `code` varchar(6) NOT NULL,
  `purpose` varchar(50) NOT NULL,
  `is_used` tinyint(1) DEFAULT NULL,
  `expires_at` datetime NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `school_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `idx_otp_school` (`school_id`),
  CONSTRAINT `otps_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `otps`
--

LOCK TABLES `otps` WRITE;
/*!40000 ALTER TABLE `otps` DISABLE KEYS */;
INSERT INTO `otps` VALUES (2,1,'413288','password_reset',1,'2026-02-07 12:00:44','2026-02-07 11:50:44',NULL),(11,1,'315133','password_reset',1,'2026-02-07 12:18:26','2026-02-07 12:08:26',NULL),(12,1,'290687','password_reset',1,'2026-02-07 12:18:27','2026-02-07 12:08:27',NULL),(19,1,'890953','password_reset',1,'2026-02-07 12:23:16','2026-02-07 12:13:16',NULL),(20,1,'256633','password_reset',1,'2026-02-07 12:23:17','2026-02-07 12:13:17',NULL),(22,1,'592339','password_reset',1,'2026-02-17 10:40:07','2026-02-17 10:30:07',NULL),(23,1,'311281','password_reset',1,'2026-02-17 10:40:07','2026-02-17 10:30:07',NULL),(24,1,'002252','password_reset',1,'2026-02-17 10:41:49','2026-02-17 10:31:49',NULL),(25,1,'465468','password_reset',0,'2026-02-17 10:41:49','2026-02-17 10:31:49',NULL),(32,16,'147092','password_reset',1,'2026-02-28 09:42:19','2026-02-28 09:32:19',12);
/*!40000 ALTER TABLE `otps` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role_permissions`
--

DROP TABLE IF EXISTS `role_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `role_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `role` varchar(10) NOT NULL,
  `module` varchar(50) NOT NULL,
  `is_allowed` tinyint(1) DEFAULT NULL,
  `school_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `school_id` (`school_id`)
) ENGINE=InnoDB AUTO_INCREMENT=78 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role_permissions`
--

LOCK TABLES `role_permissions` WRITE;
/*!40000 ALTER TABLE `role_permissions` DISABLE KEYS */;
INSERT INTO `role_permissions` VALUES (1,'T','students',0,NULL),(2,'T','teachers',0,NULL),(3,'T','classes',0,NULL),(4,'T','attendance',1,NULL),(5,'T','exams',1,NULL),(6,'T','financials',0,NULL),(7,'T','reports',0,NULL),(8,'T','manage_users',0,NULL),(9,'S','students',0,NULL),(10,'S','teachers',0,NULL),(11,'S','classes',0,NULL),(12,'S','attendance',0,NULL),(13,'S','exams',0,NULL),(14,'S','financials',0,NULL),(15,'S','reports',0,NULL),(16,'S','manage_users',0,NULL),(17,'F','students',0,NULL),(18,'F','teachers',0,NULL),(19,'F','classes',0,NULL),(20,'F','attendance',0,NULL),(21,'F','exams',0,NULL),(22,'F','financials',0,NULL),(23,'F','reports',0,NULL),(24,'F','manage_users',0,NULL),(25,'P','students',0,NULL),(26,'P','teachers',0,NULL),(27,'P','classes',0,NULL),(28,'P','attendance',0,NULL),(29,'P','exams',0,NULL),(30,'P','financials',0,NULL),(31,'P','reports',0,NULL),(32,'P','manage_users',0,NULL),(33,'T','attendance',1,8),(34,'T','classes',1,8),(35,'T','exams',1,8),(36,'T','students',1,8),(37,'S','students',1,8),(38,'S','teachers',1,8),(39,'S','financials',0,8),(40,'F','financials',1,8),(41,'P','financials',0,8),(69,'T','attendance',1,12),(70,'T','classes',1,12),(71,'T','exams',1,12),(72,'T','students',1,12),(73,'S','students',1,12),(74,'S','teachers',1,12),(75,'S','financials',0,12),(76,'F','financials',1,12),(77,'P','financials',0,12);
/*!40000 ALTER TABLE `role_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `schools`
--

DROP TABLE IF EXISTS `schools`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `schools` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(120) NOT NULL,
  `subdomain` varchar(50) NOT NULL,
  `domain` varchar(120) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `status` varchar(20) DEFAULT 'Pending',
  `subscription_plan` varchar(20) DEFAULT NULL,
  `subscription_expires_at` datetime DEFAULT NULL,
  `admin_email` varchar(120) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `address` text,
  `created_at` datetime DEFAULT NULL,
  `payment_transaction_id` varchar(100) DEFAULT NULL,
  `last_payment_status` varchar(50) DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `payment_phone` varchar(20) DEFAULT NULL,
  `requested_amount` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `subdomain` (`subdomain`),
  UNIQUE KEY `domain` (`domain`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `schools`
--

LOCK TABLES `schools` WRITE;
/*!40000 ALTER TABLE `schools` DISABLE KEYS */;
INSERT INTO `schools` VALUES (1,'Main Madrasah','madrasha',NULL,1,'Active','Pro',NULL,NULL,NULL,NULL,'2026-02-21 08:49:53',NULL,NULL,NULL,NULL,NULL),(12,'nor','baazi',NULL,1,'Active','Advanced',NULL,'raystechcenter@gmail.com',NULL,NULL,'2026-02-22 11:36:58','4e6089aa-32d7-47c8-a7c1-8cb95df41ba4','Pending',NULL,'61726623',20.00);
/*!40000 ALTER TABLE `schools` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `students`
--

DROP TABLE IF EXISTS `students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `students` (
  `id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) NOT NULL,
  `enrollment_number` varchar(20) NOT NULL,
  `date_of_birth` date DEFAULT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `father_name` varchar(100) DEFAULT NULL,
  `mother_name` varchar(100) DEFAULT NULL,
  `parent_contact` varchar(20) NOT NULL,
  `address` text,
  `current_juz` int DEFAULT NULL,
  `current_surah` varchar(100) DEFAULT NULL,
  `hifz_status` varchar(20) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `class_id` int DEFAULT NULL,
  `parent_id` int DEFAULT NULL,
  `student_user_id` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `school_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_students_enrollment_number` (`enrollment_number`),
  KEY `class_id` (`class_id`),
  KEY `parent_id` (`parent_id`),
  KEY `student_user_id` (`student_user_id`),
  KEY `ix_students_full_name` (`full_name`),
  KEY `ix_students_parent_contact` (`parent_contact`),
  KEY `school_id` (`school_id`),
  CONSTRAINT `students_ibfk_1` FOREIGN KEY (`class_id`) REFERENCES `class_schedules` (`id`),
  CONSTRAINT `students_ibfk_2` FOREIGN KEY (`parent_id`) REFERENCES `users` (`id`),
  CONSTRAINT `students_ibfk_3` FOREIGN KEY (`student_user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `students_ibfk_4` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `students`
--

LOCK TABLES `students` WRITE;
/*!40000 ALTER TABLE `students` DISABLE KEYS */;
INSERT INTO `students` VALUES (1,'Bashir Ali Muse','STD-2026-001','2017-01-02','Male','Ali Muse Omer','Sahra Omar ali','+252617220603','kismayo-Suuq Yaasin',5,NULL,'Hifz','Active',1,3,NULL,'2026-02-02 09:21:41','2026-02-09 09:19:58',1);
/*!40000 ALTER TABLE `students` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subjects`
--

DROP TABLE IF EXISTS `subjects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subjects` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `code` varchar(20) DEFAULT NULL,
  `description` text,
  `category` varchar(50) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `school_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `code` (`code`),
  KEY `school_id` (`school_id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subjects`
--

LOCK TABLES `subjects` WRITE;
/*!40000 ALTER TABLE `subjects` DISABLE KEYS */;
INSERT INTO `subjects` VALUES (1,'Hifz (Memorization)','QRN-HFZ','Memorization of the Holy Quran.','Quranic Sciences',NULL,NULL),(2,'Tajweed (Recitation)','QRN-TJW','Rules of proper Quranic recitation.','Quranic Sciences',NULL,NULL),(3,'Tafsir (Exegesis)','QRN-TFS','Interpretation and explanation of the Quran.','Quranic Sciences',NULL,NULL),(4,'Fiqh (Jurisprudence)','ISL-FQK','Practical rulings of Islamic law.','Islamic Jurisprudence',NULL,NULL),(5,'Aqeedah (Theology)','ISL-AQD','Knowledge of Islamic beliefs and pillars of faith.','Theology & Creed',NULL,NULL),(6,'Hadith (Traditions)','ISL-HDT','Study of the sayings and actions of the Prophet (PBUH).','Prophetic Traditions',NULL,NULL),(7,'Seerah (Biography)','ISL-SRH','Biography of the Prophet Muhammad (PBUH).','Prophetic Traditions',NULL,NULL),(8,'Arabic Grammar (Nahw)','ARB-NHW','Rules of Arabic sentence structure.','Languages',NULL,NULL),(9,'Arabic Morphology (Sarf)','ARB-SRF','Study of Arabic word structures.','Languages',NULL,NULL),(10,'Akhlaq (Ethics)','ETK-AKL','Islamic character and moral conduct.','Ethics & Manners',NULL,NULL),(11,'Tarbiyah (Nurturing)','ETK-TRB','Spiritual and character development.','Ethics & Manners',NULL,NULL);
/*!40000 ALTER TABLE `subjects` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `system_settings`
--

DROP TABLE IF EXISTS `system_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_settings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `key` varchar(50) NOT NULL,
  `value` text,
  `description` varchar(255) DEFAULT NULL,
  `school_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uix_school_key` (`school_id`,`key`),
  CONSTRAINT `system_settings_ibfk_1` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_settings`
--

LOCK TABLES `system_settings` WRITE;
/*!40000 ALTER TABLE `system_settings` DISABLE KEYS */;
INSERT INTO `system_settings` VALUES (1,'last_auto_billing_month','2026-02','Last month fees were auto-generated',NULL),(2,'rays_machad_name','RaysMadrasah',NULL,NULL),(3,'rays_machad_address','kismayo',NULL,NULL),(4,'rays_machad_phone','+252771990022',NULL,NULL),(5,'rays_machad_email','raystechcenter@gmail.com',NULL,NULL),(6,'active_term','Winter 2026',NULL,NULL),(7,'currency','USD',NULL,NULL),(8,'whatsapp_access_token','EAARZCLPIxWXQBQtxDDCFSwGRJAc7t4qy6i14Kxs2iLAIOgLTvzGQHGcyrZBnA1MtVxE7eNn7JDCq4ubaUG6N3hQq0dDqIZCbPTON7V56YPNI6ByJ7GZAmt4YifiVW11rKwdYFOBuFARZCr7YdpS74xQuuu8N3geyjyIGPhZBBqZAvTxFyVezpk1z7l8YrkHcf3Uy1IPsa05TkjF0VsMeaeICK6LI9eWb5a35jOxBCoh3Jkyc5avQdy1MvbvbHqk86fvr20NDDnbGpZBn5714MiZCLdulW0AZDZD',NULL,NULL),(9,'whatsapp_phone_number_id','945092975361826',NULL,NULL),(10,'whatsapp_mode','live',NULL,NULL),(18,'rays_machad_name','nor',NULL,12),(19,'active_term','First Term 2026',NULL,12);
/*!40000 ALTER TABLE `system_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teachers`
--

DROP TABLE IF EXISTS `teachers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teachers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) NOT NULL,
  `employee_number` varchar(20) NOT NULL,
  `email` varchar(120) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `specialization` varchar(100) DEFAULT NULL,
  `qualification` varchar(100) DEFAULT NULL,
  `monthly_salary` decimal(10,2) DEFAULT NULL,
  `joining_date` date DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `school_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `employee_number` (`employee_number`),
  UNIQUE KEY `email` (`email`),
  KEY `user_id` (`user_id`),
  KEY `school_id` (`school_id`),
  CONSTRAINT `teachers_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `teachers_ibfk_2` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teachers`
--

LOCK TABLES `teachers` WRITE;
/*!40000 ALTER TABLE `teachers` DISABLE KEYS */;
INSERT INTO `teachers` VALUES (1,'Mohamed Hussein','TEA-2026-001','Mohamed@gmail.com','+252617220603','Islamic Studies','batch',200.00,'2026-02-02','Active',NULL,'2026-02-02 09:19:01',1);
/*!40000 ALTER TABLE `teachers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(120) NOT NULL,
  `email` varchar(120) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` varchar(10) NOT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `last_login_at` datetime DEFAULT NULL,
  `last_login_ip` varchar(45) DEFAULT NULL,
  `last_login_attempt` datetime DEFAULT NULL,
  `login_status` varchar(20) DEFAULT NULL,
  `school_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `school_id` (`school_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Rays Tech Center','nor.jws@gmail.com','scrypt:32768:8:1$kFkUNGGCbuKMpFor$cad5c5d6f27f388554d8de39dd4238809f6babb3824f7c9987bc80a361facb88589bb5dd12453169887115f721246c0d68660ad75b49923f22b8e4aa56ebc360','A',1,NULL,'2026-02-28 10:41:16','192.145.171.21','2026-02-28 10:41:16','Success',1),(2,'cabas','cabaas@gmail.com','scrypt:32768:8:1$IKVFqPl6eFY8qBPF$bf93b4eb92d53b25889ce337aa3eb0364909e387ecb4b2136a1d3557d11800abf2ad00af17ae7453c458ef2ed02f92684a5ca25b9317a4d28b0a4088b56e5659','A',1,NULL,'2026-02-12 11:27:43','192.145.171.31','2026-02-12 11:27:43','Success',1),(3,'cabas','cabaas1@gmail.com','scrypt:32768:8:1$qFb14ixjMq8iv3W6$0f35703baac1e57be97cdddc08093ec1ab2058c87e7bc28c6c5acd71ba3bc8d85bcb660a11caa4b2e78ee5276a6af755a17b1a94714d00c018d712aa3ed1ae3d','P',1,NULL,'2026-02-02 09:32:01','192.145.171.29','2026-02-02 09:32:01','Success',1),(4,'Ibrahim Mohamed','ibra@gmail.com','scrypt:32768:8:1$p1qZ8wZIwNC83gTZ$a535087c3c99a8b6edaa3adc60a087e8e30764527eadd00b931a2a48657ec7935bea4bb99f5a688313c2d05a77e00a9599b2895307a56338c82da419b0f5e057','A',1,NULL,'2026-02-02 15:33:28','192.145.171.73','2026-02-02 15:33:28','Success',1),(5,'Bukhaari','bu@gmail.com','scrypt:32768:8:1$IzsbdrOPZ0zezia7$06d497cc0aca12cb8cacaf06e2513fd619a1852e9614912089160abdd059df0c7066bf21017d2613cafccde335129468b24f8b1d44077c4b19029a7525950a35','A',1,NULL,'2026-02-02 16:26:27','192.145.171.72','2026-02-02 16:26:27','Success',1),(6,'Siyad','siyad@gmail.com','scrypt:32768:8:1$mFLGuqlTcFQ97eJK$f7264909ca4626fd40537ab95278695edf218ba8066efb45e41020ae6e23d104eadcd28e86b603919d24059954b3d213eaa7be86cf910f1daa3053247993cee5','A',1,NULL,'2026-02-05 14:10:52','102.214.170.147','2026-02-05 14:10:52','Success',1),(16,'nor Admin','raystechcenter@gmail.com','scrypt:32768:8:1$kRRdB2iWjWXAUSYL$b050af9f24409d4c9980547d2aea112ab18dfaf9c71ab774d2040b1ab24d97c7857aa7dd33bfa526ece87151b4959430d01d31b01eaef59037b94a6106731c31','A',1,NULL,'2026-02-28 10:30:35','192.145.171.21','2026-02-28 10:30:35','Success',12);
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

-- Dump completed on 2026-02-28 12:15:42
