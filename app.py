import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# بيانات الاتصال بمشروع أبو حوراء
url = "https://lsmevvsogsqqqjyuqzbx.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxzbWV2dnNvZ3NxcXFqeXVxemJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc0MDMyOTgsImV4cCI6MjA5Mjk3OTI5OH0.ecqJS75fPbKqwSAiBzP6Qonn4cuymgwjB96tIGek8j0"
supabase = create_client(url, key)

st.set_page_config(page_title="نظام الغياب - أ. عارف الحداد", layout="wide")

st.sidebar.title("القائمة الرئيسية")
page = st.sidebar.radio("اختر النافذة:", ["نافذة الغياب", "نافذة الإدارة"])

if page == "نافذة الغياب":
    st.header("📋 تسجيل غياب الطلاب")
    teacher_id = st.text_input("أدخل رقم الهوية للمعلم", type="password")
    
    if teacher_id:
        t_query = supabase.table('teachers').select("*").eq('national_id', teacher_id).execute()
        if t_query.data:
            teacher_name = t_query.data[0]['name_tech']
            st.success(f"مرحباً أستاذ: {teacher_name}")
            target_date = st.date_input("تاريخ اليوم", datetime.now())
            s_data = supabase.table('students').select("committee").execute()
            committees = sorted(list(set([item['committee'] for item in s_data.data])))
            selected_committee = st.selectbox("اختر اللجنة", committees)
            
            st.divider()
            students_query = supabase.table('students').select("*").eq('committee', selected_committee).execute()
            
            if students_query.data:
                attendance_list = []
                for student in students_query.data:
                    col_name, col_status = st.columns([2, 2])
                    with col_name: st.write(student['student_name'])
                    with col_status:
                        status = st.radio(f"الحالة لـ {student['student_name']}", ["حاضر", "غائب", "متأخر"], key=student['id'], horizontal=True)
                    attendance_list.append({"student_name": student['student_name'], "committee": selected_committee, "section": student['section'], "status": status, "date": str(target_date), "teacher_name": teacher_name})
                
                if st.button("إرسال الغياب المؤكد"):
                    supabase.table('attendance').insert(attendance_list).execute()
                    st.balloons()
                    st.success("تم الإرسال بنجاح.. شكراً لك")
                    st.info("حقوق التصميم: أ. عارف أحمد الحداد")
        else:
            st.error("رقم الهوية غير صحيح.")

elif page == "نافذة الإدارة":
    st.header("⚙️ لوحة التحكم")
    admin_pass = st.sidebar.text_input("كلمة مرور الإدارة", type="password")
    if admin_pass == "1234":
        tab1, tab2 = st.tabs(["📊 التقارير", "🔐 الصلاحيات"])
        with tab1:
            report_date = st.date_input("اختر التاريخ", datetime.now())
            att_data = supabase.table('attendance').select("*").eq('date', str(report_date)).execute()
            if att_data.data:
                df = pd.DataFrame(att_data.data)
                st.dataframe(df[['student_name', 'section', 'committee', 'status', 'teacher_name']])
        with tab2:
            st.write("إدارة المعلمين والطلاب")
    else:
        st.info("أدخل كلمة المرور في الجانب")
