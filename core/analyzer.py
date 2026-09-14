import logging
import numpy as np
import librosa
import warnings

warnings.filterwarnings('ignore', category=UserWarning)

class AudioAnalyzerEngine:
    @staticmethod
    def analizar_audio(ruta_archivo, analisis_rapido=False):
        try:
            duracion_max = 60.0 if analisis_rapido else None
            logging.info(f"Cargando audio: {ruta_archivo} (Rápido: {analisis_rapido})")
            
            try:
                y, sr = librosa.load(ruta_archivo, sr=22050, duration=duracion_max, mono=True)
            except Exception as load_err:
                raise ValueError(f"Fallo al decodificar: {load_err}")

            if len(y) == 0:
                raise ValueError("Archivo de audio vacío o ilegible.")

            total_duration = librosa.get_duration(y=y, sr=sr)
            onset_env = librosa.onset.onset_strength(y=y, sr=sr, aggregate=np.median)

            # 1. Motor de Consenso (Sin el parámetro max_tempo que causaba el crash)
            tempos_mult = librosa.feature.tempo(y=y, sr=sr, onset_envelope=onset_env, aggregate=None)
            
            if len(tempos_mult) > 0:
                tempos_validos = tempos_mult[tempos_mult > 40]
                estimado_primario = float(np.median(tempos_validos)) if len(tempos_validos) > 0 else 120.0
            else:
                estimado_primario = 120.0

            # Calculamos los beats usando el estimado primario
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, onset_envelope=onset_env, start_bpm=estimado_primario)
            beat_times = librosa.frames_to_time(beat_frames, sr=sr)

            if len(beat_times) < 2:
                raise ValueError("No se detectaron suficientes golpes rítmicos.")

            bpm_crudo = float(tempo[0] if isinstance(tempo, (np.ndarray, list)) else tempo)
            
            # 2. Corrección Inteligente de Octava Avanzada
            fuerza_promedio = np.mean(onset_env)
            
            if bpm_crudo < 150 and (estimado_primario > 200 or fuerza_promedio > 0.4):
                altos = tempos_validos[tempos_validos > bpm_crudo * 1.5]
                if len(altos) > 0 and np.median(altos) >= bpm_crudo * 1.8:
                    bpm_crudo *= 2.0
                    logging.info(f"Corrección de octava aplicada (Doble tempo): {bpm_crudo}")
            elif bpm_crudo < 80:
                bpm_crudo *= 2.0

            bpm = round(bpm_crudo, 2)
            offset_ms = int(round(beat_times[0] * 1000))

            # 3. Métricas de Confianza Adaptativa
            intervals = np.diff(beat_times) * 1000
            mean_interval = np.mean(intervals) if len(intervals) > 0 else 1.0
            cv = np.std(intervals) / mean_interval if mean_interval > 0 else 1.0

            estabilidad = max(0.0, min(100.0, (1.0 - min(cv, 1.0)) * 100))
            consistencia = max(0.0, min(100.0, fuerza_promedio * 100))
            confianza = round((estabilidad * 0.7) + (consistencia * 0.3), 1)

            if cv < 0.15 and fuerza_promedio > 0.3:
                status, bg = "PERFECT", "#10B981"
                msg_bpm = f"Ritmo sólidamente anclado a {bpm} BPM."
            elif cv < 0.30:
                status, bg = "UNSTABLE", "#F59E0B"
                msg_bpm = f"Variaciones rítmicas menores detectadas ({bpm} BPM)."
            else:
                status, bg = "WRONG", "#EF4444"
                msg_bpm = f"Tempo extremadamente variable o ambiguo ({bpm} BPM)."

            # 4. Generación Garantizada de Secciones (Timing Points)
            chunk_duration = 15.0
            raw_sections = []
            
            for cur_t in np.arange(0, total_duration, chunk_duration):
                s_sample = int(cur_t * sr)
                e_sample = int(min(cur_t + chunk_duration, total_duration) * sr)
                y_chunk = y[s_sample:e_sample]
                
                if len(y_chunk) > sr * 2:
                    try:
                        t_chunk, _ = librosa.beat.beat_track(y=y_chunk, sr=sr)
                        b_val = float(t_chunk[0] if isinstance(t_chunk, (np.ndarray, list)) else t_chunk)
                        
                        if abs(b_val * 2 - bpm) < 5.0:
                            b_val *= 2.0
                        elif abs(b_val / 2 - bpm) < 5.0:
                            b_val /= 2.0
                            
                        if b_val > 30:
                            raw_sections.append((cur_t, min(cur_t + chunk_duration, total_duration), round(b_val, 1)))
                    except Exception as e:
                        logging.debug(f"Salto en sección {cur_t}s: {e}")

            if not raw_sections:
                raw_sections.append((0.0, total_duration, bpm))

            # Consolidar bloques continuos
            secciones = []
            if raw_sections:
                c_start, c_end, c_bpm = raw_sections[0]
                for start, end, b in raw_sections[1:]:
                    if abs(b - c_bpm) < 4.0: 
                        c_end = end
                    else:
                        secciones.append((c_start, c_end, c_bpm))
                        c_start, c_end, c_bpm = start, end, b
                secciones.append((c_start, c_end, c_bpm))

            return {
                "bpm": bpm,
                "offset": offset_ms,
                "status": status,
                "bg": bg,
                "msg_bpm": f"{msg_bpm} | Confianza: {confianza}%",
                "msg_offset": "Offset inicial detectado.",
                "confianza": confianza,
                "secciones": secciones
            }

        except Exception as e:
            logging.error(f"Fallo crítico en {ruta_archivo}: {e}")
            return {"error": str(e)}