import tkinter as tk
from tkinter import ttk, messagebox
from core.master_agent import MasterAgent
from core.voice_control import VoiceControl
import threading
import queue
import time


class VisionAIDUI:
    def __init__(self, master):
        self.master = master
        self.controller = MasterAgent()
        self.voice_control = VoiceControl()
        self.voice_queue = queue.Queue()
        self.voice_active = False
        self.setup_ui()
        self.setup_voice_thread()

    def setup_ui(self):
        self.master.title("VisionAID Controller")
        self.master.geometry("400x300")
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

        self.status_frame = ttk.LabelFrame(self.master, text="System Status")
        self.status_frame.pack(pady=10, padx=10, fill="x")

        self.status_label = ttk.Label(self.status_frame, text="Ready", foreground="green")
        self.status_label.pack()

        self.control_frame = ttk.LabelFrame(self.master, text="Agent Control")
        self.control_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.voice_feedback = ttk.Label(self.master, text="Last command: None", wraplength=350)
        self.voice_feedback.pack(pady=5)

        self.create_agent_buttons()

        ttk.Button(
            self.master,
            text="🎤 Toggle Voice Control",
            command=self.toggle_voice_control
        ).pack(pady=5)

    def create_agent_buttons(self):
        agent_config = {
            'object_detection': {'display_name': 'Object Detection'},
            'barcode_scanner': {'display_name': 'Barcode Reader'},
            'document_reader': {'display_name': 'Document OCR'}
        }

        for agent_name, config in agent_config.items():
            btn = ttk.Button(
                self.control_frame,
                text=config['display_name'],
                command=lambda n=agent_name: self.start_agent(n),
                width=20
            )
            btn.pack(pady=5)

        ttk.Button(
            self.control_frame,
            text="Exit System",
            command=self.on_close,
            style='danger.TButton'
        ).pack(pady=10)

    def setup_voice_thread(self):
        self.voice_thread = threading.Thread(target=self.voice_control_loop, daemon=True)
        self.voice_thread.start()

    def voice_control_loop(self):
        while True:
            # Pause voice listening if agent is busy
            if self.voice_active and not self.controller.agent_busy:
                try:
                    command = self.voice_control.listen()
                    if command:
                        self.voice_queue.put(command)
                        self.master.after(0, self.process_voice_command)
                except Exception as e:
                    self.voice_queue.put(f"voice_error:{str(e)}")
                    self.master.after(0, self.process_voice_command)
            time.sleep(0.5)

    def process_voice_command(self):
        try:
            command = self.voice_queue.get_nowait()
            if command.startswith("voice_error:"):
                error = command.split(":", 1)[1]
                self.status_label.config(text=f"Voice Error: {error}", foreground="red")
            else:
                self.voice_feedback.config(text=f"Last command: {command.replace('_', ' ')}")
                if command == "exit":
                    self.on_close()
                else:
                    # Only start agent if not busy
                    if not self.controller.agent_busy:
                        self.start_agent(command)
        except queue.Empty:
            pass

    def start_agent(self, agent_name):
        def run_agent():
            try:
                self.status_label.config(text=f"Starting {agent_name.replace('_', ' ')}...", foreground="blue")
                self.master.update()

                # Indicate busy
                self.controller.agent_busy = True

                self.controller.switch_agent(agent_name)

                self.status_label.config(
                    text=f"Active: {agent_name.replace('_', ' ')}",
                    foreground="green"
                )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start agent: {str(e)}")
                self.status_label.config(text="Ready", foreground="green")
            finally:
                # Reset busy when done
                self.controller.agent_busy = False

        # Run agent in a thread so UI stays responsive
        threading.Thread(target=run_agent, daemon=True).start()

    def toggle_voice_control(self):
        self.voice_active = not self.voice_active
        status = "ON" if self.voice_active else "OFF"
        self.voice_feedback.config(text=f"Voice control: {status}")

    def on_close(self):
        if messagebox.askokcancel("Quit", "Shut down all agents and exit?"):
            self.controller.cleanup()
            self.master.quit()


if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.configure('danger.TButton', foreground='red')
    app = VisionAIDUI(root)
    root.mainloop()
