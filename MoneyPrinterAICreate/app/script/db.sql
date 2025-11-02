CREATE TABLE `llm_model` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '模型ID',
  `display_name` varchar(255) NOT NULL COMMENT '模型展示名称',
  `model_name` varchar(255) NOT NULL COMMENT '模型名称',
  `base_url` varchar(255) DEFAULT NULL COMMENT '调用地址',
  `api_key` varchar(255) DEFAULT NULL COMMENT '密钥',
  `model_provider` varchar(255) DEFAULT NULL COMMENT '模型供应商',
  `model_type` enum('TEXT','IMAGE','VIDEO','AUDIO','MULTIMODAL') NOT NULL COMMENT '模型类型',
  `support_reference_image` tinyint(1) DEFAULT '0' COMMENT '是否支持参考图',
  `support_multiple_reference_images` tinyint(1) DEFAULT '0' COMMENT '是否支持多张参考图',
  `support_first_frame` tinyint(1) DEFAULT '0' COMMENT '是否支持首帧',
  `support_last_frame` tinyint(1) DEFAULT '0' COMMENT '是否支持尾帧',
  `status` int(11) DEFAULT '1' COMMENT '状态：1-启用，0-禁用',
  `operator` varchar(100) DEFAULT NULL COMMENT '操作人',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `display_name` (`display_name`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='LLM模型表';