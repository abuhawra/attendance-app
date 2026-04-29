import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# بيانات الاتصال بمشروعك (AbuHawra)
url = "https://lsmevvsogsqqqjyuqzbx.supabase.co"
# هذا هو المفتاح العام (anon key) كما يظهر في صورك
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxzbWV2dnNvZ3NxcXFqeXVxemJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc0MDMyOTgsImV4cCI6MjA5Mjk3OTI5OH0.ecqJS75fPbKqwSAiBzP6Qonn4cuymgwjB96tIGek8j0"

# إنشاء الاتصال
if 'supabase' not in st.session_state:
    st.session_state.supabase = create_client(url, key)
supabase = st.session_state.supabase

st.set_page_config(page_title="نظام الغياب - أ. عارف الحداد", layout="wide")

# القائمة الجانبية
st.sidebar.title("🏫 القائمة الرئيسية")
page = st.sidebar.radio("اختر المهمة:", ["🔑 دخول المعلم", "⚙️ لوحة الإدارة"])

# --- نافذة تسجيل دخول المعلم ---
if page == "🔑 دخول المعلم":
    st.header("🔑 دخول المعلم")
    
    # تحسين: استخدام nid.strip() لإزالة أي مسافات زائدة قد يكتبها المعلم بالخطأ
    nid_input = st.text_input("أدخل رقم السجل المدني:", key="nid_field")
    
    if st.button("دخول"):
        if nid_input:
            with st.spinner('جاري التحقق من الهوية...'):
                try:
                    # تعديل جوهري: البحث باستخدام national_id بدلاً من teacher_id
                    res = supabase.table("teachers").select("*").eq("national_id", nid_input.strip()).execute()
                    
                    if res.data:
                        teacher_name = res.data[0]['name_tech']
                        st.success(f"مرحباً بك أستاذ: **{teacher_name}**")
                        
                        st.divider()
                        # --- هنا تبدأ واجهة التحضير ---
                        target_date = st.date_input("📅 تاريخ اليوم", datetime.now())
                        
                        # جلب اللجان
                        s_data = supabase.table('students').select("committee").execute()
                        committees = sorted(list(set([item['committee'] for item in s_data.data if item['committee']])))
                        selected_committee = st.selectbox("🎯 اختر اللجنة", committees)
                        
                        if selected_committee:
                            st.write(f"### طلاب لجنة: {selected_committee}")
                            students_query = supabase.table('students').select("*").eq('committee', selected_committee).execute()
                            
                            if students_query.data:
                                attendance_list = []
                                for student in students_query.data:
                                    col1, col2 = st.columns([2, 2])
                                    with col1: st.write(f"👤 {student['student_name']}")
                                    with col2:
                                        status = st.radio(f"حالة {student['student_name']}", ["حاضر", "غائب", "متأخر"], key=f"std_{student['id']}", horizontal=True)
                                    
                                    attendance_list.append({
                                        "student_name": student['student_name'],
                                        "committee": selected_committee,
                                        "status": status,
                                        "date": str(target_date),
                                        "teacher_name": teacher_name
                                    })
                                
                                if st.button("💾 حفظ الغياب"):
                                    supabase.table('attendance').insert(attendance_list).execute()
                                    st.balloons()
                                    st.success("تم الحفظ بنجاح")
                            else:
                                st.warning("لا يوجد طلاب في هذه اللجنة.")
                    else:
                        st.error("⚠️ رقم السجل المدني غير مسجل في النظام.")
                except Exception as e:
                    st.error(f"حدث خطأ في الاتصال بقاعدة البيانات: {e}")
        else:
            st.warning("يرجى إدخال رقم السجل أولاً.")

# --- نافذة الإدارة ---
elif page == "⚙️ لوحة الإدارة":
    st.header("⚙️ لوحة الإدارة")
    admin_pass = st.sidebar.text_input("كلمة مرور الإدارة", type="password")
    if admin_pass == "1234":
        st.info("مرحباً بك في لوحة الإدارة. يمكنك هنا سحب التقارير.")
        # إضافة كود التقارير هنا...
    else:
        st.write("الرجاء إدخال كلمة المرور في القائمة الجانبية.")
