import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# بيانات الاتصال بمشروع أبو حوراء
url = "https://lsmevvsogsqqqjyuqzbx.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxzbWV2dnNvZ3NxcXFqeXVxemJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc0MDMyOTgsImV4cCI6MjA5Mjk3OTI5OH0.ecqJS75fPbKqwSAiBzP6Qonn4cuymgwjB96tIGek8j0"

# إنشاء الاتصال مرة واحدة فقط لتحسين الأداء
if 'supabase' not in st.session_state:
    st.session_state.supabase = create_client(url, key)

supabase = st.session_state.supabase

st.set_page_config(page_title="نظام الغياب - أ. عارف الحداد", layout="wide")

# القائمة الجانبية
st.sidebar.markdown("### 🏫 نظام إدارة الغياب")
page = st.sidebar.radio("انتقل إلى:", ["📋 نافذة التحضير", "⚙️ لوحة الإدارة"])

# --- 1. نافذة التحضير (للمعلمين) ---
if page == "📋 نافذة التحضير":
    st.header("📋 تسجيل غياب الطلاب")
    
    with st.expander("🔐 تسجيل دخول المعلم", expanded=True):
        teacher_id = st.text_input("أدخل رقم الهوية (السجل المدني)", type="password")
        btn_login = st.button("دخول")

    if teacher_id or btn_login:
        # البحث عن المعلم في قاعدة البيانات
        t_query = supabase.table('teachers').select("*").eq('national_id', teacher_id.strip()).execute()
        
        if t_query.data:
            teacher_name = t_query.data[0]['name_tech']
            st.success(f"مرحباً بك أستاذ: **{teacher_name}**")
            
            st.divider()
            
            # اختيار التاريخ واللجنة
            col1, col2 = st.columns(2)
            with col1:
                target_date = st.date_input("📅 تاريخ اليوم", datetime.now())
            with col2:
                # جلب اللجان المتوفرة من جدول الطلاب
                s_data = supabase.table('students').select("committee").execute()
                all_committees = sorted(list(set([item['committee'] for item in s_data.data if item['committee']])))
                selected_committee = st.selectbox("🎯 اختر اللجنة", all_committees)
            
            if selected_committee:
                # جلب طلاب اللجنة المختارة
                students_query = supabase.table('students').select("*").eq('committee', selected_committee).execute()
                
                if students_query.data:
                    st.info(f"عدد الطلاب في هذه اللجنة: {len(students_query.data)}")
                    
                    attendance_list = []
                    # عرض الطلاب في شكل قائمة مرتبة
                    for student in students_query.data:
                        col_name, col_status = st.columns([2, 2])
                        with col_name:
                            st.write(f"👤 **{student['student_name']}**")
                        with col_status:
                            status = st.radio(
                                f"الحالة لـ {student['student_name']}", 
                                ["حاضر", "غائب", "متأخر"], 
                                key=f"id_{student['id']}", 
                                horizontal=True
                            )
                        
                        attendance_list.append({
                            "student_name": student['student_name'],
                            "committee": selected_committee,
                            "section": student.get('section', 'غير محدد'),
                            "status": status,
                            "date": str(target_date),
                            "teacher_name": teacher_name
                        })
                    
                    st.divider()
                    if st.button("💾 إرسال الغياب المؤكد إلى النظام"):
                        with st.spinner('جاري الحفظ...'):
                            supabase.table('attendance').insert(attendance_list).execute()
                            st.balloons()
                            st.success(f"تم تسجيل غياب لـ {len(attendance_list)} طالب بنجاح.")
                            st.caption("حقوق التصميم والبرمجة: أ. عارف أحمد الحداد")
                else:
                    st.warning("لا يوجد طلاب مسجلين في هذه اللجنة.")
        else:
            if teacher_id:
                st.error("⚠️ رقم الهوية غير مسجل! يرجى التأكد من الرقم أو مراجعة الإدارة.")

# --- 2. نافذة الإدارة (للإداري فقط) ---
elif page == "⚙️ لوحة الإدارة":
    st.header("⚙️ لوحة تحكم النظام")
    admin_pass = st.sidebar.text_input("🔑 كلمة مرور الإدارة", type="password")
    
    if admin_pass == "1234":
        tab1, tab2 = st.tabs(["📊 تقارير الغياب", "👥 إدارة البيانات"])
        
        with tab1:
            st.subheader("استخراج التقارير")
            report_date = st.date_input("اختر التاريخ المطلوب", datetime.now(), key="report_date")
            
            att_data = supabase.table('attendance').select("*").eq('date', str(report_date)).execute()
            
            if att_data.data:
                df = pd.DataFrame(att_data.data)
                st.write(f"### تقرير يوم: {report_date}")
                # عرض الأعمدة المهمة فقط
                st.dataframe(df[['student_name', 'committee', 'status', 'teacher_name']], use_container_width=True)
                
                # خيار تحميل التقرير
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 تحميل التقرير (Excel/CSV)", csv, f"attendance_{report_date}.csv", "text/csv")
            else:
                st.warning("لا توجد بيانات غياب مسجلة لهذا التاريخ حتى الآن.")
        
        with tab2:
            st.subheader("إحصائيات سريعة")
            st.write("يمكنك متابعة حالة الجداول من هنا قريباً.")
            if st.button("تحديث البيانات"):
                st.rerun()
    else:
        st.info("يرجى إدخال كلمة مرور الإدارة في القائمة الجانبية للوصول للتقارير.")
