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

CREATE TABLE `creation_template` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '模板ID',
  `template_name` varchar(255) NOT NULL COMMENT '模板名称',
  `script_prompt` text COMMENT '剧本创作提示词',
  `character_prompt` text COMMENT '角色创建提示词',
  `scene_prompt` text COMMENT '场景创建提示词',
  `shot_prompt` text COMMENT '分镜制作提示词',
  `image_description_prompt` text COMMENT '画面描述生成提示词',
  `bgm_prompt` text COMMENT '背景音乐创造提示词',
  `video_generation_prompt` text COMMENT '视频画面生成提示词',
  `operator` varchar(100) NOT NULL COMMENT '操作人',
  `status` enum('ACTIVE','INACTIVE') DEFAULT NULL COMMENT '状态',
  `created_at` datetime DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime DEFAULT (now()) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `template_name` (`template_name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='剧本创作模板';

CREATE TABLE `dict_management` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '字典ID',
  `dict_name` varchar(255) NOT NULL COMMENT '字典名称',
  `dict_key` varchar(100) NOT NULL COMMENT '字典键',
  `dict_value` varchar(500) NOT NULL COMMENT '字典值',
  `dict_type` varchar(100) NOT NULL COMMENT '字典类型',
  `description` varchar(500) DEFAULT NULL COMMENT '字典描述',
  `sort_order` int(11) DEFAULT NULL COMMENT '排序序号',
  `status` enum('ACTIVE','INACTIVE') DEFAULT NULL COMMENT '状态',
  `operator` varchar(100) NOT NULL COMMENT '操作人',
  `created_at` datetime DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime DEFAULT (now()) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `dict_name` (`dict_name`),
  UNIQUE KEY `dict_key` (`dict_key`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='字典管理';