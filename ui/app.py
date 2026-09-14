import os
import threading
import logging
import customtkinter as ctk
from tkinter import filedialog
from core.analyzer import AudioAnalyzerEngine
from core.i18n import TRANSLATIONS

class BPMAnalyzerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.idioma_actual = "Español (Latinoamérica)"
        
        self.title(self.t("title"))
        self.geometry("980x720")
        self.minsize(860, 580)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.historial_datos = []
        self.audio_actual = None
        self.current_offset_val = 0

        self._build_sidebar()
        self._build_main_content()
        self.cambiar_pestana("bpm")

    def t(self, key):
        """Devuelve el texto traducido según el idioma actual"""
        return TRANSLATIONS.get(self.idioma_actual, TRANSLATIONS["Español (Latinoamérica)"]).get(key, key)

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=290, corner_radius=0, fg_color="#0F172A")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(2, weight=1)
        self.sidebar.grid_columnconfigure(0, weight=1)

        self.lbl_historial = ctk.CTkLabel(self.sidebar, text=self.t("historial"), font=ctk.CTkFont(size=15, weight="bold"), text_color="#F8FAFC")
        self.lbl_historial.grid(row=0, column=0, padx=12, pady=(15, 8), sticky="w")
        
        self.scroll_historial = ctk.CTkScrollableFrame(self.sidebar, corner_radius=8, fg_color="#1E293B")
        self.scroll_historial.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")

    def _build_main_content(self):
        self.main = ctk.CTkFrame(self, corner_radius=0, fg_color="#1E293B")
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_rowconfigure(1, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        self.tab_bar = ctk.CTkFrame(self.main, height=50, corner_radius=0, fg_color="#0F172A")
        self.tab_bar.grid(row=0, column=0, sticky="ew")

        self.btn_bpm = ctk.CTkButton(self.tab_bar, text=self.t("btn_bpm"), command=lambda: self.cambiar_pestana("bpm"), width=130)
        self.btn_bpm.pack(side="left", padx=10, pady=8)
        
        self.btn_offset = ctk.CTkButton(self.tab_bar, text=self.t("btn_offset"), command=lambda: self.cambiar_pestana("offset"), width=130)
        self.btn_offset.pack(side="left", padx=4, pady=8)

        self.btn_settings = ctk.CTkButton(self.tab_bar, text=self.t("btn_settings"), command=lambda: self.cambiar_pestana("settings"), width=110, fg_color="#475569")
        self.btn_settings.pack(side="left", padx=4, pady=8)

        self.body = ctk.CTkScrollableFrame(self.main, fg_color="transparent")
        self.body.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)

        self.frame_bpm = ctk.CTkFrame(self.body, fg_color="transparent")
        self.frame_offset = ctk.CTkFrame(self.body, fg_color="transparent")
        self.frame_settings = ctk.CTkFrame(self.body, fg_color="transparent")

        self._build_bpm_tab()
        self._build_offset_tab()
        self._build_settings_tab()

    def _build_bpm_tab(self):
        self.drop = ctk.CTkFrame(self.frame_bpm, border_width=2, border_color="#3B82F6", corner_radius=10, fg_color="#0F172A")
        self.drop.pack(fill="x", padx=5, pady=5)
        
        self.lbl_drop_title = ctk.CTkLabel(self.drop, text=self.t("drop_title"), font=ctk.CTkFont(size=15, weight="bold"), text_color="white")
        self.lbl_drop_title.pack(pady=(15, 4))
        
        btn_frame = ctk.CTkFrame(self.drop, fg_color="transparent")
        btn_frame.pack(pady=(0, 15))
        
        self.btn_fast_analysis = ctk.CTkButton(btn_frame, text=self.t("btn_fast"), command=lambda: self.cargar_audios(rapido=True), fg_color="#475569")
        self.btn_fast_analysis.pack(side="left", padx=5)
        
        self.btn_full_analysis = ctk.CTkButton(btn_frame, text=self.t("btn_full"), command=lambda: self.cargar_audios(rapido=False), fg_color="#2563EB")
        self.btn_full_analysis.pack(side="left", padx=5)

        self.status_label = ctk.CTkLabel(self.frame_bpm, text=self.t("waiting"), text_color="#94A3B8")
        self.status_label.pack(pady=8)

        self.bpm_val_label = ctk.CTkLabel(self.frame_bpm, text="BPM: --", font=ctk.CTkFont(size=24, weight="bold"), text_color="#F8FAFC")
        self.bpm_val_label.pack(pady=15)

        self.badge_bpm = ctk.CTkFrame(self.frame_bpm, corner_radius=8, fg_color="#334155")
        self.badge_bpm.pack(fill="x", padx=5, pady=5, ipady=6)
        
        self.badge_bpm_text = ctk.CTkLabel(self.badge_bpm, text=self.t("no_data"), font=ctk.CTkFont(size=15, weight="bold"), text_color="white")
        self.badge_bpm_text.pack(pady=(4, 0))
        
        self.info_bpm_text = ctk.CTkLabel(self.badge_bpm, text=self.t("no_data_info"), text_color="#CBD5E1", wraplength=600)
        self.info_bpm_text.pack(pady=(2, 6))

        self.changes_scroll = ctk.CTkScrollableFrame(self.frame_bpm, fg_color="#0F172A", height=130, corner_radius=6)
        self.changes_scroll.pack(fill="x", padx=5, pady=15)

    def _build_offset_tab(self):
        self.offset_val_label = ctk.CTkLabel(self.frame_offset, text="Offset: -- ms", font=ctk.CTkFont(size=24, weight="bold"), text_color="#F8FAFC")
        self.offset_val_label.pack(pady=20)
        
        btn_box = ctk.CTkFrame(self.frame_offset, fg_color="transparent")
        btn_box.pack(pady=10)
        for d in [-10, -1, 1, 10]:
            ctk.CTkButton(btn_box, text=f"{'+' if d>0 else ''}{d} ms", width=70, command=lambda val=d: self.modificar_offset(val)).pack(side="left", padx=4)

        self.lbl_offset_changes = ctk.CTkLabel(self.frame_offset, text=self.t("offset_changes_title"), font=ctk.CTkFont(size=16, weight="bold"), text_color="white")
        self.lbl_offset_changes.pack(pady=(25, 10))
        
        self.offset_changes_scroll = ctk.CTkScrollableFrame(self.frame_offset, fg_color="#0F172A", height=250, corner_radius=6)
        self.offset_changes_scroll.pack(fill="both", expand=True, padx=10, pady=5)

    def _build_settings_tab(self):
        ctk.CTkLabel(self.frame_settings, text="⚙️ " + self.t("settings_title"), font=ctk.CTkFont(size=20, weight="bold"), text_color="#F8FAFC").pack(pady=(20, 15))
        
        card = ctk.CTkFrame(self.frame_settings, fg_color="#0F172A", corner_radius=10)
        card.pack(fill="x", padx=10, pady=10, ipady=15)

        self.lbl_select_lang = ctk.CTkLabel(card, text=self.t("select_lang"), font=ctk.CTkFont(size=14, weight="bold"), text_color="#CBD5E1")
        self.lbl_select_lang.pack(pady=(15, 5))

        idiomas_disponibles = list(TRANSLATIONS.keys())
        self.lang_menu = ctk.CTkOptionMenu(card, values=idiomas_disponibles, command=self.cambiar_idioma, width=240)
        self.lang_menu.set(self.idioma_actual)
        self.lang_menu.pack(pady=10)

    def cambiar_idioma(self, nuevo_idioma):
        self.idioma_actual = nuevo_idioma
        self.title(self.t("title"))
        
        # Actualizamos textos fijos de la interfaz en tiempo real
        self.lbl_historial.configure(text=self.t("historial"))
        self.btn_bpm.configure(text=self.t("btn_bpm"))
        self.btn_offset.configure(text=self.t("btn_offset"))
        self.btn_settings.configure(text=self.t("btn_settings"))
        self.lbl_drop_title.configure(text=self.t("drop_title"))
        self.btn_fast_analysis.configure(text=self.t("btn_fast"))
        self.btn_full_analysis.configure(text=self.t("btn_full"))
        self.lbl_offset_changes.configure(text=self.t("offset_changes_title"))
        self.lbl_select_lang.configure(text=self.t("select_lang"))

        if not self.audio_actual:
            self.badge_bpm_text.configure(text=self.t("no_data"))
            self.info_bpm_text.configure(text=self.t("no_data_info"))
            self.status_label.configure(text=self.t("waiting"))
        else:
            self.actualizar_lista_offsets()

    def modificar_offset(self, delta):
        if not self.audio_actual or self.audio_actual['offset'] == "--":
            return
            
        self.current_offset_val = max(0, self.current_offset_val + delta)
        self.actualizar_lista_offsets()

    def actualizar_lista_offsets(self):
        self.offset_val_label.configure(text=f"Offset: {self.current_offset_val} ms")
        
        for w in self.offset_changes_scroll.winfo_children(): w.destroy()
        
        secciones = self.audio_actual.get("secciones", [])
        if not secciones:
            ctk.CTkLabel(self.offset_changes_scroll, text=self.t("no_sections"), text_color="#94A3B8").pack(pady=10)
            return

        base_offset_original = self.audio_actual['offset']
        shift_manual = self.current_offset_val - base_offset_original

        for i, (s, e, b) in enumerate(secciones):
            if i == 0:
                ms_final = self.current_offset_val
            else:
                ms_final = max(0, int(s * 1000) + shift_manual)

            f = ctk.CTkFrame(self.offset_changes_scroll, fg_color="#1E293B")
            f.pack(fill="x", pady=4, padx=2)
            
            texto = f"{self.t('timing_point')} {i+1}   ➔   Offset: {ms_final} ms   |   BPM: {b}"
            ctk.CTkLabel(f, text=texto, text_color="#FCA5A5", font=ctk.CTkFont(weight="bold")).pack(padx=15, pady=8, anchor="w")

    def cambiar_pestana(self, tab):
        self.frame_bpm.pack_forget()
        self.frame_offset.pack_forget()
        self.frame_settings.pack_forget()
        
        if tab == "bpm":
            self.frame_bpm.pack(fill="both", expand=True)
        elif tab == "offset":
            self.frame_offset.pack(fill="both", expand=True)
        elif tab == "settings":
            self.frame_settings.pack(fill="both", expand=True)

    def cargar_audios(self, rapido):
        rutas = filedialog.askopenfilenames(filetypes=[("Audios", "*.mp3 *.ogg *.wav")])
        if rutas:
            threading.Thread(target=self.procesar_lote, args=(list(rutas)[:50], rapido), daemon=True).start()

    def procesar_lote(self, rutas, rapido):
        for idx, ruta in enumerate(rutas, 1):
            nombre = os.path.basename(ruta)
            texto_estado = f"Analizando ({idx}/{len(rutas)}): {nombre}..."
            self.after(0, lambda t=texto_estado: self.status_label.configure(text=t))
            
            res = AudioAnalyzerEngine.analizar_audio(ruta, analisis_rapido=rapido)
            
            if "error" in res:
                logging.error(f"Error procesando {nombre}: {res['error']}")
                item = {
                    "nombre": nombre,
                    "ruta": ruta,
                    "bpm": "ERROR",
                    "offset": "--",
                    "status": "FALLO",
                    "bg": "#DC2626",
                    "msg_bpm": f"Error técnico: {res['error']}",
                    "msg_offset": "Error",
                    "secciones": []
                }
            else:
                item = {"nombre": nombre, "ruta": ruta, **res}
                
            self.historial_datos.append(item)
            self.after(0, self.refrescar_sidebar)
            
            if idx == len(rutas):
                self.after(0, self.seleccionar_cancion, item)

        self.after(0, lambda: self.status_label.configure(text=self.t("analysis_finished"), text_color="#10B981"))

    def refrescar_sidebar(self):
        for w in self.scroll_historial.winfo_children(): w.destroy()
        for item in reversed(self.historial_datos):
            ctk.CTkButton(self.scroll_historial, text=f"[{item['status']}]\n{item['nombre'][:24]}", fg_color="#0F172A", height=46, command=lambda d=item: self.seleccionar_cancion(d)).pack(fill="x", pady=3, padx=2)

    def format_time(self, seconds):
        return f"{int(seconds // 60):02d}:{int(seconds % 60):02d}"

    def seleccionar_cancion(self, item):
        self.audio_actual = item
        self.bpm_val_label.configure(text=f"BPM: {item['bpm']}")
        self.badge_bpm_text.configure(text=item['status'])
        self.badge_bpm.configure(fg_color=item['bg'])
        self.info_bpm_text.configure(text=item['msg_bpm'])
        
        self.current_offset_val = item['offset'] if item['offset'] != "--" else 0
        
        if item['offset'] != "--":
            self.actualizar_lista_offsets()
        else:
            self.offset_val_label.configure(text="Offset: --")
            for w in self.offset_changes_scroll.winfo_children(): w.destroy()

        for w in self.changes_scroll.winfo_children(): w.destroy()
        secciones = item.get("secciones", [])
        if not secciones:
            if item['status'] == "FALLO":
                ctk.CTkLabel(self.changes_scroll, text="No se pudo procesar el archivo.", text_color="#EF4444").pack(pady=10)
            else:
                ctk.CTkLabel(self.changes_scroll, text="No se detectaron secciones de tempo.").pack(pady=10)
        else:
            for s, e, b in secciones:
                f = ctk.CTkFrame(self.changes_scroll, fg_color="#1E293B")
                f.pack(fill="x", pady=2, padx=2)
                ctk.CTkLabel(f, text=f"⏱️ {self.format_time(s)} - {self.format_time(e)}  ➔  {b} BPM", text_color="#38BDF8").pack(padx=10, pady=6, anchor="w")