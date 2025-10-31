import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.llm_model import LLMModel, ModelType
from app.models.llm_schema import LLMModelCreate, LLMModelUpdate, LLMModelQuery
from app.services.llm_model_service import LLMModelService
import time


def model_management_page():
    """模型管理页面"""
    st.title("模型管理")
    
    # 初始化session state
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = None
    if "refresh_trigger" not in st.session_state:
        st.session_state.refresh_trigger = 0
    if "search_name" not in st.session_state:
        st.session_state.search_name = ""
    if "model_type_filter" not in st.session_state:
        st.session_state.model_type_filter = ""
    
    # 创建数据库会话
    db_gen = get_db()
    db: Session = next(db_gen)
    
    try:
        # 页面布局：左侧列表，右侧详情/编辑表单
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("模型列表")
            
            # 搜索和筛选
            search_name = st.text_input("搜索模型名称", value=st.session_state.search_name)
            model_type_filter = st.selectbox(
                "模型类型筛选",
                options=[("", "全部")] + [(t.value, t.value) for t in ModelType],
                format_func=lambda x: "全部" if x[0] == "" else x[1],
                index=[("", "全部")] + [(t.value, t.value) for t in ModelType].index((st.session_state.model_type_filter, st.session_state.model_type_filter)) if st.session_state.model_type_filter else 0
            )
            
            # 查询按钮
            if st.button("查询"):
                st.session_state.search_name = search_name
                st.session_state.model_type_filter = model_type_filter[0]
                st.session_state.refresh_trigger += 1
                st.rerun()
            
            # 刷新按钮
            if st.button("刷新列表"):
                st.session_state.refresh_trigger += 1
                st.rerun()
            
            # 查询模型列表
            query = LLMModelQuery(
                display_name=st.session_state.search_name if st.session_state.search_name else None,
                model_type=st.session_state.model_type_filter if st.session_state.model_type_filter else None,
                page=1,
                page_size=100  # 显示所有模型
            )
            
            models, total = LLMModelService.list_models(db, query)
            
            # 显示模型列表为表格
            if models:
                # 准备表格数据
                table_data = []
                for model in models:
                    table_data.append({
                        "ID": model.id,
                        "展示名称": model.display_name,
                        "模型名称": model.model_name,
                        "模型类型": model.model_type.value,
                        "状态": "启用" if model.status == 1 else "禁用",
                        "创建时间": model.created_at.strftime('%Y-%m-%d %H:%M:%S') if model.created_at else ""
                    })
                
                # 显示表格
                df = pd.DataFrame(table_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # 显示操作按钮
                st.subheader("操作")
                selected_model_id = st.selectbox("选择模型", options=[m.id for m in models], format_func=lambda x: next((m.display_name for m in models if m.id == x), ""))
                
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                with col_btn1:
                    if st.button("编辑选中模型", key="edit_selected"):
                        selected_model = next((m for m in models if m.id == selected_model_id), None)
                        if selected_model:
                            st.session_state.selected_model = selected_model
                            st.rerun()
                
                with col_btn2:
                    if st.button("删除选中模型", key="delete_selected"):
                        try:
                            selected_model = next((m for m in models if m.id == selected_model_id), None)
                            if selected_model:
                                LLMModelService.delete_model(db, selected_model.id)
                                st.success(f"模型 {selected_model.display_name} 删除成功")
                                time.sleep(1)
                                st.rerun()
                        except Exception as e:
                            st.error(f"删除失败: {str(e)}")
                
                with col_btn3:
                    if st.button("添加新模型", key="add_new"):
                        st.session_state.selected_model = "new"
                        st.rerun()
            else:
                st.info("暂无模型数据")
                if st.button("添加新模型", key="add_new_empty"):
                    st.session_state.selected_model = "new"
                    st.rerun()
        
        with col2:
            # 右侧显示详情或编辑表单
            if st.session_state.selected_model == "new":
                create_model_form(db)
            elif st.session_state.selected_model:
                edit_model_form(db, st.session_state.selected_model)
            else:
                st.info("请选择操作")
                
    finally:
        # 关闭数据库会话
        try:
            next(db_gen, None)  # This will trigger the finally block in get_db
        except StopIteration:
            pass


def create_model_form(db: Session):
    """创建模型表单"""
    st.subheader("添加新模型")
    
    # 返回按钮
    if st.button("← 返回列表"):
        st.session_state.selected_model = None
        st.rerun()
    
    with st.form("create_model_form"):
        display_name = st.text_input("模型展示名称 *")
        model_name = st.text_input("模型名称 *")
        base_url = st.text_input("调用地址")
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
        
        status = st.radio("状态", options=[(1, "启用"), (0, "禁用")], format_func=lambda x: x[1])
        operator = st.text_input("操作人 *")
        
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
                    status=status[0],
                    operator=operator
                )
                
                LLMModelService.create_model(db, model_data)
                st.success("模型创建成功！")
                time.sleep(1)
                st.session_state.selected_model = None
                st.rerun()
            except Exception as e:
                st.error(f"创建失败: {str(e)}")


def edit_model_form(db: Session, model):
    """编辑模型表单"""
    st.subheader(f"编辑模型: {model.display_name}")
    
    # 返回按钮
    if st.button("← 返回列表"):
        st.session_state.selected_model = None
        st.rerun()
    
    with st.form("edit_model_form"):
        display_name = st.text_input("模型展示名称 *", value=model.display_name)
        model_name = st.text_input("模型名称 *", value=model.model_name)
        base_url = st.text_input("调用地址", value=model.base_url if model.base_url else "")
        api_key = st.text_input("密钥", type="password", value=model.api_key if model.api_key else "")
        
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
        
        status = st.radio(
            "状态", 
            options=[(1, "启用"), (0, "禁用")], 
            index=0 if model.status == 1 else 1,
            format_func=lambda x: x[1]
        )
        operator = st.text_input("操作人 *", value=model.operator if model.operator else "")
        
        submitted = st.form_submit_button("更新模型")
        
        if submitted:
            # 验证必填字段
            if not display_name or not model_name or not operator:
                st.error("请填写所有必填字段（模型展示名称、模型名称、操作人）")
                return
            
            try:
                model_data = LLMModelUpdate(
                    display_name=display_name if display_name != model.display_name else None,
                    model_name=model_name if model_name != model.model_name else None,
                    base_url=base_url if base_url != (model.base_url or "") else None,
                    api_key=api_key if api_key != (model.api_key or "") else None,
                    model_type=model_type if model_type != model.model_type.value else None,
                    support_reference_image=support_reference_image if support_reference_image != model.support_reference_image else None,
                    support_multiple_reference_images=support_multiple_reference_images if support_multiple_reference_images != model.support_multiple_reference_images else None,
                    support_first_frame=support_first_frame if support_first_frame != model.support_first_frame else None,
                    support_last_frame=support_last_frame if support_last_frame != model.support_last_frame else None,
                    status=status[0] if status[0] != model.status else None,
                    operator=operator
                )
                
                # 移除None值
                update_data = {k: v for k, v in model_data.model_dump().items() if v is not None}
                if not update_data:
                    st.warning("没有检测到任何更改")
                    return
                    
                model_data = LLMModelUpdate(**update_data)
                LLMModelService.update_model(db, model.id, model_data)
                st.success("模型更新成功！")
                time.sleep(1)
                st.session_state.selected_model = None
                st.rerun()
            except Exception as e:
                st.error(f"更新失败: {str(e)}")