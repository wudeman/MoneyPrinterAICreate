import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.llm_model import LLMModel, ModelType
from app.models.llm_schema import LLMModelCreate, LLMModelUpdate, LLMModelQuery
from app.services.llm_model_service import LLMModelService
import time
import streamlit.components.v1 as components

# 已经移除streamlit-aggrid导入，统一使用HTML表格+query params方案
AGGRID_AVAILABLE = False
import os


def update_model_status(db: Session, model_id: int, status: bool):
    """更新模型状态"""
    try:
        # 获取当前模型信息以获取operator
        current_model = LLMModelService.get_model(db, model_id)
        if not current_model:
            st.error("模型不存在")
            return
            
        model_data = LLMModelUpdate(
            status=1 if status else 0,
            operator=current_model.operator or "system"  # 使用当前模型的operator或默认值
        )
        LLMModelService.update_model(db, model_id, model_data)
        st.success(f"模型状态已{'启用' if status else '禁用'}")
        time.sleep(1)
        st.session_state.refresh_trigger += 1
        st.rerun()
    except Exception as e:
        st.error(f"更新状态失败: {str(e)}")


def handle_edit_model(model):
    """处理编辑模型"""
    st.session_state.selected_model = model
    st.session_state.model_page = "edit"
    st.rerun()


def handle_delete_model(db: Session, model_id: int, display_name: str):
    """处理删除模型"""
    try:
        if st.session_state.get(f"confirm_delete_{model_id}", False):
            LLMModelService.delete_model(db, model_id)
            st.success(f"模型 {display_name} 删除成功")
            time.sleep(1)
            st.session_state.refresh_trigger += 1
            # 清除确认状态
            if f"confirm_delete_{model_id}" in st.session_state:
                del st.session_state[f"confirm_delete_{model_id}"]
            st.rerun()
        else:
            st.session_state[f"confirm_delete_{model_id}"] = True
            st.warning(f"再次点击删除按钮确认删除模型 {display_name}")
            st.rerun()
    except Exception as e:
        st.error(f"删除失败: {str(e)}")


def model_management_page():
    """模型管理页面"""
    st.title("模型管理")
    
    # 初始化session state
    if "model_page" not in st.session_state:
        st.session_state.model_page = "list"
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = None
    if "refresh_trigger" not in st.session_state:
        st.session_state.refresh_trigger = 0
    if "search_name" not in st.session_state:
        st.session_state.search_name = ""
    if "model_type_filter" not in st.session_state:
        st.session_state.model_type_filter = ""
    if "current_page" not in st.session_state:
        st.session_state.current_page = 1
    if "page_size" not in st.session_state:
        st.session_state.page_size = 10
    
    # 创建数据库会话
    db_gen = get_db()
    db: Session = next(db_gen)
    
    try:
        # 根据当前页面状态显示不同内容
        if st.session_state.model_page == "list":
            display_model_list_page(db)
        elif st.session_state.model_page == "create":
            display_create_model_page(db)
        elif st.session_state.model_page == "edit" and st.session_state.selected_model:
            display_edit_model_page(db, st.session_state.selected_model)
    finally:
        # 关闭数据库会话
        try:
            next(db_gen, None)  # This will trigger the finally block in get_db
        except StopIteration:
            pass


def display_model_list_page(db: Session):
    """显示模型列表页面"""
    st.subheader("模型列表")
    
    # 搜索、筛选和按钮区域 - 一行布局
    col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1, 1, 1, 1])
    
    with col1:
        search_name = st.text_input("搜索模型名称", value=st.session_state.search_name)
    
    with col2:
        model_type_options = [("", "全部")] + [(t.value, t.value) for t in ModelType]
        model_type_filter = st.selectbox(
            "模型类型筛选",
            options=model_type_options,
            format_func=lambda x: x[1],
            index=0
        )
    
    with col3:
        # 每页显示数量
        page_size = st.selectbox(
            "每页数量",
            options=[5, 10, 20, 50],
            index=[5, 10, 20, 50].index(st.session_state.page_size) if st.session_state.page_size in [5, 10, 20, 50] else 1
        )
    
    with col4:
        # 查询按钮
        if st.button("查询"):
            st.session_state.search_name = search_name
            st.session_state.model_type_filter = model_type_filter[0] if model_type_filter[0] != "" else ""
            st.session_state.page_size = page_size
            st.session_state.current_page = 1  # 重置到第一页
            st.session_state.refresh_trigger += 1
            st.rerun()
    
    with col5:
        # 新增按钮
        if st.button("添加新模型"):
            st.session_state.model_page = "create"
            st.session_state.selected_model = None
            st.rerun()
    
    with col6:
        # 刷新按钮
        if st.button("刷新列表", key="refresh_list"):
            st.session_state.refresh_trigger += 1
            st.rerun()
    
    # 查询模型列表
    query = LLMModelQuery(
        display_name=st.session_state.search_name if st.session_state.search_name else None,
        model_type=st.session_state.model_type_filter if st.session_state.model_type_filter else None,
        page=st.session_state.current_page,
        page_size=st.session_state.page_size
    )
    
    models, total = LLMModelService.list_models(db, query)
    
    # 计算分页信息
    total_pages = max(1, (total + st.session_state.page_size - 1) // st.session_state.page_size)
    start_item = (st.session_state.current_page - 1) * st.session_state.page_size + 1
    end_item = min(st.session_state.current_page * st.session_state.page_size, total)
    
    # 显示分页信息和统计
    st.write(f"显示第 {start_item} - {end_item} 条，共 {total} 条记录")
    
    # 显示模型列表
    if models:
        # 为每个模型初始化会话状态
        for model in models:
            # 初始化密钥显示状态
            key_toggle_key = f"toggle_key_{model.id}"
            if key_toggle_key not in st.session_state:
                st.session_state[key_toggle_key] = False
        
        # 添加CSS样式 - 优化居中显示
        st.markdown("""
        <style>
            .model-table-header {
                background-color: #f0f2f6;
                padding: 12px 8px;
                border-radius: 8px;
                margin-bottom: 8px;
                font-weight: bold;
                text-align: center;
            }
            .model-table-row {
                padding: 12px 8px;
                border-bottom: 1px solid #e6e6e6;
                text-align: center;
            }
            .model-table-row:hover {
                background-color: #f8f9fa;
            }
            .status-enabled {
                color: #28a745;
                font-weight: bold;
            }
            .status-disabled {
                color: #dc3545;
                font-weight: bold;
            }
            .feature-supported {
                color: #28a745;
                font-size: 16px;
            }
            .feature-unsupported {
                color: #6c757d;
                font-size: 16px;
            }
            .action-buttons {
                display: flex;
                gap: 8px;
                justify-content: center;
                align-items: center;
            }
            .key-display {
                font-family: monospace;
                padding: 6px 8px;
                border: 1px solid #e6e6e6;
                border-radius: 4px;
                background-color: #f8f9fa;
                min-height: 38px;
                display: flex;
                align-items: center;
                justify-content: center;
                text-align: center;
            }
            .key-toggle-btn {
                background: none;
                border: none;
                cursor: pointer;
                padding: 6px;
                border-radius: 4px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 14px;
            }
            .key-toggle-btn:hover {
                background-color: #e9ecef;
            }
            .center-content {
                display: flex;
                justify-content: center;
                align-items: center;
                text-align: center;
                height: 100%;
            }
            .text-truncate {
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                max-width: 100%;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # 表头 - 居中显示
        st.markdown("""
        <div class="model-table-header">
            <div style="display: grid; grid-template-columns: 1fr 1fr 1.5fr 1fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 1fr 1.2fr 1.2fr 1.5fr; gap: 8px; align-items: center; text-align: center;">
                <div>展示名称</div>
                <div>模型名称</div>
                <div>调用地址</div>
                <div>密钥</div>
                <div>模型类型</div>
                <div>参考图</div>
                <div>多参考图</div>
                <div>首帧</div>
                <div>尾帧</div>
                <div>状态</div>
                <div>操作人</div>
                <div>更新时间</div>
                <div>操作</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 表格内容 - 所有内容居中显示
        for i, model in enumerate(models):
            with st.container():
                # 使用列布局创建表格行
                cols = st.columns([1, 1, 1.5, 1, 0.8, 0.8, 0.8, 0.8, 0.8, 1, 1.2, 1.2, 1.5])
                
                with cols[0]:
                    # 展示名称 - 居中显示
                    st.markdown(f'<div class="center-content"><div class="text-truncate" title="{model.display_name}">{model.display_name}</div></div>', unsafe_allow_html=True)
                
                with cols[1]:
                    # 模型名称 - 居中显示
                    st.markdown(f'<div class="center-content"><div class="text-truncate" title="{model.model_name}">{model.model_name}</div></div>', unsafe_allow_html=True)
                
                with cols[2]:
                    # 调用地址 - 居中显示
                    base_url_display = model.base_url if model.base_url else "-"
                    st.markdown(f'<div class="center-content"><div class="text-truncate" title="{base_url_display}">{base_url_display}</div></div>', unsafe_allow_html=True)
                
                with cols[3]:
                    # 密钥显示 - 居中显示
                    key_col1, key_col2 = st.columns([3, 1])
                    with key_col1:
                        if st.session_state[f"toggle_key_{model.id}"]:
                            # 显示密钥
                            key_display = model.api_key if model.api_key else "-"
                            st.markdown(f'<div class="key-display text-truncate" title="{key_display}">{key_display}</div>', unsafe_allow_html=True)
                        else:
                            # 隐藏密钥
                            key_display = "*" * 10 if model.api_key else "-"
                            st.markdown(f'<div class="key-display">{key_display}</div>', unsafe_allow_html=True)
                    with key_col2:
                        # 使用按钮切换显示状态 - 居中显示
                        st.markdown('<div class="center-content">', unsafe_allow_html=True)
                        if st.session_state[f"toggle_key_{model.id}"]:
                            if st.button("👁️", key=f"hide_{model.id}", help="隐藏密钥"):
                                st.session_state[f"toggle_key_{model.id}"] = False
                                st.rerun()
                        else:
                            if st.button("👁️", key=f"show_{model.id}", help="显示密钥"):
                                st.session_state[f"toggle_key_{model.id}"] = True
                                st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                
                with cols[4]:
                    # 模型类型 - 居中显示
                    type_mapping = {
                        "text": "文本",
                        "image": "图像", 
                        "video": "视频",
                        "audio": "音频"
                    }
                    type_display = type_mapping.get(model.model_type.value, model.model_type.value)
                    st.markdown(f'<div class="center-content">{type_display}</div>', unsafe_allow_html=True)
                
                with cols[5]:
                    # 参考图 - 居中显示
                    feature_class = "feature-supported" if model.support_reference_image else "feature-unsupported"
                    icon = "✅" if model.support_reference_image else "❌"
                    st.markdown(f'<div class="center-content"><span class="{feature_class}">{icon}</span></div>', unsafe_allow_html=True)
                
                with cols[6]:
                    # 多参考图 - 居中显示
                    feature_class = "feature-supported" if model.support_multiple_reference_images else "feature-unsupported"
                    icon = "✅" if model.support_multiple_reference_images else "❌"
                    st.markdown(f'<div class="center-content"><span class="{feature_class}">{icon}</span></div>', unsafe_allow_html=True)
                
                with cols[7]:
                    # 首帧 - 居中显示
                    feature_class = "feature-supported" if model.support_first_frame else "feature-unsupported"
                    icon = "✅" if model.support_first_frame else "❌"
                    st.markdown(f'<div class="center-content"><span class="{feature_class}">{icon}</span></div>', unsafe_allow_html=True)
                
                with cols[8]:
                    # 尾帧 - 居中显示
                    feature_class = "feature-supported" if model.support_last_frame else "feature-unsupported"
                    icon = "✅" if model.support_last_frame else "❌"
                    st.markdown(f'<div class="center-content"><span class="{feature_class}">{icon}</span></div>', unsafe_allow_html=True)
                
                with cols[9]:
                    # 状态 - 居中显示
                    status_class = "status-enabled" if model.status == 1 else "status-disabled"
                    status_text = "启用" if model.status == 1 else "禁用"
                    st.markdown(f'<div class="center-content"><span class="{status_class}">{status_text}</span></div>', unsafe_allow_html=True)
                
                with cols[10]:
                    # 操作人 - 居中显示
                    operator_display = model.operator if model.operator else "-"
                    st.markdown(f'<div class="center-content"><div class="text-truncate" title="{operator_display}">{operator_display}</div></div>', unsafe_allow_html=True)
                
                with cols[11]:
                    # 更新时间 - 居中显示
                    update_time = model.updated_at.strftime('%Y-%m-%d %H:%M') if model.updated_at else "-"
                    st.markdown(f'<div class="center-content">{update_time}</div>', unsafe_allow_html=True)
                
                with cols[12]:
                    # 操作按钮 - 居中显示
                    st.markdown('<div class="center-content">', unsafe_allow_html=True)
                    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
                    
                    with btn_col1:
                        if st.button("✏️", key=f"edit_{model.id}", help="编辑模型", use_container_width=True):
                            handle_edit_model(model)
                    
                    with btn_col2:
                        # 删除按钮
                        delete_confirm = st.session_state.get(f"confirm_delete_{model.id}", False)
                        delete_key = f"delete_{model.id}"
                        if delete_confirm:
                            if st.button("🗑️", key=delete_key, help="确认删除", type="primary", use_container_width=True):
                                handle_delete_model(db, model.id, model.display_name)
                        else:
                            if st.button("🗑️", key=delete_key, help="删除模型", use_container_width=True):
                                handle_delete_model(db, model.id, model.display_name)
                    
                    with btn_col3:
                        # 状态切换按钮
                        status_key = f"status_{model.id}"
                        if model.status == 1:
                            if st.button("⏸️", key=status_key, help="禁用模型", use_container_width=True):
                                update_model_status(db, model.id, False)
                        else:
                            if st.button("▶️", key=status_key, help="启用模型", use_container_width=True):
                                update_model_status(db, model.id, True)
                    st.markdown('</div>', unsafe_allow_html=True)
        
        # 分页控件
        st.markdown("---")
        display_pagination_controls(total_pages)
        
    else:
        st.info("暂无模型数据")
        if st.button("添加新模型", key="add_new_empty"):
            st.session_state.model_page = "create"
            st.rerun()


def display_pagination_controls(total_pages: int):
    """显示分页控件"""
    if total_pages <= 1:
        return
    
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    with col1:
        # 第一页
        if st.button("⏮️ 第一页", key="first_page", use_container_width=True):
            if st.session_state.current_page > 1:
                st.session_state.current_page = 1
                st.rerun()
    
    with col2:
        # 上一页
        if st.button("◀️ 上一页", key="prev_page", use_container_width=True):
            if st.session_state.current_page > 1:
                st.session_state.current_page -= 1
                st.rerun()
    
    with col3:
        # 页码显示和跳转 - 居中显示
        st.markdown('<div class="center-content" style="flex-direction: column; gap: 8px;">', unsafe_allow_html=True)
        current_page = st.session_state.current_page
        page_input = st.number_input(
            "跳转到页码",
            min_value=1,
            max_value=total_pages,
            value=current_page,
            key="page_jump_input"
        )
        
        if page_input != current_page:
            st.session_state.current_page = page_input
            st.rerun()
        
        st.write(f"第 {current_page} 页 / 共 {total_pages} 页")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        # 下一页
        if st.button("下一页 ▶️", key="next_page", use_container_width=True):
            if st.session_state.current_page < total_pages:
                st.session_state.current_page += 1
                st.rerun()
    
    with col5:
        # 最后一页
        if st.button("最后一页 ⏭️", key="last_page", use_container_width=True):
            if st.session_state.current_page < total_pages:
                st.session_state.current_page = total_pages
                st.rerun()


def display_create_model_page(db: Session):
    """显示创建模型页面"""
    st.subheader("添加新模型")
    
    # 返回按钮
    if st.button("← 返回列表"):
        st.session_state.model_page = "list"
        st.session_state.current_page = 1  # 返回时重置到第一页
        st.rerun()
    
    with st.form("create_model_form"):
        display_name = st.text_input("模型展示名称 *")
        model_name = st.text_input("模型名称 *")
        base_url = st.text_input("调用地址")
        
        # 密钥字段 - 使用Streamlit密码框自带图标
        api_key = st.text_input("密钥", type="password")
        
        model_type = st.selectbox(
            "模型类型 *",
            options=[t.value for t in ModelType],
            format_func=lambda x: {
                "text": "文本模型",
                "image": "图像模型",
                "video": "视频模型",
                "audio": "音频模型"
            }.get(x, x)
        )
        
        # 特性支持选项
        st.subheader("特性支持")
        col1, col2 = st.columns(2)
        with col1:
            support_reference_image = st.checkbox("支持参考图")
            support_first_frame = st.checkbox("支持首帧")
        with col2:
            support_multiple_reference_images = st.checkbox("支持多张参考图")
            support_last_frame = st.checkbox("支持尾帧")
        
        status = st.checkbox("启用状态", value=True)
        operator = st.text_input("操作人 *")
        
        # 使用 st.form_submit_button() 创建提交按钮
        submitted = st.form_submit_button("添加模型")
        
        if submitted:
            # 验证必填字段
            if not display_name or not model_name or not operator:
                st.error("请填写所有必填字段（模型展示名称、模型名称、操作人）")
                return
            
            try:
                model_data = LLMModelCreate(
                    display_name=display_name,
                    model_name=model_name,
                    base_url=base_url if base_url else None,
                    api_key=api_key if api_key else None,
                    model_type=model_type,
                    support_reference_image=support_reference_image,
                    support_multiple_reference_images=support_multiple_reference_images,
                    support_first_frame=support_first_frame,
                    support_last_frame=support_last_frame,
                    status=1 if status else 0,
                    operator=operator
                )
                
                LLMModelService.create_model(db, model_data)
                st.success("模型创建成功！")
                time.sleep(1)
                st.session_state.model_page = "list"
                st.session_state.current_page = 1  # 创建成功后回到第一页
                st.rerun()
            except Exception as e:
                st.error(f"创建失败: {str(e)}")


def display_edit_model_page(db: Session, model):
    """显示编辑模型页面"""
    st.subheader(f"编辑模型: {model.display_name}")
    
    # 返回按钮
    if st.button("← 返回列表"):
        st.session_state.model_page = "list"
        st.session_state.selected_model = None
        st.rerun()
    
    # 编辑表单 - 保持与新增页面相同的样式
    with st.form("edit_model_form"):
        display_name = st.text_input("模型展示名称 *", value=model.display_name)
        model_name = st.text_input("模型名称 *", value=model.model_name)
        base_url = st.text_input("调用地址", value=model.base_url if model.base_url else "")
        
        # 密钥字段 - 与新增页面相同，使用密码输入框
        api_key = st.text_input(
            "密钥", 
            type="password",
            value="",  # 留空，不显示原密钥
            placeholder="输入新密钥或留空保持原密钥"
        )
        
        model_type = st.selectbox(
            "模型类型 *",
            options=[t.value for t in ModelType],
            index=[t.value for t in ModelType].index(model.model_type.value) if model.model_type else 0,
            format_func=lambda x: {
                "text": "文本模型",
                "image": "图像模型",
                "video": "视频模型",
                "audio": "音频模型"
            }.get(x, x)
        )
        
        # 特性支持选项
        st.subheader("特性支持")
        col1, col2 = st.columns(2)
        with col1:
            support_reference_image = st.checkbox(
                "支持参考图", 
                value=model.support_reference_image if model.support_reference_image else False
            )
            support_first_frame = st.checkbox(
                "支持首帧", 
                value=model.support_first_frame if model.support_first_frame else False
            )
        with col2:
            support_multiple_reference_images = st.checkbox(
                "支持多张参考图", 
                value=model.support_multiple_reference_images if model.support_multiple_reference_images else False
            )
            support_last_frame = st.checkbox(
                "支持尾帧", 
                value=model.support_last_frame if model.support_last_frame else False
            )
        
        status = st.checkbox("启用状态", value=model.status == 1)
        operator = st.text_input("操作人 *", value=model.operator if model.operator else "")
        
        # 使用 st.form_submit_button() 创建提交按钮
        submitted = st.form_submit_button("更新模型")
        
        if submitted:
            # 验证必填字段
            if not display_name or not model_name or not operator:
                st.error("请填写所有必填字段（模型展示名称、模型名称、操作人）")
                return
            
            try:
                # 构建更新数据
                update_data = {}
                
                if display_name != model.display_name:
                    update_data["display_name"] = display_name
                if model_name != model.model_name:
                    update_data["model_name"] = model_name
                if base_url != (model.base_url or ""):
                    update_data["base_url"] = base_url if base_url else None
                if api_key:  # 只有输入新密钥时才更新
                    update_data["api_key"] = api_key
                if model_type != model.model_type.value:
                    update_data["model_type"] = model_type
                if support_reference_image != model.support_reference_image:
                    update_data["support_reference_image"] = support_reference_image
                if support_multiple_reference_images != model.support_multiple_reference_images:
                    update_data["support_multiple_reference_images"] = support_multiple_reference_images
                if support_first_frame != model.support_first_frame:
                    update_data["support_first_frame"] = support_first_frame
                if support_last_frame != model.support_last_frame:
                    update_data["support_last_frame"] = support_last_frame
                if (1 if status else 0) != model.status:
                    update_data["status"] = 1 if status else 0
                if operator != (model.operator or ""):
                    update_data["operator"] = operator
                
                # 确保operator字段始终存在，因为它是必需字段
                if "operator" not in update_data:
                    update_data["operator"] = operator if operator else (model.operator or "")
                
                if not update_data:
                    st.warning("没有检测到任何更改")
                    return
                    
                model_data = LLMModelUpdate(**update_data)
                LLMModelService.update_model(db, model.id, model_data)
                st.success("模型更新成功！")
                time.sleep(1)
                st.session_state.model_page = "list"
                st.session_state.selected_model = None
                st.rerun()
            except Exception as e:
                st.error(f"更新失败: {str(e)}")