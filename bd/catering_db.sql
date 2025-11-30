-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: catering_db
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `adicionales`
--

DROP TABLE IF EXISTS `adicionales`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `adicionales` (
  `id_adicional` int NOT NULL AUTO_INCREMENT,
  `nombre_adicional` varchar(100) NOT NULL,
  `descripcion` text,
  `precio` decimal(10,2) NOT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id_adicional`),
  UNIQUE KEY `nombre_adicional` (`nombre_adicional`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `adicionales`
--

LOCK TABLES `adicionales` WRITE;
/*!40000 ALTER TABLE `adicionales` DISABLE KEYS */;
INSERT INTO `adicionales` VALUES (1,'Decoración temática','Decoración personalizada según el evento',350.00,1),(2,'Barra de bebidas','Servicio de bar con bebidas alcohólicas y sin alcohol',450.00,1),(3,'Postres gourmet','Mesa de postres premium con opciones variadas',280.00,1),(4,'DJ y sonido','Servicio de música y sonido profesional',500.00,1),(5,'Fotografía','Sesión fotográfica profesional del evento',600.00,1);
/*!40000 ALTER TABLE `adicionales` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menus_especiales`
--

DROP TABLE IF EXISTS `menus_especiales`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menus_especiales` (
  `id_menu_especial` int NOT NULL AUTO_INCREMENT,
  `id_pedido` int NOT NULL,
  `tipo_menu` enum('Vegano','Celíaco','Alérgico') NOT NULL,
  `cantidad` int NOT NULL,
  PRIMARY KEY (`id_menu_especial`),
  KEY `id_pedido` (`id_pedido`),
  CONSTRAINT `menus_especiales_ibfk_1` FOREIGN KEY (`id_pedido`) REFERENCES `pedidos` (`id_pedido`) ON DELETE CASCADE,
  CONSTRAINT `menus_especiales_chk_1` CHECK ((`cantidad` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menus_especiales`
--

LOCK TABLES `menus_especiales` WRITE;
/*!40000 ALTER TABLE `menus_especiales` DISABLE KEYS */;
INSERT INTO `menus_especiales` VALUES (1,1,'Vegano',5),(2,1,'Celíaco',1),(3,1,'Alérgico',4),(4,2,'Vegano',2),(5,2,'Celíaco',1),(6,3,'Vegano',2),(7,3,'Celíaco',1);
/*!40000 ALTER TABLE `menus_especiales` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `paquetes`
--

DROP TABLE IF EXISTS `paquetes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `paquetes` (
  `id_paquete` int NOT NULL AUTO_INCREMENT,
  `nombre_paquete` enum('Básico','Estándar','Premium') NOT NULL,
  `descripcion` text,
  `precio_base` decimal(10,2) NOT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id_paquete`),
  UNIQUE KEY `nombre_paquete` (`nombre_paquete`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `paquetes`
--

LOCK TABLES `paquetes` WRITE;
/*!40000 ALTER TABLE `paquetes` DISABLE KEYS */;
INSERT INTO `paquetes` VALUES (1,'Básico','Incluye menú estándar y servicio básico de mesa',45.00,1),(2,'Estándar','Incluye menú mejorado, decoración simple y servicio completo',75.00,1),(3,'Premium','Incluye menú gourmet, decoración temática y servicio VIP',120.00,1);
/*!40000 ALTER TABLE `paquetes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedido_adicionales`
--

DROP TABLE IF EXISTS `pedido_adicionales`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedido_adicionales` (
  `id_pedido_adicional` int NOT NULL AUTO_INCREMENT,
  `id_pedido` int NOT NULL,
  `id_adicional` int NOT NULL,
  PRIMARY KEY (`id_pedido_adicional`),
  KEY `id_pedido` (`id_pedido`),
  KEY `id_adicional` (`id_adicional`),
  CONSTRAINT `pedido_adicionales_ibfk_1` FOREIGN KEY (`id_pedido`) REFERENCES `pedidos` (`id_pedido`) ON DELETE CASCADE,
  CONSTRAINT `pedido_adicionales_ibfk_2` FOREIGN KEY (`id_adicional`) REFERENCES `adicionales` (`id_adicional`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedido_adicionales`
--

LOCK TABLES `pedido_adicionales` WRITE;
/*!40000 ALTER TABLE `pedido_adicionales` DISABLE KEYS */;
INSERT INTO `pedido_adicionales` VALUES (1,1,2),(2,2,1),(3,2,4),(4,3,1);
/*!40000 ALTER TABLE `pedido_adicionales` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedidos`
--

DROP TABLE IF EXISTS `pedidos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedidos` (
  `id_pedido` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int NOT NULL,
  `id_paquete` int NOT NULL,
  `fecha_evento` date NOT NULL,
  `cantidad_invitados` int NOT NULL,
  `precio_total` decimal(10,2) NOT NULL,
  `estado` enum('Pendiente','Confirmado','En preparación','Listo para entrega','Completado','Cancelado') NOT NULL DEFAULT 'Pendiente',
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_pedido`),
  KEY `id_usuario` (`id_usuario`),
  KEY `id_paquete` (`id_paquete`),
  CONSTRAINT `pedidos_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE,
  CONSTRAINT `pedidos_ibfk_2` FOREIGN KEY (`id_paquete`) REFERENCES `paquetes` (`id_paquete`) ON DELETE RESTRICT,
  CONSTRAINT `pedidos_chk_1` CHECK ((`cantidad_invitados` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedidos`
--

LOCK TABLES `pedidos` WRITE;
/*!40000 ALTER TABLE `pedidos` DISABLE KEYS */;
INSERT INTO `pedidos` VALUES (1,2,1,'2025-12-06',30,1800.00,'Completado','2025-11-29 03:56:05','2025-11-30 17:15:37'),(2,2,1,'2025-12-07',5,1075.00,'Completado','2025-11-30 16:47:40','2025-11-30 17:13:42'),(3,2,1,'2025-12-08',5,575.00,'Completado','2025-11-30 17:30:37','2025-11-30 17:38:58'),(4,2,1,'2025-12-08',50,2250.00,'Completado','2025-11-30 17:46:28','2025-11-30 17:57:03'),(5,2,1,'2025-12-07',10,450.00,'Pendiente','2025-11-30 18:14:34','2025-11-30 18:14:34');
/*!40000 ALTER TABLE `pedidos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `nombre_usuario` varchar(50) NOT NULL,
  `contraseña` varchar(255) NOT NULL,
  `nombre_completo` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `rol` enum('cliente','admin','cocinero') NOT NULL DEFAULT 'cliente',
  `fecha_registro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `nombre_usuario` (`nombre_usuario`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'admin','$pbkdf2-sha256$29000$N0boPScEAEDo/b.XsnaOUQ$mAHXEZHHFYgm.HSAOQ7UCrIb7MbFjSZ.kh18nB55WOU','Administrador Del Sistema','admin@gmail.com','admin','2025-11-29 03:52:48'),(2,'Joaquin','$pbkdf2-sha256$29000$4Pwfo1SqdQ7hPCdkLEVo7Q$pJ6Bk6nGLj10ROrdu9rcokanXqLBu4l11KnPzZXzkOw','Joaquin Pomayay','joaquinpomayay@gmail.com','cliente','2025-11-29 03:54:21'),(4,'cocinero','$pbkdf2-sha256$29000$aW1tDcF4bw1B6L3XuldKyQ$Pi21ZQZ4sckAILF0pYaWtcDr9MOQ1gfkMxbtUpJYfgs','cocinero del sistema','cocinero@gmail.com','cocinero','2025-11-30 16:51:00'),(5,'Hector Cocinero','$pbkdf2-sha256$29000$E0KIMQZAiFHqvTcGIIQQYg$QK7AsVQdS15keBGucGZa1rOQMbJ5aN88gCUz9o/fkVw','Hector','hector@gmail.com','cocinero','2025-11-30 17:55:56');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `vista_insumos_semanales`
--

DROP TABLE IF EXISTS `vista_insumos_semanales`;
/*!50001 DROP VIEW IF EXISTS `vista_insumos_semanales`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vista_insumos_semanales` AS SELECT 
 1 AS `semana`,
 1 AS `total_invitados_normales`,
 1 AS `total_veganos`,
 1 AS `total_celiacos`,
 1 AS `total_alergicos`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vista_pedidos_completos`
--

DROP TABLE IF EXISTS `vista_pedidos_completos`;
/*!50001 DROP VIEW IF EXISTS `vista_pedidos_completos`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vista_pedidos_completos` AS SELECT 
 1 AS `id_pedido`,
 1 AS `fecha_evento`,
 1 AS `cantidad_invitados`,
 1 AS `precio_total`,
 1 AS `estado`,
 1 AS `fecha_creacion`,
 1 AS `cliente`,
 1 AS `email_cliente`,
 1 AS `nombre_paquete`,
 1 AS `precio_base`*/;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `vista_insumos_semanales`
--

/*!50001 DROP VIEW IF EXISTS `vista_insumos_semanales`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vista_insumos_semanales` AS select yearweek(`p`.`fecha_evento`,0) AS `semana`,sum(`p`.`cantidad_invitados`) AS `total_invitados_normales`,coalesce(sum((case when (`me`.`tipo_menu` = 'Vegano') then `me`.`cantidad` else 0 end)),0) AS `total_veganos`,coalesce(sum((case when (`me`.`tipo_menu` = 'Celíaco') then `me`.`cantidad` else 0 end)),0) AS `total_celiacos`,coalesce(sum((case when (`me`.`tipo_menu` = 'Alérgico') then `me`.`cantidad` else 0 end)),0) AS `total_alergicos` from (`pedidos` `p` left join `menus_especiales` `me` on((`p`.`id_pedido` = `me`.`id_pedido`))) where (`p`.`estado` = 'Confirmado') group by yearweek(`p`.`fecha_evento`,0) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vista_pedidos_completos`
--

/*!50001 DROP VIEW IF EXISTS `vista_pedidos_completos`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vista_pedidos_completos` AS select `p`.`id_pedido` AS `id_pedido`,`p`.`fecha_evento` AS `fecha_evento`,`p`.`cantidad_invitados` AS `cantidad_invitados`,`p`.`precio_total` AS `precio_total`,`p`.`estado` AS `estado`,`p`.`fecha_creacion` AS `fecha_creacion`,`u`.`nombre_completo` AS `cliente`,`u`.`email` AS `email_cliente`,`paq`.`nombre_paquete` AS `nombre_paquete`,`paq`.`precio_base` AS `precio_base` from ((`pedidos` `p` join `usuarios` `u` on((`p`.`id_usuario` = `u`.`id_usuario`))) join `paquetes` `paq` on((`p`.`id_paquete` = `paq`.`id_paquete`))) order by `p`.`fecha_evento` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-30 18:20:16
