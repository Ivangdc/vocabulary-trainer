import streamlit as st
import pandas as pd
import random
from datetime import datetime
import json
import os
from collections import defaultdict

class VocabularyTrainer:
    def __init__(self):
        self.history = self.load_history()
        self.df = self.load_sample_data()  # En producción, esto se conectaría a Google Sheets

    @staticmethod
    def load_sample_data():
        # Datos de ejemplo - en producción, esto vendría de Google Sheets
        return pd.DataFrame({
            'español': ['perro', 'gato', 'casa', 'coche', 'libro'],
            'ingles': ['dog', 'cat', 'house', 'car', 'book'],
            'tematica': ['animales', 'animales', 'hogar', 'transporte', 'educación'],
            'comentarios': ['', '', '', '', '']
        })

    def load_history(self):
        if 'history' not in st.session_state:
            st.session_state.history = {}
        return st.session_state.history

    def save_history(self):
        st.session_state.history = self.history

    def get_available_topics(self):
        return sorted(self.df['tematica'].unique())

    def get_word_weight(self, word):
        if word not in self.history:
            return 1.0
        correct = self.history[word]['correct']
        total = self.history[word]['total']
        if total == 0:
            return 1.0
        success_rate = correct / total
        return 1.0 - success_rate

    def select_word(self, selected_topic=None):
        if selected_topic and selected_topic != "Todas las temáticas":
            topic_df = self.df[self.df['tematica'] == selected_topic]
            if topic_df.empty:
                return None
            weights = [self.get_word_weight(word) for word in topic_df['español']]
            word_index = random.choices(range(len(topic_df)), weights=weights)[0]
            return topic_df.iloc[word_index]
        else:
            weights = [self.get_word_weight(word) for word in self.df['español']]
            word_index = random.choices(range(len(self.df)), weights=weights)[0]
            return self.df.iloc[word_index]

    def reset_statistics(self):
        self.history = {}
        self.save_history()

def main():
    st.set_page_config(page_title="Entrenador de Vocabulario", page_icon="📚")
    
    st.title("📚 Entrenador de Vocabulario")
    
    trainer = VocabularyTrainer()
    
    # Sidebar
    st.sidebar.title("Menú")
    menu_option = st.sidebar.radio(
        "Elige una opción:",
        ["Practicar", "Estadísticas", "Resetear Estadísticas"]
    )
    
    if menu_option == "Practicar":
        st.header("Práctica")
        
        topics = ["Todas las temáticas"] + trainer.get_available_topics()
        selected_topic = st.selectbox("Elige una temática:", topics)
        
        if selected_topic == "Todas las temáticas":
            selected_topic = None
        
        if 'current_word' not in st.session_state:
            st.session_state.current_word = trainer.select_word(selected_topic)
        
        if st.session_state.current_word is not None:
            st.write(f"**Palabra en español:** {st.session_state.current_word['español']}")
            
            user_answer = st.text_input("Escribe la traducción en inglés:", key="answer_input")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Comprobar"):
                    if user_answer.lower() == st.session_state.current_word['ingles'].lower():
                        st.success("¡Correcto!")
                        # Actualizar estadísticas
                        word = st.session_state.current_word['español']
                        if word not in trainer.history:
                            trainer.history[word] = {'correct': 0, 'total': 0, 'tematica': st.session_state.current_word['tematica']}
                        trainer.history[word]['correct'] += 1
                        trainer.history[word]['total'] += 1
                    else:
                        st.error(f"Incorrecto. La respuesta correcta era: {st.session_state.current_word['ingles']}")
                        # Actualizar estadísticas
                        word = st.session_state.current_word['español']
                        if word not in trainer.history:
                            trainer.history[word] = {'correct': 0, 'total': 0, 'tematica': st.session_state.current_word['tematica']}
                        trainer.history[word]['total'] += 1
                    
                    trainer.save_history()
            
            with col2:
                if st.button("Siguiente palabra"):
                    st.session_state.current_word = trainer.select_word(selected_topic)
                    st.experimental_rerun()
    
    elif menu_option == "Estadísticas":
        st.header("Estadísticas")
        
        if not trainer.history:
            st.info("Aún no hay estadísticas disponibles.")
        else:
            tematica_stats = defaultdict(lambda: {'correct': 0, 'total': 0})
            
            for word, data in trainer.history.items():
                tematica = data.get('tematica', 'Sin temática')
                tematica_stats[tematica]['correct'] += data['correct']
                tematica_stats[tematica]['total'] += data['total']
            
            for tematica, stats in tematica_stats.items():
                correct = stats['correct']
                total = stats['total']
                success_rate = (correct / total * 100) if total > 0 else 0
                
                st.write(f"### {tematica}")
                col1, col2, col3 = st.columns(3)
                col1.metric("Correctas", correct)
                col2.metric("Total", total)
                col3.metric("Tasa de éxito", f"{success_rate:.1f}%")
                st.progress(success_rate / 100)
    
    elif menu_option == "Resetear Estadísticas":
        st.header("Resetear Estadísticas")
        
        st.warning("Esta acción eliminará todas tus estadísticas de manera permanente.")
        if st.button("Resetear estadísticas"):
            trainer.reset_statistics()
            st.success("Estadísticas reseteadas correctamente.")

if __name__ == "__main__":
    main()
