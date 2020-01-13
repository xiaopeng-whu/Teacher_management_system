/*
Navicat MySQL Data Transfer

Source Server         : localhost_3306
Source Server Version : 50627
Source Host           : localhost:3306
Source Database       : school_teacher_information

Target Server Type    : MYSQL
Target Server Version : 50627
File Encoding         : 65001

Date: 2020-01-13 20:31:52
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `admin`
-- ----------------------------
DROP TABLE IF EXISTS `admin`;
CREATE TABLE `admin` (
  `username` varchar(15) NOT NULL,
  `password` varchar(15) NOT NULL,
  PRIMARY KEY (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of admin
-- ----------------------------
INSERT INTO `admin` VALUES ('root', '123456');

-- ----------------------------
-- Table structure for `research`
-- ----------------------------
DROP TABLE IF EXISTS `research`;
CREATE TABLE `research` (
  `tea_no` varchar(15) NOT NULL,
  `research_dir` varchar(15) NOT NULL DEFAULT '',
  `research_sit` varchar(15) DEFAULT NULL,
  `patent` varchar(10) DEFAULT NULL,
  `paper_name` varchar(20) DEFAULT NULL,
  `paper_level` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`tea_no`,`research_dir`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of research
-- ----------------------------
INSERT INTO `research` VALUES ('1710111', '数据库应用', '进行中', '数据库安全技术', '数据库安全技术革命', 'A');
INSERT INTO `research` VALUES ('2', '2', '2', '2', '2', '2');

-- ----------------------------
-- Table structure for `teacher_basic`
-- ----------------------------
DROP TABLE IF EXISTS `teacher_basic`;
CREATE TABLE `teacher_basic` (
  `tea_no` varchar(15) NOT NULL,
  `tea_name` varchar(5) NOT NULL,
  `sex` varchar(1) NOT NULL,
  `degree` varchar(5) NOT NULL,
  `dept` varchar(10) DEFAULT NULL,
  `graduate_sch` varchar(10) NOT NULL,
  `health` varchar(3) DEFAULT NULL,
  `title` varchar(5) DEFAULT NULL,
  `duty` varchar(10) DEFAULT NULL,
  `award_or_punish` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`tea_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of teacher_basic
-- ----------------------------
INSERT INTO `teacher_basic` VALUES ('1710111', '周红', '女', '博士', '国家网络安全学院', '武汉大学', '良好', '教授', '授课', '最受欢迎的导师');
INSERT INTO `teacher_basic` VALUES ('1710112', '小明', '男', '硕士', '经管院', '华中科技大学', '良好', '教授', '授课', '青年学者');
INSERT INTO `teacher_basic` VALUES ('2', '2', '男', '2', '2', '2', '2', '2', '2', '2');
INSERT INTO `teacher_basic` VALUES ('3', '3', '女', '3', '3', '3', '3', '3', '3', '3');

-- ----------------------------
-- Table structure for `teaching`
-- ----------------------------
DROP TABLE IF EXISTS `teaching`;
CREATE TABLE `teaching` (
  `tea_no` varchar(15) NOT NULL,
  `tea_name` varchar(5) NOT NULL,
  `cour_no` varchar(15) NOT NULL DEFAULT '',
  `cour_name` varchar(10) DEFAULT NULL,
  `cour_hour` varchar(10) DEFAULT NULL,
  `credit` varchar(3) DEFAULT NULL,
  `cour_type` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`tea_no`,`cour_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of teaching
-- ----------------------------
INSERT INTO `teaching` VALUES ('1710111', '周红', '20181001', '数据库原理', '54', '3', '专业必修课');
INSERT INTO `teaching` VALUES ('2', '3', '3', '3', '3', '3', '3');
INSERT INTO `teaching` VALUES ('3', '4', '4', '4', '4', '4', '4');
