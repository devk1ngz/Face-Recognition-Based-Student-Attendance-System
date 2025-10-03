import gradio as gr
from auth.auth import login, get_session
from pipelines.attendance import attendance

def login_ui(username, password):
    ok, user = login(username, password)
    if ok:
        return f"Đăng nhập thành công! Xin chào {user['username']}"
    else:
        return "Sai tài khoản hoặc mật khẩu!"

def attendance_ui(class_id):
    from face.embedder import get_embedding  # load model ArcFace trước
    model_arcface = None  # TODO: load thật
    return attendance(class_id, model_arcface)

def create_interface():
    with gr.Blocks() as demo:
        gr.Markdown("# Hệ thống điểm danh bằng khuôn mặt")
        with gr.Tab("Đăng nhập"):
            username = gr.Textbox(label="Tên đăng nhập")
            password = gr.Textbox(label="Mật khẩu", type="password")
            out = gr.Textbox(label="Kết quả")
            btn = gr.Button("Đăng nhập")
            btn.click(fn=login_ui, inputs=[username, password], outputs=out)

        with gr.Tab("Điểm danh"):
            class_id = gr.Textbox(label="Mã lớp học")
            result = gr.Textbox(label="Kết quả điểm danh")
            btn2 = gr.Button("Điểm danh")
            btn2.click(fn=attendance_ui, inputs=[class_id], outputs=result)

    return demo
